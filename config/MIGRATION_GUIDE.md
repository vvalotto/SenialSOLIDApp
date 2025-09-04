# Guía de Migración: XML a YAML
## Migrado automáticamente el 2025-09-04 10:36:29

### Resumen
Este documento describe la migración del sistema de configuración de XML a YAML realizada automáticamente.

### Archivos Creados
- `config/config.yaml` - Configuración principal en formato YAML
- `config/config_schema.yaml` - Schema de validación
- `config/environments/` - Configuraciones específicas por entorno
- `.env.migrated` - Variables de entorno extraídas del XML

### Cambios Principales
1. **Formato**: De XML a YAML con soporte para variables de entorno
2. **Entornos**: Soporte para desarrollo, testing y producción
3. **Validación**: Schema JSON para validar configuración
4. **Flexibilidad**: Variables de entorno con valores por defecto

### Cómo Usar el Nuevo Sistema

#### Importación Básica
```python
from config.config_loader import load_config, get_config_value


# Cargar configuración completa
config = load_config(environment='development')

# Obtener valor específico
threshold = get_config_value('processing.threshold', default=5)
```

#### Uso con Configurador Modernizado
```python
from 03_aplicacion.contenedor.configurador_modern import ConfiguradorCompatible

# Drop-in replacement del configurador original
configurador = ConfiguradorCompatible()

# Verificar si está usando configuración moderna
if configurador.is_using_modern_config():
    print("✅ Usando configuración YAML moderna")
else:
    print("📄 Usando configuración XML legacy")
```

### Variables de Entorno Disponibles
Ver archivo `.env.migrated` para lista completa de variables migradas.

### Configuración por Entornos

#### Desarrollo
```bash
export ENVIRONMENT=development
```
- Directorio: `datos/dev`
- Umbral reducido para testing rápido
- Debug habilitado

#### Testing  
```bash
export ENVIRONMENT=testing
```
- Directorio: `datos/test`
- Umbral elevado para pruebas rigurosas
- Sin debug

#### Producción
```bash
export ENVIRONMENT=production
```
- Directorio configurable vía `PROD_DATA_DIR`
- Configuración optimizada para rendimiento
- Logging nivel INFO

### Migración Gradual
El sistema mantiene compatibilidad hacia atrás:
1. Si YAML no está disponible, usa XML automáticamente
2. Todas las funciones legacy siguen funcionando
3. Se puede forzar el uso de XML con `force_legacy=True`

### Validación de Configuración
```bash
python scripts/test_config.py
```

### Rollback
Si es necesario volver al sistema XML:
1. Los archivos XML originales están en `config/backups/`
2. Usar `ConfiguradorCompatible(force_legacy=True)`
3. O simplemente eliminar los archivos YAML

### Beneficios del Nuevo Sistema
- ✅ Configuración flexible con variables de entorno
- ✅ Soporte para múltiples entornos
- ✅ Validación de configuración con schemas
- ✅ Mejor legibilidad y mantenimiento
- ✅ Compatibilidad hacia atrás completa
- ✅ Eliminación de configuración duplicada
