# Novi - Agente PQR (Peticiones, Quejas y Reclamos)
## Especificaciones de Requisitos - Versión 1.0

### Resumen del Proyecto
Novi es un agente inteligente para gestionar PQR (Peticiones, Quejas y Reclamos) que permite a los clientes crear incidencias, consultar su estado y recibir notificaciones inmediatas.

## Historias de Usuario

### HU-001: Crear PQR Simple
**Como** cliente  
**Quiero** crear una PQR para reportar un problema simple  
**Para** obtener una solución a mi incidencia  

**Criterios de Aceptación:**
- Puedo describir mi problema en lenguaje natural
- El sistema categoriza automáticamente la incidencia
- Recibo un número de ticket único
- La PQR se almacena en el sistema

### HU-002: Consultar Estado de PQR
**Como** cliente  
**Quiero** consultar el estado de mi PQR  
**Para** conocer el progreso de mi solicitud  

**Criterios de Aceptación:**
- Puedo buscar por número de ticket
- Veo el estado actual (Creada, En Proceso, Resuelta, Cerrada)
- Veo la fecha de creación y última actualización
- Veo comentarios o actualizaciones del agente

### HU-004: Consultar FAQs Antes de Crear PQR
**Como** cliente  
**Quiero** obtener respuestas a preguntas frecuentes  
**Para** resolver mi consulta sin necesidad de crear una PQR  

**Criterios de Aceptación:**
- El agente consulta FAQs automáticamente antes de crear PQR
- Recibo respuesta inmediata si mi consulta está en las FAQs
- Solo se crea PQR si el problema no está cubierto en FAQs
- Las FAQs se actualizan dinámicamente desde archivo CSV

### HU-003: Recibir Notificación Inmediata
**Como** cliente  
**Quiero** recibir confirmación inmediata cuando creo una PQR  
**Para** tener evidencia de que mi solicitud fue registrada  

**Criterios de Aceptación:**
- Recibo notificación por email al crear la PQR
- La notificación incluye el número de ticket
- El sistema confirma el envío de la notificación

## Requisitos Funcionales

### RF-001: Gestión de PQR
- **Crear PQR:** El sistema debe permitir crear incidencias simples con descripción en texto libre
- **Categorización:** Clasificar automáticamente las PQR por tipo (Pedido Incompleto, Producto Defectuoso, Retraso en Entrega, etc.)
- **Generación de Ticket:** Asignar número único de seguimiento
- **Almacenamiento:** Persistir la información de la PQR

### RF-002: Consulta de Estado
- **Búsqueda por Ticket:** Permitir consulta por número de ticket
- **Estados Disponibles:** Creada, En Proceso, Resuelta, Cerrada
- **Historial:** Mostrar cronología de cambios de estado
- **Información Detallada:** Mostrar descripción, categoría, fechas y comentarios

### RF-004: Sistema de FAQs Integrado
- **Consulta Automática:** El agente debe consultar FAQs antes de crear PQR
- **Respuesta Directa:** Proporcionar respuestas inmediatas para consultas comunes
- **Actualización Dinámica:** FAQs actualizables via archivo CSV en S3
- **Template Engine:** Uso de Jinja2 para integrar FAQs en prompt del agente
- **Categorización:** FAQs organizadas por categorías (TIEMPOS, CANCELACIONES, ENTREGAS, ESTADOS)

### RF-003: Sistema de Notificaciones
- **Notificación de Creación:** Enviar confirmación inmediata al crear PQR
- **Canales:** Email como canal principal (SNS como stub)
- **Contenido:** Incluir número de ticket, descripción y próximos pasos

## Requisitos Técnicos

### RT-001: Arquitectura del Sistema
- **Backend:** Arquitectura serverless con Amazon Bedrock Agent
- **Base de Datos:** DynamoDB para persistencia de PQR
- **Compute:** AWS Lambda Functions (Python 3.12)
- **API:** Amazon API Gateway + Bedrock Agent Action Groups
- **Región:** us-west-2 (Oregon)

### RT-002: Modelo de Datos DynamoDB
```json
{
  "TableName": "novi-pqr",
  "KeySchema": [
    {
      "AttributeName": "pqrId",
      "KeyType": "HASH"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "pqrId",
      "AttributeType": "S"
    }
  ],
  "BillingMode": "PAY_PER_REQUEST"
}
```

**Estructura de Item PQR:**
```json
{
  "pqrId": "PQR-2024-001234",
  "customerName": "Juan Pérez",
  "customerEmail": "juan@email.com",
  "invoiceNumber": "INV-2024-5678",
  "category": "PEDIDO_INCOMPLETO",
  "description": "Mi pedido llegó incompleto, faltan 2 productos",
  "status": "CREADA",
  "createdAt": "2024-10-21T17:52:02Z",
  "updatedAt": "2024-10-21T17:52:02Z",
  "timeline": [
    {
      "timestamp": "2024-10-21T17:52:02Z",
      "status": "CREADA",
      "comment": "PQR creada automáticamente"
    }
  ]
}
```

### RT-003: Endpoints API y Action Groups
- **POST /agent** - Endpoint principal para interactuar con Bedrock Agent
- **Action Group: createPQR** - Crear nueva PQR via Bedrock Agent
- **Action Group: checkPQR** - Consultar PQR por ticket via Bedrock Agent
- **Documentación:** OpenAPI specification para Action Groups

### RT-005: Amazon Bedrock Agent
- **Foundation Model:** Claude 3.5 Sonnet para procesamiento de lenguaje natural
- **Action Groups:** Integración con Lambda functions via OpenAPI specification
- **Guardrails:** Configuración de filtros de contenido y políticas de temas
- **Prompt Engineering:** Sistema de prompts dinámicos con integración de FAQs
- **Session Management:** Manejo de sesiones de conversación con clientes

### RT-004: Integración de Notificaciones
- **Amazon SNS:** Servicio principal para notificaciones
- **Email:** Notificaciones por email via SNS
- **Templates:** Mensajes estructurados para confirmación de PQR

### RT-005: Infrastructure as Code (CDK)
- **Deployment Automatizado:** Toda la infraestructura debe ser desplegada usando AWS CDK
- **Versionado:** Infraestructura versionada junto con el código de aplicación
- **Reproducibilidad:** Entornos idénticos en desarrollo, staging y producción
- **Stack Principal:** Un stack CDK que incluya todos los recursos AWS necesarios

### RT-006: Estructura CDK
```typescript
// Stack principal que incluye:
- DynamoDB Table (novi-pqr)
- Lambda Functions (create-pqr, check-pqr, invoke-agent, process-faqs-template)
- API Gateway REST API
- SNS Topic para notificaciones
- S3 Bucket para FAQs
- IAM Roles y Policies
- Bedrock Agent (configuración manual inicial)
```
- **Reglas de Negocio:** Sistema basado en palabras clave
### RT-007: Categorización Automática
  - Pedido Incompleto
  - Producto Defectuoso
  - Retraso en Entrega
  - Problema de Facturación
  - Solicitud de Información
  - Otros

## Requisitos No Funcionales

### RNF-001: Rendimiento
- Tiempo de respuesta < 2 segundos para creación de PQR
- Tiempo de respuesta < 1 segundo para consultas
- Soporte para 100 PQR concurrentes

### RNF-002: Disponibilidad
- Disponibilidad del 99% durante horario laboral
- Manejo graceful de errores con mensajes informativos

### RNF-003: Seguridad
- Validación de entrada para prevenir inyección SQL
- Sanitización de datos de usuario
- Logs de auditoría para todas las operaciones

### RNF-004: Usabilidad
- Interfaz simple e intuitiva
- Mensajes de error claros en español
- Confirmaciones visuales para todas las acciones

## Casos de Uso Específicos

### CU-001: Pedido Incompleto
**Escenario:** Cliente recibe pedido con productos faltantes
**Flujo:**
1. Cliente describe: "Mi pedido llegó incompleto, faltan 2 productos"
2. Sistema categoriza como "Pedido Incompleto"
3. Genera ticket PQR-2024-001
4. Envía email de confirmación
5. Cliente puede consultar estado con el ticket

### CU-002: Consulta de Estado
**Escenario:** Cliente quiere saber el progreso de su PQR
**Flujo:**
1. Cliente ingresa número de ticket
2. Sistema muestra estado actual y historial
3. Muestra próximos pasos esperados

## Criterios de Aceptación del MVP

### Funcionalidad Mínima Viable
- ✅ Crear PQR con descripción libre
- ✅ Asignar categoría automática básica
- ✅ Generar número de ticket único
- ✅ Consultar PQR por número de ticket
- ✅ Mostrar estados básicos (Creada, En Proceso, Resuelta)
- ✅ Enviar email de confirmación (stub)
- ✅ API REST documentada

### Criterios de Calidad
- Cobertura de pruebas > 80%
- Documentación completa de API
- Manejo de errores implementado
- Validación de datos de entrada
- Logs estructurados para debugging

## Matriz de Trazabilidad

### Historias de Usuario → Requisitos Funcionales → Implementación
| Historia | Requisito Funcional | Componente Técnico | Estado |
|----------|-------------------|-------------------|---------|
| HU-001 | RF-001 | create-pqr Lambda + DynamoDB | ✅ Especificado |
| HU-002 | RF-002 | check-pqr Lambda + DynamoDB | ✅ Especificado |
| HU-003 | RF-003 | SNS + Email Templates | ✅ Especificado |
| HU-004 | RF-004 | Bedrock Agent + FAQs S3 + Jinja2 | ✅ Especificado |

### Requisitos Técnicos → Componentes AWS
| Requisito | Servicio AWS | Configuración | Estado |
|-----------|-------------|---------------|---------|
| RT-001 | Lambda + API Gateway | Python 3.12, us-west-2 | ✅ Definido |
| RT-002 | DynamoDB | Pay-per-request, pqrId PK | ✅ Definido |
| RT-003 | API Gateway + Bedrock | Action Groups OpenAPI | ✅ Definido |
| RT-004 | SNS | Email notifications | ✅ Definido |
| RT-005 | Bedrock Agent | Claude 3.5 Sonnet | ✅ Definido |
| RT-006 | CDK Stack | Infrastructure as Code | ✅ Definido |

## Roadmap Futuro (Post-MVP)

### Versión 1.1
- Integración real con Amazon SNS
- Notificaciones por SMS
- Dashboard web para consultas

### Versión 1.2
- Chatbot integrado para creación de PQR
- Categorización con ML/AI
- Escalamiento automático de PQR críticas

### Versión 2.0
- Integración con sistemas CRM
- Analytics y reportes
- API para integraciones externas
