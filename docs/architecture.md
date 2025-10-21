# Arquitectura - Novi PQR MVP

## Diagrama
```
Cliente → API Gateway → Lambda Functions → DynamoDB
                            ↓
                    Bedrock Agent (próximo)
```

## Componentes

### AWS Services
- **API Gateway**: REST API endpoints
- **Lambda**: Funciones Python 3.12
- **DynamoDB**: Base de datos NoSQL
- **IAM**: Roles y permisos

### Funciones Lambda
- `create_pqr`: Crear nuevas PQR
- `check_pqr`: Consultar estado de PQR

### Base de Datos
- Tabla: `novi-pqr-table`
- Partition Key: `pqr_id`
- Billing: Pay-per-request

## Próximos Pasos
- Integración Bedrock Agent
- Action Groups OpenAPI
- Sistema de FAQs
