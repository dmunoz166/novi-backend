# API Documentation - Novi PQR

## Base URL
`https://uuwyl5urj2.execute-api.us-west-2.amazonaws.com/prod/`

## Endpoints

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
  "pqr_id": "pqr_1729540369",
  "status": "CREADA",
  "message": "PQR creada exitosamente"
}
```

### GET /pqr/{pqr_id} - Consultar PQR
**Respuesta:**
```json
{
  "pqr_id": "pqr_1729540369",
  "customer_email": "cliente@email.com",
  "description": "Descripción del problema",
  "status": "CREADA",
  "created_at": "2024-10-21T17:52:49Z"
}
```
