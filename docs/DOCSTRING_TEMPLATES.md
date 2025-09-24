# SSA-27: Docstring Templates y Ejemplos

**Epic:** SSA-3 [EPIC-QUALITY] Mejoras de Calidad y Mantenibilidad
**Ticket:** SSA-27 - Code Documentation Standards
**Fecha:** 2025-09-22
**Responsable:** Victor Valotto

---

## 🎯 **Propósito**

Este documento proporciona templates y ejemplos específicos para documentar código en el proyecto SenialSOLIDApp usando Google Style docstrings, adaptados para la arquitectura DDD del proyecto.

---

## 📝 **Templates por Tipo de Elemento**

### **1. Domain Models (Entidades y Value Objects)**

#### **Template para Entidades**

```python
class EntityName(BaseClass):
    """Brief description of the domain entity.

    Detailed description explaining the entity's role in the domain,
    its business significance, and relationships with other entities.
    Include aggregate boundary information if applicable.

    This entity represents [business concept] and enforces [business rules].
    It participates in [use cases] and maintains [invariants].

    Attributes:
        attribute1: Business meaning of this attribute
        attribute2: Another important domain attribute
        _private_attr: Internal implementation detail

    Example:
        Creating and using the entity:

        >>> entity = EntityName()
        >>> entity.business_operation()
        >>> print(entity.important_property)
        Expected business outcome
    """

    def __init__(self, required_param: Type, optional_param: Type = default) -> None:
        """Initialize entity with required domain data.

        Args:
            required_param: Business-critical parameter description
            optional_param: Optional parameter with business default

        Raises:
            DomainException: When business rules are violated
            ValidationException: When parameters don't meet constraints
        """

    @property
    def business_property(self) -> Type:
        """Get entity's business property.

        Returns:
            Type: The business value with its significance

        Note:
            This property represents [business concept] and is used
            in [specific business scenarios].
        """

    def domain_operation(self, param: Type) -> Type:
        """Perform important domain operation.

        Implements business rule: [specific business rule description].
        This operation ensures [business invariant] is maintained.

        Args:
            param: Parameter with business meaning

        Returns:
            Type: Result with business significance

        Raises:
            BusinessRuleException: When business logic prevents operation
            DomainException: When domain constraints are violated

        Example:
            >>> entity.domain_operation(valid_business_value)
            Expected business result
        """
```

#### **Template para Value Objects**

```python
class ValueObjectName:
    """Value object representing [business concept].

    Immutable value object that encapsulates [business attribute]
    and ensures [business constraints]. Following DDD principles,
    this object has no identity and is compared by value equality.

    Business Rules:
        - Rule 1: Description of business constraint
        - Rule 2: Another business validation
        - Rule 3: Domain-specific requirement

    Attributes:
        value: The encapsulated business value
        derived_property: Computed business attribute

    Example:
        Creating and comparing value objects:

        >>> vo1 = ValueObjectName("valid_value")
        >>> vo2 = ValueObjectName("valid_value")
        >>> print(vo1 == vo2)  # True - value equality
        True
    """
```

### **2. Application Services**

#### **Template para Application Services**

```python
class ApplicationServiceName:
    """Application service for [specific use case area].

    Orchestrates [domain area] use cases by coordinating domain objects,
    infrastructure services, and external integrations. Implements
    application-level transaction boundaries and error handling.

    This service handles:
        - Use case 1: Description
        - Use case 2: Description
        - Cross-cutting concern: Description

    Dependencies:
        repository: Domain repository for [entity] persistence
        external_service: Integration with [external system]
        event_publisher: For publishing domain events

    Example:
        Using the application service:

        >>> service = ApplicationServiceName(dependencies)
        >>> result = service.execute_use_case(parameters)
        >>> print(result.success)
        True
    """

    def __init__(self, repository: RepositoryType,
                 external_service: ServiceType) -> None:
        """Initialize application service with dependencies.

        Args:
            repository: Repository for domain persistence
            external_service: External service integration

        Raises:
            ConfigurationException: When dependencies are invalid
        """

    def execute_primary_use_case(self, command: CommandType) -> ResultType:
        """Execute the primary use case for [business operation].

        Implements the [use case name] by:
        1. Validating command data
        2. Loading relevant domain objects
        3. Executing business logic
        4. Persisting changes
        5. Publishing events

        Args:
            command: Command object with use case parameters

        Returns:
            ResultType: Use case execution result with status

        Raises:
            UseCaseException: When use case execution fails
            ValidationException: When command data is invalid
            DomainException: When business rules prevent execution

        Example:
            >>> command = CreateCommand(valid_data)
            >>> result = service.execute_primary_use_case(command)
            >>> print(result.entity_id)
            "ENT_001"
        """
```

### **3. Infrastructure Components**

#### **Template para Repositories**

```python
class ConcreteRepository(AbstractRepository):
    """Infrastructure implementation of [Entity] repository.

    Provides persistence for [Entity] aggregate using [technology/approach].
    Implements the Repository pattern to maintain separation between
    domain logic and data access concerns.

    Storage Details:
        - Technology: [Database/File system/etc.]
        - Schema: [Table/Document structure]
        - Indexing: [Performance considerations]
        - Transactions: [Consistency approach]

    Args:
        connection: Database/storage connection
        mapper: Object-relational mapping component

    Example:
        Using the repository:

        >>> repo = ConcreteRepository(connection, mapper)
        >>> entity = repo.find_by_id("ENT_001")
        >>> repo.save(modified_entity)
    """

    def find_by_business_criteria(self, criteria: CriteriaType) -> List[EntityType]:
        """Find entities matching business criteria.

        Translates business query into infrastructure-specific operation
        while maintaining domain abstraction.

        Args:
            criteria: Business criteria for entity selection

        Returns:
            List[EntityType]: Entities matching the criteria

        Raises:
            RepositoryException: When data access fails
            DataIntegrityException: When data consistency issues found

        Example:
            >>> criteria = BusinessCriteria(status="active")
            >>> entities = repo.find_by_business_criteria(criteria)
            >>> print(len(entities))
            5
        """
```

#### **Template para External Service Adapters**

```python
class ExternalServiceAdapter:
    """Adapter for integrating with [External System Name].

    Translates between domain objects and external service protocol,
    implementing the Adapter pattern to isolate external dependencies
    from core business logic.

    Integration Details:
        - Protocol: [REST/SOAP/Message Queue/etc.]
        - Authentication: [Method used]
        - Rate Limiting: [Constraints and handling]
        - Error Handling: [Retry/Circuit breaker strategy]

    Args:
        client: External service client instance
        config: Service configuration parameters

    Example:
        Using the adapter:

        >>> adapter = ExternalServiceAdapter(client, config)
        >>> result = adapter.call_external_operation(domain_data)
        >>> print(result.success)
        True
    """

    def translate_to_external_format(self, domain_object: DomainType) -> ExternalType:
        """Convert domain object to external service format.

        Args:
            domain_object: Domain entity to convert

        Returns:
            ExternalType: Object in external service format

        Raises:
            TranslationException: When conversion fails
            ValidationException: When domain object is invalid

        Example:
            >>> external_data = adapter.translate_to_external_format(entity)
            >>> print(external_data.external_id)
            "EXT_12345"
        """
```

### **4. Exception Classes**

#### **Template para Domain Exceptions**

```python
class DomainSpecificException(BaseDomainException):
    """Exception for [specific domain violation].

    Represents violation of [business rule/constraint] in the [domain area].
    Provides rich context for debugging and user feedback while maintaining
    domain language and concepts.

    Business Context:
        This exception occurs when [business scenario] violates [rule].
        It typically happens during [operation] and affects [stakeholders].

    Attributes:
        business_context: Dict with domain-specific error details
        recovery_suggestions: List of possible recovery actions
        error_code: Domain-specific error identifier

    Example:
        Handling domain exception:

        >>> try:
        ...     domain_operation()
        >>> except DomainSpecificException as e:
        ...     print(e.business_context)
        ...     print(e.recovery_suggestions)
    """

    def __init__(self, business_reason: str, context: Dict[str, Any],
                 recovery_options: List[str] = None) -> None:
        """Initialize domain exception with business context.

        Args:
            business_reason: Business explanation of the violation
            context: Domain-specific context for debugging
            recovery_options: Suggested recovery actions

        Example:
            >>> raise DomainSpecificException(
            ...     "Signal capacity exceeded business limits",
            ...     {"current_size": 150, "limit": 100, "signal_id": "SIG_001"},
            ...     ["Reduce signal size", "Request capacity increase"]
            ... )
        """
```

### **5. Utility Functions**

#### **Template para Utility Functions**

```python
def utility_function_name(param1: Type, param2: Type = default) -> ReturnType:
    """Brief description of utility function purpose.

    More detailed explanation of what the function does, why it exists,
    and how it fits into the overall system architecture. Include any
    performance considerations or usage guidelines.

    Args:
        param1: Description of first parameter and its constraints
        param2: Description of second parameter with default behavior

    Returns:
        ReturnType: Description of return value and its significance

    Raises:
        UtilityException: When utility operation fails
        ValueError: When input parameters are invalid

    Example:
        Basic usage:

        >>> result = utility_function_name("input", 42)
        >>> print(result)
        Expected output

    Note:
        Important considerations about performance, thread safety,
        or usage limitations.
    """
```

### **6. Test Functions**

#### **Template para Test Functions**

```python
def test_specific_behavior(self):
    """Test that [specific behavior] works correctly.

    Verifies [business rule/technical requirement] by:
    1. Setting up [test scenario]
    2. Executing [operation under test]
    3. Asserting [expected outcome]

    This test covers [test category: unit/integration/acceptance]
    and validates [specific aspect of the system].

    Test Data:
        - Input: [description of test input]
        - Expected: [description of expected result]
        - Edge Cases: [description of edge cases covered]
    """
```

### **7. Configuration Classes**

#### **Template para Configuration**

```python
class ConfigurationClass:
    """Configuration for [component/subsystem].

    Encapsulates configuration parameters for [specific area] with
    validation, defaults, and environment-specific overrides.
    Follows configuration as code principles.

    Configuration Scope:
        - Environment: [dev/test/prod considerations]
        - Security: [sensitive data handling]
        - Validation: [parameter constraints]
        - Dependencies: [related configurations]

    Attributes:
        setting1: Description and valid values
        setting2: Another configuration parameter

    Example:
        Loading and using configuration:

        >>> config = ConfigurationClass.from_environment()
        >>> print(config.setting1)
        "production_value"
    """

    @classmethod
    def from_environment(cls, env_prefix: str = "APP") -> "ConfigurationClass":
        """Load configuration from environment variables.

        Args:
            env_prefix: Prefix for environment variable names

        Returns:
            ConfigurationClass: Validated configuration instance

        Raises:
            ConfigurationException: When required settings are missing
            ValidationException: When settings have invalid values

        Example:
            >>> config = ConfigurationClass.from_environment("SENIAL")
            >>> print(config.is_valid())
            True
        """
```

---

## 🔧 **Templates Específicos para el Proyecto**

### **Template para Señal (Domain Entity)**

```python
class Senial(SenialBase):
    """Domain entity representing a signal in the signal processing system.

    A Senial encapsulates signal data and behavior following DDD principles.
    It maintains signal values, metadata, and provides operations for
    signal manipulation within domain constraints.

    Business Rules:
        - Signal capacity cannot exceed configured maximum (tamanio)
        - All values must be numeric (int or float)
        - Signal ID must be unique within the system
        - Acquisition date is immutable once set

    Attributes:
        id: Unique identifier for the signal
        comentario: Human-readable description of signal purpose
        fecha_adquisicion: Timestamp when signal was acquired
        cantidad: Current number of values stored
        tamanio: Maximum capacity for signal values
        valores: List containing the actual signal measurements

    Example:
        Creating and manipulating a signal:

        >>> signal = Senial(tamanio=100)
        >>> signal.id = "SIG_001"
        >>> signal.comentario = "Temperature readings from sensor A"
        >>> signal.poner_valor(25.5)
        >>> print(f"Signal has {signal.cantidad} values")
        Signal has 1 values
    """

    def poner_valor(self, valor: Union[int, float]) -> None:
        """Add a measurement value to the signal.

        Implements business rule: Signal capacity must not exceed maximum
        configured size to prevent memory issues and maintain performance.

        Args:
            valor: Numeric measurement value to add to signal

        Raises:
            ValidationException: When signal is at capacity or value is invalid

        Example:
            >>> signal = Senial(tamanio=5)
            >>> signal.poner_valor(10.5)
            >>> signal.poner_valor(12.3)
            >>> print(signal.cantidad)
            2
        """

    def obtener_valor(self, indice: int) -> float:
        """Retrieve signal value at specified index.

        Args:
            indice: Zero-based index of value to retrieve

        Returns:
            float: Signal measurement value at the specified position

        Raises:
            ValidationException: When index is out of bounds

        Example:
            >>> signal.poner_valor(15.7)
            >>> value = signal.obtener_valor(0)
            >>> print(value)
            15.7
        """
```

### **Template para ControladorAdquisicion (Application Service)**

```python
class ControladorAdquisicion:
    """Application service for signal acquisition and management operations.

    Orchestrates signal acquisition use cases by coordinating domain objects,
    repositories, and external acquisition sources. Implements transaction
    boundaries and error handling with recovery strategies from SSA-26.

    Use Cases Handled:
        - Signal acquisition from configured sources
        - Signal identification and metadata management
        - Signal persistence and retrieval operations
        - Signal listing and search operations

    Dependencies:
        Configurador: DI container providing acquisition and repository services
        Exception handlers: SSA-26 error handling with recovery patterns
        Logging: Structured logging for operations monitoring

    Example:
        Basic signal acquisition workflow:

        >>> controller = ControladorAdquisicion()
        >>> signal = controller.adquirir_senial()
        >>> controller.identificar_senial(signal, "New Signal")
        >>> controller.guardar_senial(signal)
    """

    def adquirir_senial(self) -> Senial:
        """Acquire a signal from the configured acquisition source.

        Coordinates the signal acquisition process using the configured
        adquisidor from the DI container and applies exception handling
        with automatic recovery strategies.

        Use Case Flow:
        1. Get configured adquisidor from DI container
        2. Execute signal reading operation
        3. Retrieve acquired signal with metadata
        4. Apply error handling and recovery if needed

        Returns:
            Senial: Newly acquired signal with basic metadata

        Raises:
            AcquisitionException: When signal acquisition fails after retries
            ValidationException: When acquired signal doesn't meet constraints
            ConfigurationException: When adquisidor is not properly configured

        Example:
            >>> controller = ControladorAdquisicion()
            >>> signal = controller.adquirir_senial()
            >>> print(f"Acquired signal with {signal.cantidad} values")
            Acquired signal with 50 values
        """

    def guardar_senial(self, senial: Senial) -> None:
        """Persist signal to the configured repository.

        Saves the provided signal using the repository pattern while
        applying SSA-26 exception handling and recovery strategies.
        Maintains transaction boundaries for data consistency.

        Args:
            senial: Domain entity to persist, must have valid ID and data

        Raises:
            RepositoryException: When persistence operation fails after retries
            ValidationException: When signal state is invalid for persistence
            DataAccessException: When underlying storage is unavailable

        Example:
            >>> signal = Senial()
            >>> signal.id = "SIG_001"
            >>> signal.poner_valor(25.5)
            >>> controller.guardar_senial(signal)
        """
```

---

## 📊 **Guidelines de Uso**

### **Cuándo Usar Cada Template**

| Tipo de Código | Template | Nivel de Detalle | Ejemplo |
|----------------|----------|------------------|---------|
| **Domain Entities** | Domain Model Template | Máximo | Senial, SenialBase |
| **Application Services** | Application Service Template | Alto | ControladorAdquisicion |
| **Infrastructure** | Repository/Adapter Template | Medio | ContextoPickle |
| **Utilities** | Utility Function Template | Bajo | Helper functions |
| **Tests** | Test Function Template | Específico | Test cases |

### **Secciones Obligatorias por Context**

| Context | Brief | Args/Returns | Raises | Example | Note |
|---------|-------|--------------|--------|---------|------|
| **Public API** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Domain Logic** | ✅ | ✅ | ✅ | 🔶 | ✅ |
| **Infrastructure** | ✅ | ✅ | ✅ | 🔶 | 🔶 |
| **Private Methods** | ✅ | 🔶 | 🔶 | ❌ | 🔶 |
| **Tests** | ✅ | ❌ | ❌ | ❌ | 🔶 |

**Leyenda:** ✅ Obligatorio | 🔶 Recomendado | ❌ No necesario

---

## 🎯 **Best Practices**

### **1. Business Language**
- Usar terminología del dominio en las descripciones
- Explicar reglas de negocio, no solo implementación técnica
- Incluir contexto DDD cuando sea relevante

### **2. Error Handling**
- Documentar todas las excepciones posibles
- Explicar cuándo y por qué se lanzan
- Incluir estrategias de recovery cuando aplique

### **3. Examples**
- Proporcionar ejemplos realistas del dominio
- Mostrar casos de uso típicos
- Incluir edge cases importantes

### **4. Type Information**
- Usar type hints comprehensivos
- Documentar constraints de tipos
- Explicar relaciones entre tipos

### **5. Performance Notes**
- Mencionar consideraciones de performance
- Documentar complexity algorithms cuando relevante
- Advertir sobre operaciones costosas

---

## 🔄 **Template Evolution**

### **Feedback Loop**
1. **Usar templates** en código nuevo
2. **Recopilar feedback** del equipo
3. **Refinar templates** basado en experiencia
4. **Actualizar estándares** según necesidades

### **Version Control**
- Templates versionados con el proyecto
- Cambios documentados en changelog
- Backward compatibility considerada

---

*Este documento es parte del ticket SSA-27 y proporciona templates prácticos para documentación consistente.*

**Última Actualización:** 2025-09-22
**Versión:** 1.0
**Próxima Revisión:** Post-implementation feedback