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

### RF-003: Sistema de Notificaciones
- **Notificación de Creación:** Enviar confirmación inmediata al crear PQR
- **Canales:** Email como canal principal (SNS como stub)
- **Contenido:** Incluir número de ticket, descripción y próximos pasos

## Requisitos Técnicos

### RT-001: Arquitectura del Sistema
- **Backend:** API REST con Node.js/Express
- **Base de Datos:** PostgreSQL para persistencia de PQR
- **Autenticación:** JWT para identificación de usuarios
- **Documentación:** OpenAPI/Swagger para endpoints

### RT-002: Modelo de Datos
```sql
-- Tabla principal de PQR
CREATE TABLE pqr (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Creada',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de historial de estados
CREATE TABLE pqr_history (
    id SERIAL PRIMARY KEY,
    pqr_id INTEGER REFERENCES pqr(id),
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    comment TEXT,
    changed_at TIMESTAMP DEFAULT NOW()
);
```

### RT-003: Endpoints API
- **POST /api/pqr** - Crear nueva PQR
- **GET /api/pqr/:ticketNumber** - Consultar PQR por ticket
- **PUT /api/pqr/:ticketNumber/status** - Actualizar estado
- **GET /api/pqr/:ticketNumber/history** - Obtener historial

### RT-004: Integración de Notificaciones
- **Email Service:** Integración con servicio SMTP
- **SNS Stub:** Preparación para Amazon SNS (implementación futura)
- **Templates:** Plantillas HTML para emails de notificación

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
