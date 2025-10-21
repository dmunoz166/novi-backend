import json
import boto3
import os
from typing import Dict, Any
from botocore.exceptions import ClientError

# Cliente DynamoDB - inicialización simple
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table_name = os.environ.get('PQR_TABLE_NAME', 'novi-pqr-table')
table = dynamodb.Table(table_name)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Función Lambda para consultar PQRs
    Siguiendo principio de simplicidad-first
    """
    print(f"Evento recibido: {json.dumps(event)}")
    
    try:
        # Obtener PQR ID del path parameter
        pqr_id = None
        if 'pathParameters' in event and event['pathParameters']:
            pqr_id = event['pathParameters'].get('pqr_id')
        
        if not pqr_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'pqr_id es requerido en el path'
                })
            }
        
        print(f"Consultando PQR: {pqr_id}")
        
        # Consultar DynamoDB
        response = table.get_item(
            Key={'pqr_id': pqr_id}
        )
        
        # Verificar si el item existe
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'PQR no encontrada',
                    'pqr_id': pqr_id
                })
            }
        
        # Obtener el item
        pqr_item = response['Item']
        
        # Preparar respuesta - solo campos necesarios para simplicidad
        pqr_data = {
            'pqr_id': pqr_item['pqr_id'],
            'customer_email': pqr_item['customer_email'],
            'description': pqr_item['description'],
            'status': pqr_item['status'],
            'priority': pqr_item.get('priority', 'MEDIA'),
            'category': pqr_item.get('category', 'GENERAL'),
            'created_at': pqr_item['created_at'],
            'updated_at': pqr_item['updated_at']
        }
        
        # Respuesta exitosa
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS simple para MVP
            },
            'body': json.dumps({
                'message': 'PQR encontrada',
                'pqr': pqr_data
            })
        }
        
        print(f"PQR consultada exitosamente: {pqr_id}")
        return response
        
    except ClientError as e:
        print(f"Error de DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error consultando la base de datos',
                'details': str(e)  # Para debugging en MVP
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
