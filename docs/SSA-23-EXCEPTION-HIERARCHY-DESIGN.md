# SSA-23: Custom Exception Hierarchy Design

## 🏗️ Arquitectura de Excepciones - Diseño Detallado

### 📋 Principios de Diseño

1. **Integración SSA-22 Automática**: Todas las excepciones loggean automáticamente
2. **Context Enrichment**: Información contextual rica para debugging
3. **Recovery Strategy Integration**: Cada excepción define su estrategia de recuperación
4. **Layer Separation**: Excepciones específicas por capa arquitectural
5. **User-Friendly Messages**: Mensajes diferenciados para usuarios vs desarrolladores

## 🌳 Jerarquía de Excepciones

```
SenialSOLIDException (Base)
├── DomainException
│   ├── ValidationException
│   ├── ProcessingException
│   ├── AcquisitionException
│   └── RepositoryException
├── InfrastructureException
│   ├── ConfigurationException
│   ├── DataAccessException
│   └── NetworkException
└── PresentationException
    ├── WebException
    └── ConsoleException
```

## 🎯 Base Exception Class

```python
class SenialSOLIDException(Exception):
    """
    Base exception class for SenialSOLID application
    Provides automatic SSA-22 logging integration and context enrichment
    """

    def __init__(
        self,
        message: str,
        user_message: str = None,
        context: Dict[str, Any] = None,
        recovery_suggestion: str = None,
        error_code: str = None,
        cause: Exception = None
    ):
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message
        self.context = context or {}
        self.recovery_suggestion = recovery_suggestion
        self.error_code = error_code or self._generate_error_code()
        self.cause = cause
        self.timestamp = datetime.utcnow()

        # Automatic structured logging
        self._log_exception()

    def _generate_error_code(self) -> str:
        """Generate unique error code for tracking"""
        return f"{self.__class__.__name__}_{int(time.time())}"

    def _log_exception(self):
        """Automatic SSA-22 structured logging"""
        logger = get_logger(self.__class__.__module__)
        logger.error(
            f"Exception: {self.__class__.__name__}",
            extra={
                "error_code": self.error_code,
                "error_type": self.__class__.__name__,
                "message": self.message,
                "user_message": self.user_message,
                "context": self.context,
                "recovery_suggestion": self.recovery_suggestion,
                "cause": str(self.cause) if self.cause else None,
                "timestamp": self.timestamp.isoformat()
            },
            exc_info=True
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            "error_code": self.error_code,
            "error_type": self.__class__.__name__,
            "message": self.message,
            "user_message": self.user_message,
            "context": self.context,
            "recovery_suggestion": self.recovery_suggestion,
            "timestamp": self.timestamp.isoformat()
        }
```

## 🏭 Domain Layer Exceptions

### ValidationException
```python
class ValidationException(DomainException):
    """Input validation and business rule violations"""

    def __init__(self, field: str, value: Any, rule: str, **kwargs):
        context = {
            "field": field,
            "invalid_value": str(value),
            "validation_rule": rule
        }
        super().__init__(
            f"Validation failed for {field}: {rule}",
            user_message=f"Valor inválido para {field}",
            context=context,
            recovery_suggestion=f"Verifique que {field} cumple con: {rule}",
            **kwargs
        )
```

### ProcessingException
```python
class ProcessingException(DomainException):
    """Signal processing errors with performance context"""

    def __init__(self, operation: str, signal_id: str = None, **kwargs):
        context = {
            "operation": operation,
            "signal_id": signal_id,
            "processing_stage": "unknown"
        }
        super().__init__(
            f"Processing failed: {operation}",
            user_message="Error procesando señal",
            context=context,
            recovery_suggestion="Verifique los parámetros de procesamiento",
            **kwargs
        )
```

### AcquisitionException
```python
class AcquisitionException(DomainException):
    """Signal acquisition errors with source context"""

    def __init__(self, source: str, source_type: str = "unknown", **kwargs):
        context = {
            "source": source,
            "source_type": source_type,
            "acquisition_method": "unknown"
        }
        super().__init__(
            f"Acquisition failed from {source}",
            user_message="Error adquiriendo señal",
            context=context,
            recovery_suggestion="Verifique la fuente de datos y conectividad",
            **kwargs
        )
```

### RepositoryException
```python
class RepositoryException(DomainException):
    """Repository and persistence errors"""

    def __init__(self, operation: str, entity_id: str = None, **kwargs):
        context = {
            "operation": operation,
            "entity_id": entity_id,
            "repository_type": "file_based"
        }
        super().__init__(
            f"Repository operation failed: {operation}",
            user_message="Error accediendo a datos almacenados",
            context=context,
            recovery_suggestion="Verifique permisos de archivo y espacio en disco",
            **kwargs
        )
```

## 🔧 Infrastructure Layer Exceptions

### ConfigurationException
```python
class ConfigurationException(InfrastructureException):
    """Configuration loading and validation errors"""

    def __init__(self, config_key: str, config_file: str = None, **kwargs):
        context = {
            "config_key": config_key,
            "config_file": config_file,
            "config_type": "yaml"
        }
        super().__init__(
            f"Configuration error: {config_key}",
            user_message="Error en configuración del sistema",
            context=context,
            recovery_suggestion="Verifique el archivo de configuración",
            **kwargs
        )
```

### DataAccessException
```python
class DataAccessException(InfrastructureException):
    """File I/O and data access errors with retry context"""

    def __init__(self, file_path: str, operation: str, **kwargs):
        context = {
            "file_path": file_path,
            "operation": operation,
            "retry_count": 0,
            "max_retries": 3
        }
        super().__init__(
            f"Data access failed: {operation} on {file_path}",
            user_message="Error accediendo a archivo",
            context=context,
            recovery_suggestion="Verifique que el archivo existe y tiene permisos",
            **kwargs
        )
```

## 🌐 Presentation Layer Exceptions

### WebException
```python
class WebException(PresentationException):
    """Web layer errors with HTTP context"""

    def __init__(self, endpoint: str, http_status: int = 500, **kwargs):
        context = {
            "endpoint": endpoint,
            "http_status": http_status,
            "request_method": "unknown"
        }
        super().__init__(
            f"Web error at {endpoint}",
            user_message="Error en la aplicación web",
            context=context,
            recovery_suggestion="Intente nuevamente o contacte soporte",
            **kwargs
        )
```

## 🔄 Recovery Strategies

### Strategy Interface
```python
class RecoveryStrategy:
    """Base class for recovery strategies"""

    def can_recover(self, exception: SenialSOLIDException) -> bool:
        """Check if this strategy can handle the exception"""
        raise NotImplementedError

    def recover(self, exception: SenialSOLIDException, context: Dict = None) -> Any:
        """Attempt recovery and return result or raise"""
        raise NotImplementedError
```

### File I/O Recovery Strategy
```python
class FileIORecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for file I/O operations"""

    def can_recover(self, exception: SenialSOLIDException) -> bool:
        return isinstance(exception, DataAccessException)

    def recover(self, exception: DataAccessException, context: Dict = None) -> Any:
        """Implement retry with exponential backoff"""
        max_retries = exception.context.get("max_retries", 3)
        current_retry = exception.context.get("retry_count", 0)

        if current_retry < max_retries:
            # Implement retry logic with backoff
            time.sleep(2 ** current_retry)
            exception.context["retry_count"] = current_retry + 1
            # Re-attempt operation
            return self._retry_operation(exception, context)
        else:
            # Max retries reached, escalate
            raise exception
```

### Processing Fallback Strategy
```python
class ProcessingFallbackStrategy(RecoveryStrategy):
    """Graceful degradation for signal processing"""

    def can_recover(self, exception: SenialSOLIDException) -> bool:
        return isinstance(exception, ProcessingException)

    def recover(self, exception: ProcessingException, context: Dict = None) -> Any:
        """Implement simplified processing as fallback"""
        operation = exception.context.get("operation")

        if operation == "complex_filter":
            # Fallback to simple processing
            logger.warning("Falling back to simple processing",
                         extra={"original_operation": operation})
            return self._simple_processing_fallback(context)
        else:
            raise exception
```

## 🧪 Exception Usage Patterns

### Domain Layer Pattern
```python
# ❌ Current (Generic)
try:
    valor = self._valores[indice]
    return valor
except Exception as e:
    logger.error("Error obteniendo valor por índice", ...)
    return None

# ✅ New (Specific)
try:
    valor = self._valores[indice]
    return valor
except IndexError as e:
    raise ValidationException(
        field="indice",
        value=indice,
        rule=f"must be between 0 and {len(self._valores)-1}",
        cause=e
    )
```

### Application Layer Pattern
```python
# ❌ Current (Re-raising without value)
try:
    senial = a.obtener_senial_adquirida()
    return senial
except Exception as exAdq:
    logger.error("Error durante adquisición de señal", exc_info=True)
    raise exAdq

# ✅ New (With recovery strategy)
try:
    senial = a.obtener_senial_adquirida()
    return senial
except AcquisitionException as e:
    # Attempt recovery
    recovery_strategy = AcquisitionRecoveryStrategy()
    if recovery_strategy.can_recover(e):
        return recovery_strategy.recover(e, {"fallback_source": "demo"})
    raise
```

### Infrastructure Layer Pattern
```python
# ❌ Current (Mixed logging + re-raising)
try:
    with open(ubicacion, 'r') as archivo:
        return pickle.load(archivo)
except IOError as eIO:
    logger.writelines('Error loading file')  # Legacy logging
    raise eIO

# ✅ New (Structured with recovery)
try:
    with open(ubicacion, 'r') as archivo:
        return pickle.load(archivo)
except IOError as e:
    raise DataAccessException(
        file_path=ubicacion,
        operation="load",
        cause=e
    )
```

## 📊 Migration Priority Matrix

| Exception Type | Current Count | Priority | Complexity | Impact |
|----------------|---------------|----------|------------|---------|
| Generic `Exception` | 85+ | 🔴 HIGH | Low | Critical |
| File I/O errors | 15+ | 🟡 MEDIUM | Medium | High |
| Processing errors | 10+ | 🟡 MEDIUM | High | High |
| Config errors | 5+ | 🟠 LOW | Low | Medium |

## 🎯 Implementation Phases

### Phase 2A: Create Exception Classes (1 day)
- Implement base `SenialSOLIDException`
- Create 5 main exception types
- Add SSA-22 auto-logging integration

### Phase 2B: Recovery Strategies (1 day)
- Implement 3 core recovery strategies
- File I/O retry mechanism
- Processing fallback patterns

### Phase 3: Layer-by-layer Migration (3 days)
- **Day 1**: Domain layer (highest impact)
- **Day 2**: Application layer (business logic)
- **Day 3**: Infrastructure + Presentation layers

## 🔗 Integration Points

### SSA-22 Logging Integration
- Automatic structured logging on exception creation
- Rich context information in logs
- Error correlation with request IDs
- Performance metrics in exception context

### Configuration Integration (SSA-9)
- Exception handling configuration in YAML
- Recovery strategy configuration
- Retry limits and timeouts
- Error notification settings

---

**Estado:** Diseño Completado ✅
**Próximo:** Implementación de Exception Classes
**Estimación Total:** 5-7 días de desarrollo