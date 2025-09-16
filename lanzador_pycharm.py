#!/usr/bin/env python3
"""
Lanzador de aplicación consola para PyCharm - SenialSOLIDApp
Version optimizada para ejecución desde PyCharm con configuración automática de rutas
"""

# CONFIGURACIÓN AUTOMÁTICA DE RUTAS PARA PYCHARM
import sys
import os
from pathlib import Path

# Configurar rutas automáticamente
current_file = Path(__file__).resolve()
project_root = current_file.parent

# Rutas necesarias
required_paths = [
    project_root,
    project_root / "01_presentacion",
    project_root / "01_presentacion" / "consola",
    project_root / "03_aplicacion",
    project_root / "04_dominio",
    project_root / "05_Infraestructura",
    project_root / "config",
]

# Agregar rutas al PYTHONPATH
for path in required_paths:
    path_str = str(path)
    if path_str not in sys.path and path.exists():
        sys.path.insert(0, path_str)

print("🔧 PYTHONPATH configurado automáticamente para PyCharm")
print("📍 Rutas agregadas:", len([p for p in required_paths if p.exists()]))

# Importar el lanzador original
try:
    os.chdir(project_root / "01_presentacion" / "consola")
    from presentacion_consola import AplicacionSOLID

    print("✅ Módulos importados correctamente")
    print("🚀 Iniciando aplicación consola...")
    print("")

    # Ejecutar la aplicación
    AplicacionSOLID.iniciar()

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Verifica que todas las carpetas tengan archivos __init__.py")
except Exception as e:
    print(f"❌ Error ejecutando la aplicación: {e}")
    print("💡 Verifica la configuración del proyecto")