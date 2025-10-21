# Documentación Automática - Finalización de Tareas

## Regla de Documentación
**Al completar cada tarea del TODO list, ejecutar automáticamente:**

### 1. Actualizar Documentación
- Crear/actualizar archivos en carpeta `docs/`
- Generar documentación mínima pero completa
- Incluir ejemplos de uso cuando aplique

### 2. Generar Changelog
- Actualizar `CHANGELOG.md` con cambios realizados
- Formato simple: fecha, tarea completada, cambios principales
- Una línea por cambio significativo

### 3. Commit Automático
- Hacer commit con mensaje descriptivo
- Formato: `docs: [TAREA] - descripción breve`
- Incluir archivos de documentación y changelog

## Q Developer Actions
Cuando completes una tarea:

1. **PREGUNTAR**: "¿Actualizo la documentación y hago commit?"
2. **ESPERAR CONFIRMACIÓN** del usuario
3. **SI CONFIRMADO**: Ejecutar secuencia completa
4. **MOSTRAR**: Resumen de archivos creados/modificados

## Archivos a Mantener
- `README.md` - Documentación principal del proyecto
- `docs/api.md` - Documentación de API
- `docs/architecture.md` - Arquitectura del sistema
- `docs/deployment.md` - Guía de despliegue
- `CHANGELOG.md` - Historial de cambios

## Formato Changelog
```markdown
## [Fecha] - Tarea Completada

### Añadido
- Funcionalidad X implementada
- Test Y creado

### Modificado
- Endpoint Z actualizado

### Técnico
- Stack desplegado en us-west-2
```

## Validación Requerida
- **SIEMPRE** pedir confirmación antes de hacer commit
- Mostrar preview de cambios de documentación
- Permitir al usuario revisar antes de confirmar
