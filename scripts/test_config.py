#!/usr/bin/env python3
"""
Script de prueba para el nuevo sistema de configuración
======================================================
Valida que la configuración YAML funciona correctamente en todos los entornos.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.config_loader import ConfigLoader, load_config, get_config_value
    from jsonschema import ValidationError
    import yaml
except ImportError as e:
    print(f"❌ Error: Dependencias faltantes - {e}")
    print("💡 Instala las dependencias: pip install -r requirements.txt")
    sys.exit(1)


def test_config_loading():
    """Prueba la carga básica de configuración."""
    print("🔄 Probando carga de configuración básica...")
    
    try:
        config = load_config(environment='development')
        print("✅ Configuración cargada exitosamente")
        
        # Verificar estructura básica
        required_keys = ['app', 'paths', 'acquisition', 'processing', 'storage', 'computed_paths']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Clave requerida faltante: {key}")
        
        print("✅ Estructura de configuración válida")
        return config
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return None


def test_environments():
    """Prueba la carga de configuración para diferentes entornos."""
    print("\n🔄 Probando configuraciones por entorno...")
    
    environments = ['development', 'testing', 'production']
    
    for env in environments:
        try:
            config = load_config(environment=env)
            print(f"✅ Entorno '{env}': OK")
            
            # Verificar que el entorno se aplicó correctamente
            if config['app']['environment'] != env:
                print(f"⚠️  Advertencia: Entorno esperado '{env}', obtenido '{config['app']['environment']}'")
            
        except Exception as e:
            print(f"❌ Entorno '{env}': Error - {e}")


def test_environment_variables():
    """Prueba el manejo de variables de entorno."""
    print("\n🔄 Probando variables de entorno...")
    
    # Establecer una variable de entorno de prueba
    test_var_name = 'TEST_PROCESSING_THRESHOLD'
    test_var_value = '99'
    
    os.environ[test_var_name] = test_var_value
    
    # Crear configuración temporal con esa variable
    test_config_content = f"""
app:
  name: "TestApp"
  version: "1.0"
  environment: development

paths:
  base_data_dir: dados

processing:
  type: umbral
  threshold: ${{{test_var_name}:-5}}
  signal:
    type: pila
    size: 20

acquisition:
  type: senoidal
  input_file: test.txt
  signal:
    type: pila
    size: 20

storage:
  context_type: archivo
"""
    
    # Escribir archivo temporal
    temp_config_path = project_root / "config" / "temp_test.yaml"
    
    try:
        with open(temp_config_path, 'w') as f:
            f.write(test_config_content)
        
        # Crear loader temporal
        loader = ConfigLoader()
        # Hackear temporalmente para usar el archivo de prueba
        original_load = loader._load_raw_config
        
        def load_test_config():
            with open(temp_config_path, 'r') as f:
                return yaml.safe_load(f)
        
        loader._load_raw_config = load_test_config
        
        config = loader.load_config(validate_schema=False)  # Sin validación por ser config temporal
        
        if config['processing']['threshold'] == int(test_var_value):
            print("✅ Variables de entorno funcionando correctamente")
        else:
            print(f"❌ Variable de entorno no aplicada. Esperado: {test_var_value}, Obtenido: {config['processing']['threshold']}")
        
    except Exception as e:
        print(f"❌ Error probando variables de entorno: {e}")
    
    finally:
        # Limpiar
        if temp_config_path.exists():
            temp_config_path.unlink()
        if test_var_name in os.environ:
            del os.environ[test_var_name]


def test_schema_validation():
    """Prueba la validación de schema."""
    print("\n🔄 Probando validación de schema...")
    
    try:
        # Cargar con validación habilitada (por defecto)
        config = load_config(environment='development', validate_schema=True)
        print("✅ Validación de schema: OK")
        
    except ValidationError as e:
        print(f"❌ Error de validación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False
    
    return True


def test_config_values():
    """Prueba la obtención de valores específicos de configuración."""
    print("\n🔄 Probando obtención de valores específicos...")
    
    try:
        # Probar función de conveniencia
        threshold = get_config_value('processing.threshold', environment='development')
        if threshold is not None:
            print(f"✅ Valor obtenido: processing.threshold = {threshold}")
        else:
            print("❌ No se pudo obtener valor de configuración")
            
        # Probar valor por defecto
        non_existent = get_config_value('non.existent.key', default='default_value')
        if non_existent == 'default_value':
            print("✅ Valores por defecto funcionando")
        else:
            print(f"❌ Valor por defecto no funcionó. Obtenido: {non_existent}")
            
    except Exception as e:
        print(f"❌ Error obteniendo valores específicos: {e}")


def test_computed_paths():
    """Prueba que los paths computados sean correctos."""
    print("\n🔄 Probando paths computados...")
    
    try:
        config = load_config(environment='development')
        computed_paths = config.get('computed_paths', {})
        
        required_computed_paths = [
            'project_root', 'base_data_dir', 'input_dir', 
            'acquisition_dir', 'processing_dir', 'input_file_path'
        ]
        
        for path_key in required_computed_paths:
            if path_key in computed_paths:
                path_value = computed_paths[path_key]
                print(f"✅ {path_key}: {path_value}")
            else:
                print(f"❌ Path computado faltante: {path_key}")
                
    except Exception as e:
        print(f"❌ Error verificando paths computados: {e}")


def print_config_summary(config):
    """Imprime un resumen de la configuración cargada."""
    print("\n📋 Resumen de configuración:")
    print("=" * 50)
    
    if config:
        print(f"App: {config['app']['name']} v{config['app']['version']}")
        print(f"Entorno: {config['app']['environment']}")
        print(f"Directorio base: {config.get('computed_paths', {}).get('base_data_dir', 'N/A')}")
        print(f"Umbral de procesamiento: {config['processing']['threshold']}")
        print(f"Tamaño de señal: {config['acquisition']['signal']['size']}")
        print("=" * 50)


def main():
    """Función principal del script de prueba."""
    print("🧪 Iniciando pruebas del sistema de configuración")
    print("=" * 60)
    
    # Pruebas básicas
    config = test_config_loading()
    if not config:
        print("❌ Pruebas abortadas - error en carga básica")
        sys.exit(1)
    
    test_environments()
    test_environment_variables()
    
    if test_schema_validation():
        test_config_values()
        test_computed_paths()
        print_config_summary(config)
    
    print("\n✅ Pruebas completadas")
    print("\n💡 Para usar el nuevo sistema:")
    print("   from config.config_loader import load_config, get_config_value")
    print("   config = load_config(environment='development')")


if __name__ == "__main__":
    main()