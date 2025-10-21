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
Amazon Bedrock Agent (novi-agent) - Amazon Nova Pro
       ↓
Action Groups (OpenAPI)
       ↓
Lambda: bedrock-actions (Unificada) - Python 3.12
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

### 5.1 Lambda: invoke-agent (Proxy Bedrock)
```python
import json
import boto3
import hashlib
import os

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

def lambda_handler(event, context):
    try:
        # Extraer texto del body
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        input_text = body.get('message', '')
        
        # Session management con IP + User-Agent
        ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
        user_agent = event.get('headers', {}).get('User-Agent', 'unknown')
        session_id = hashlib.md5(f"{ip}-{user_agent}".encode()).hexdigest()[:16]
        
        response = bedrock_agent.invoke_agent(
            agentId=os.environ['BEDROCK_AGENT_ID'],
            agentAliasId=os.environ['BEDROCK_AGENT_ALIAS_ID'],
            sessionId=session_id,
            inputText=input_text
        )
        
        # Procesar EventStream
        result = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'response': result})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error procesando solicitud'})
        }
```

### 5.2 Lambda: bedrock-actions (Action Groups Unificadas)
```python
import json
import boto3
import os
import time

def handler(event, context):
    """Lambda unificada para Action Groups de Bedrock Agent"""
    try:
        # Extraer información del evento de Bedrock Agent
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', '')
        parameters = event.get('parameters', [])
        request_body = event.get('requestBody', {})
        
        # Convertir parámetros a diccionario
        params_dict = {}
        for param in parameters:
            params_dict[param['name']] = param['value']
        
        # Extraer contenido del request body
        body_content = {}
        if request_body and 'content' in request_body:
            for content_type, content in request_body['content'].items():
                if 'properties' in content:
                    for prop in content['properties']:
                        body_content[prop['name']] = prop['value']
        
        # Combinar parámetros
        all_params = {**params_dict, **body_content}
        
        # Enrutar según la operación
        if api_path == '/createPQR' and http_method == 'POST':
            result = create_pqr(all_params)
        elif api_path == '/checkPQR' and http_method == 'POST':
            result = check_pqr(all_params)
        else:
            result = {'error': f'Operación no soportada: {http_method} {api_path}'}
        
        # Formato de respuesta para Bedrock Agent
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': http_method,
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"Error en bedrock_actions: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': http_method,
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({'error': 'Error interno del servidor'})
                    }
                }
            }
        }

def create_pqr(params):
    """Crear nueva PQR"""
    # Validar parámetros requeridos
    required_fields = ['customer_email', 'description', 'priority', 'category']
    for field in required_fields:
        if field not in params or not params[field]:
            return {'error': f'Campo requerido faltante: {field}'}
    
    # Generar ID único y guardar en DynamoDB
    pqr_id = f"pqr_{int(time.time())}"
    dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
    table = dynamodb.Table(os.environ['PQR_TABLE_NAME'])
    
    item = {
        'pqr_id': pqr_id,
        'customer_email': params['customer_email'],
        'description': params['description'],
        'priority': params['priority'],
        'category': params['category'],
        'status': 'CREADA',
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    
    table.put_item(Item=item)
    
    return {
        'pqr_id': pqr_id,
        'status': 'CREADA',
        'message': 'PQR creada exitosamente'
    }

def check_pqr(params):
    """Consultar PQR existente"""
    pqr_id = params.get('pqr_id')
    if not pqr_id:
        return {'error': 'pqr_id requerido'}
    
    # Consultar DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
    table = dynamodb.Table(os.environ['PQR_TABLE_NAME'])
    
    response = table.get_item(Key={'pqr_id': pqr_id})
    
    if 'Item' not in response:
        return {'error': 'PQR no encontrada'}
    
    item = response['Item']
    return {
        'pqr_id': item['pqr_id'],
        'customer_email': item['customer_email'],
        'description': item['description'],
        'status': item['status'],
        'created_at': item['created_at']
    }
```

## 6. Configuración Bedrock Agent (CDK)

### 6.1 Recurso bedrock.CfnAgent en CDK
```typescript
const bedrockAgent = new bedrock.CfnAgent(this, 'NoviAgent', {
  agentName: 'novi-pqr-agent',
  description: 'Agente para gestión de PQR de NovaMarket',
  foundationModel: 'arn:aws:bedrock:us-west-2:436187211477:inference-profile/us.amazon.nova-pro-v1:0',
  instruction: 'Eres Novi, asistente de PQR para NovaMarket...',
  agentResourceRoleArn: bedrockAgentRole.roleArn,
  autoPrepare: true,
  actionGroups: [{
    actionGroupName: 'pqr-actions',
    description: 'Acciones para crear y consultar PQR',
    apiSchema: {
      s3: {
        s3BucketName: openApiSchemaBucket.bucketName,
        s3ObjectKey: 'openapi-schema.yaml'
      }
    },
    actionGroupExecutor: {
      lambda: bedrockActionsFunction.functionArn
    }
  }]
});
```

### 6.2 Integración de FAQs con Jinja2

**Archivo CSV: prompts/faqs-novi.csv**
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
