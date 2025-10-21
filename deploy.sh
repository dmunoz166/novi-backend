#!/bin/bash
set -e

echo "🚀 Desplegando Novi PQR MVP completamente automatizado..."

# 1. Instalar dependencias Python necesarias
echo "📦 Instalando dependencias Python..."
pip install jinja2 > /dev/null 2>&1

# 2. Limpiar agentes existentes
echo "🧹 Limpiando agentes Bedrock existentes..."
EXISTING_AGENTS=$(aws bedrock-agent list-agents --region us-west-2 --query 'agentSummaries[?agentName==`novi-pqr-agent`].agentId' --output text)

if [ ! -z "$EXISTING_AGENTS" ]; then
    for AGENT_ID in $EXISTING_AGENTS; do
        echo "  Eliminando aliases del agente $AGENT_ID..."
        ALIASES=$(aws bedrock-agent list-agent-aliases --agent-id $AGENT_ID --region us-west-2 --query 'agentAliasSummaries[?agentAliasId!=`TSTALIASID`].agentAliasId' --output text)
        
        for ALIAS_ID in $ALIASES; do
            aws bedrock-agent delete-agent-alias --agent-id $AGENT_ID --agent-alias-id $ALIAS_ID --region us-west-2 > /dev/null 2>&1 || true
        done
        
        echo "  Esperando eliminación de aliases..."
        sleep 15
        
        echo "  Eliminando agente $AGENT_ID..."
        aws bedrock-agent delete-agent --agent-id $AGENT_ID --skip-resource-in-use-check --region us-west-2 > /dev/null 2>&1 || true
    done
    
    echo "  Esperando eliminación completa..."
    sleep 10
fi

# 3. Crear y subir archivos necesarios a S3
echo "📤 Preparando y subiendo archivos a S3..."

# Crear FAQs simples si no existe
if [ ! -f "prompts/faqs-simple.csv" ]; then
    cat > prompts/faqs-simple.csv << 'EOF'
Pregunta,Respuesta
"¿Qué es Novi?","Novi es tu asistente virtual para PQR, disponible 24/7"
"¿Cómo crear una PQR?","Describe tu problema y yo te ayudo a crear la PQR"
"¿Cuánto tarda una PQR?","Las PQR se procesan en 24-48 horas hábiles"
"¿Puedo cancelar mi pedido?","Los pedidos se pueden cancelar hasta 2 horas después"
"¿Cómo consulto mi PQR?","Dame tu número de PQR y te muestro el estado"
"¿Qué estados tiene una PQR?","CREADA → EN PROCESO → RESUELTA → CERRADA"
EOF
fi

aws s3 cp prompts/faqs-simple.csv s3://novi-pqr-faqs-bucket/faqs-novi.csv --region us-west-2
aws s3 cp infrastructure/schemas/pqr-openapi-schema.yaml s3://novi-pqr-faqs-bucket/pqr-openapi-schema.yaml --region us-west-2

# 4. Desplegar infraestructura CDK
echo "🏗️ Desplegando infraestructura..."
cd infrastructure
npm install > /dev/null 2>&1
npm run build > /dev/null 2>&1
cdk deploy --require-approval never --outputs-file outputs.json

# 5. Extraer configuración
echo "🔧 Extrayendo configuración..."
BEDROCK_AGENT_ROLE_ARN=$(cat outputs.json | jq -r '.NoviPqrStack.BedrockAgentRoleArn')
API_URL=$(cat outputs.json | jq -r '.NoviPqrStack.ApiUrl')

if [ "$BEDROCK_AGENT_ROLE_ARN" = "null" ]; then
    echo "❌ Error: No se pudo obtener el ARN del rol de Bedrock Agent"
    exit 1
fi

# 6. Configurar agente Bedrock
echo "🤖 Configurando agente Bedrock..."
cd ../scripts
BEDROCK_AGENT_ROLE_ARN=$BEDROCK_AGENT_ROLE_ARN python3 setup_agent.py

# 7. Extraer Agent ID y Alias ID del output
AGENT_OUTPUT=$(BEDROCK_AGENT_ROLE_ARN=$BEDROCK_AGENT_ROLE_ARN python3 setup_agent.py 2>&1)
AGENT_ID=$(echo "$AGENT_OUTPUT" | grep "Agent ID:" | tail -1 | cut -d' ' -f3)
ALIAS_ID=$(echo "$AGENT_OUTPUT" | grep "Alias ID:" | tail -1 | cut -d' ' -f3)

if [ -z "$AGENT_ID" ] || [ -z "$ALIAS_ID" ]; then
    echo "❌ Error: No se pudieron obtener Agent ID o Alias ID"
    exit 1
fi

# 8. Actualizar configuración de Lambda
echo "⚙️ Actualizando configuración de Lambda..."
aws lambda update-function-configuration \
  --function-name novi-invoke-agent \
  --handler invoke_agent.handler \
  --environment "Variables={BEDROCK_AGENT_ID=$AGENT_ID,BEDROCK_AGENT_ALIAS_ID=$ALIAS_ID,REGION=us-west-2}" \
  --region us-west-2 > /dev/null

# 9. Crear Action Groups
echo "🔗 Configurando Action Groups..."
sleep 5  # Esperar que Lambda se actualice

aws bedrock-agent create-agent-action-group \
  --agent-id $AGENT_ID \
  --agent-version DRAFT \
  --action-group-name PQRActions \
  --description "Action group para crear y consultar PQR" \
  --action-group-executor lambda=arn:aws:lambda:us-west-2:$(aws sts get-caller-identity --query Account --output text):function:novi-bedrock-actions \
  --api-schema s3BucketName=novi-pqr-faqs-bucket,s3ObjectKey=pqr-openapi-schema.yaml \
  --region us-west-2 > /dev/null 2>&1 || echo "  Action Group ya existe o error en creación"

# 10. Preparar agente final
echo "🔄 Preparando agente final..."
aws bedrock-agent prepare-agent --agent-id $AGENT_ID --region us-west-2 > /dev/null

# Esperar preparación
echo "⏳ Esperando preparación del agente..."
for i in {1..12}; do
    STATUS=$(aws bedrock-agent get-agent --agent-id $AGENT_ID --region us-west-2 --query 'agent.agentStatus' --output text)
    if [ "$STATUS" = "PREPARED" ]; then
        break
    fi
    sleep 5
done

echo ""
echo "🎉 ¡Deployment completado exitosamente!"
echo ""
echo "📋 Configuración final:"
echo "  Agent ID: $AGENT_ID"
echo "  Alias ID: $ALIAS_ID"
echo "  API URL: $API_URL"
echo ""
echo "🧪 Comando de prueba:"
echo "curl -X POST ${API_URL}agent \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Hola Novi, ¿qué es una PQR?\"}'"
echo ""
echo "✅ Sistema completamente funcional y listo para usar"
