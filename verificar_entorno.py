#!/usr/bin/env python3
"""
Script de verificación del entorno para modernización SenialSOLIDApp
Uso: python3 verificar_entorno.py
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def print_header(text):
    """Imprime header con formato"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_check(item, status, details=""):
    """Imprime resultado de verificación"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

def check_python_version():
    """Verifica versión de Python"""
    print_header("VERIFICACIÓN DE PYTHON")
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    # Verificar versión mínima (3.11)
    is_valid = version_info >= (3, 11)
    print_check(
        f"Versión de Python: {version_str}", 
        is_valid,
        "Requerido: Python 3.11+" if not is_valid else "✓ Versión compatible"
    )
    
    return is_valid

def check_virtual_environment():
    """Verifica entorno virtual"""
    print_header("VERIFICACIÓN DE ENTORNO VIRTUAL")
    
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print_check(
        "Entorno virtual activo", 
        in_venv,
        "Ejecutar: source venv/bin/activate" if not in_venv else f"✓ Activo: {sys.prefix}"
    )
    
    venv_exists = Path("venv").exists()
    print_check(
        "Directorio venv existe", 
        venv_exists,
        "Ejecutar: python3 -m venv venv" if not venv_exists else "✓ Directorio encontrado"
    )
    
    return in_venv and venv_exists

def check_project_files():
    """Verifica archivos del proyecto"""
    print_header("VERIFICACIÓN DE ARCHIVOS DEL PROYECTO")
    
    required_files = {
        "requirements.txt": "Dependencias de producción",
        "requirements-dev.txt": "Dependencias de desarrollo", 
        ".env.example": "Plantilla de configuración",
        "pyproject.toml": "Configuración del proyecto",
        ".gitignore": "Archivos ignorados por Git",
        "setup_entorno.sh": "Script de configuración"
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        exists = Path(file_path).exists()
        print_check(f"{file_path}", exists, description)
        if not exists:
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Verifica dependencias instaladas"""
    print_header("VERIFICACIÓN DE DEPENDENCIAS")
    
    critical_packages = [
        "Flask",
        "Flask-WTF", 
        "Flask-SQLAlchemy",
        "pytest",
        "black",
        "pylint"
    ]
    
    try:
        import pkg_resources
        installed_packages = {pkg.project_name.lower(): pkg.version 
                            for pkg in pkg_resources.working_set}
        
        all_installed = True
        for package in critical_packages:
            is_installed = package.lower() in installed_packages
            version = installed_packages.get(package.lower(), "No instalado")
            print_check(
                f"{package}", 
                is_installed,
                f"Versión: {version}" if is_installed else "Ejecutar: pip install -r requirements-dev.txt"
            )
            if not is_installed:
                all_installed = False
                
        return all_installed
        
    except ImportError:
        print_check("pkg_resources", False, "Módulo no disponible")
        return False

def check_directory_structure():
    """Verifica estructura de directorios"""
    print_header("VERIFICACIÓN DE ESTRUCTURA DE DIRECTORIOS")
    
    required_dirs = [
        "logs",
        "datos/entrada", 
        "tests/unit",
        "tests/integration",
        "docs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print_check(f"Directorio: {dir_path}", exists)
        if not exists:
            all_exist = False
    
    return all_exist

def check_git_repository():
    """Verifica repositorio Git"""
    print_header("VERIFICACIÓN DE GIT")
    
    git_exists = Path(".git").exists()
    print_check("Repositorio Git inicializado", git_exists)
    
    if git_exists:
        try:
            # Verificar estado del repositorio
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            has_changes = bool(result.stdout.strip())
            print_check(
                "Estado del repositorio", 
                not has_changes,
                "Hay cambios sin commitear" if has_changes else "✓ Repositorio limpio"
            )
            
            # Verificar commits
            try:
                subprocess.run(
                    ["git", "log", "-1", "--oneline"], 
                    capture_output=True, 
                    check=True
                )
                print_check("Commits existentes", True, "✓ Historial encontrado")
            except subprocess.CalledProcessError:
                print_check("Commits existentes", False, "Sin commits aún")
                
        except subprocess.CalledProcessError:
            print_check("Git funcional", False, "Error ejecutando comandos git")
            return False
    
    return git_exists

def check_configuration():
    """Verifica archivos de configuración"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN")
    
    # Verificar .env
    env_exists = Path(".env").exists()
    print_check(
        "Archivo .env", 
        env_exists,
        "Copiar .env.example a .env y configurar" if not env_exists else "✓ Configurado"
    )
    
    # Verificar configuración XML
    xml_configs = [
        "03_aplicacion/datos/configuracion.xml",
        "01_presentacion/webapp/datos/configuracion.xml"
    ]
    
    xml_valid = True
    for xml_path in xml_configs:
        exists = Path(xml_path).exists()
        print_check(f"Configuración XML: {xml_path}", exists)
        if not exists:
            xml_valid = False
    
    return env_exists and xml_valid

def generate_report():
    """Genera reporte completo"""
    print_header("REPORTE DE VERIFICACIÓN COMPLETO")
    
    checks = [
        ("Python", check_python_version),
        ("Entorno Virtual", check_virtual_environment), 
        ("Archivos del Proyecto", check_project_files),
        ("Dependencias", check_dependencies),
        ("Estructura de Directorios", check_directory_structure),
        ("Repositorio Git", check_git_repository),
        ("Configuración", check_configuration)
    ]
    
    results = {}
    total_passed = 0
    
    for name, check_func in checks:
        try:
            result = check_func()
            results[name] = result
            if result:
                total_passed += 1
        except Exception as e:
            print(f"❌ Error verificando {name}: {e}")
            results[name] = False
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    success_rate = (total_passed / len(checks)) * 100
    
    if success_rate == 100:
        print("🎉 ¡ENTORNO COMPLETAMENTE CONFIGURADO!")
        print("✅ Todos los checks pasaron. Listo para comenzar la modernización.")
    elif success_rate >= 80:
        print("⚠️  ENTORNO MAYORMENTE CONFIGURADO")
        print(f"✅ {total_passed}/{len(checks)} checks pasaron ({success_rate:.1f}%)")
        print("Resolver los issues menores antes de continuar.")
    else:
        print("❌ ENTORNO REQUIERE CONFIGURACIÓN")
        print(f"❌ {total_passed}/{len(checks)} checks pasaron ({success_rate:.1f}%)")
        print("Ejecutar setup_entorno.sh para resolver los problemas.")
    
    # Próximos pasos
    print("\n📝 PRÓXIMOS PASOS:")
    if success_rate < 100:
        print("1. Resolver los issues identificados arriba")
        print("2. Re-ejecutar: python3 verificar_entorno.py")
        if success_rate < 80:
            print("3. Ejecutar: bash setup_entorno.sh")
    else:
        print("1. Crear branch para SENIAL-1: git checkout -b feature/SENIAL-1")
        print("2. Comenzar modernización de Python")
        print("3. Ejecutar tests: pytest")
    
    return success_rate >= 80

if __name__ == "__main__":
    print("🔍 Verificando entorno para modernización SenialSOLIDApp...")
    success = generate_report()
    sys.exit(0 if success else 1)