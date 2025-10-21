# Novi PQR – Backend MVP

Backend mínimo para Novi, el agente GenAI de gestión de PQR de NovaMarket. Permite crear PQR y consultar su estado a través de un Bedrock Agent.

## 🚀 Estado Actual

### ✅ Completado
- **Infraestructura AWS**: CDK stack desplegado en us-west-2
- **API REST**: Endpoints funcionales para crear y consultar PQRs
- **Base de datos**: DynamoDB configurada y operativa
- **Funciones Lambda**: Implementadas con validación y manejo de errores
- **Tests**: 10 tests unitarios ejecutándose correctamente

### 🔄 En desarrollo
- Integración con Bedrock Agent
- Procesamiento de FAQs
- Action Groups y OpenAPI spec

## 📡 API Endpoints

**Base URL**: `https://uuwyl5urj2.execute-api.us-west-2.amazonaws.com/prod/`

### Crear PQR
```bash
POST /pqr
Content-Type: application/json

{
  "customer_email": "cliente@novamarket.com",
  "description": "Descripción del problema",
  "priority": "ALTA|MEDIA|BAJA",
  "category": "PEDIDOS|GENERAL|SOPORTE"
}
```

### Consultar PQR
```bash
GET /pqr/{pqr_id}
```

## 🏗️ Arquitectura

```
API Gateway → Lambda Functions → DynamoDB
                    ↓
              Bedrock Agent (próximo)
```

## 🧪 Testing

```bash
cd tests
python3 run_tests.py
```

## 📁 Estructura

```
novi/
├── infrastructure/     # CDK stack (TypeScript)
├── lambda-functions/   # Código Python de las funciones
├── tests/             # Tests unitarios
└── design-specs/      # Documentación de diseño
```