# Novi PQR MVP - Plan de Implementación Simplificado

## Principio: Velocidad > Sofisticación
**Objetivo:** MVP funcional en 4 semanas priorizando simplicidad y velocidad de implementación.

---

## SEMANA 1: Fundación AWS y CDK Básico

### Día 1-2: Setup Ambiente AWS
- [ ] Configurar credenciales AWS para us-west-2
- [ ] Verificar acceso a Bedrock en us-west-2
- [ ] Crear bucket S3 manual para FAQs (novi-pqr-faqs)
- [ ] Subir faqs-novi.csv inicial a S3

### Día 3-5: CDK Stack Mínimo
- [ ] `cdk init app --language typescript`
- [ ] Crear stack básico con DynamoDB table (novi-pqr)
- [ ] Agregar SNS topic para emails
- [ ] `cdk deploy` y verificar recursos creados
- [ ] Documentar ARNs y nombres de recursos

---

## SEMANA 2: Lambda Functions Core

### Día 6-7: create-pqr Lambda
- [ ] Crear lambda/create-pqr/create_pqr.py
- [ ] Implementar validación básica (4 campos requeridos)
- [ ] Implementar escritura a DynamoDB (estructura simple)
- [ ] Implementar SNS publish (mensaje básico)
- [ ] Hardcodear nombres de recursos (documentar)
- [ ] Testing manual con eventos de prueba

### Día 8-9: check-pqr Lambda
- [ ] Crear lambda/check-pqr/check_pqr.py
- [ ] Implementar consulta DynamoDB por pqrId
- [ ] Retornar JSON simple con status
- [ ] Manejo básico de errores (404, 500)
- [ ] Testing manual con datos de prueba

### Día 10: API Gateway Básico
- [ ] Agregar API Gateway al CDK stack
- [ ] Configurar 2 endpoints: POST /pqr, GET /pqr/{id}
- [ ] Integrar con Lambda functions
- [ ] `cdk deploy` y probar con curl
- [ ] Documentar URLs de endpoints

---

## SEMANA 3: Bedrock Agent (Configuración Manual)

### Día 11-12: Bedrock Agent Setup
- [ ] Crear agente "novi-agent" en AWS Console
- [ ] Configurar Claude 3.5 Sonnet
- [ ] Crear Action Group manual con OpenAPI básico
- [ ] Vincular Action Group con Lambda functions
- [ ] Probar agente en consola AWS

### Día 13-14: invoke-agent Lambda
- [ ] Crear lambda/invoke-agent/invoke_agent.py
- [ ] Implementar bedrock-agent-runtime.invoke_agent()
- [ ] Hardcodear agent-id y alias-id
- [ ] Agregar endpoint POST /agent al API Gateway
- [ ] Testing básico con mensajes de prueba

### Día 15: FAQs Básico
- [ ] Crear prompt simple con FAQs hardcodeadas
- [ ] Actualizar prompt del agente manualmente
- [ ] Probar respuestas de FAQs vs creación de PQR
- [ ] Ajustar prompt según resultados

---

## SEMANA 4: Testing y Producción

### Día 16-17: Testing End-to-End
- [ ] Probar flujo completo: mensaje → agente → crear PQR → email
- [ ] Probar consulta de PQR via agente
- [ ] Probar respuestas de FAQs
- [ ] Validar casos de error básicos
- [ ] Documentar casos de prueba exitosos

### Día 18-19: Deployment Producción
- [ ] Crear environment de producción (mismo stack)
- [ ] Configurar monitoreo básico CloudWatch
- [ ] Configurar alertas para errores Lambda
- [ ] Smoke testing en producción
- [ ] Documentar URLs y configuración final

### Día 20: Documentación y Entrega
- [ ] Crear README con instrucciones de uso
- [ ] Documentar endpoints API
- [ ] Documentar proceso de actualización FAQs
- [ ] Crear guía de troubleshooting básica
- [ ] Entrega del MVP funcional

---

## Decisiones de Simplicidad

### ✅ Implementación Simple
- **DynamoDB:** Solo partition key (pqrId), sin GSI
- **Logging:** `print()` statements en Lambda
- **Validación:** Checks básicos con if/else
- **Configuración:** Hardcodear ARNs y nombres (documentar)
- **Testing:** Manual + casos básicos automatizados
- **Bedrock Agent:** Configuración manual en consola
- **FAQs:** Prompt estático inicial, actualización manual

### 📝 Para Versión 2 (Post-MVP)
- Logger estructurado con niveles
- Validación con esquemas (Pydantic)
- Configuración desde variables de entorno
- Testing exhaustivo automatizado
- FAQs dinámicos con Jinja2
- CDK para Bedrock Agent
- Múltiples ambientes

## Criterios de Éxito MVP

### Funcionalidad Mínima
- [ ] Cliente puede crear PQR via agente conversacional
- [ ] Cliente recibe número de ticket único
- [ ] Cliente puede consultar estado de PQR
- [ ] Cliente recibe email de confirmación
- [ ] Agente responde FAQs básicas sin crear PQR

### Métricas Técnicas
- [ ] Tiempo respuesta < 5 segundos (relajado para MVP)
- [ ] Manejo básico de errores implementado
- [ ] Logs visibles en CloudWatch
- [ ] API documentada con ejemplos
- [ ] Deployment reproducible con CDK

## Estructura Final del Proyecto

```
novi-backend/
├── cdk/
│   ├── lib/novi-pqr-stack.ts          # Stack principal
│   ├── lambda/
│   │   ├── create-pqr/create_pqr.py   # Crear PQR
│   │   ├── check-pqr/check_pqr.py     # Consultar PQR
│   │   └── invoke-agent/invoke_agent.py # Proxy Bedrock
│   ├── package.json
│   └── cdk.json
├── docs/
│   ├── api-endpoints.md               # Documentación API
│   └── troubleshooting.md             # Guía de problemas
└── README.md                          # Instrucciones principales
```

## Comandos Esenciales

```bash
# Setup inicial
cdk init app --language typescript
npm install

# Desarrollo
cdk synth                    # Validar template
cdk deploy                   # Desplegar cambios
cdk destroy                  # Limpiar recursos (dev)

# Testing
curl -X POST [API_URL]/pqr   # Probar creación
curl [API_URL]/pqr/PQR-123   # Probar consulta
```

---

**Duración Total: 4 semanas (20 días hábiles)**
**Enfoque: Funcionalidad > Perfección técnica**
**Resultado: MVP completamente funcional y desplegado**
