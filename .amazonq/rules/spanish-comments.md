# Comentarios en Español

## Regla de Idioma
- Todos los comentarios en el código deben escribirse en español
- Incluye comentarios de documentación, explicaciones inline y comentarios de bloque
- Los nombres de variables y funciones pueden mantenerse en inglés por convención
- Los mensajes de commit y documentación técnica también deben estar en español

## Ejemplos
```javascript
// Función para validar credenciales de usuario
function validateCredentials(username, password) {
    // Verificar que los campos no estén vacíos
    if (!username || !password) {
        return false;
    }
    
    // Validar formato de email si es necesario
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(username);
}
```

## Q Developer Actions
Cuando escribas código, Q Developer debe:
- Generar todos los comentarios en español
- Sugerir comentarios descriptivos para funciones complejas
- Explicar la lógica del código en español
- Mantener consistencia en el idioma de los comentarios
