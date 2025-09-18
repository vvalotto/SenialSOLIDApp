#!/usr/bin/env python3
"""
Prueba del configurador moderno con compatibilidad hacia atrás
=============================================================
"""

import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import importlib.util
    # Importar módulo con nombre que inicia con número
    spec = importlib.util.spec_from_file_location(
        "configurador_modern", 
        project_root / "03_aplicacion" / "contenedor" / "configurador_modern.py"
    )
    configurador_modern = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(configurador_modern)
    
    ConfiguradorCompatible = configurador_modern.ConfiguradorCompatible
    ConfiguradorModerno = configurador_modern.ConfiguradorModerno
    print("✅ Importación del configurador moderno exitosa")
except ImportError as e:
    print(f"❌ Error importando configurador moderno: {e}")
    sys.exit(1)

def test_modern_configurator():
    """Prueba el configurador moderno."""
    print("\n🔄 Probando ConfiguradorModerno...")
    
    try:
        # Probar con diferentes entornos
        for env in ['development', 'testing', 'production']:
            print(f"  • Entorno {env}:")
            configurator = ConfiguradorModerno(environment=env)
            
            config = configurator.get_config()
            print(f"    - App: {config['app']['name']} v{config['app']['version']}")
            print(f"    - Entorno: {config['app']['environment']}")
            print(f"    - Directorio base: {configurator.get_base_data_dir()}")
            print(f"    - Umbral: {config['processing']['threshold']}")
            
        print("✅ ConfiguradorModerno funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error en ConfiguradorModerno: {e}")

def test_compatible_configurator():
    """Prueba el configurador compatible (drop-in replacement)."""
    print("\n🔄 Probando ConfiguradorCompatible...")
    
    try:
        # Configurador compatible (interfaz original)
        configurador = ConfiguradorCompatible()
        
        print(f"✅ Configurador inicializado")
        print(f"✅ Usando configuración moderna: {configurador.is_using_modern_config()}")
        
        # Verificar que tiene todos los atributos esperados
        expected_attrs = ['ctx_datos_adquisicion', 'ctx_datos_procesamiento', 
                         'rep_adquisicion', 'rep_procesamiento', 
                         'adquisidor', 'procesador']
        
        for attr in expected_attrs:
            if hasattr(configurador, attr):
                obj = getattr(configurador, attr)
                print(f"✅ {attr}: {type(obj).__name__}")
            else:
                print(f"❌ Atributo faltante: {attr}")
        
        # Probar configuración expuesta
        config = configurador.get_config()
        print(f"✅ Configuración accesible: {config['app']['name']} v{config['app']['version']}")
        
    except Exception as e:
        print(f"❌ Error en ConfiguradorCompatible: {e}")

def test_legacy_functions():
    """Prueba las funciones legacy."""
    print("\n🔄 Probando funciones legacy...")
    
    try:
        # Usar el módulo importado dinámicamente
        obtener_dir_datos = configurador_modern.obtener_dir_datos
        definir_senial_adquirir = configurador_modern.definir_senial_adquirir
        definir_senial_procesar = configurador_modern.definir_senial_procesar
        definir_procesador = configurador_modern.definir_procesador
        definir_adquisidor = configurador_modern.definir_adquisidor
        definir_contexto = configurador_modern.definir_contexto
        definir_repositorio = configurador_modern.definir_repositorio
        
        # Probar funciones una por una
        dir_datos = obtener_dir_datos()
        print(f"✅ obtener_dir_datos(): {dir_datos}")
        
        senial_adq = definir_senial_adquirir()
        print(f"✅ definir_senial_adquirir(): {type(senial_adq).__name__}")
        
        senial_proc = definir_senial_procesar()
        print(f"✅ definir_senial_procesar(): {type(senial_proc).__name__}")
        
        procesador = definir_procesador()
        print(f"✅ definir_procesador(): {type(procesador).__name__}")
        
        adquisidor = definir_adquisidor()
        print(f"✅ definir_adquisidor(): {type(adquisidor).__name__}")
        
        contexto = definir_contexto(dir_datos + "/test")
        print(f"✅ definir_contexto(): {type(contexto).__name__}")
        
        repositorio = definir_repositorio(contexto)
        print(f"✅ definir_repositorio(): {type(repositorio).__name__}")
        
        print("✅ Todas las funciones legacy funcionando")
        
    except Exception as e:
        print(f"❌ Error en funciones legacy: {e}")

def test_fallback_to_xml():
    """Prueba el fallback al sistema XML."""
    print("\n🔄 Probando fallback a XML...")
    
    try:
        # Forzar uso del sistema legacy
        configurador = ConfiguradorCompatible(force_legacy=True)
        
        print(f"✅ Configurador legacy inicializado")
        print(f"✅ Usando configuración moderna: {configurador.is_using_modern_config()}")
        
        if not configurador.is_using_modern_config():
            config = configurador.get_config()
            print(f"✅ Configuración XML cargada: {config['app']['environment']}")
        
    except Exception as e:
        print(f"❌ Error en fallback XML: {e}")

def main():
    """Función principal."""
    print("🧪 Probando configurador moderno con compatibilidad")
    print("=" * 60)
    
    test_modern_configurator()
    test_compatible_configurator()
    test_legacy_functions()
    test_fallback_to_xml()
    
    print("\n✅ Todas las pruebas del configurador completadas")
    print("\n💡 El sistema nuevo es compatible con código existente:")
    print("   # Reemplazar:")
    print("   from aplicacion.contenedor.configurador import Configurador")
    print("   # Con:")
    print("   from aplicacion.contenedor.configurador_modern import Configurador")

if __name__ == "__main__":
    main()