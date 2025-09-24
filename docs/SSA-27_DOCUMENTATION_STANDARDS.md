# SSA-27: Code Documentation Standards

**Epic:** SSA-3 [EPIC-QUALITY] Mejoras de Calidad y Mantenibilidad
**Ticket:** SSA-27 - Code Documentation Standards
**Fecha:** 2025-09-22
**Responsable:** Victor Valotto
**Status:** ✅ ACTIVO

---

## 🎯 **Propósito**

Este documento establece los estándares de documentación de código para el proyecto SenialSOLIDApp, definiendo guidelines consistentes para mejorar maintainability, team collaboration y developer onboarding.

---

## 📋 **Standards Generales**

### **1. Principios de Documentación**

- **Clarity over Brevity**: Documentación clara y comprensible antes que concisa
- **Why over What**: Explicar el propósito y la lógica, no solo la implementación
- **Context Awareness**: Considerar el contexto DDD y arquitectura del proyecto
- **Consistency**: Aplicar estándares uniformes en todo el codebase
- **Maintainability**: Documentación que se mantiene actualizada con el código

### **2. Scope de Documentación**

| Elemento | Nivel de Documentación | Estándar |
|----------|------------------------|----------|
| **Public APIs** | Completa | Google Style + Type hints |
| **Domain Models** | Completa | DDD patterns + business logic |
| **Application Services** | Completa | Use cases + dependencies |
| **Infrastructure** | Selectiva | Complex implementations |
| **Private Methods** | Mínima | Solo lógica compleja |
| **Test Functions** | Descriptiva | Purpose + test scenarios |

---

## 📝 **Docstring Standards**

### **Google Style Docstrings (Estándar Adoptado)**

Siguiendo **PEP 257** y **Google Style Guide** para Python docstrings.

#### **Estructura Básica**

```python
def function_name(param1: Type, param2: Type = default) -> ReturnType:
    """Brief description (one line).

    More detailed description if needed. Explain the purpose, behavior,
    and any important implementation details relevant to the DDD context.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter. Defaults to default_value.

    Returns:
        Description of return value and its significance

    Raises:
        ExceptionType: Description of when this exception is raised
        AnotherException: Description of another exception

    Example:
        Basic usage example:

        >>> result = function_name("value", 10)
        >>> print(result)
        Expected output
    """
```

### **Secciones Obligatorias**

| Sección | Cuando Usar | Obligatorio |
|---------|-------------|-------------|
| **Brief Description** | Siempre | ✅ SÍ |
| **Detailed Description** | Funciones complejas | 🔶 CONDICIONAL |
| **Args** | Funciones con parámetros | ✅ SÍ |
| **Returns** | Funciones que retornan valores | ✅ SÍ |
| **Raises** | Funciones que lanzan excepciones | ✅ SÍ |
| **Example** | APIs públicas | 🔶 RECOMENDADO |
| **Note** | Consideraciones especiales | 🔶 CONDICIONAL |

---

## 🏗️ **Documentación por Tipo de Elemento**

### **1. Domain Models (Entidades)**

```python
class Senial(SenialBase):
    """Domain entity representing a signal in the signal processing system.

    A Senial encapsulates signal data and behavior following DDD principles.
    It maintains signal values, metadata, and provides operations for
    signal manipulation within domain constraints.

    This class implements the Repository pattern interface and follows
    SOLID principles for signal data management.

    Attributes:
        id: Unique identifier for the signal
        comentario: Human-readable description
        fecha_adquisicion: Timestamp when signal was acquired
        cantidad: Current number of values in the signal
        tamanio: Maximum capacity of the signal
        valores: List containing the signal values

    Example:
        Creating and using a signal:

        >>> signal = Senial(tamanio=100)
        >>> signal.id = "SIG_001"
        >>> signal.poner_valor(1.5)
        >>> print(signal.cantidad)
        1
    """
```

### **2. Application Services**

```python
class ControladorAdquisicion:
    """Application service for signal acquisition operations.

    Orchestrates signal acquisition use cases by coordinating domain objects
    and infrastructure services. Implements the Application Service pattern
    in the DDD architecture.

    This controller handles:
    - Signal acquisition from various sources
    - Signal identification and metadata management
    - Repository operations for signal persistence
    - Exception handling with recovery strategies

    Dependencies:
        - Configurador: DI container for acquiring dependencies
        - Repository: Signal persistence abstraction
        - Exception handlers: SSA-26 error handling patterns
    """

    def adquirir_senial(self) -> Senial:
        """Acquire a signal from the configured acquisition source.

        Coordinates the signal acquisition process using the configured
        adquisidor and applies exception handling with recovery strategies.

        Returns:
            Senial: The acquired signal with metadata

        Raises:
            AcquisitionException: When signal acquisition fails
            ValidationException: When acquired signal is invalid
            RepositoryException: When persistence operations fail

        Example:
            >>> controller = ControladorAdquisicion()
            >>> signal = controller.adquirir_senial()
            >>> print(f"Signal acquired: {signal.id}")
        """
```

### **3. Infrastructure Components**

```python
class ContextoPickle(BaseContexto):
    """Pickle-based persistence context for entity serialization.

    Infrastructure implementation of the Repository pattern using Python's
    pickle serialization for data persistence. Provides CRUD operations
    with exception handling and audit/trace capabilities.

    This implementation:
    - Serializes domain entities to pickle files
    - Manages file-based storage with directory structure
    - Implements audit and trace patterns from SSA-26
    - Provides recovery strategies for I/O operations

    Args:
        recurso: Directory path where pickle files will be stored

    Raises:
        ConfigurationException: When resource path is invalid
        DataAccessException: When file I/O operations fail
    """
```

### **4. Utility Functions**

```python
def handle_with_recovery(operation: Callable, operation_name: str,
                        context: Dict, max_attempts: int = 3) -> Any:
    """Execute operation with automatic retry and recovery strategies.

    Implements the recovery pattern from SSA-26 by providing automatic
    retry logic, exception context enrichment, and fallback mechanisms
    for resilient operation execution.

    Args:
        operation: Function to execute with recovery
        operation_name: Human-readable name for logging/monitoring
        context: Additional context for error reporting
        max_attempts: Maximum retry attempts before giving up

    Returns:
        Any: Result of the successful operation execution

    Raises:
        Original exception: After all recovery attempts exhausted

    Example:
        >>> def risky_operation():
        ...     return api_call()
        >>> result = handle_with_recovery(
        ...     risky_operation, "api_call", {"endpoint": "/data"}
        ... )
    """
```

---

## 🔧 **Type Hints Standards**

### **Type Annotation Requirements**

| Scope | Type Hints Required | Examples |
|-------|-------------------|----------|
| **Public APIs** | ✅ Obligatorio | Function signatures, return types |
| **Domain Models** | ✅ Obligatorio | Properties, method parameters |
| **Application Services** | ✅ Obligatorio | Service methods, dependencies |
| **Infrastructure** | 🔶 Recomendado | Complex implementations |
| **Private Methods** | 🔶 Opcional | Complex logic only |

### **Type Hint Examples**

```python
from typing import List, Dict, Optional, Union, Callable, Any
from abc import ABC, abstractmethod

# Domain Model
class Senial:
    def __init__(self, tamanio: int = 10) -> None:
        self._valores: List[float] = []
        self._cantidad: int = 0

    def poner_valor(self, valor: Union[int, float]) -> None:
        """Add value to signal."""
        pass

    def obtener_valor(self, indice: int) -> Optional[float]:
        """Get value at index."""
        pass

# Application Service
class ControladorAdquisicion:
    def listar_seniales_adquiridas(self) -> List[Dict[str, Any]]:
        """List all acquired signals with metadata."""
        pass

# Infrastructure
class BaseContexto(ABC):
    @abstractmethod
    def persistir(self, entidad: Any, id_entidad: str) -> None:
        """Persist entity with given ID."""
        pass
```

---

## 💬 **Inline Comments Standards**

### **When to Use Inline Comments**

- **Complex business logic** that isn't obvious
- **DDD patterns** implementation details
- **Performance optimizations** or trade-offs
- **Workarounds** for library limitations
- **Security considerations**

### **Comment Style Guidelines**

```python
# Good: Explains WHY, not WHAT
# Use repository pattern to maintain domain boundary separation
repository = Configurador.rep_adquisicion

# Good: Explains business rule
# Signal capacity must not exceed domain constraints for memory management
if self._cantidad >= self._tamanio:
    raise ValidationException(...)

# Good: Explains complex logic
# Apply exponential backoff for acquisition retry to prevent system overload
for attempt in range(max_attempts):
    time.sleep(2 ** attempt)

# Bad: Explains obvious code
# Increment counter by 1
counter += 1

# Bad: Outdated or incorrect comment
# TODO: This will be fixed later (from 2023)
```

### **TODO Comments Format**

```python
# TODO(SSA-XX): Description of what needs to be done
# FIXME(issue-reference): Description of the problem
# NOTE: Important information for future developers
# HACK: Temporary solution with explanation why
```

---

## 📚 **Documentation Architecture**

### **DDD-Specific Documentation**

#### **Domain Layer Documentation**

- **Business rules** and invariants
- **Entity relationships** and aggregates
- **Domain events** and their triggers
- **Value objects** and their constraints

#### **Application Layer Documentation**

- **Use cases** and their flows
- **Service dependencies** and their purposes
- **Transaction boundaries**
- **Integration with domain layer**

#### **Infrastructure Layer Documentation**

- **External service integrations**
- **Data mapping strategies**
- **Performance considerations**
- **Configuration requirements**

### **Architecture Documentation Format**

```python
class SenialRepository(ABC):
    """Abstract repository for Signal aggregate persistence.

    Domain Repository Pattern:
        Provides abstraction layer between domain and infrastructure,
        allowing domain logic to remain independent of persistence details.

    Aggregate Boundary:
        This repository manages the Senial aggregate root and ensures
        consistency of all operations within the aggregate boundary.

    Transaction Management:
        All repository operations should maintain ACID properties
        and support unit of work pattern for consistency.
    """
```

---

## 🔍 **Quality Standards**

### **Documentation Quality Gates**

| Metric | Target | Tool | Enforcement |
|--------|--------|------|-------------|
| **Docstring Coverage** | 90%+ | pydocstyle | Quality gates |
| **Type Hint Coverage** | 85%+ | mypy | Quality gates |
| **Documentation Lint Score** | 9.0/10 | pydocstyle | Quality gates |
| **API Documentation** | 100% | Sphinx | Manual review |

### **Review Checklist Items**

- [ ] All public methods have complete docstrings
- [ ] Args, Returns, Raises sections are accurate
- [ ] Type hints are comprehensive and correct
- [ ] Examples are provided for complex APIs
- [ ] Business context is explained for domain code
- [ ] DDD patterns are documented appropriately
- [ ] Inline comments explain WHY, not WHAT
- [ ] TODO comments follow format standards

---

## 🛠️ **Tools and Configuration**

### **pydocstyle Configuration**

```ini
# .pydocstyle
[pydocstyle]
convention = google
add-ignore = D100,D104,D213,D203
match-dir = (?!tests).*
match = (?!test_).*\.py
```

### **mypy Configuration for Documentation**

```ini
# mypy.ini
[mypy]
# Type checking configuration that supports documentation
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### **Quality Gates Integration**

```yaml
# quality_gates.yaml - Documentation section
documentation:
  pydocstyle:
    enabled: true
    score_threshold: 9.0
    coverage_threshold: 90.0
  type_hints:
    enabled: true
    coverage_threshold: 85.0
  sphinx_build:
    enabled: true
    require_success: true
```

---

## 📖 **Examples and Templates**

### **Complete Function Example**

```python
def guardar_senial(self, senial: Senial) -> None:
    """Save signal to the configured repository with recovery handling.

    Persists the provided signal using the repository pattern while
    applying SSA-26 exception handling and recovery strategies. This
    operation maintains domain integrity by validating signal state
    before persistence.

    Args:
        senial: Domain entity to persist. Must have valid ID and data.

    Raises:
        RepositoryException: When persistence operation fails
        ValidationException: When signal state is invalid
        DataAccessException: When underlying storage is unavailable

    Example:
        Saving a newly acquired signal:

        >>> controller = ControladorAdquisicion()
        >>> signal = Senial(tamanio=100)
        >>> signal.id = "SIG_001"
        >>> signal.poner_valor(1.5)
        >>> controller.guardar_senial(signal)

    Note:
        This method uses transaction boundaries to ensure consistency
        and implements automatic retry logic for transient failures.
    """
    signal_id = getattr(senial, 'id', 'unknown')

    def _guardar_en_repo():
        """Internal function for repository save with recovery support."""
        # Business rule: Validate signal before persistence
        if not hasattr(senial, 'id') or not senial.id:
            raise ValidationException("Signal must have valid ID")

        rep = Configurador.rep_adquisicion
        rep.guardar(senial)
        logger.info("Señal guardada exitosamente",
                   extra={"senial_id": signal_id})

    try:
        return handle_with_recovery(
            operation=_guardar_en_repo,
            operation_name="guardar_senial",
            context={
                "senial_id": signal_id,
                "repository_type": type(Configurador.rep_adquisicion).__name__,
                "senial_cantidad": getattr(senial, '_cantidad', 0)
            },
            max_attempts=3
        )
    except RepositoryException:
        # Re-raise repository exceptions as-is
        raise
    except Exception as ex:
        # Wrap unexpected exceptions with context
        raise RepositoryException(
            operation="guardar",
            entity_type="senial",
            entity_id=signal_id,
            context={
                "repository_type": type(Configurador.rep_adquisicion).__name__,
                "senial_cantidad": getattr(senial, '_cantidad', 0)
            },
            cause=ex
        )
```

---

## 🔄 **Maintenance and Updates**

### **Documentation Lifecycle**

1. **Creation**: Follow templates and standards
2. **Review**: Use checklist for quality assurance
3. **Maintenance**: Update with code changes
4. **Validation**: Automated quality gate checks

### **Update Process**

- Documentation updates **required** with feature PRs
- Breaking changes **must** update API documentation
- Standards evolution through team discussion
- Regular review of documentation quality metrics

---

## 📞 **References and Support**

### **Standards References**

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Domain-Driven Design](https://domainlanguage.com/ddd/)

### **Project Context**

- **SSA-25**: Quality metrics and linting integration
- **SSA-26**: Exception handling patterns
- **DDD Architecture**: Domain-driven design implementation
- **SOLID Principles**: Code organization patterns

---

*Este documento es parte del ticket SSA-27 y se actualiza conforme evolucionan los estándares del proyecto.*

**Última Actualización:** 2025-09-22
**Versión:** 1.0
**Status:** ✅ ACTIVO