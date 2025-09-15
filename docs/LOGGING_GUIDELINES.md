# Guía de Logging Estructurado - SenialSOLID

## Objetivo
Este documento describe las mejores prácticas para el uso del sistema de logging estructurado implementado en SenialSOLID como parte del ticket SSA-22.

## Sistema de Logging

### Configuración
El sistema utiliza logging estructurado con formato JSON y rotación automática de archivos. La configuración se encuentra en:
- `config/logging_config.py` - Implementación del sistema
- `config/config.yaml` - Configuración externa

### Niveles de Logging
- **DEBUG**: Información detallada para debugging
- **INFO**: Información general del flujo de aplicación
- **WARNING**: Situaciones inesperadas pero manejables
- **ERROR**: Errores que afectan funcionalidad
- **CRITICAL**: Errores críticos que pueden parar la aplicación

## Uso Básico

### Importar Logger
```python
from config.logging_config import get_logger

logger = get_logger(__name__)
```

### Logging Simple
```python
# Información general
logger.info("Procesamiento iniciado")

# Advertencias
logger.warning("Capacidad de señal excedida")

# Errores
logger.error("Error procesando señal", exc_info=True)
```

### Logging Estructurado con Contexto
```python
# Con información contextual
logger.info("Señal adquirida exitosamente", extra={
    "signal_id": senial.id,
    "cantidad_valores": senial.cantidad,
    "tipo_adquisicion": "senoidal"
})

# Para operaciones web
logger.info("Request completado", extra={
    "request_id": request_id,
    "method": request.method,
    "status_code": response.status_code,
    "processing_time_ms": 150.5
})
```

## Mejores Prácticas

### 1. Niveles Apropiados por Módulo

#### Application Services (03_aplicacion)
- **INFO**: Inicio/fin de operaciones de negocio
- **WARNING**: Validaciones fallidas, datos inconsistentes
- **ERROR**: Errores en lógica de aplicación

```python
logger.info("Iniciando adquisición de señal")
logger.warning("Error de entrada: se esperaba número entero")
logger.error("Error durante adquisición de señal", exc_info=True)
```

#### Domain Logic (04_dominio)
- **DEBUG**: Detalles de procesamiento interno
- **INFO**: Operaciones importantes del dominio
- **WARNING**: Violaciones de reglas de negocio

```python
logger.debug("Aplicando función umbral", extra={"valor": valor, "umbral": umbral})
logger.info("Procesamiento completado", extra={"valores_procesados": count})
logger.warning("Capacidad de señal excedida", extra={"actual": actual, "maximo": maximo})
```

#### Infrastructure (05_Infraestructura)
- **DEBUG**: Operaciones de persistencia detalladas
- **INFO**: Operaciones CRUD exitosas
- **ERROR**: Errores de I/O, conexiones

```python
logger.debug("Guardando entidad", extra={"tipo": "pickle", "ubicacion": path})
logger.info("Entidad persistida exitosamente", extra={"id": entity_id})
logger.error("Error de I/O", extra={"archivo": filename}, exc_info=True)
```

#### Web Layer (01_presentacion)
- **INFO**: Requests, responses, operaciones de usuario
- **WARNING**: Páginas no encontradas, validaciones
- **ERROR**: Errores internos del servidor

```python
logger.info("Request iniciado", extra={
    "request_id": g.request_id,
    "method": request.method,
    "path": request.path
})
```

### 2. Información Contextual

#### Siempre Incluir
- **IDs únicos**: request_id, signal_id, user_id, session_id
- **Métricas**: tiempo de procesamiento, tamaños, contadores
- **Estado**: valores actuales vs. esperados

#### Nunca Incluir
- **Información sensible**: contraseñas, tokens, datos personales
- **Datos masivos**: arrays completos, objetos grandes
- **Stack traces**: excepto en nivel ERROR con exc_info=True

### 3. Formato de Mensajes
- **Usar presente**: "Procesando señal" no "Procesará señal"
- **Ser específico**: "Error conectando a base de datos" no "Error"
- **Incluir contexto relevante**: IDs, valores, estados

### 4. Manejo de Excepciones
```python
try:
    # operación
except SpecificException as e:
    logger.error("Error específico durante operación", extra={
        "operacion": "adquisicion",
        "signal_id": signal_id
    }, exc_info=True)
    raise
```

## Configuración por Entorno

### Development
- Nivel: DEBUG
- Consola: Habilitada
- Archivo: Habilitado
- Rotación: Cada 5MB

### Testing
- Nivel: WARNING
- Consola: Deshabilitada
- Archivo: Habilitado
- Logs mínimos para tests

### Production
- Nivel: INFO
- Consola: Deshabilitada
- Archivo: Habilitado
- Rotación: Cada 10MB, 10 backups

## Variables de Entorno

```bash
# Nivel de logging
LOG_LEVEL=INFO

# Directorio de logs
LOG_DIR=/var/log/senialsolid

# Rotación
LOG_MAX_SIZE=10
LOG_BACKUP_COUNT=5

# Salidas
LOG_CONSOLE=false
LOG_FILE=true
```

## Archivos de Logs

### Estructura
```
logs/
├── app.log          # Log principal de aplicación
├── error.log        # Solo errores y críticos
├── app.log.1        # Rotación automática
└── app.log.2
```

### Formato JSON
```json
{
  "timestamp": "2025-09-15T14:30:22Z",
  "level": "INFO",
  "logger": "03_aplicacion.managers.controlador_adquisicion",
  "message": "Señal adquirida exitosamente",
  "module": "controlador_adquisicion",
  "function": "adquirir_senial",
  "line": 18,
  "signal_id": "100",
  "cantidad_valores": 20
}
```

## Migración de Print Statements

### Antes (NO HACER)
```python
print("Procesando...")
print("Error:", str(exception))
```

### Después (HACER)
```python
logger.info("Iniciando procesamiento", extra={"tipo": "umbral"})
logger.error("Error en procesamiento", exc_info=True)
```

## Monitoreo y Análisis

### Queries Útiles (usando jq)
```bash
# Errores en las últimas 24h
grep ERROR logs/error.log | jq '.'

# Requests más lentos
grep "Request completado" logs/app.log | jq 'select(.processing_time_ms > 1000)'

# Operaciones por módulo
grep INFO logs/app.log | jq '.logger' | sort | uniq -c
```

### Métricas a Monitorear
- **Errores por minuto**: Alertar si > 10
- **Tiempo de response**: P95 < 2000ms
- **Throughput**: Requests por segundo
- **Utilización de recursos**: Memoria, CPU

## Solución de Problemas

### Logger No Configurado
```python
# Asegúrate de llamar setup antes de usar
from config.logging_config import LoggerFactory
LoggerFactory.setup()
```

### Logs No Aparecen
1. Verificar nivel de logging
2. Verificar permisos directorio logs/
3. Revisar configuración en config.yaml

### Performance
- Usar nivel INFO en producción
- Evitar logging excesivo en loops
- No hacer I/O síncrono en logging

---

**Implementado por**: SSA-22 Structured Logging
**Fecha**: 2025-09-15
**Versión**: 1.0