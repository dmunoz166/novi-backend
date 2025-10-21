import json
import boto3
import uuid
import os
from datetime import datetime
from typing import Dict, Any

# Cliente DynamoDB - inicialización simple
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table_name = os.environ.get('PQR_TABLE_NAME', 'novi-pqr-table')
table = dynamodb.Table(table_name)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Función Lambda para crear PQRs
    Siguiendo principio de simplicidad-first
    """
    print(f"Evento recibido: {json.dumps(event)}")
    
    try:
        # Parsear el body del request
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Validación básica - simplicidad primero
        customer_email = body.get('customer_email')
        description = body.get('description')
        
        if not customer_email:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'customer_email es requerido'
                })
            }
        
        if not description:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'description es requerida'
                })
            }
        
        # Generar PQR ID único
        pqr_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Crear item para DynamoDB - estructura simple
        pqr_item = {
            'pqr_id': pqr_id,
            'customer_email': customer_email,
            'description': description,
            'status': 'CREADA',
            'created_at': timestamp,
            'updated_at': timestamp,
            'priority': body.get('priority', 'MEDIA'),  # Valor por defecto
            'category': body.get('category', 'GENERAL')  # Valor por defecto
        }
        
        # Guardar en DynamoDB
        print(f"Guardando PQR en DynamoDB: {pqr_id}")
        table.put_item(Item=pqr_item)
        
        # Respuesta exitosa
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS simple para MVP
            },
            'body': json.dumps({
                'message': 'PQR creada exitosamente',
                'pqr_id': pqr_id,
                'status': 'CREADA',
                'created_at': timestamp
            })
        }
        
        print(f"PQR creada exitosamente: {pqr_id}")
        return response
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'JSON inválido en el body del request'
            })
        }
    
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)  # Para debugging en MVP
            })
        }
