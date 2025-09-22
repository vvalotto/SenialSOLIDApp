# SSA-25: Guía de Estándares de Calidad de Código

**Epic:** SSA-3 [EPIC-QUALITY] Mejoras de Calidad y Mantenibilidad
**Versión:** 1.0
**Fecha:** 2025-09-20
**Responsable:** Victor Valotto

---

## 🎯 Introducción

Esta guía establece los estándares de calidad de código para el proyecto **SenialSOLIDApp** como parte del ticket SSA-25. Define métricas, herramientas, procesos y mejores prácticas para mantener un código de alta calidad siguiendo principios DDD y SOLID.

## 📋 Métricas de Calidad Establecidas

### 🎯 Objetivos por Sprint

| Métrica | Sprint 3 (Baseline) | Sprint 4 | Sprint 5 | Sprint 6 |
|---------|---------------------|----------|----------|----------|
| **Pylint Score** | 7.5/10 | 8.0/10 | 8.5/10 | 9.0/10 |
| **Code Coverage** | 70% | 75% | 80% | 85% |
| **Max Complexity** | ≤15 | ≤12 | ≤10 | ≤8 |
| **Maintainability** | ≥50 | ≥55 | ≥60 | ≥65 |
| **Type Coverage** | 25% | 40% | 60% | 80% |

### 🔥 Quality Gates (BLOCKER)

Los siguientes umbrales **NO** pueden ser excedidos:

- **Pylint Score:** < 8.0/10
- **Code Coverage:** < 70%
- **Cyclomatic Complexity:** > 10 por función
- **Maintainability Index:** < 20
- **Security Issues:** > 0 (Bandit)

---

## 🛠️ Herramientas de Calidad

### 1. 🔍 **Pylint** - Análisis Estático
**Configuración:** `.pylintrc`

**Propósito:** Detecta errores, problemas de estilo y violaciones de convenciones.

```bash
# Ejecutar pylint
pylint aplicacion dominio infraestructura presentacion config

# Solo errores críticos
pylint --errors-only aplicacion/
```

**Configuración DDD-Friendly:**
- Nombres de clases DDD permitidos (Repository, Service, Factory)
- Deshabilitado `missing-docstring` para métodos privados
- Complejidad máxima ajustada para patterns DDD

### 2. 🎨 **Flake8** - Style Guide (PEP8)
**Configuración:** `setup.cfg`

**Propósito:** Enforce PEP8 style guidelines y detectar errores de sintaxis.

```bash
# Ejecutar flake8
flake8 aplicacion dominio infraestructura presentacion config

# Con estadísticas
flake8 --count --statistics aplicacion/
```

**Configuración:**
- Línea máxima: 100 caracteres
- Compatible con Black
- Ignora conflictos con formateo automático

### 3. 📝 **MyPy** - Type Checking
**Configuración:** `mypy.ini`

**Propósito:** Verificación de tipos estática gradual.

```bash
# Ejecutar mypy
mypy aplicacion dominio infraestructura presentacion config

# Solo errores críticos
mypy --no-error-summary aplicacion/
```

**Estrategia Gradual:**
- **Dominio:** Typing estricto (90%+ coverage)
- **Aplicación:** Typing moderado (75%+ coverage)
- **Infraestructura:** Typing básico (50%+ coverage)
- **Presentación:** Typing opcional (30%+ coverage)

### 4. 🔄 **Radon** - Métricas de Complejidad
**Configuración:** `.radon.cfg`

**Propósito:** Medir complejidad ciclomática y mantenibilidad.

```bash
# Complejidad ciclomática
radon cc aplicacion dominio --min C

# Índice de mantenibilidad
radon mi aplicacion dominio -s

# Métricas raw
radon raw aplicacion dominio -s
```

**Umbrales:**
- **A (1-5):** ✅ Simple - Objetivo
- **B (6-10):** ✅ Moderado - Aceptable
- **C (11-20):** ⚠️ Complejo - Revisar
- **D (21-30):** ❌ Muy Complejo - Refactorizar
- **E (31+):** 🚨 Extremo - Reescribir

### 5. 📊 **Coverage.py** - Cobertura de Código
**Configuración:** `.coveragerc`

**Propósito:** Medir cobertura de tests.

```bash
# Ejecutar con coverage
coverage run -m pytest tests/

# Generar reporte
coverage report --show-missing

# Reporte HTML
coverage html
```

**Objetivos de Cobertura:**
- **Dominio:** 90%+ (lógica de negocio crítica)
- **Aplicación:** 85%+ (casos de uso)
- **Infraestructura:** 70%+ (acceso a datos)
- **Presentación:** 60%+ (controladores)

### 6. 🛡️ **Bandit** - Security Linting
**Configuración:** `pyproject.toml`

**Propósito:** Detectar vulnerabilidades de seguridad.

```bash
# Ejecutar bandit
bandit -r aplicacion dominio infraestructura presentacion

# Con configuración
bandit -c pyproject.toml -r .
```

---

## 🚀 Uso de Scripts Automatizados

### 🔍 Quality Check Script
**Archivo:** `scripts/quality_check.py`

Ejecuta todas las herramientas de calidad automáticamente:

```bash
# Ejecutar todos los checks
python scripts/quality_check.py

# Solo módulos específicos
python scripts/quality_check.py --modules aplicacion dominio

# Formato JSON para CI/CD
python scripts/quality_check.py --format json --output results.json

# Formato YAML
python scripts/quality_check.py --format yaml
```

**Características:**
- ✅ Ejecuta todas las herramientas
- ✅ Valida quality gates automáticamente
- ✅ Genera reportes en múltiples formatos
- ✅ Exit code 0/1 para CI/CD
- ✅ Configuración desde `quality_gates.yaml`

### 📊 Dashboard Generator
**Archivo:** `scripts/generate_reports.py`

Genera dashboard HTML con métricas visuales:

```bash
# Generar dashboard
python scripts/generate_reports.py

# Con archivo específico
python scripts/generate_reports.py --output dashboard.html
```

**Características:**
- 📊 Dashboard responsive HTML
- 📈 Gráficos de métricas en tiempo real
- 🎯 Estado de quality gates visual
- 📱 Compatible móvil/desktop
- 🔄 Auto-refresh cada 24h

---

## 🔧 Pre-commit Hooks

### Instalación
```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Instalar commit-msg hook
pre-commit install --hook-type commit-msg
```

### Hooks Configurados

**En cada commit:**
- ✅ Black (formateo automático)
- ✅ isort (ordenamiento imports)
- ✅ Flake8 (style checking)
- ✅ Trailing whitespace fix
- ✅ End of file fix
- ✅ YAML/JSON validation

**En cada push:**
- 🔍 MyPy (type checking)
- 🔄 Radon complexity check
- 🛡️ Bandit security check
- 🚪 Quality gates validation

### Bypass (Solo Emergencias)
```bash
# Bypass pre-commit (NO recomendado)
git commit --no-verify -m "Emergency fix"

# Bypass específico hook
SKIP=pylint git commit -m "Skip pylint for this commit"
```

---

## 📝 Estándares de Código

### 🏛️ Arquitectura DDD

**Estructura por Capas:**
```
dominio/          # Lógica de negocio pura
├── modelo/       # Entidades y Value Objects
├── repositorios/ # Interfaces de persistencia
└── exceptions/   # Excepciones de dominio

aplicacion/       # Casos de uso y orchestración
├── patterns/     # Patterns de aplicación
├── validation/   # Validación de entrada
└── managers/     # Coordinadores de procesos

infraestructura/  # Implementaciones técnicas
├── acceso_datos/ # Repositorios concretos
└── utilidades/   # Servicios técnicos

presentacion/     # Interfaz de usuario
├── webapp/       # Flask web interface
└── consola/      # CLI interface
```

### 📏 Convenciones de Naming

**Clases:**
```python
# ✅ Correcto - PascalCase
class UserRepository:
class OrderService:
class PaymentProcessor:

# ❌ Incorrecto
class userRepository:
class order_service:
```

**Funciones y Variables:**
```python
# ✅ Correcto - snake_case
def calculate_total_amount():
user_email = "user@example.com"
processing_result = process_order()

# ❌ Incorrecto
def calculateTotalAmount():
userEmail = "user@example.com"
```

**Constantes:**
```python
# ✅ Correcto - UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30

# ❌ Incorrecto
maxRetryAttempts = 3
default_timeout = 30
```

### 🎯 Type Hints Progresivos

**Nivel 1 - Dominio (Strict):**
```python
from typing import Protocol, Optional, List

class UserRepository(Protocol):
    def find_by_id(self, user_id: int) -> Optional[User]:
        ...

    def save(self, user: User) -> User:
        ...

def calculate_discount(
    amount: Decimal,
    discount_rate: float
) -> Decimal:
    return amount * Decimal(str(1 - discount_rate))
```

**Nivel 2 - Aplicación (Moderate):**
```python
from typing import Dict, Any

def process_payment(
    payment_data: Dict[str, Any]
) -> PaymentResult:
    # Implementación
    pass
```

**Nivel 3 - Infraestructura (Basic):**
```python
def connect_to_database(config):
    # Type hints opcionales aquí
    pass
```

### 🧪 Testing Standards

**Nombres de Tests:**
```python
# ✅ Correcto - test_should_behavior_when_condition
def test_should_return_user_when_valid_id_provided():
def test_should_raise_exception_when_user_not_found():
def test_should_calculate_discount_when_rate_is_valid():

# ❌ Incorrecto
def test_user():
def test_calculation():
```

**Estructura AAA:**
```python
def test_should_calculate_total_when_items_provided():
    # Arrange
    items = [Item("Product A", 10.0), Item("Product B", 15.0)]
    calculator = TotalCalculator()

    # Act
    total = calculator.calculate(items)

    # Assert
    assert total == 25.0
```

### 📚 Documentación

**Docstrings (Google Style):**
```python
def calculate_signal_frequency(
    signal_data: List[float],
    sample_rate: int
) -> float:
    """Calcula la frecuencia dominante de una señal.

    Args:
        signal_data: Lista de valores de la señal.
        sample_rate: Frecuencia de muestreo en Hz.

    Returns:
        Frecuencia dominante en Hz.

    Raises:
        ValueError: Si signal_data está vacío.

    Example:
        >>> data = [1.0, 2.0, 1.0, -1.0, -2.0, -1.0]
        >>> freq = calculate_signal_frequency(data, 1000)
        >>> print(f"Frecuencia: {freq} Hz")
    """
```

---

## 🚨 Manejo de Violaciones

### Severity Levels

**🚨 BLOCKER (Bloquea merge/deploy):**
- Pylint score < 8.0
- Coverage < 70%
- Security issues (Bandit)
- Syntax errors

**❌ CRITICAL (Fix within 1 day):**
- Complexity > 10
- Major code smells
- Type errors en dominio

**⚠️ MAJOR (Fix within sprint):**
- Maintainability < 20
- Missing type hints en aplicación
- Code duplication

**💡 MINOR (Fix cuando sea posible):**
- Style violations
- Missing docstrings
- Optimization opportunities

### Proceso de Resolución

1. **Detección Automática**
   - Pre-commit hooks
   - CI/CD pipeline
   - Quality dashboard

2. **Notificación**
   - GitHub status checks
   - Dashboard alerts
   - Email reports (opcional)

3. **Resolución**
   - Assign owner
   - Create issue/task
   - Fix & verify
   - Update metrics

---

## 🔄 Integración CI/CD

### GitHub Actions (Futuro - Sprint 4)

```yaml
name: Quality Gates
on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Quality Checks
        run: python scripts/quality_check.py --format json

      - name: Generate Dashboard
        run: python scripts/generate_reports.py

      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: quality-reports
          path: quality_reports/
```

### Quality Gates en Pull Requests

**Checks Requeridos:**
- ✅ Pylint score ≥ 8.0
- ✅ Coverage ≥ 70%
- ✅ No security issues
- ✅ Max complexity ≤ 10
- ✅ All tests passing

---

## 📊 Monitoreo y Métricas

### Dashboard URL
```
file://quality_reports/latest_dashboard.html
```

### Comandos de Monitoreo

```bash
# Estado rápido
python scripts/quality_check.py

# Dashboard completo
python scripts/generate_reports.py

# Solo pylint
pylint aplicacion dominio --score=y

# Solo coverage
coverage report

# Solo complexity
radon cc aplicacion dominio -s
```

### Métricas de Trending

**Tracking Semanal:**
- Pylint score evolution
- Coverage percentage changes
- Complexity trends
- Issues resolved/introduced

---

## 🎓 Mejores Prácticas

### ✅ DOs

1. **Siempre ejecutar quality checks antes de commit**
2. **Escribir tests para nueva funcionalidad**
3. **Mantener funciones simples (< 10 complexity)**
4. **Usar type hints en código de dominio**
5. **Documentar APIs públicas**
6. **Resolver issues de quality gates inmediatamente**

### ❌ DON'Ts

1. **NO hacer bypass de pre-commit hooks rutinariamente**
2. **NO ignorar warnings de security (Bandit)**
3. **NO crear funciones con complexity > 15**
4. **NO reducir artificialmente coverage con exclusions**
5. **NO hacer commits sin ejecutar tests**

### 🔧 Refactoring Guidelines

**Cuando Refactorizar:**
- Complexity grade D o F
- Pylint score < 7.0 en un archivo
- Coverage < 60% en módulo crítico
- Duplicación de código > 15 líneas

**Cómo Refactorizar:**
1. Crear tests para funcionalidad existente
2. Aplicar patterns apropiados (Strategy, Factory, etc.)
3. Extraer métodos/clases
4. Verificar que quality gates pasan
5. Actualizar documentación

---

## 📞 Soporte y Contacto

**Responsable de Calidad:** Victor Valotto
**Email:** vvalotto@gmail.com
**Jira Project:** SSA
**Wiki:** [Confluence Quality Standards](https://vvalotto.atlassian.net/wiki/)

**Canales de Comunicación:**
- 🐛 Issues: GitHub Issues
- 📊 Métricas: Quality Dashboard
- 📚 Docs: `docs/` directory
- 🔧 Tools: `scripts/` directory

---

## 📅 Roadmap de Calidad

### Sprint 3 (Actual) ✅
- ✅ Baseline establecido
- ✅ Quality gates definidos
- ✅ Herramientas configuradas
- ✅ Scripts automatizados

### Sprint 4 (Próximo)
- 🔄 CI/CD integration
- 🔄 Quality gates enforcement
- 🔄 Advanced reporting
- 🔄 Team training

### Sprint 5 (Futuro)
- 🔮 Advanced metrics
- 🔮 Performance monitoring
- 🔮 Technical debt tracking
- 🔮 Quality coaching

### Sprint 6 (Futuro)
- 🔮 Quality excellence
- 🔮 Automated refactoring suggestions
- 🔮 Predictive quality analytics
- 🔮 Quality culture establishment

---

**📋 Última Actualización:** 2025-09-20
**📈 Versión:** 1.0
**🎯 Estado:** Active Implementation