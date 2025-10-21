import json
import boto3
import os
import time

def handler(event, context):
    """
    Lambda unificada para Action Groups de Bedrock Agent
    """
    try:
        print(f"Event recibido: {json.dumps(event)}")
        
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
        
        # Extraer contenido del request body si existe
        body_content = {}
        if request_body and 'content' in request_body:
            for content_type, content in request_body['content'].items():
                if 'properties' in content:
                    for prop in content['properties']:
                        body_content[prop['name']] = prop['value']
        
        # Combinar parámetros y body
        all_params = {**params_dict, **body_content}
        
        # Enrutar según la operación
        if api_path == '/createPQR' and http_method == 'POST':
            result = create_pqr(all_params)
        elif api_path == '/checkPQR' and http_method == 'POST':
            result = check_pqr(all_params)
        else:
            result = {
                'error': f'Operación no soportada: {http_method} {api_path}'
            }
        
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
    try:
        # Validar parámetros requeridos
        required_fields = ['customer_email', 'description', 'priority', 'category']
        for field in required_fields:
            if field not in params or not params[field]:
                return {'error': f'Campo requerido faltante: {field}'}
        
        # Generar ID único
        pqr_id = f"pqr_{int(time.time())}"
        
        # Crear item para DynamoDB
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
        
        # Guardar en DynamoDB
        table.put_item(Item=item)
        
        return {
            'pqr_id': pqr_id,
            'status': 'CREADA',
            'message': 'PQR creada exitosamente'
        }
        
    except Exception as e:
        print(f"Error creando PQR: {str(e)}")
        return {'error': 'Error creando PQR'}

def check_pqr(params):
    """Consultar PQR existente"""
    try:
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
        
    except Exception as e:
        print(f"Error consultando PQR: {str(e)}")
        return {'error': 'Error consultando PQR'}
