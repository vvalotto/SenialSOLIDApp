#!/usr/bin/env python3
"""
Script de migración de configuración XML a YAML
===============================================
Migra la configuración existente de XML al nuevo sistema YAML manteniendo valores actuales.
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from xml.dom import minidom
import yaml

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def backup_existing_config():
    """Crea backup de la configuración XML existente."""
    print("🔄 Creando backup de configuración actual...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_root / "config" / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    xml_files = [
        "03_aplicacion/datos/configuracion.xml",
        "01_presentacion/webapp/datos/configuracion.xml"
    ]
    
    backed_up_files = []
    for xml_file in xml_files:
        xml_path = project_root / xml_file
        if xml_path.exists():
            backup_path = backup_dir / xml_path.name
            shutil.copy2(xml_path, backup_path)
            backed_up_files.append(str(backup_path))
            print(f"✅ Backup: {xml_file} -> {backup_path}")
    
    return backup_dir, backed_up_files


def parse_xml_config(xml_path: Path) -> dict:
    """Parsea el archivo XML y extrae la configuración."""
    if not xml_path.exists():
        raise FileNotFoundError(f"Archivo XML no encontrado: {xml_path}")
    
    print(f"📄 Parseando: {xml_path}")
    
    try:
        conf = minidom.parse(str(xml_path))
        
        # Extraer valores
        dir_datos = conf.getElementsByTagName("dir_recurso_datos")[0].firstChild.data.strip()
        
        # Adquisidor
        adq_node = conf.getElementsByTagName("adquisidor")[0]
        adq_type = adq_node.firstChild.data.strip()
        adq_param_nodes = adq_node.getElementsByTagName("param")
        adq_input_file = adq_param_nodes[0].firstChild.data.strip() if adq_param_nodes else "datos.txt"
        
        # Procesador  
        proc_node = conf.getElementsByTagName("procesador")[0]
        proc_type = proc_node.firstChild.data.strip()
        proc_param_nodes = proc_node.getElementsByTagName("param")
        proc_threshold = int(proc_param_nodes[0].firstChild.data.strip()) if proc_param_nodes else 5
        
        # Señales
        senial_adq_node = conf.getElementsByTagName("senial_adq")[0]
        senial_adq_type = senial_adq_node.firstChild.data.strip()
        senial_adq_size = int(senial_adq_node.getElementsByTagName("tamanio")[0].firstChild.data.strip())
        
        senial_pro_node = conf.getElementsByTagName("senial_pro")[0]  
        senial_pro_type = senial_pro_node.firstChild.data.strip()
        senial_pro_size = int(senial_pro_node.getElementsByTagName("tamanio")[0].firstChild.data.strip())
        
        # Contexto
        contexto = conf.getElementsByTagName("contexto")[0].firstChild.data.strip()
        
        return {
            'dir_datos': dir_datos,
            'adquisidor': {
                'type': adq_type,
                'input_file': adq_input_file
            },
            'procesador': {
                'type': proc_type,
                'threshold': proc_threshold
            },
            'senial_adq': {
                'type': senial_adq_type,
                'size': senial_adq_size
            },
            'senial_pro': {
                'type': senial_pro_type,
                'size': senial_pro_size
            },
            'contexto': contexto
        }
        
    except Exception as e:
        raise ValueError(f"Error parseando XML {xml_path}: {e}")


def create_yaml_config(parsed_xml: dict) -> dict:
    """Crea la estructura YAML basada en la configuración XML parseada."""
    
    # Extraer nombre base del archivo de entrada para INPUT_SUBDIR
    input_file = parsed_xml['adquisidor']['input_file']
    if '/' in input_file:
        input_subdir = input_file.split('/')[0] 
        input_filename = input_file.split('/')[-1]
    else:
        input_subdir = "entrada"
        input_filename = input_file
    
    yaml_config = {
        'app': {
            'name': 'SenialSOLID',
            'version': '2.0',
            'environment': '${ENVIRONMENT:-development}'
        },
        'paths': {
            'base_data_dir': '${BASE_DATA_DIR:-' + parsed_xml['dir_datos'] + '}',
            'input_subdir': '${INPUT_SUBDIR:-' + input_subdir + '}',
            'acquisition_subdir': '${ACQ_SUBDIR:-adq}',
            'processing_subdir': '${PROC_SUBDIR:-pro}'
        },
        'acquisition': {
            'type': '${ACQUISITION_TYPE:-' + parsed_xml['adquisidor']['type'] + '}',
            'input_file': '${INPUT_FILE:-' + input_filename + '}',
            'signal': {
                'type': '${ACQ_SIGNAL_TYPE:-' + parsed_xml['senial_adq']['type'] + '}',
                'size': '${ACQ_SIGNAL_SIZE:-' + str(parsed_xml['senial_adq']['size']) + '}'
            }
        },
        'processing': {
            'type': '${PROCESSING_TYPE:-' + parsed_xml['procesador']['type'] + '}',
            'threshold': '${PROCESSING_THRESHOLD:-' + str(parsed_xml['procesador']['threshold']) + '}',
            'signal': {
                'type': '${PROC_SIGNAL_TYPE:-' + parsed_xml['senial_pro']['type'] + '}',
                'size': '${PROC_SIGNAL_SIZE:-' + str(parsed_xml['senial_pro']['size']) + '}'
            }
        },
        'storage': {
            'context_type': '${STORAGE_CONTEXT:-' + parsed_xml['contexto'] + '}'
        },
        'environments': {
            'development': {
                'paths': {
                    'base_data_dir': 'datos/dev'
                },
                'processing': {
                    'threshold': max(1, parsed_xml['procesador']['threshold'] - 2)  # Umbral más bajo para dev
                },
                'acquisition': {
                    'signal': {
                        'size': max(5, parsed_xml['senial_adq']['size'] // 2)  # Señales más pequeñas para dev
                    }
                },
                'debug': True
            },
            'testing': {
                'paths': {
                    'base_data_dir': 'datos/test'
                },
                'processing': {
                    'threshold': parsed_xml['procesador']['threshold'] * 2  # Umbral más alto para testing
                },
                'debug': False
            },
            'production': {
                'paths': {
                    'base_data_dir': '${PROD_DATA_DIR:-' + parsed_xml['dir_datos'] + '}'
                },
                'processing': {
                    'threshold': '${PROD_THRESHOLD:-' + str(parsed_xml['procesador']['threshold']) + '}'
                },
                'acquisition': {
                    'signal': {
                        'size': '${PROD_SIGNAL_SIZE:-' + str(parsed_xml['senial_adq']['size']) + '}'
                    }
                },
                'debug': False,
                'logging_level': 'INFO'
            }
        }
    }
    
    return yaml_config


def write_yaml_config(yaml_config: dict, output_path: Path):
    """Escribe la configuración YAML al archivo."""
    print(f"📝 Escribiendo configuración YAML: {output_path}")
    
    # Crear directorio si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Crear contenido con comentarios
    yaml_content = f"""# SenialSOLID Configuration (migrado desde XML)
# ===============================================
# Migrado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Configuración principal del sistema con soporte para variables de entorno

"""
    
    # Convertir a YAML con formato limpio
    yaml_str = yaml.dump(yaml_config, default_flow_style=False, sort_keys=False, indent=2)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content + yaml_str)
    
    print(f"✅ Configuración YAML creada: {output_path}")


def create_migration_env_file(parsed_xml: dict):
    """Crea un archivo .env con los valores migrados."""
    env_file = project_root / ".env.migrated"
    
    print(f"📝 Creando archivo de entorno migrado: {env_file}")
    
    # Extraer valores actuales
    input_file = parsed_xml['adquisidor']['input_file']
    if '/' in input_file:
        input_subdir = input_file.split('/')[0] 
        input_filename = input_file.split('/')[-1]
    else:
        input_subdir = "entrada"
        input_filename = input_file
    
    env_content = f"""# Variables de entorno migradas desde configuración XML
# ====================================================
# Archivo generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Copiar valores relevantes a .env según sea necesario

ENVIRONMENT=development

# Paths migrados
BASE_DATA_DIR={parsed_xml['dir_datos']}
INPUT_SUBDIR={input_subdir}
ACQ_SUBDIR=adq
PROC_SUBDIR=pro

# Configuración de adquisición
ACQUISITION_TYPE={parsed_xml['adquisidor']['type']}
ACQ_SIGNAL_TYPE={parsed_xml['senial_adq']['type']}
ACQ_SIGNAL_SIZE={parsed_xml['senial_adq']['size']}
INPUT_FILE={input_filename}

# Configuración de procesamiento
PROCESSING_TYPE={parsed_xml['procesador']['type']}
PROCESSING_THRESHOLD={parsed_xml['procesador']['threshold']}
PROC_SIGNAL_TYPE={parsed_xml['senial_pro']['type']}
PROC_SIGNAL_SIZE={parsed_xml['senial_pro']['size']}

# Configuración de almacenamiento
STORAGE_CONTEXT={parsed_xml['contexto']}

# Configuraciones específicas de producción
PROD_DATA_DIR={parsed_xml['dir_datos']}
PROD_THRESHOLD={parsed_xml['procesador']['threshold']}
PROD_SIGNAL_SIZE={parsed_xml['senial_adq']['size']}
MAX_PROCESSES=4
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Archivo de entorno migrado creado: {env_file}")


def create_migration_documentation():
    """Crea documentación de la migración."""
    doc_file = project_root / "config" / "MIGRATION_GUIDE.md"
    
    print(f"📚 Creando documentación de migración: {doc_file}")
    
    doc_content = f"""# Guía de Migración: XML a YAML
## Migrado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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
from aplicacion.contenedor.configurador_modern import ConfiguradorCompatible

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
"""
    
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ Documentación de migración creada: {doc_file}")


def main():
    """Función principal del script de migración."""
    print("🚀 Iniciando migración de configuración XML a YAML")
    print("=" * 60)
    
    try:
        # 1. Crear backup
        backup_dir, backed_up_files = backup_existing_config()
        print(f"📦 Backup creado en: {backup_dir}")
        
        # 2. Parsear XML principal
        xml_path = project_root / "03_aplicacion" / "datos" / "configuracion.xml"
        if not xml_path.exists():
            print(f"❌ Archivo XML no encontrado: {xml_path}")
            sys.exit(1)
        
        parsed_config = parse_xml_config(xml_path)
        print("✅ Configuración XML parseada correctamente")
        
        # 3. Generar configuración YAML
        yaml_config = create_yaml_config(parsed_config)
        
        # 4. Escribir archivo YAML principal
        yaml_output = project_root / "config" / "config.yaml"
        write_yaml_config(yaml_config, yaml_output)
        
        # 5. Crear archivo de variables de entorno migrado
        create_migration_env_file(parsed_config)
        
        # 6. Crear documentación
        create_migration_documentation()
        
        print("\n✅ Migración completada exitosamente")
        print("=" * 60)
        print("📋 Próximos pasos:")
        print("1. Revisar config/config.yaml")  
        print("2. Copiar variables de .env.migrated a .env según necesidad")
        print("3. Probar con: python scripts/test_config.py")
        print("4. Actualizar código para usar configurador moderno")
        print("5. Backup disponible en:", backup_dir)
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        print("🔄 Se mantuvo la configuración original")
        sys.exit(1)


if __name__ == "__main__":
    main()