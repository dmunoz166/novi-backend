#!/usr/bin/env python3
"""
Script para configurar el agente Bedrock de Novi con todas las configuraciones necesarias.
Automatiza la creación, configuración completa del agente y procesamiento de FAQs.
"""

import boto3
import json
import time
import sys
import csv
import os
from io import StringIO
from botocore.exceptions import ClientError
from jinja2 import Template

# Configuración
REGION = 'us-west-2'
AGENT_NAME = 'novi-pqr-agent'
AGENT_ROLE_ARN = os.environ.get('BEDROCK_AGENT_ROLE_ARN', 'arn:aws:iam::436187211477:role/NoviPqrStack-BedrockAgentRole7C982E0C-9YfNYqr9Ak5a')
FOUNDATION_MODEL = 'arn:aws:bedrock:us-west-2:436187211477:inference-profile/us.amazon.nova-pro-v1:0'
FAQS_BUCKET = 'novi-pqr-faqs-bucket'
FAQS_KEY = 'faqs-novi.csv'  # Archivo ya subido a S3 desde prompts/

# Clientes AWS
bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)

def process_faqs():
    """Procesar FAQs desde S3 y generar instrucciones"""
    try:
        print("📋 Procesando FAQs desde S3...")
        
        # Leer CSV desde S3
        csv_obj = s3.get_object(Bucket=FAQS_BUCKET, Key=FAQS_KEY)
        csv_content = csv_obj['Body'].read().decode('utf-8')
        
        # Procesar CSV
        faqs = []
        reader = csv.DictReader(StringIO(csv_content))
        current_category = "GENERAL"
        
        for row in reader:
            pregunta = row.get('Pregunta', '') or ''
            respuesta = row.get('Respuesta', '') or ''
            
            # Verificar si es una línea de categoría
            if respuesta.strip() == '' and pregunta.strip() != '':
                current_category = pregunta.strip('"')
                continue
            
            # Verificar si es una FAQ válida
            if pregunta.strip() and respuesta.strip():
                faqs.append({
                    'pregunta': pregunta.strip('"'),
                    'respuesta': respuesta.strip('"'),
                    'categoria': current_category
                })
        
        print(f"✅ Procesadas {len(faqs)} FAQs")
        
        # Template Jinja2 para instrucciones del agente
        template_str = """Eres Novi, un asistente especializado en gestión de PQR (Peticiones, Quejas y Reclamos) para NovaMarket.

## Preguntas Frecuentes
{% for faq in faqs %}
**P: {{ faq.pregunta }}**
R: {{ faq.respuesta }}

{% endfor %}

## Funciones Principales
1. **PRIMERO**: Consultar las FAQs anteriores para responder preguntas comunes
2. **SEGUNDO**: Crear PQR solo si no está cubierto en FAQs
3. **TERCERO**: Consultar estado de PQR existentes

## Reglas Importantes
- SIEMPRE consulta las FAQs antes de crear una PQR
- Si la pregunta está en las FAQs, responde directamente SIN crear PQR
- Solo crea PQR para problemas específicos no cubiertos en FAQs
- Para crear PQR necesitas: customer_email, description, priority (ALTA/MEDIA/BAJA), category (PEDIDOS/GENERAL/SOPORTE/FACTURACION)
- Si falta información, solicítala al usuario antes de crear la PQR
- Mantén un tono profesional y empático

## Categorías de PQR
- PEDIDOS: Problemas con pedidos (incompletos, defectuosos, retrasos)
- GENERAL: Consultas generales sobre productos o servicios
- SOPORTE: Problemas técnicos o de soporte
- FACTURACION: Problemas con facturación o pagos

## Prioridades
- ALTA: Problemas críticos que afectan el servicio
- MEDIA: Problemas importantes pero no críticos
- BAJA: Consultas o problemas menores"""
        
        # Generar prompt final
        template = Template(template_str)
        instruction = template.render(faqs=faqs)
        
        return instruction, len(faqs)
        
    except Exception as e:
        print(f"❌ Error procesando FAQs: {e}")
        return None, 0

def create_agent():
    """Crear agente Bedrock con FAQs integradas"""
    try:
        # Procesar FAQs primero
        instruction, faqs_count = process_faqs()
        if not instruction:
            print("⚠️ Usando instrucciones básicas sin FAQs")
            instruction = """Eres Novi, asistente especializado en gestión de PQR para NovaMarket.
Ayuda a crear PQR y consultar su estado. Mantén un tono profesional y empático."""
        
        response = bedrock_agent.create_agent(
            agentName=AGENT_NAME,
            foundationModel=FOUNDATION_MODEL,
            instruction=instruction,
            agentResourceRoleArn=AGENT_ROLE_ARN,
            idleSessionTTLInSeconds=600
        )
        
        agent_id = response['agent']['agentId']
        print(f"✅ Agente creado: {agent_id} (con {faqs_count} FAQs)")
        return agent_id
        
    except ClientError as e:
        print(f"❌ Error creando agente: {e}")
        return None

def create_agent_alias(agent_id):
    """Crear alias para el agente"""
    try:
        response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName='AgentTestAlias',
            routingConfiguration=[
                {
                    'agentVersion': 'DRAFT'
                }
            ]
        )
        
        alias_id = response['agentAlias']['agentAliasId']
        print(f"✅ Alias creado: {alias_id}")
        return alias_id
        
    except ClientError as e:
        print(f"❌ Error creando alias: {e}")
        return None

def prepare_agent(agent_id):
    """Preparar agente"""
    try:
        response = bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"✅ Agente preparado: {response['agentStatus']}")
        
        # Esperar a que esté listo
        while True:
            status_response = bedrock_agent.get_agent(agentId=agent_id)
            status = status_response['agent']['agentStatus']
            print(f"Estado del agente: {status}")
            
            if status == 'PREPARED':
                break
            elif status == 'FAILED':
                print("❌ Preparación falló")
                return False
                
            time.sleep(5)
        
        return True
        
    except ClientError as e:
        print(f"❌ Error preparando agente: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Configurando agente Bedrock de Novi con FAQs...")
    
    # Crear agente
    agent_id = create_agent()
    if not agent_id:
        sys.exit(1)
    
    # Preparar agente
    if not prepare_agent(agent_id):
        sys.exit(1)
    
    # Crear alias
    alias_id = create_agent_alias(agent_id)
    if not alias_id:
        sys.exit(1)
    
    print(f"""
🎉 ¡Configuración completada!

Agent ID: {agent_id}
Alias ID: {alias_id}
Región: {REGION}
Modelo: Amazon Nova Pro
FAQs: Integradas desde S3

Para probar:
curl -X POST https://your-api-gateway-url/agent \\
  -H "Content-Type: application/json" \\
  -d '{{"message": "Hola Novi"}}'
""")

if __name__ == "__main__":
    main()
