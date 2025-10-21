# Simplicidad Primero - MVP Rápido

## Principio Fundamental
**Velocidad de implementación > Sofisticación técnica**

## Reglas de Desarrollo

### Arquitectura
- Usar servicios AWS managed siempre que sea posible
- Evitar abstracciones complejas o patrones avanzados
- Una función = una responsabilidad específica
- Configuración manual aceptable si acelera el desarrollo

### Código
- Código directo y legible sobre optimizaciones prematuras
- Usar bibliotecas estándar antes que dependencias externas
- Hardcodear valores si acelera el MVP (documentar para refactoring)
- Logging simple con print() en Lambda es suficiente para MVP

### Testing
- Tests funcionales básicos > cobertura exhaustiva
- Probar casos felices primero, edge cases después
- Testing manual aceptable para validación rápida
- Automatización solo para casos críticos

### Deployment
- CDK para infraestructura, pero configuración simple
- Un stack, un ambiente inicialmente
- Configuración manual de Bedrock Agent es aceptable
- Monitoreo básico con CloudWatch por defecto

## Q Developer Actions
Cuando implementes funcionalidades:
- Elige la solución más directa que funcione
- Pregunta "¿esto es necesario para el MVP?" antes de agregar complejidad
- Usa servicios AWS con configuración por defecto cuando sea posible
- Documenta decisiones de simplicidad para futuras mejoras

## Ejemplos de Aplicación

### ✅ Hacer (Simple)
```python
# Logging directo
print(f"PQR creada: {pqr_id}")

# Validación básica
if not customer_email:
    return {"error": "Email requerido"}

# Configuración hardcodeada
REGION = "us-west-2"
```

### ❌ Evitar (Complejo para MVP)
```python
# Logger configurado
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Validación con esquemas
from pydantic import BaseModel, EmailStr

# Configuración desde variables
REGION = os.getenv("AWS_REGION", "us-east-1")
```

## Criterios de Decisión
1. **¿Funciona para el MVP?** → Implementar
2. **¿Es crítico para la funcionalidad?** → Implementar simple
3. **¿Es optimización o mejora?** → Documentar para v2
4. **¿Bloquea el desarrollo?** → Buscar alternativa más simple
