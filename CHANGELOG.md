# Changelog - Novi PQR

## [2024-10-21] - Semana 0 y 1 Completadas

### Añadido
- Infraestructura CDK completa con TypeScript
- Funciones Lambda create_pqr y check_pqr
- API Gateway con endpoints REST
- DynamoDB table novi-pqr-table
- Suite de 10 tests unitarios
- Documentación de despliegue y API

### Técnico
- Stack desplegado en us-west-2
- Python 3.12 runtime para Lambda
- Pay-per-request billing DynamoDB
- IAM roles configurados
- Validación de entrada implementada

### Testing
- Tests unitarios con mocking
- Validación de casos de éxito y error
- Cobertura de funcionalidad core
