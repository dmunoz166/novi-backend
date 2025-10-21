# Novi PQR – Backend MVP

Backend completo para Novi, el agente GenAI de gestión de PQR de NovaMarket. Sistema funcional con Amazon Bedrock Agent, API REST y deployment automatizado.

## 🚀 Estado Actual

### ✅ MVP COMPLETADO
- **Infraestructura AWS**: CDK stack optimizado en us-west-2
- **Bedrock Agent**: Amazon Nova Pro con FAQs integradas
- **API REST**: Endpoint principal `/agent` funcional
- **Base de datos**: DynamoDB configurada y operativa
- **Funciones Lambda**: 2 funciones unificadas y optimizadas
- **Deployment**: Script automatizado completo
- **Cleanup**: Arquitectura limpia y mantenible

## 🚀 Deployment Rápido

```bash
# Deployment completo automatizado
./deploy.sh
```

**El script automáticamente:**
1. Instala dependencias CDK
2. Compila y despliega infraestructura
3. Configura agente Bedrock con FAQs
4. Proporciona comando de prueba

## 📡 API Endpoint

**Endpoint Principal:**
```bash
POST /agent
{
  "message": "Hola Novi, necesito ayuda con mi pedido"
}
```

**Respuesta:**
```json
{
  "response": "Hola! Soy Novi. ¿En qué puedo ayudarte con tu pedido?"
}
```

## 🏗️ Arquitectura Final

```
Cliente → API Gateway → invoke_agent.py → Bedrock Agent (Nova Pro)
                                              ↓
                                        Action Groups
                                              ↓
                                      bedrock_actions.py
                                              ↓
                                          DynamoDB
```

## 📁 Estructura Optimizada

```
novi/
├── scripts/
│   └── setup_agent.py              # Configuración automatizada del agente
├── lambda-functions/
│   ├── invoke_agent.py             # Proxy Bedrock con session management
│   ├── bedrock_actions.py          # Action Groups unificadas (create/check PQR)
│   └── requirements.txt            # Dependencias Python
├── infrastructure/                 # CDK stack (TypeScript)
├── tests/                         # Tests unitarios
├── design-specs/                  # Especificaciones actualizadas
├── prompts/
│   └── faqs-novi.csv               # FAQs para integración (subido a S3)
├── deploy.sh                      # Script de deployment automatizado
└── README.md                      # Esta documentación
```

## 🔧 Desarrollo

### Comandos Esenciales
```bash
# Deployment completo
./deploy.sh

# Solo infraestructura
cd infrastructure && cdk deploy

# Solo configuración de agente
cd scripts && python3 setup_agent.py

# Testing
cd tests && python3 run_tests.py
```

### Variables de Entorno
- `BEDROCK_AGENT_ROLE_ARN`: ARN del rol IAM (auto-configurado)
- `PQR_TABLE_NAME`: Nombre de tabla DynamoDB
- `REGION`: us-west-2

## 🎯 Funcionalidades

### ✅ Implementadas
- **Conversación Natural**: Interacción fluida con agente
- **FAQs Integradas**: Respuestas automáticas a preguntas frecuentes
- **Creación de PQR**: Solo cuando no está cubierto en FAQs
- **Consulta de Estado**: Seguimiento de PQR existentes
- **Session Management**: Conversaciones persistentes por usuario
- **Deployment Automatizado**: Un comando despliega todo

### 🔄 Capacidades del Agente
- Responde FAQs sin crear PQR innecesarias
- Crea PQR con validación completa de campos
- Consulta estado de PQR existentes
- Mantiene contexto conversacional
- Categoriza automáticamente problemas

## 📊 Métricas MVP

- **Tiempo de deployment**: ~5 minutos
- **Tiempo de respuesta**: <3 segundos
- **Funciones Lambda**: 2 (optimizado desde 4)
- **Archivos de código**: Reducido 60%
- **Complejidad**: Mínima y mantenible

## 🧪 Testing

```bash
# Después del deployment, probar:
curl -X POST [API_URL]/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto tiempo tarda una PQR?"}'
```

## 📈 Progreso Final

- **Semana 1**: ✅ Infraestructura base
- **Semana 2**: ✅ Bedrock Agent + FAQs
- **Semana 3**: ✅ Cleanup + Automatización
- **MVP**: ✅ **COMPLETADO Y FUNCIONAL**

---

**🎉 MVP Novi PQR listo para producción**
