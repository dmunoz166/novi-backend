#!/bin/bash
set -e

echo "🚀 Desplegando Novi PQR MVP..."

# 1. Instalar dependencias y build CDK
echo "📦 Instalando dependencias CDK..."
cd infrastructure
npm install
npm run build

# 2. Desplegar infraestructura CDK
echo "🏗️ Desplegando infraestructura..."
cdk deploy --require-approval never --outputs-file outputs.json

# 3. Extraer ARN del rol de Bedrock Agent
echo "🔧 Extrayendo configuración..."
BEDROCK_AGENT_ROLE_ARN=$(cat outputs.json | jq -r '.NoviPqrStack.BedrockAgentRoleArn')

if [ "$BEDROCK_AGENT_ROLE_ARN" = "null" ]; then
    echo "❌ Error: No se pudo obtener el ARN del rol de Bedrock Agent"
    exit 1
fi

echo "✅ Rol de Bedrock Agent: $BEDROCK_AGENT_ROLE_ARN"

# 4. Configurar agente Bedrock
echo "🤖 Configurando agente Bedrock..."
cd ../scripts
BEDROCK_AGENT_ROLE_ARN=$BEDROCK_AGENT_ROLE_ARN python3 setup_agent.py

# 5. Obtener Agent ID y Alias ID del output del script
# (El script debería imprimir estos valores)

echo "🎉 ¡Deployment completado!"
echo ""
echo "Para probar:"
echo "curl -X POST \$(cat infrastructure/outputs.json | jq -r '.NoviPqrStack.ApiUrl')agent \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Hola Novi\"}'"
