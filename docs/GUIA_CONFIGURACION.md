# 🚀 Guía Completa de Configuración del Entorno
## Modernización SenialSOLIDApp

---

## 📋 **CHECKLIST DE PREPARACIÓN**

### ✅ **FASE 0: PRE-REQUISITOS**
- [ ] Python 3.11+ instalado
- [ ] Git instalado y configurado
- [ ] Editor de código (VS Code, PyCharm, etc.)
- [ ] Acceso al directorio del proyecto

### ✅ **FASE 1: CONFIGURACIÓN AUTOMÁTICA**
- [ ] Ejecutar: `bash setup_entorno.sh`
- [ ] Activar entorno virtual: `source venv/bin/activate`
- [ ] Verificar instalación: `python3 verificar_entorno.py`

### ✅ **FASE 2: CONFIGURACIÓN MANUAL**
- [ ] Copiar `.env.example` a `.env`
- [ ] Personalizar variables de entorno
- [ ] Configurar Git user/email
- [ ] Crear commit inicial

---

## 🔧 **COMANDOS RÁPIDOS**

### **Configuración en Un Solo Comando:**
```bash
chmod +x setup_entorno.sh && bash setup_entorno.sh && source venv/bin/activate && python3 verificar_entorno.py
```

### **Activación Diaria del Entorno:**
```bash
cd /Users/victor/PycharmProjects/SenialSOLIDApp
source venv/bin/activate
```

### **Verificación Rápida:**
```bash
python3 verificar_entorno.py
```

---

## 📁 **ESTRUCTURA RESULTANTE**

```
SenialSOLIDApp/
├── 📁 01_presentacion/        # [EXISTENTE] Interfaces usuario
├── 📁 02_servicios/           # [EXISTENTE] Servicios aplicación  
├── 📁 03_aplicacion/          # [EXISTENTE] Lógica aplicación
├── 📁 04_dominio/             # [EXISTENTE] Modelos dominio
├── 📁 05_Infraestructura/     # [EXISTENTE] Acceso datos
├── 📁 venv/                   # [NUEVO] Entorno virtual
├── 📁 logs/                   # [NUEVO] Archivos de log
├── 📁 datos/entrada/          # [NUEVO] Datos de entrada
├── 📁 tests/                  # [NUEVO] Pruebas unitarias
│   ├── 📁 unit/               
│   └── 📁 integration/        
├── 📁 docs/                   # [NUEVO] Documentación
├── 📄 requirements.txt        # [NUEVO] Dependencias producción
├── 📄 requirements-dev.txt    # [NUEVO] Dependencias desarrollo
├── 📄 pyproject.toml          # [NUEVO] Configuración proyecto
├── 📄 .env.example            # [NUEVO] Plantilla configuración
├── 📄 .env                    # [NUEVO] Variables entorno (no versionado)
├── 📄 .gitignore              # [NUEVO] Archivos ignorados
├── 📄 setup_entorno.sh        # [NUEVO] Script configuración
├── 📄 verificar_entorno.py    # [NUEVO] Script verificación
└── 📄 GUIA_CONFIGURACION.md   # [NUEVO] Esta guía
```

---

## 🛠 **HERRAMIENTAS INSTALADAS**

### **Dependencias de Producción:**
- **Flask 3.0.0** - Framework web moderno
- **Flask-Bootstrap4** - Componentes UI
- **Flask-WTF** - Manejo de formularios
- **Flask-SQLAlchemy** - ORM de base de datos
- **python-decouple** - Gestión de configuración
- **structlog** - Logging estructurado

### **Dependencias de Desarrollo:**
- **pytest** - Framework de testing
- **black** - Formateador de código
- **pylint** - Análisis estático
- **mypy** - Type checking
- **bandit** - Análisis de seguridad
- **pre-commit** - Hooks de Git

---

## ⚙️ **CONFIGURACIÓN DE HERRAMIENTAS**

### **VS Code (Recomendado)**
Extensiones útiles:
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter", 
        "ms-python.pylint",
        "ms-python.mypy-type-checker",
        "ms-toolsai.jupyter"
    ]
}
```

### **Pre-commit Hooks**
```bash
# Instalar hooks (opcional)
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

---

## 🧪 **TESTING**

### **Ejecutar Tests:**
```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Solo tests unitarios
pytest tests/unit/

# Test específico
pytest tests/unit/test_senial.py::test_poner_valor
```

### **Análisis de Calidad:**
```bash
# Formatear código
black .

# Análisis estático  
pylint **/*.py

# Type checking
mypy .

# Análisis de seguridad
bandit -r . -f json
```

---

## 🚀 **COMENZAR DESARROLLO**

### **1. Preparar para SENIAL-1:**
```bash
# Crear branch para primer ticket
git checkout -b feature/SENIAL-1-modernizar-python

# Verificar estado
git status
python3 verificar_entorno.py
```

### **2. Flujo de Desarrollo Típico:**
```bash
# 1. Activar entorno
source venv/bin/activate

# 2. Hacer cambios de código
# ... editar archivos ...

# 3. Ejecutar tests
pytest

# 4. Formatear código  
black .

# 5. Commit cambios
git add .
git commit -m "SENIAL-1: Descripción del cambio"

# 6. Push a remote (cuando esté listo)
git push origin feature/SENIAL-1-modernizar-python
```

---

## 🔍 **TROUBLESHOOTING**

### **Error: "No module named 'xxx'"**
```bash
# Verificar entorno virtual activo
which python3  # Debe mostrar ruta con /venv/

# Reinstalar dependencias
pip install -r requirements-dev.txt
```

### **Error: "Permission denied"**
```bash
# Hacer scripts ejecutables
chmod +x setup_entorno.sh
chmod +x verificar_entorno.py
```

### **Error: "Git not initialized"**
```bash
# Inicializar Git
git init
git add .
git commit -m "Initial commit"
```

### **Problemas con Python Version**
```bash
# Verificar versión
python3 --version

# Si es < 3.11, instalar versión nueva
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

---

## 📞 **SOPORTE**

### **Verificar Estado del Entorno:**
```bash
python3 verificar_entorno.py
```

### **Re-ejecutar Configuración:**
```bash
bash setup_entorno.sh
```

### **Reset Completo (si es necesario):**
```bash
# ⚠️ CUIDADO: Esto elimina el entorno virtual
rm -rf venv/
bash setup_entorno.sh
```

---

## 🎯 **PRÓXIMOS PASOS DESPUÉS DE LA CONFIGURACIÓN**

1. **✅ Verificar que todo funciona:** `python3 verificar_entorno.py`
2. **🔧 Comenzar con SENIAL-1:** Modernizar shebang de Python
3. **🧪 Crear primer test:** Para validar funcionalidad existente
4. **📝 Documentar cambios:** En cada commit
5. **🔄 Seguir el roadmap:** Según el plan de 5 sprints

---

*Esta guía fue generada automáticamente para la modernización del proyecto SenialSOLIDApp.*