#!/bin/bash
# Script de configuración del entorno para modernización SenialSOLIDApp
# Uso: bash setup_entorno.sh

set -e  # Salir si hay errores

echo "🚀 Configurando entorno para modernización SenialSOLIDApp..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Python 3.11+
echo "📋 Paso 1: Verificando Python..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
    log_info "Python $PYTHON_VERSION ✓"
else
    log_error "Python 3.11+ requerido. Actual: $PYTHON_VERSION"
    echo "Instalar Python 3.11+ desde: https://www.python.org/downloads/"
    exit 1
fi

# 2. Crear entorno virtual
echo "📋 Paso 2: Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Entorno virtual creado"
else
    log_warning "Entorno virtual ya existe"
fi

# Activar entorno virtual
source venv/bin/activate
log_info "Entorno virtual activado"

# 3. Actualizar pip
echo "📋 Paso 3: Actualizando pip..."
pip install --upgrade pip
log_info "pip actualizado"

# 4. Crear archivos de dependencias
echo "📋 Paso 4: Creando archivos de dependencias..."

# requirements.txt para producción
cat > requirements.txt << 'EOF'
# Flask y extensiones modernas
Flask==3.0.0
Flask-Bootstrap4==4.0.2
Flask-Moment==1.0.5
Flask-WTF==1.2.1
Flask-SQLAlchemy==3.1.1

# WTForms
WTForms==3.1.0

# Configuración y logging
python-decouple==3.8
structlog==23.2.0

# Validación
cerberus==1.3.5

# Base de datos
SQLAlchemy==2.0.23

# Utilidades
click==8.1.7
EOF

# requirements-dev.txt para desarrollo
cat > requirements-dev.txt << 'EOF'
# Incluir dependencias de producción
-r requirements.txt

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0
pytest-mock==3.12.0

# Code Quality
black==23.11.0
flake8==6.1.0
pylint==3.0.3
mypy==1.7.1

# Security
bandit==1.7.5
safety==2.3.5

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==1.3.0

# Development utilities
ipython==8.18.1
pre-commit==3.5.0
EOF

log_info "Archivos de dependencias creados"

# 5. Instalar dependencias de desarrollo
echo "📋 Paso 5: Instalando dependencias..."
pip install -r requirements-dev.txt
log_info "Dependencias instaladas"

# 6. Crear archivo .env.example
echo "📋 Paso 6: Configurando variables de entorno..."
cat > .env.example << 'EOF'
# Configuración de Flask
FLASK_APP=01_presentacion/webapp/webapp_solid.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# Base de datos
DATABASE_URL=sqlite:///data.sqlite
SQLALCHEMY_DATABASE_URI=sqlite:///data.sqlite

# Configuración de la aplicación
CONFIG_XML_PATH=03_aplicacion/datos/configuracion.xml
LOG_LEVEL=INFO
LOG_FILE=logs/application.log

# Rutas de datos (cambiar según tu entorno)
DIR_RECURSO_DATOS=./datos/
DIR_ENTRADA_DATOS=./datos/entrada/datos.txt
EOF

log_info "Archivo .env.example creado"

# 7. Crear estructura de directorios
echo "📋 Paso 7: Creando estructura de directorios..."
mkdir -p logs
mkdir -p datos/entrada
mkdir -p tests/{unit,integration}
mkdir -p docs

log_info "Estructura de directorios creada"

# 8. Configurar Git (si no está inicializado)
if [ ! -d ".git" ]; then
    echo "📋 Paso 8: Inicializando Git..."
    git init
    log_info "Repositorio Git inicializado"
fi

# 9. Crear .gitignore
echo "📋 Paso 9: Configurando .gitignore..."
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.development
.env.test
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation
docs/_build/

# Backup files
*_BACKUP_*

# Flask instance folder
instance/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
EOF

log_info ".gitignore configurado"

# 10. Crear pyproject.toml
echo "📋 Paso 10: Creando pyproject.toml..."
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "senial-solid-app"
version = "4.0.1"
description = "Aplicación SOLID para procesamiento de señales"
authors = [
    {name = "Victor", email = "victor@example.com"},
]
license = {file = "LICENSE"}
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "Flask>=3.0.0",
    "Flask-Bootstrap4>=4.0.2",
    "Flask-Moment>=1.0.5",
    "Flask-WTF>=1.2.1",
    "Flask-SQLAlchemy>=3.1.1",
    "WTForms>=3.1.0",
    "python-decouple>=3.8",
    "structlog>=23.2.0",
    "cerberus>=1.3.5",
    "SQLAlchemy>=2.0.23",
    "click>=8.1.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "pytest-cov>=4.1.0",
    "pytest-flask>=1.3.0",
    "pytest-mock>=3.12.0",
    "black>=23.11.0",
    "flake8>=6.1.0",
    "pylint>=3.0.3",
    "mypy>=1.7.1",
    "bandit>=1.7.5",
    "safety>=2.3.5",
    "sphinx>=7.2.6",
    "sphinx-rtd-theme>=1.3.0",
    "ipython>=8.18.1",
    "pre-commit>=3.5.0",
]

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=.",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pylint.messages_control]
disable = "C0114,C0115,C0116"  # missing docstrings

[tool.bandit]
exclude_dirs = ["tests", "venv"]
EOF

log_info "pyproject.toml creado"

echo ""
echo "🎉 ¡Entorno configurado exitosamente!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Activar entorno virtual: source venv/bin/activate"
echo "2. Copiar .env.example a .env y configurar variables"
echo "3. Ejecutar tests: pytest"
echo "4. Iniciar desarrollo con SENIAL-1"
echo ""
echo "🔗 Archivos creados:"
echo "   - requirements.txt (dependencias de producción)"
echo "   - requirements-dev.txt (dependencias de desarrollo)"
echo "   - .env.example (plantilla de configuración)"
echo "   - pyproject.toml (configuración del proyecto)"
echo "   - .gitignore (archivos ignorados)"
echo "   - Estructura de directorios (logs/, datos/, tests/, docs/)"