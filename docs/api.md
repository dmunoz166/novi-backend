# API Documentation - Novi PQR

## Base URL
`https://uuwyl5urj2.execute-api.us-west-2.amazonaws.com/prod/`

## Endpoints

### POST /agent - Bedrock Agent (NUEVO)
```json
{
  "message": "Hola Novi, necesito ayuda con una PQR"
}
```

**Respuesta:**
```json
{
  "response": "Hola, soy Novi, tu asistente de PQR. ¿En qué puedo ayudarte hoy?",
  "session_id": "27687b28-d4c1-4e42-8279-5567fed7117c",
  "message": "Respuesta del agente Novi"
}
```

### POST /pqr - Crear PQR
```json
{
  "customer_email": "cliente@email.com",
  "description": "Descripción del problema",
  "priority": "ALTA|MEDIA|BAJA",
  "category": "PEDIDOS|GENERAL|SOPORTE"
}
```

**Respuesta:**
```json
{
  "pqr_id": "23a3a33d-2885-48a1-9b33-89a2fed61959",
  "status": "CREADA",
  "message": "PQR creada exitosamente"
}
```

### GET /pqr/{pqr_id} - Consultar PQR
**Respuesta:**
```json
{
  "message": "PQR encontrada",
  "pqr": {
    "pqr_id": "23a3a33d-2885-48a1-9b33-89a2fed61959",
    "customer_email": "cliente@email.com",
    "description": "Descripción del problema",
    "status": "CREADA",
    "created_at": "2025-10-21T19:31:59.753222"
  }
}
```

## Estado
- ✅ Todos los endpoints funcionando
- ✅ Bedrock Agent respondiendo
- 🔄 Action Groups en desarrollo
