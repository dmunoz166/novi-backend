import json
import boto3
import os
import uuid
import logging
import hashlib
from botocore.exceptions import ClientError
from botocore.config import Config

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente Bedrock Agent Runtime con timeouts amplios
try:
    bedrock_agent_runtime_config = Config(
        read_timeout=900,
        connect_timeout=900,
        retries={'max_attempts': 0}
    )
    bedrock_agent_runtime = boto3.client(
        'bedrock-agent-runtime',
        region_name='us-west-2',
        config=bedrock_agent_runtime_config
    )
except Exception as e:
    logger.error(f"Error inicializando cliente bedrock-agent-runtime: {str(e)}")
    raise e

def get_session_id(event):
    """Genera session_id persistente basado en el cliente"""
    try:
        # Opción 1: Usar session_id del body si existe
        body = json.loads(event.get('body', '{}'))
        if body.get('session_id'):
            return body['session_id']
        
        # Opción 2: Generar basado en IP + User-Agent
        ip = event['requestContext']['identity']['sourceIp']
        user_agent = event['headers'].get('User-Agent', '')
        
        # Crear hash único pero consistente
        session_data = f"{ip}-{user_agent}"
        session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
        
        return f"session-{session_id}"
        
    except Exception as e:
        logger.warning(f"Error generando session_id: {str(e)}")
        # Fallback: usar request ID
        return event.get('requestContext', {}).get('requestId', str(uuid.uuid4()))

def _response_http(status_code, body_dict):
    """Construye respuesta HTTP JSON con CORS"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body_dict, default=str)
    }

def _invoke_agent_and_parse_stream(agent_id, agent_alias_id, session_id, input_text):
    """Invoca agente Bedrock y procesa el stream"""
    final_text = ""
    
    invoke_params = {
        'agentId': agent_id,
        'agentAliasId': agent_alias_id,
        'sessionId': session_id,
        'inputText': input_text,
        'enableTrace': False
    }
    
    logger.info(f"Invocando agente: {agent_id}/{agent_alias_id}")
    
    try:
        response = bedrock_agent_runtime.invoke_agent(**invoke_params)
    except ClientError as e:
        logger.error(f"Error en invoke_agent: {str(e)}")
        raise
    
    # Procesar stream de respuesta
    for event in response['completion']:
        if 'chunk' in event:
            chunk = event['chunk']
            decoded_chunk_bytes = chunk['bytes'].decode('utf-8', errors='replace')
            final_text += decoded_chunk_bytes
        elif 'error' in event:
            logger.error(f"Error en stream: {event['error']}")
    
    return final_text

def handler(event, context):
    """Handler principal de la Lambda"""
    logger.info(f"Evento recibido: {json.dumps(event)}")
    
    # Manejar OPTIONS para CORS
    if event.get('httpMethod') == 'OPTIONS':
        return _response_http(204, {})
    
    # Obtener cuerpo de la solicitud
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
    except json.JSONDecodeError as e:
        logger.error(f"JSON inválido: {str(e)}")
        return _response_http(400, {'error': 'JSON inválido'})
    
    # Extraer parámetros
    message = body.get('message')
    if not message:
        return _response_http(400, {'error': 'Parámetro message requerido'})
    
    # Usar variables de entorno para agent_id y alias_id
    agent_id = os.environ.get('BEDROCK_AGENT_ID')
    agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID')
    
    if not agent_id or not agent_alias_id:
        return _response_http(500, {'error': 'Configuración del agente faltante'})
    
    # Generar session_id persistente
    session_id = get_session_id(event)
    logger.info(f"Usando session_id: {session_id}")
    
    try:
        # Invocar agente
        response_text = _invoke_agent_and_parse_stream(
            agent_id, agent_alias_id, session_id, message
        )
        
        logger.info(f"Respuesta del agente: {response_text[:200]}...")
        
        # Construir respuesta
        response_payload = {
            'response': response_text,
            'session_id': session_id,
            'message': 'Respuesta del agente Novi'
        }
        
        return _response_http(200, response_payload)
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"Error Bedrock: {error_code} - {error_message}")
        
        status_code_map = {
            "ResourceNotFoundException": 404,
            "ValidationException": 400,
            "ThrottlingException": 429,
            "AccessDeniedException": 403
        }
        http_status_code = status_code_map.get(error_code, 502)
        
        return _response_http(http_status_code, {
            'error': f'Error del agente Bedrock ({error_code})',
            'details': error_message
        })
        
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return _response_http(500, {
            'error': 'Error interno del servidor',
            'details': str(e)
        })
