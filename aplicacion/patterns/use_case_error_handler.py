"""
SSA-26 Academic Use Case Error Handler
Educational error handling for application layer use cases

This module demonstrates how to implement use case error handling
in clean architecture with educational examples for signal processing.
"""

from typing import Any, Dict, Optional, Callable, Type, List
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# Import SSA-23 exception hierarchy
try:
    from dominio.exceptions.custom_exceptions import (
        DomainException,
        BusinessRuleViolationException,
        ValidationException,
        ApplicationException
    )
    SSA23_AVAILABLE = True
except ImportError:
    SSA23_AVAILABLE = False
    # Fallback classes
    class DomainException(Exception):
        pass
    class BusinessRuleViolationException(DomainException):
        pass
    class ValidationException(Exception):
        pass
    class ApplicationException(Exception):
        pass

# Import SSA-26 patterns
from dominio.patterns.error_boundaries.domain_boundary import DomainErrorBoundary
from dominio.patterns.messaging.user_message_formatter import (
    AcademicErrorMessageFormatter,
    ErrorSeverity,
    ErrorCategory
)
from dominio.patterns.resilience.simple_retry import SimpleRetryPattern


class UseCaseExecutionMode(Enum):
    """Educational use case execution modes"""
    NORMAL = "normal"              # Full functionality
    DEGRADED = "degraded"         # Limited functionality
    SAFE_MODE = "safe_mode"       # Minimal functionality
    EMERGENCY = "emergency"       # Critical operations only


class FallbackStrategy(Enum):
    """Educational fallback strategies for use case failures"""
    DEFAULT_VALUES = "default_values"     # Use predetermined defaults
    CACHED_RESULTS = "cached_results"     # Return cached data
    SIMPLIFIED_LOGIC = "simplified_logic" # Use simpler algorithm
    USER_PROMPT = "user_prompt"          # Ask user for guidance
    GRACEFUL_SKIP = "graceful_skip"      # Skip non-critical operations


@dataclass
class UseCaseContext:
    """Educational use case execution context"""
    use_case_name: str
    execution_mode: UseCaseExecutionMode
    user_session_id: Optional[str]
    request_parameters: Dict[str, Any]
    fallback_enabled: bool
    educational_mode: bool
    timestamp: datetime


@dataclass
class UseCaseResult:
    """Educational use case execution result with learning context"""
    success: bool
    result: Any
    execution_mode: UseCaseExecutionMode
    fallback_used: Optional[FallbackStrategy]
    errors_encountered: List[Exception]
    warnings: List[str]
    educational_notes: List[str]
    performance_impact: Optional[float]  # Percentage impact from fallbacks


class GracefulDegradation:
    """
    Academic Graceful Degradation for Use Cases

    This class demonstrates how to implement graceful degradation patterns
    in application layer use cases for educational purposes.

    Educational Purposes:
    - Shows how to handle partial system failures
    - Demonstrates fallback strategies for different scenarios
    - Illustrates user experience preservation during errors
    - Provides examples for signal processing use cases

    Examples:
        >>> degradation = GracefulDegradation()
        >>> result = degradation.execute_with_fallback(
        ...     primary_operation=lambda: process_advanced_signal(data),
        ...     fallback_operation=lambda: process_basic_signal(data),
        ...     fallback_strategy=FallbackStrategy.SIMPLIFIED_LOGIC
        ... )
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize graceful degradation with educational configuration

        Args:
            logger: Optional logger for educational debugging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.formatter = AcademicErrorMessageFormatter(educational_mode=True)

        # Educational fallback configurations for signal processing
        self.fallback_configs = {
            "signal_processing": {
                "default_sample_rate": 44100,
                "default_frequency": 1000,
                "simplified_filter_order": 2,  # Instead of higher orders
                "basic_window_function": "hamming"  # Instead of complex windows
            },
            "data_acquisition": {
                "default_duration": 1.0,  # 1 second default
                "fallback_channels": 1,   # Mono instead of stereo
                "safe_amplitude": 1.0     # Safe amplitude level
            },
            "file_operations": {
                "default_format": "csv",
                "fallback_encoding": "utf-8",
                "simplified_precision": 6  # Decimal places
            }
        }

    def execute_with_fallback(self, primary_operation: Callable[[], Any],
                            fallback_operation: Optional[Callable[[], Any]] = None,
                            fallback_strategy: FallbackStrategy = FallbackStrategy.DEFAULT_VALUES,
                            context: Optional[UseCaseContext] = None) -> UseCaseResult:
        """
        Execute operation with graceful degradation fallback

        This method demonstrates how to gracefully handle failures by
        falling back to simpler or safer operations.

        Args:
            primary_operation: The primary operation to attempt
            fallback_operation: Optional fallback operation
            fallback_strategy: Strategy to use for fallback
            context: Optional execution context

        Returns:
            UseCaseResult with execution outcome and educational information
        """
        context = context or UseCaseContext(
            use_case_name="unknown_operation",
            execution_mode=UseCaseExecutionMode.NORMAL,
            user_session_id=None,
            request_parameters={},
            fallback_enabled=True,
            educational_mode=True,
            timestamp=datetime.now()
        )

        errors_encountered = []
        warnings = []
        educational_notes = []

        # Try primary operation first
        try:
            if context.educational_mode:
                self.logger.info(f"Executing primary operation: {context.use_case_name}")
                educational_notes.append("Intentando operación principal con funcionalidad completa")

            result = primary_operation()

            educational_notes.append("Operación principal completada exitosamente sin necesidad de fallback")

            return UseCaseResult(
                success=True,
                result=result,
                execution_mode=context.execution_mode,
                fallback_used=None,
                errors_encountered=errors_encountered,
                warnings=warnings,
                educational_notes=educational_notes,
                performance_impact=0.0
            )

        except Exception as primary_error:
            errors_encountered.append(primary_error)

            if context.educational_mode:
                self.logger.warning(
                    f"Primary operation failed: {context.use_case_name}",
                    extra={
                        "error_type": type(primary_error).__name__,
                        "error_message": str(primary_error),
                        "will_attempt_fallback": context.fallback_enabled
                    }
                )

            educational_notes.append(
                f"Operación principal falló: {type(primary_error).__name__} - "
                "Activando estrategia de degradación graceful"
            )

            if not context.fallback_enabled:
                educational_notes.append("Fallback deshabilitado - propagando error original")
                return UseCaseResult(
                    success=False,
                    result=None,
                    execution_mode=UseCaseExecutionMode.EMERGENCY,
                    fallback_used=None,
                    errors_encountered=errors_encountered,
                    warnings=warnings,
                    educational_notes=educational_notes,
                    performance_impact=None
                )

            # Attempt fallback
            return self._execute_fallback(
                fallback_operation, fallback_strategy, primary_error,
                context, errors_encountered, warnings, educational_notes
            )

    def _execute_fallback(self, fallback_operation: Optional[Callable[[], Any]],
                         fallback_strategy: FallbackStrategy,
                         primary_error: Exception,
                         context: UseCaseContext,
                         errors_encountered: List[Exception],
                         warnings: List[str],
                         educational_notes: List[str]) -> UseCaseResult:
        """Execute fallback strategy with educational logging"""

        try:
            if fallback_strategy == FallbackStrategy.DEFAULT_VALUES:
                result = self._fallback_to_defaults(context, educational_notes)
                performance_impact = 10.0  # Minimal impact

            elif fallback_strategy == FallbackStrategy.SIMPLIFIED_LOGIC and fallback_operation:
                result = fallback_operation()
                performance_impact = 25.0  # Some reduction in capability
                educational_notes.append("Usando lógica simplificada - funcionalidad reducida pero operacional")

            elif fallback_strategy == FallbackStrategy.CACHED_RESULTS:
                result = self._fallback_to_cache(context, educational_notes)
                performance_impact = 5.0  # Fast cached response

            elif fallback_strategy == FallbackStrategy.GRACEFUL_SKIP:
                result = self._fallback_graceful_skip(context, educational_notes)
                performance_impact = 50.0  # Significant functionality reduction

            else:
                # Default fallback
                result = self._fallback_to_defaults(context, educational_notes)
                performance_impact = 15.0

            warnings.append(f"Sistema operando en modo degradado usando {fallback_strategy.value}")

            return UseCaseResult(
                success=True,
                result=result,
                execution_mode=UseCaseExecutionMode.DEGRADED,
                fallback_used=fallback_strategy,
                errors_encountered=errors_encountered,
                warnings=warnings,
                educational_notes=educational_notes,
                performance_impact=performance_impact
            )

        except Exception as fallback_error:
            errors_encountered.append(fallback_error)
            educational_notes.append("Fallback también falló - sistema en modo de emergencia")

            self.logger.error(
                f"Fallback strategy failed: {fallback_strategy.value}",
                extra={
                    "fallback_error": str(fallback_error),
                    "primary_error": str(primary_error),
                    "use_case": context.use_case_name
                }
            )

            return UseCaseResult(
                success=False,
                result=None,
                execution_mode=UseCaseExecutionMode.EMERGENCY,
                fallback_used=fallback_strategy,
                errors_encountered=errors_encountered,
                warnings=warnings,
                educational_notes=educational_notes,
                performance_impact=None
            )

    def _fallback_to_defaults(self, context: UseCaseContext, educational_notes: List[str]) -> Dict[str, Any]:
        """Fallback strategy using predetermined default values"""
        educational_notes.append("Usando valores por defecto seguros para mantener operatividad básica")

        if "signal" in context.use_case_name.lower():
            defaults = self.fallback_configs["signal_processing"]
            educational_notes.append(
                f"Configuración de señal por defecto: {defaults['default_sample_rate']} Hz, "
                f"frecuencia {defaults['default_frequency']} Hz"
            )
            return defaults

        elif "acquisition" in context.use_case_name.lower():
            defaults = self.fallback_configs["data_acquisition"]
            educational_notes.append(
                f"Configuración de adquisición segura: {defaults['default_duration']}s, "
                f"amplitud {defaults['safe_amplitude']}V"
            )
            return defaults

        else:
            # Generic defaults
            educational_notes.append("Usando configuración genérica por defecto")
            return {
                "mode": "safe",
                "timeout": 30,
                "retries": 1,
                "educational_note": "Configuración mínima segura"
            }

    def _fallback_to_cache(self, context: UseCaseContext, educational_notes: List[str]) -> Dict[str, Any]:
        """Fallback strategy using cached results"""
        educational_notes.append(
            "Usando resultados en caché - los datos pueden no estar actualizados pero son funcionales"
        )

        # Simulate cached result (in real implementation, this would read from cache)
        cached_result = {
            "data_source": "cache",
            "timestamp": context.timestamp.isoformat(),
            "note": "Datos en caché del último procesamiento exitoso",
            "freshness": "potentially_stale",
            "educational_context": "Los datos en caché permiten continuidad operacional durante fallos"
        }

        return cached_result

    def _fallback_graceful_skip(self, context: UseCaseContext, educational_notes: List[str]) -> Dict[str, Any]:
        """Fallback strategy that gracefully skips non-essential operations"""
        educational_notes.append(
            "Omitiendo operaciones no críticas - funcionalidad básica mantenida"
        )

        return {
            "operation_status": "partially_completed",
            "skipped_operations": ["advanced_filtering", "detailed_analysis", "complex_transformations"],
            "completed_operations": ["basic_validation", "essential_processing"],
            "user_message": "Operación completada con funcionalidad reducida",
            "educational_context": "El skip graceful prioriza operaciones críticas sobre las opcionales"
        }


class UseCaseErrorHandler:
    """
    Academic Use Case Error Handler for SenialSOLIDApp

    This class demonstrates comprehensive error handling at the application
    layer with educational examples for signal processing use cases.

    Educational Purposes:
    - Shows integration between different error handling patterns
    - Demonstrates transaction-like behavior in use cases
    - Illustrates error recovery and graceful degradation
    - Provides examples of educational error reporting

    Examples:
        >>> error_handler = UseCaseErrorHandler()
        >>> result = error_handler.execute_use_case(
        ...     use_case_operation=lambda: process_signal_pipeline(data),
        ...     use_case_name="signal_processing_pipeline",
        ...     enable_retry=True,
        ...     enable_fallback=True
        ... )
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize use case error handler

        Args:
            logger: Optional logger for educational debugging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.domain_boundary = DomainErrorBoundary(logger=self.logger)
        self.retry_pattern = SimpleRetryPattern(logger=self.logger)
        self.graceful_degradation = GracefulDegradation(logger=self.logger)
        self.formatter = AcademicErrorMessageFormatter(educational_mode=True)

    def execute_use_case(self, use_case_operation: Callable[[], Any],
                        use_case_name: str,
                        context: Optional[Dict[str, Any]] = None,
                        enable_retry: bool = True,
                        enable_fallback: bool = True,
                        fallback_operation: Optional[Callable[[], Any]] = None) -> UseCaseResult:
        """
        Execute use case with comprehensive error handling

        This method demonstrates how to combine multiple error handling
        patterns (retry, fallback, graceful degradation) in use case execution.

        Args:
            use_case_operation: The use case operation to execute
            use_case_name: Descriptive name for the use case
            context: Optional execution context
            enable_retry: Whether to enable retry on transient failures
            enable_fallback: Whether to enable graceful degradation
            fallback_operation: Optional fallback operation

        Returns:
            UseCaseResult with comprehensive execution information
        """
        context = context or {}

        use_case_context = UseCaseContext(
            use_case_name=use_case_name,
            execution_mode=UseCaseExecutionMode.NORMAL,
            user_session_id=context.get("user_session_id"),
            request_parameters=context,
            fallback_enabled=enable_fallback,
            educational_mode=True,
            timestamp=datetime.now()
        )

        educational_notes = [
            f"Iniciando ejecución de caso de uso: {use_case_name}",
            f"Retry habilitado: {enable_retry}, Fallback habilitado: {enable_fallback}"
        ]

        def wrapped_operation():
            return self.domain_boundary.safe_execute(
                use_case_operation,
                use_case_name,
                context
            )

        try:
            if enable_retry:
                # Execute with retry pattern first
                retry_result = self.retry_pattern.retry_operation(
                    wrapped_operation,
                    use_case_name
                )

                if retry_result.success:
                    educational_notes.extend([
                        f"Caso de uso completado exitosamente en {retry_result.total_attempts} intentos",
                        f"Duración total: {retry_result.total_duration_ms:.2f}ms"
                    ])

                    return UseCaseResult(
                        success=True,
                        result=retry_result.result,
                        execution_mode=use_case_context.execution_mode,
                        fallback_used=None,
                        errors_encountered=[],
                        warnings=[],
                        educational_notes=educational_notes,
                        performance_impact=0.0 if retry_result.total_attempts == 1 else 10.0
                    )
                else:
                    educational_notes.append(
                        f"Retry pattern falló después de {retry_result.total_attempts} intentos - "
                        "intentando fallback si está habilitado"
                    )

                    if not enable_fallback:
                        raise retry_result.final_exception
            else:
                # Execute directly without retry
                result = wrapped_operation()
                return UseCaseResult(
                    success=True,
                    result=result,
                    execution_mode=use_case_context.execution_mode,
                    fallback_used=None,
                    errors_encountered=[],
                    warnings=[],
                    educational_notes=educational_notes,
                    performance_impact=0.0
                )

        except Exception as error:
            educational_notes.append(f"Error en ejecución principal: {type(error).__name__}")

            if enable_fallback:
                # Try graceful degradation
                fallback_result = self.graceful_degradation.execute_with_fallback(
                    primary_operation=wrapped_operation,
                    fallback_operation=fallback_operation,
                    fallback_strategy=FallbackStrategy.DEFAULT_VALUES,
                    context=use_case_context
                )

                # Merge educational notes
                fallback_result.educational_notes.extend(educational_notes)
                return fallback_result
            else:
                # No fallback - return failure
                educational_notes.append("Fallback deshabilitado - propagando error")
                return UseCaseResult(
                    success=False,
                    result=None,
                    execution_mode=UseCaseExecutionMode.EMERGENCY,
                    fallback_used=None,
                    errors_encountered=[error],
                    warnings=[],
                    educational_notes=educational_notes,
                    performance_impact=None
                )