# Novi PQR MVP - Diseño Técnico Optimizado

## 1. Resumen Ejecutivo

Sistema de gestión de PQR basado en Amazon Bedrock Agent con arquitectura serverless optimizada para implementación rápida en 3 semanas. Región: **us-west-2 (Oregon)**.

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Arquitectura
```
Cliente/Frontend
       ↓
API Gateway (REST)
       ↓
Lambda: invoke-agent (Python 3.12)
       ↓
Amazon Bedrock Agent (novi-agent)
       ↓
Action Groups (OpenAPI)
       ↓
Lambda Functions (create-pqr, check-pqr) - Python 3.12
       ↓
DynamoDB (Simplificado) + SNS (Email)
```

## 3. Esquema de DynamoDB Simplificado (us-west-2)

### 3.1 Tabla Principal: PQR
```json
{
  "TableName": "novi-pqr",
  "KeySchema": [
    {
      "AttributeName": "pqrId",
      "KeyType": "HASH"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "pqrId",
      "AttributeType": "S"
    }
  ],
  "BillingMode": "PAY_PER_REQUEST"
}
```

### 3.2 Estructura de Item PQR
```json
{
  "pqrId": "PQR-2024-001234",
  "customerName": "Juan Pérez",
  "customerEmail": "juan@email.com",
  "invoiceNumber": "INV-2024-5678",
  "category": "PEDIDO_INCOMPLETO",
  "description": "Mi pedido llegó incompleto, faltan 2 productos",
  "status": "CREADA",
  "createdAt": "2024-10-21T17:52:02Z",
  "updatedAt": "2024-10-21T17:52:02Z",
  "timeline": [
    {
      "timestamp": "2024-10-21T17:52:02Z",
      "status": "CREADA",
      "comment": "PQR creada automáticamente"
    }
  ]
}
```

## 4. Especificación API (OpenAPI)

### 4.1 Action Group OpenAPI para Bedrock Agent
```yaml
openapi: 3.0.0
info:
  title: Novi PQR API
  version: 1.0.0
paths:
  /pqr:
    post:
      summary: Crear nueva PQR
      operationId: createPQR
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - customerName
                - customerEmail
                - category
                - description
              properties:
                customerName:
                  type: string
                  description: Nombre completo del cliente
                customerEmail:
                  type: string
                  format: email
                  description: Email del cliente
                invoiceNumber:
                  type: string
                  description: Número de factura (opcional)
                category:
                  type: string
                  enum: [PEDIDO_INCOMPLETO, PRODUCTO_DEFECTUOSO, RETRASO_ENTREGA, PROBLEMA_FACTURACION, SOLICITUD_INFO, OTROS]
                description:
                  type: string
                  description: Descripción detallada del problema
      responses:
        '200':
          description: PQR creada exitosamente
  /pqr/{pqrId}:
    get:
      summary: Consultar estado de PQR
      operationId: checkPQR
      parameters:
        - name: pqrId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Estado de PQR
```

## 5. Código Lambda Functions (Python 3.12)

### 5.1 Lambda: invoke-agent
```python
import json
import boto3
import os

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

def lambda_handler(event, context):
    try:
        # Extraer texto del body
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        input_text = body.get('message', '')
        
        response = bedrock_agent.invoke_agent(
            agentId=os.environ['BEDROCK_AGENT_ID'],
            agentAliasId=os.environ['BEDROCK_AGENT_ALIAS_ID'],
            sessionId=context.aws_request_id,
            inputText=input_text
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response, default=str)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error procesando solicitud'})
        }
```

### 5.2 Lambda: create-pqr
```python
import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
sns = boto3.client('sns', region_name='us-west-2')
table = dynamodb.Table(os.environ['PQR_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Parsear payload
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Validar campos requeridos
        required_fields = ['customerName', 'customerEmail', 'category', 'description']
        for field in required_fields:
            if not body.get(field):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Campo requerido faltante: {field}'})
                }
        
        # Generar ID único
        pqr_id = f"PQR-{datetime.now().year}-{int(datetime.now().timestamp())}"
        timestamp = datetime.now().isoformat()
        
        # Crear item PQR
        pqr_item = {
            'pqrId': pqr_id,
            'customerName': body['customerName'],
            'customerEmail': body['customerEmail'],
            'invoiceNumber': body.get('invoiceNumber', ''),
            'category': body['category'],
            'description': body['description'],
            'status': 'CREADA',
            'createdAt': timestamp,
            'updatedAt': timestamp,
            'timeline': [
                {
                    'timestamp': timestamp,
                    'status': 'CREADA',
                    'comment': 'PQR creada automáticamente'
                }
            ]
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=pqr_item)
        
        # Enviar notificación email
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Subject=f'PQR Creada: {pqr_id}',
            Message=f"""Su PQR ha sido creada exitosamente.

Número de ticket: {pqr_id}
Estado: CREADA

Descripción: {body['description']}

Recibirá actualizaciones por email."""
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'pqrId': pqr_id,
                'status': 'CREADA',
                'nextSteps': 'Su PQR ha sido registrada. Recibirá actualizaciones por email.'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor'})
        }
```

### 5.3 Lambda: check-pqr
```python
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table(os.environ['PQR_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        pqr_id = event['pathParameters']['pqrId']
        
        # Consultar PQR
        response = table.get_item(Key={'pqrId': pqr_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'PQR no encontrada'})
            }
        
        pqr = response['Item']
        
        # Preparar respuesta
        result = {
            'pqrId': pqr['pqrId'],
            'status': pqr['status'],
            'createdAt': pqr['createdAt'],
            'updatedAt': pqr['updatedAt'],
            'timeline': pqr['timeline']
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error consultando PQR'})
        }
```

## 6. Configuración Bedrock Agent

### 6.1 Integración de FAQs con Jinja2

**Archivo CSV: @prompts/faqs-novi.csv**
```csv
pregunta,respuesta,categoria
"¿Cuánto tiempo tarda en procesarse una PQR?","Las PQR se procesan en un plazo de 24-48 horas hábiles","TIEMPOS"
"¿Puedo cancelar mi pedido?","Los pedidos pueden cancelarse hasta 2 horas después de realizado","CANCELACIONES"
"¿Cómo cambio mi dirección de entrega?","Contacta servicio al cliente antes del envío","ENTREGAS"
"¿Qué estados tiene una PQR?","CREADA → EN PROCESO → RESUELTA/RECHAZADA → CERRADA","ESTADOS"
```

**Lambda: process-faqs-template**
```python
import csv
import boto3
from jinja2 import Template
import os

def lambda_handler(event, context):
    # Leer CSV desde S3
    s3 = boto3.client('s3')
    csv_obj = s3.get_object(Bucket=os.environ['FAQS_BUCKET'], Key='prompts/faqs-novi.csv')
    csv_content = csv_obj['Body'].read().decode('utf-8')
    
    # Procesar CSV
    faqs = []
    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        faqs.append(row)
    
    # Template Jinja2
    template_str = """
Eres Novi, un asistente especializado en gestión de PQR para NovaMarket.

## Preguntas Frecuentes
{% for faq in faqs %}
**P: {{ faq.pregunta }}**
R: {{ faq.respuesta }}

{% endfor %}

## Funciones Principales
1. Responder preguntas usando las FAQs anteriores
2. Crear PQR solo si no está cubierto en FAQs
3. Consultar estado de PQR existentes

Reglas importantes:
- SIEMPRE consulta las FAQs antes de crear una PQR
- Si la pregunta está en las FAQs, responde directamente
- Solo crea PQR para problemas específicos no cubiertos
- Categoriza automáticamente según el problema reportado
"""
    
    template = Template(template_str)
    prompt_final = template.render(faqs=faqs)
    
    # Actualizar Bedrock Agent
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
    bedrock_agent.update_agent(
        agentId=os.environ['BEDROCK_AGENT_ID'],
        instruction=prompt_final
    )
    
    return {'statusCode': 200, 'body': f'Prompt actualizado con {len(faqs)} FAQs'}
```

### 6.2 Prompt del Agente (Generado por Template)
```
Eres Novi, un asistente especializado en gestión de PQR (Peticiones, Quejas y Reclamos) para NovaMarket.

Tu función es:
1. Ayudar a los clientes a crear PQR de manera clara y estructurada
2. Consultar el estado de PQR existentes
3. Proporcionar información sobre el proceso de resolución

Reglas importantes:
- Solo puedes crear PQR y consultar su estado
- Siempre solicita información completa: nombre, email, categoría y descripción
- Categoriza automáticamente según el problema reportado
- Mantén un tono profesional y empático
- No inventes información que no tengas

Categorías disponibles:
- PEDIDO_INCOMPLETO: Productos faltantes en el pedido
- PRODUCTO_DEFECTUOSO: Productos dañados o con fallas
- RETRASO_ENTREGA: Pedidos que no llegaron a tiempo
- PROBLEMA_FACTURACION: Errores en facturación o cobros
- SOLICITUD_INFO: Solicitudes de información general
- OTROS: Cualquier otro tipo de problema
```

## 7. Plan de Implementación (3 Semanas)

### Semana 1: Infraestructura Base
**Días 1-2:**
- Configurar DynamoDB table (simplificada)
- Crear Lambda functions en Python 3.12
- Configurar API Gateway

**Días 3-5:**
- Implementar create-pqr Lambda
- Implementar check-pqr Lambda
- Configurar SNS para emails
- Testing unitario básico

### Semana 2: Bedrock Agent + FAQs
**Días 6-7:**
- Crear Bedrock Agent en us-west-2
- Configurar S3 bucket para FAQs CSV
- Implementar process-faqs-template Lambda

**Días 8-9:**
- Configurar Action Groups con OpenAPI
- Implementar invoke-agent Lambda
- Procesar FAQs con Jinja2 y actualizar prompt

**Día 10:**
- Configurar Guardrails
- Testing de integración FAQs + PQR
- Ajustes de prompts

### Semana 3: Testing y Deployment
**Días 11-13:**
- Testing end-to-end
- Optimización de performance
- Documentación

**Días 14-15:**
- Deployment a producción
- Monitoreo inicial
- Ajustes finales

## 8. Estimación de Costos AWS (Mensual) - us-west-2

### 8.1 Supuestos de Uso
- 1,000 PQR creadas por mes
- 3,000 consultas de estado por mes
- 50 usuarios activos por día

### 8.2 Costos Detallados

**Amazon Bedrock (us-west-2)**
- Claude 3.5 Sonnet: ~$0.003 por 1K tokens
- Estimado: 2K tokens por interacción
- 4,000 interacciones/mes × 2K tokens × $0.003/1K = $24.00

**Lambda Functions (Python 3.12)**
- 5,000 invocaciones/mes × $0.0000002 = $0.001
- Compute time: 5,000 × 200ms × $0.0000166667 = $0.17

**S3 (FAQs Storage)**
- Storage: 1MB × $0.023/GB = $0.000023
- Requests: 100 × $0.0004/1K = $0.00004

**DynamoDB (Pay-per-request)**
- 1,000 writes × $1.25/million = $0.00125
- 3,000 reads × $0.25/million = $0.00075
- Storage: 1GB × $0.25 = $0.25

**API Gateway**
- 4,000 requests × $3.50/million = $0.014

**SNS**
- 1,000 emails × $0.50/1,000 = $0.50

**Total Estimado: ~$25.00/mes**

## 9. Estrategia de Testing

### 9.1 Testing Unitario (Python)
```python
import pytest
import json
from moto import mock_dynamodb, mock_sns
from create_pqr import lambda_handler

@mock_dynamodb
@mock_sns
def test_create_pqr_success():
    # Setup mock DynamoDB table
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.create_table(
        TableName='test-pqr-table',
        KeySchema=[{'AttributeName': 'pqrId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'pqrId', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Test event
    event = {
        'body': json.dumps({
            'customerName': 'Test User',
            'customerEmail': 'test@email.com',
            'category': 'PEDIDO_INCOMPLETO',
            'description': 'Test description'
        })
    }
    
    # Mock environment
    import os
    os.environ['PQR_TABLE_NAME'] = 'test-pqr-table'
    os.environ['SNS_TOPIC_ARN'] = 'arn:aws:sns:us-west-2:123456789012:test-topic'
    
    # Execute
    result = lambda_handler(event, None)
    
    # Assert
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert 'pqrId' in body
    assert body['status'] == 'CREADA'

def test_create_pqr_missing_fields():
    event = {
        'body': json.dumps({
            'customerName': 'Test User'
            # Missing required fields
        })
    }
    
    result = lambda_handler(event, None)
    assert result['statusCode'] == 400
```

## 10. Optimizaciones Implementadas

### 10.1 DynamoDB Simplificado
- **Eliminado GSI**: Sin índices secundarios para reducir complejidad
- **Pay-per-request**: Sin provisioning de capacidad
- **Consultas simples**: Solo por pqrId (clave primaria)

### 10.2 Python 3.12 Runtime
- **Mejor performance**: Runtime más eficiente que Node.js para este caso
- **Sintaxis simple**: Código más legible y mantenible
- **Boto3 nativo**: SDK AWS optimizado para Python

### 10.3 Región us-west-2
- **Costos optimizados**: Oregon tiene precios competitivos
- **Latencia**: Buena para usuarios en América
- **Disponibilidad de servicios**: Bedrock disponible

## 12. Infrastructure as Code (CDK)

### 12.1 Stack Principal: NoviPqrStack
```typescript
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';

export class NoviPqrStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const pqrTable = new dynamodb.Table(this, 'NoviPqrTable', {
      tableName: 'novi-pqr',
      partitionKey: { name: 'pqrId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // S3 Bucket para FAQs
    const faqsBucket = new s3.Bucket(this, 'NoviPqrFaqsBucket', {
      bucketName: 'novi-pqr-faqs-bucket',
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // SNS Topic
    const notificationTopic = new sns.Topic(this, 'NoviPqrNotifications', {
      topicName: 'novi-pqr-notifications'
    });

    // Lambda Functions
    const createPqrFunction = new lambda.Function(this, 'CreatePqrFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'create_pqr.lambda_handler',
      code: lambda.Code.fromAsset('lambda/create-pqr'),
      environment: {
        PQR_TABLE_NAME: pqrTable.tableName,
        SNS_TOPIC_ARN: notificationTopic.topicArn
      }
    });

    const checkPqrFunction = new lambda.Function(this, 'CheckPqrFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'check_pqr.lambda_handler',
      code: lambda.Code.fromAsset('lambda/check-pqr'),
      environment: {
        PQR_TABLE_NAME: pqrTable.tableName
      }
    });

    const processFaqsFunction = new lambda.Function(this, 'ProcessFaqsFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'process_faqs.lambda_handler',
      code: lambda.Code.fromAsset('lambda/process-faqs'),
      environment: {
        FAQS_BUCKET: faqsBucket.bucketName,
        BEDROCK_AGENT_ID: 'PLACEHOLDER' // Se configura manualmente
      }
    });

    const invokeAgentFunction = new lambda.Function(this, 'InvokeAgentFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'invoke_agent.lambda_handler',
      code: lambda.Code.fromAsset('lambda/invoke-agent'),
      environment: {
        BEDROCK_AGENT_ID: 'PLACEHOLDER',
        BEDROCK_AGENT_ALIAS_ID: 'PLACEHOLDER'
      }
    });

    // Permisos
    pqrTable.grantReadWriteData(createPqrFunction);
    pqrTable.grantReadData(checkPqrFunction);
    notificationTopic.grantPublish(createPqrFunction);
    faqsBucket.grantRead(processFaqsFunction);

    // Permisos Bedrock
    const bedrockPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:InvokeAgent',
        'bedrock:UpdateAgent'
      ],
      resources: ['*']
    });
    
    invokeAgentFunction.addToRolePolicy(bedrockPolicy);
    processFaqsFunction.addToRolePolicy(bedrockPolicy);

    // API Gateway
    const api = new apigateway.RestApi(this, 'NoviPqrApi', {
      restApiName: 'Novi PQR API',
      description: 'API para gestión de PQR con Bedrock Agent'
    });

    // Endpoints
    const pqrResource = api.root.addResource('pqr');
    pqrResource.addMethod('POST', new apigateway.LambdaIntegration(createPqrFunction));
    
    const pqrIdResource = pqrResource.addResource('{pqrId}');
    pqrIdResource.addMethod('GET', new apigateway.LambdaIntegration(checkPqrFunction));

    // Endpoint principal para agente
    const agentResource = api.root.addResource('agent');
    agentResource.addMethod('POST', new apigateway.LambdaIntegration(invokeAgentFunction));

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'URL de la API'
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: pqrTable.tableName,
      description: 'Nombre de la tabla DynamoDB'
    });
  }
}
```

### 12.2 Estructura de Directorios CDK
```
novi-backend/
├── cdk/
│   ├── app.ts
│   ├── lib/
│   │   └── novi-pqr-stack.ts
│   ├── lambda/
│   │   ├── create-pqr/
│   │   │   ├── create_pqr.py
│   │   │   └── requirements.txt
│   │   ├── check-pqr/
│   │   │   ├── check_pqr.py
│   │   │   └── requirements.txt
│   │   ├── invoke-agent/
│   │   │   ├── invoke_agent.py
│   │   │   └── requirements.txt
│   │   └── process-faqs/
│   │       ├── process_faqs.py
│   │       └── requirements.txt
│   ├── package.json
│   ├── tsconfig.json
│   └── cdk.json
└── README.md
```

### 12.3 Comandos de Deployment
```bash
# Instalar dependencias
npm install

# Compilar TypeScript
npm run build

# Sintetizar template CloudFormation
cdk synth

# Desplegar stack
cdk deploy NoviPqrStack

# Destruir stack (desarrollo)
cdk destroy NoviPqrStack
```

---

## 13. Próximos Pasos Post-MVP

### 11.1 Mejoras Inmediatas (Mes 2)
- Agregar GSI para consultas por email si es necesario
- Dashboard web para consultas
- Notificaciones SMS via SNS

### 11.2 Funcionalidades Avanzadas (Mes 3-6)
- Chatbot web integrado
- Categorización con ML
- Analytics y reportes

---

**Documento optimizado para implementación rápida del MVP Novi PQR**
