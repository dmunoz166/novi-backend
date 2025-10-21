# Arquitectura - Novi PQR MVP

## Diagrama
```
Cliente → API Gateway → Lambda Functions → DynamoDB
                ↓
        invoke-agent Lambda
                ↓
        Bedrock Agent (8R0NANUHIS) → Action Groups → bedrock_actions Lambda
                ↓
        Claude 3.5 Sonnet + FAQs (Jinja2)
```

## Componentes

### AWS Services
- **API Gateway**: REST API endpoints
- **Lambda**: Funciones Python 3.12
- **DynamoDB**: Base de datos NoSQL
- **Bedrock Agent**: Claude 3.5 Sonnet con Action Groups
- **IAM**: Roles y permisos

### Funciones Lambda
- `create_pqr`: Crear nuevas PQR
- `check_pqr`: Consultar estado de PQR
- `invoke_agent`: Proxy para Bedrock Agent
- `bedrock_actions`: Action Groups handler
- `process_faqs_template`: FAQs con Jinja2

### Base de Datos
- Tabla: `novi-pqr-table`
- Partition Key: `pqr_id`
- Billing: Pay-per-request

## Estado Actual
- ✅ Bedrock Agent funcionando (ID: 8R0NANUHIS)
- ✅ API REST operativa
- ✅ DynamoDB almacenando datos
- 🔄 Action Groups en desarrollo
- 🔄 FAQs integration pendiente
