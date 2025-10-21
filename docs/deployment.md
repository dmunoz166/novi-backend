# Guía de Despliegue - Novi PQR

## Requisitos
- AWS CLI configurado
- Node.js 18+
- Python 3.12

## Despliegue Rápido
```bash
cd infrastructure
npm install
cdk deploy
```

## Verificación
```bash
# Probar API
curl -X POST https://uuwyl5urj2.execute-api.us-west-2.amazonaws.com/prod/pqr \
  -H "Content-Type: application/json" \
  -d '{"customer_email":"test@test.com","description":"test","priority":"MEDIA","category":"GENERAL"}'

# Ejecutar tests
cd ../tests && python3 run_tests.py
```

## Recursos Creados
- DynamoDB: `novi-pqr-table`
- Lambda: `create_pqr`, `check_pqr`
- API Gateway: REST API con endpoints /pqr
