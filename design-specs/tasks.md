# Novi PQR MVP - Lista de Tareas de Implementación

## Resumen del Proyecto
Implementación de sistema de gestión de PQR basado en Amazon Bedrock Agent con arquitectura serverless en us-west-2. Duración: 3 semanas.

---

## SEMANA 0: Configuración de Infrastructure as Code (CDK)

### Tarea 0: Configuración Inicial de CDK
*Referencia: RT-005, RT-006, Diseño Sección 12*

#### 0.1 Setup del Proyecto CDK
- [ ] Inicializar proyecto CDK en TypeScript
- [ ] Configurar estructura de directorios según diseño
- [ ] Instalar dependencias CDK necesarias
- [ ] Configurar tsconfig.json y cdk.json
- [ ] Crear app.ts principal

#### 0.2 Desarrollo del Stack Principal
- [ ] Crear NoviPqrStack en lib/novi-pqr-stack.ts
- [ ] Implementar DynamoDB Table con configuración simplificada
- [ ] Implementar S3 Bucket para FAQs
- [ ] Implementar SNS Topic para notificaciones
- [ ] Configurar outputs del stack

#### 0.3 Configuración de Lambda Functions en CDK
- [ ] Crear estructura de directorios lambda/
- [ ] Configurar Lambda Functions en el stack
- [ ] Establecer variables de entorno
- [ ] Configurar permisos IAM básicos
- [ ] Implementar políticas para Bedrock

#### 0.4 Configuración de API Gateway
- [ ] Implementar API Gateway REST en CDK
- [ ] Configurar recursos y métodos
- [ ] Integrar con Lambda Functions
- [ ] Configurar CORS básico

#### 0.5 Testing y Deployment CDK
- [ ] Ejecutar cdk synth para validar template
- [ ] Realizar primer deployment en ambiente de desarrollo
- [ ] Verificar creación de todos los recursos
- [ ] Documentar proceso de deployment

---

## SEMANA 1: Infraestructura Base y Servicios Core

### Tarea 1: Validación de Infraestructura CDK
*Referencia: Diseño Sección 3 - Esquema DynamoDB, Sección 2 - Arquitectura, Tarea 0*

#### 1.1 Verificación de Recursos Desplegados
- [ ] Verificar tabla `novi-pqr` creada correctamente en us-west-2
- [ ] Confirmar configuración PAY_PER_REQUEST en DynamoDB
- [ ] Validar bucket S3 para FAQs con estructura correcta
- [ ] Verificar tópico SNS y permisos
- [ ] Probar conectividad entre recursos

#### 1.2 Configuración Post-Deployment
- [ ] Subir archivo inicial `faqs-novi.csv` a S3
- [ ] Configurar suscripción email de prueba en SNS
- [ ] Validar permisos IAM generados por CDK
- [ ] Probar endpoints de API Gateway básicos

### Tarea 2: Implementación de Lambda Functions
*Referencia: RF-001, RF-002, HU-001, HU-002, Diseño Sección 5, Sección 12 CDK*

#### 2.1 Lambda: create-pqr (Código en CDK)
- [ ] Implementar create_pqr.py en lambda/create-pqr/
- [ ] Implementar validación de campos requeridos (customerName, customerEmail, category, description)
- [ ] Implementar generación de ID único formato `PQR-YYYY-timestamp`
- [ ] Implementar escritura a DynamoDB con estructura definida
- [ ] Implementar envío de notificación SNS
- [ ] Crear requirements.txt con dependencias
- [ ] Implementar manejo de errores y logging
- [ ] Crear tests unitarios básicos

#### 2.2 Lambda: check-pqr (Código en CDK)
- [ ] Implementar check_pqr.py en lambda/check-pqr/
- [ ] Implementar consulta por pqrId desde DynamoDB
- [ ] Implementar respuesta con estructura JSON definida
- [ ] Implementar manejo de PQR no encontrada (404)
- [ ] Crear requirements.txt con dependencias
- [ ] Implementar manejo de errores y logging
- [ ] Crear tests unitarios básicos

#### 2.3 Deployment y Testing de Lambda Functions
- [ ] Ejecutar cdk deploy para actualizar Lambda functions
- [ ] Probar endpoints con Postman/curl
- [ ] Validar logs en CloudWatch
- [ ] Verificar permisos IAM automáticos de CDK

### Tarea 3: Testing de Integración Básica
*Referencia: Diseño Sección 9 - Estrategia de Testing*

#### 3.1 Tests de Funcionalidad Core
- [ ] Probar creación de PQR con datos válidos
- [ ] Probar creación de PQR con datos inválidos
- [ ] Probar consulta de PQR existente
- [ ] Probar consulta de PQR inexistente
- [ ] Verificar envío de notificaciones email
- [ ] Validar estructura de datos en DynamoDB

---

## SEMANA 2: Bedrock Agent y Sistema de FAQs

### Tarea 4: Configuración de Amazon Bedrock Agent
*Referencia: RF-001 Categorización, HU-001, Diseño Sección 6*

#### 4.1 Creación del Agente Bedrock
- [ ] Crear agente `novi-agent` en us-west-2
- [ ] Configurar Foundation Model (Claude 3.5 Sonnet)
- [ ] Establecer configuración básica del agente
- [ ] Configurar permisos IAM para Action Groups

#### 4.2 Configuración de Action Groups
- [ ] Crear especificación OpenAPI para endpoints PQR
- [ ] Definir operaciones createPQR y checkPQR
- [ ] Configurar esquemas de request/response
- [ ] Vincular Action Groups con Lambda functions
- [ ] Probar invocación básica de Action Groups

### Tarea 5: Sistema de FAQs con Jinja2
*Referencia: Diseño Sección 6.1 - Integración de FAQs*

#### 5.1 Lambda: process-faqs-template
- [ ] Crear función Lambda en Python 3.12
- [ ] Instalar dependencia Jinja2 en layer o package
- [ ] Implementar lectura de CSV desde S3
- [ ] Implementar procesamiento con template Jinja2
- [ ] Implementar actualización de prompt del agente
- [ ] Configurar variables de entorno (FAQS_BUCKET, BEDROCK_AGENT_ID)
- [ ] Crear archivo FAQs inicial con 5-10 preguntas comunes

#### 5.2 Integración de FAQs en Prompt
- [ ] Crear template Jinja2 para prompt del agente
- [ ] Integrar FAQs en prompt con formato estructurado
- [ ] Configurar reglas para consultar FAQs antes de crear PQR
- [ ] Probar actualización automática de prompt
- [ ] Validar respuestas del agente con FAQs

### Tarea 6: Lambda: invoke-agent
*Referencia: Diseño Sección 5.1*

#### 6.1 Desarrollo de Proxy Lambda
- [ ] Crear función Lambda en Python 3.12
- [ ] Implementar invocación a Bedrock Agent Runtime
- [ ] Configurar manejo de sesiones
- [ ] Implementar parsing de respuestas del agente
- [ ] Configurar variables de entorno (BEDROCK_AGENT_ID, BEDROCK_AGENT_ALIAS_ID)
- [ ] Integrar con API Gateway como endpoint principal
- [ ] Implementar manejo de errores específicos de Bedrock

### Tarea 7: Configuración de Guardrails
*Referencia: Diseño Sección 6.3*

#### 7.1 Implementación de Guardrails
- [ ] Crear configuración de Guardrails para PQR domain
- [ ] Configurar filtros de contenido (HATE, VIOLENCE)
- [ ] Establecer topic policy para gestión PQR
- [ ] Vincular Guardrails con el agente
- [ ] Probar restricciones de contenido

---

## SEMANA 3: Testing, Optimización y Deployment

### Tarea 8: Testing End-to-End
*Referencia: Todos los RF, HU-001, HU-002, HU-003*

#### 8.1 Flujos Completos de Usuario
- [ ] Probar flujo completo: crear PQR → recibir email → consultar estado
- [ ] Probar categorización automática con diferentes tipos de problemas
- [ ] Probar respuestas de FAQs sin crear PQR
- [ ] Probar manejo de errores en cada componente
- [ ] Validar tiempos de respuesta < 2 segundos (RNF-001)

#### 8.2 Testing de Casos Específicos
- [ ] Probar caso "Pedido Incompleto" (CU-001)
- [ ] Probar consulta de estado (CU-002)
- [ ] Probar diferentes categorías de PQR
- [ ] Validar estados: CREADA, EN PROCESO, RESUELTA, RECHAZADA, CERRADA
- [ ] Probar con datos de producción simulados

### Tarea 9: Optimización y Performance
*Referencia: RNF-001, RNF-002*

#### 9.1 Optimización de Performance
- [ ] Optimizar tiempos de respuesta de Lambda functions
- [ ] Configurar timeouts apropiados
- [ ] Implementar retry logic para servicios externos
- [ ] Optimizar consultas a DynamoDB
- [ ] Configurar CloudWatch metrics y alarms

#### 9.2 Seguridad y Validación
- [ ] Implementar validación de entrada completa (RNF-003)
- [ ] Configurar sanitización de datos de usuario
- [ ] Establecer logs de auditoría
- [ ] Configurar rate limiting en API Gateway
- [ ] Revisar permisos IAM mínimos necesarios

### Tarea 10: Documentación y Deployment
*Referencia: RT-004*

#### 10.1 Documentación
- [ ] Crear documentación de API con Swagger/OpenAPI
- [ ] Documentar proceso de actualización de FAQs
- [ ] Crear guía de troubleshooting
- [ ] Documentar variables de entorno y configuración
- [ ] Crear README para deployment

#### 10.2 Deployment a Producción
- [ ] Crear script de deployment automatizado
- [ ] Configurar environment de producción
- [ ] Migrar datos de prueba si es necesario
- [ ] Configurar monitoreo en CloudWatch
- [ ] Establecer alertas para errores críticos
- [ ] Realizar smoke tests en producción

### Tarea 11: Validación Final y Entrega
*Referencia: Criterios de Aceptación del MVP*

#### 11.1 Validación de Criterios de Aceptación
- [ ] ✅ Crear PQR con descripción libre
- [ ] ✅ Asignar categoría automática básica
- [ ] ✅ Generar número de ticket único
- [ ] ✅ Consultar PQR por número de ticket
- [ ] ✅ Mostrar estados básicos (Creada, En Proceso, Resuelta)
- [ ] ✅ Enviar email de confirmación
- [ ] ✅ API REST documentada

#### 11.2 Métricas de Calidad
- [ ] Verificar cobertura de pruebas > 80%
- [ ] Validar documentación completa de API
- [ ] Confirmar manejo de errores implementado
- [ ] Verificar validación de datos de entrada
- [ ] Confirmar logs estructurados para debugging

---

## Criterios de Definición de Terminado (DoD)

### Para cada Stack CDK:
- [ ] Código TypeScript implementado y compilado
- [ ] Template CloudFormation sintetizado sin errores
- [ ] Deployment exitoso en ambiente de desarrollo
- [ ] Recursos AWS creados correctamente
- [ ] Outputs del stack documentados
- [ ] Rollback strategy definida

### Para cada Lambda Function:
- [ ] Código implementado y testeado
- [ ] Variables de entorno configuradas
- [ ] Permisos IAM establecidos
- [ ] Logs estructurados implementados
- [ ] Tests unitarios con > 80% cobertura
- [ ] Manejo de errores completo

### Para cada Integración:
- [ ] Conexión establecida y probada
- [ ] Manejo de errores de red implementado
- [ ] Timeouts configurados apropiadamente
- [ ] Retry logic implementado donde sea necesario
- [ ] Monitoreo y alertas configurados

### Para el Sistema Completo:
- [ ] Todos los flujos end-to-end funcionando
- [ ] Performance requirements cumplidos
- [ ] Seguridad validada
- [ ] Documentación completa
- [ ] Deployment automatizado
- [ ] Monitoreo en producción activo

---

**Total de Sub-tareas: 105**
**Estimación: 3.5 semanas (17 días hábiles)**
**Equipo: 1-2 desarrolladores**
