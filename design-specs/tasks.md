# Novi PQR MVP - Plan de Implementación Simplificado

## Principio: Velocidad > Sofisticación
**Objetivo:** MVP funcional en 3 semanas priorizando simplicidad y velocidad de implementación.

---

## SEMANA 1: Fundación AWS y CDK Básico ✅ COMPLETADA

### Día 1-2: Setup Ambiente AWS ✅
- [x] Configurar credenciales AWS para us-west-2
- [x] Verificar acceso a Bedrock en us-west-2
- [x] Crear bucket S3 manual para FAQs (novi-pqr-faqs)
- [x] Subir faqs-novi.csv inicial a S3

### Día 3-5: CDK Stack Mínimo ✅
- [x] `cdk init app --language typescript`
- [x] Crear stack básico con DynamoDB table (novi-pqr)
- [x] Agregar SNS topic para emails
- [x] `cdk deploy` y verificar recursos creados
- [x] Documentar ARNs y nombres de recursos

---

## SEMANA 2: Lambda Functions Core ✅ COMPLETADA

### Día 6-7: Lambda Functions Unificadas ✅
- [x] Crear bedrock_actions.py (unifica create-pqr y check-pqr)
- [x] Implementar validación básica (4 campos requeridos)
- [x] Implementar escritura a DynamoDB (estructura simple)
- [x] Implementar consulta DynamoDB por pqrId
- [x] Manejo básico de errores (404, 500)
- [x] Testing manual con eventos de prueba

### Día 8-9: invoke-agent Lambda ✅
- [x] Crear invoke_agent.py con session management
- [x] Implementar bedrock-agent-runtime.invoke_agent()
- [x] Resolver manejo de EventStream en respuesta
- [x] Configurar variables de entorno con agent-id
- [x] Testing básico con mensajes de prueba - ¡FUNCIONANDO!

### Día 10: API Gateway Básico ✅
- [x] Agregar API Gateway al CDK stack
- [x] Configurar endpoint: POST /agent (principal)
- [x] Integrar con invoke_agent Lambda
- [x] `cdk deploy` y probar con curl
- [x] Documentar URLs de endpoints

---

## SEMANA 2: Bedrock Agent & FAQs Integration ✅ COMPLETADA

### Día 11-12: Bedrock Agent Setup ✅
- [x] Crear agente Bedrock básico exitosamente
- [x] Resolver problemas de acceso con modelos Claude (marketplace)
- [x] Migrar a Amazon Nova Pro para evitar restricciones
- [x] Configurar agent con Nova Pro (Agent ID: FAJTBGUBHQ)
- [x] Crear IAM roles y permisos necesarios

### Día 13-14: Action Groups & Integration ✅
- [x] Crear OpenAPI schema para Action Groups (createPQR, checkPQR)
- [x] Configurar Action Groups manualmente en consola AWS
- [x] Integrar bedrock_actions.py con Action Groups
- [x] Testing: agente → "crear PQR" → llamada a createPQR
- [x] Testing: agente → "consultar PQR" → llamada a checkPQR
- [x] Verificar flujo end-to-end completo

### Día 15: FAQs Integration & Automation ✅
- [x] Crear archivo FAQs básico (faqs-novi.csv) con preguntas frecuentes
- [x] **Crear script unificado setup_agent.py que:**
  - [x] Procesa FAQs desde S3 usando Jinja2
  - [x] Crea agente con Amazon Nova Pro
  - [x] Integra FAQs directamente en instrucciones
  - [x] Prepara y crea alias automáticamente
- [x] Eliminar funciones Lambda redundantes (process_faqs_template)
- [x] Probar respuestas de FAQs vs creación de PQR
- [x] Testing end-to-end: conversación natural → acción automática

---

## SEMANA 3: Testing, Security & Production Deployment

### Día 16-17: Testing End-to-End ✅
- [x] Probar flujo completo: mensaje → agente → crear PQR
- [x] Probar consulta de PQR via agente
- [x] Probar respuestas de FAQs automáticas
- [x] Validar casos de error básicos
- [x] Documentar casos de prueba exitosos

### Día 18-19: Cleanup & Optimization ✅
- [x] Limpiar archivos de test temporales en raíz
- [x] Unificar funciones Lambda (bedrock_actions.py)
- [x] Eliminar código redundante y archivos no utilizados
- [x] Actualizar documentación con cambios realizados

### Día 20: Documentación Final 🔄
- [ ] Actualizar README con configuración final
- [ ] Documentar proceso de deployment con script unificado
- [ ] Crear guía de troubleshooting actualizada
- [ ] Entrega del MVP funcional

---

## Cambios Realizados vs Plan Original

### ✅ Simplificaciones Exitosas
- **Script Unificado:** `setup_agent.py` automatiza toda la configuración
- **Lambda Unificada:** `bedrock_actions.py` maneja ambas operaciones PQR
- **Modelo Optimizado:** Amazon Nova Pro evita restricciones de marketplace
- **FAQs Integradas:** Procesamiento directo en setup sin Lambda separada
- **Cleanup Completo:** Eliminación de archivos redundantes y temporales

### 📝 Arquitectura Final Simplificada
```
Cliente → API Gateway → invoke_agent.py → Bedrock Agent (Nova Pro)
                                              ↓
                                        Action Groups
                                              ↓
                                      bedrock_actions.py
                                              ↓
                                          DynamoDB
```

## Decisiones de Simplicidad Aplicadas

### ✅ Implementación Simple
- **Configuración:** Script único para setup completo
- **Lambda Functions:** Solo 2 funciones (invoke_agent + bedrock_actions)
- **Modelo:** Amazon Nova Pro sin restricciones
- **FAQs:** Integración directa en instrucciones del agente
- **Testing:** Manual + casos básicos automatizados

### 📝 Eliminado (Complejidad Innecesaria)
- Funciones Lambda separadas para create/check PQR
- Función Lambda para procesamiento de FAQs
- Archivos de test temporales en raíz
- Configuración manual compleja de agente

## Criterios de Éxito MVP ✅ ALCANZADOS

### Funcionalidad Mínima ✅
- [x] Cliente puede crear PQR via agente conversacional
- [x] Cliente recibe número de ticket único
- [x] Cliente puede consultar estado de PQR
- [x] Agente responde FAQs básicas sin crear PQR
- [x] Session management para conversaciones persistentes

### Métricas Técnicas ✅
- [x] Tiempo respuesta < 5 segundos
- [x] Manejo básico de errores implementado
- [x] Logs visibles en CloudWatch
- [x] Deployment automatizado con script unificado
- [x] Arquitectura limpia y mantenible

## Estructura Final del Proyecto

```
novi/
├── scripts/
│   └── setup_agent.py              # Script unificado de configuración
├── lambda-functions/
│   ├── invoke_agent.py             # Proxy Bedrock con session management
│   ├── bedrock_actions.py          # Action Groups unificadas
│   └── requirements.txt            # Dependencias
├── infrastructure/                 # CDK stack (TypeScript)
├── tests/                         # Tests unitarios
├── design-specs/                  # Especificaciones actualizadas
├── docs/                          # Documentación
├── prompts/
│   └── faqs-novi.csv               # FAQs para integración
└── README.md                      # Instrucciones principales
```

## Comandos Esenciales Actualizados

```bash
# Setup completo automatizado
cd scripts
python3 setup_agent.py

# Desarrollo CDK
cd infrastructure
cdk synth                    # Validar template
cdk deploy                   # Desplegar cambios

# Testing
curl -X POST [API_URL]/agent -d '{"message": "Hola Novi"}'
```

---

**Estado: MVP COMPLETADO**
**Duración Real: 2.5 semanas**
**Enfoque: Funcionalidad > Perfección técnica ✅**
**Resultado: MVP completamente funcional, limpio y desplegado ✅**
