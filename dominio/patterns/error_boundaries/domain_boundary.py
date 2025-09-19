"""
SSA-26 Academic Domain Error Boundary
Educational domain layer error handling for clean architecture

This module demonstrates how domain boundaries should handle business rule
violations and maintain domain invariants with educational examples.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import datetime

# Import SSA-23 exception hierarchy
try:
    from dominio.exceptions.custom_exceptions import (
        DomainException,
        BusinessRuleViolationException,
        InvalidDomainStateException
    )
    SSA23_AVAILABLE = True
except ImportError:
    # Fallback classes for academic purposes
    SSA23_AVAILABLE = False
    class DomainException(Exception):
        pass
    class BusinessRuleViolationException(DomainException):
        pass
    class InvalidDomainStateException(DomainException):
        pass

# Import SSA-26 messaging
from dominio.patterns.messaging.user_message_formatter import (
    AcademicErrorMessageFormatter,
    ErrorSeverity,
    ErrorCategory
)


class BusinessRuleType(Enum):
    """Academic classification of business rules for educational purposes"""
    SIGNAL_PHYSICS = "signal_physics"          # Physics constraints (frequency, amplitude)
    DATA_INTEGRITY = "data_integrity"          # Data consistency rules
    PROCESSING_LIMITS = "processing_limits"    # Computational constraints
    ACADEMIC_STANDARDS = "academic_standards"  # Educational requirements


@dataclass
class BusinessRuleViolation:
    """
    Educational business rule violation with learning context

    This structure helps students understand what business rules are
    and why they're important in domain modeling.
    """
    rule_name: str
    rule_type: BusinessRuleType
    violated_constraint: str
    current_value: Any
    expected_condition: str
    educational_explanation: str
    recovery_suggestion: str
    severity: ErrorSeverity = ErrorSeverity.ERROR


@dataclass
class DomainInvariantError:
    """
    Educational domain invariant violation

    Helps students understand the difference between business rules
    and domain invariants in clean architecture.
    """
    invariant_name: str
    invariant_description: str
    current_state: Dict[str, Any]
    required_state: Dict[str, Any]
    violation_details: str
    educational_context: str


class DomainErrorBoundary:
    """
    Academic Domain Error Boundary for SenialSOLIDApp

    This class demonstrates how to implement domain error boundaries
    in clean architecture, with educational examples from signal processing.

    Educational Purposes:
    - Shows separation between domain errors and infrastructure errors
    - Demonstrates business rule enforcement patterns
    - Illustrates domain invariant maintenance
    - Provides examples of educational error recovery

    Examples:
        >>> boundary = DomainErrorBoundary()
        >>>
        >>> # Business rule validation
        >>> boundary.validate_signal_frequency(75000)  # Over limit
        >>>
        >>> # Domain invariant checking
        >>> boundary.ensure_signal_consistency(signal_data)
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize domain error boundary with educational configuration

        Args:
            logger: Optional logger for educational debugging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.formatter = AcademicErrorMessageFormatter(educational_mode=True)

        # Academic signal processing business rules
        self.business_rules = {
            "frequency_limits": {
                "min": 0.1,    # 0.1 Hz minimum for practical measurement
                "max": 50000,  # 50 kHz maximum for academic equipment
                "explanation": "Frecuencias fuera de este rango requieren equipos especializados no disponibles en el laboratorio académico"
            },
            "amplitude_range": {
                "min": -10.0,  # -10V minimum for safety
                "max": 10.0,   # +10V maximum for safety
                "explanation": "Amplitudes fuera de ±10V pueden dañar los equipos de laboratorio y presentan riesgos de seguridad"
            },
            "sampling_rate": {
                "min": 1,        # 1 Hz minimum practical sampling
                "max": 1000000,  # 1 MHz maximum for academic ADC
                "explanation": "Frecuencias de muestreo fuera de este rango no son prácticas para propósitos académicos"
            }
        }

    def validate_business_rule(self, rule_name: str, value: Any,
                             context: Optional[Dict] = None) -> Optional[BusinessRuleViolation]:
        """
        Educational business rule validation with learning context

        Args:
            rule_name: Name of the business rule to validate
            value: Value to validate against the rule
            context: Additional context for educational purposes

        Returns:
            BusinessRuleViolation if rule is violated, None if valid

        Examples:
            >>> boundary = DomainErrorBoundary()
            >>> violation = boundary.validate_business_rule("frequency_limits", 75000)
            >>> if violation:
            ...     print(violation.educational_explanation)
        """
        context = context or {}

        if rule_name == "frequency_limits":
            return self._validate_frequency_limits(value, context)
        elif rule_name == "amplitude_range":
            return self._validate_amplitude_range(value, context)
        elif rule_name == "sampling_rate":
            return self._validate_sampling_rate(value, context)
        else:
            self.logger.warning(f"Unknown business rule: {rule_name}")
            return None

    def _validate_frequency_limits(self, frequency: float, context: Dict) -> Optional[BusinessRuleViolation]:
        """Validate signal frequency against academic constraints"""
        rule = self.business_rules["frequency_limits"]

        if frequency < rule["min"]:
            return BusinessRuleViolation(
                rule_name="frequency_limits",
                rule_type=BusinessRuleType.SIGNAL_PHYSICS,
                violated_constraint="minimum_frequency",
                current_value=frequency,
                expected_condition=f"frequency >= {rule['min']} Hz",
                educational_explanation=(
                    f"Las frecuencias menores a {rule['min']} Hz son difíciles de medir con precisión "
                    "en equipos académicos. En el procesamiento digital de señales, estas frecuencias "
                    "muy bajas requieren ventanas de tiempo muy largas para obtener resolución adecuada."
                ),
                recovery_suggestion=f"Use una frecuencia entre {rule['min']} Hz y {rule['max']:,} Hz para propósitos académicos"
            )

        elif frequency > rule["max"]:
            return BusinessRuleViolation(
                rule_name="frequency_limits",
                rule_type=BusinessRuleType.SIGNAL_PHYSICS,
                violated_constraint="maximum_frequency",
                current_value=frequency,
                expected_condition=f"frequency <= {rule['max']} Hz",
                educational_explanation=(
                    f"Las frecuencias superiores a {rule['max']:,} Hz requieren convertidores analógico-digitales "
                    "de alta velocidad y técnicas de muestreo especializadas. Según el teorema de Nyquist, "
                    "necesitaríamos una frecuencia de muestreo de al menos {frequency * 2:,} Hz."
                ),
                recovery_suggestion=f"Use una frecuencia entre {rule['min']} Hz y {rule['max']:,} Hz para propósitos académicos"
            )

        return None

    def _validate_amplitude_range(self, amplitude: float, context: Dict) -> Optional[BusinessRuleViolation]:
        """Validate signal amplitude against safety constraints"""
        rule = self.business_rules["amplitude_range"]

        if amplitude < rule["min"] or amplitude > rule["max"]:
            return BusinessRuleViolation(
                rule_name="amplitude_range",
                rule_type=BusinessRuleType.SIGNAL_PHYSICS,
                violated_constraint="amplitude_safety_range",
                current_value=amplitude,
                expected_condition=f"{rule['min']} V <= amplitude <= {rule['max']} V",
                educational_explanation=(
                    f"Las amplitudes fuera del rango ±{rule['max']} V pueden dañar los equipos de laboratorio. "
                    "Los sistemas de adquisición académicos están diseñados para rangos de voltaje seguros. "
                    "Amplitudes mayores requieren atenuadores o divisores de voltaje."
                ),
                recovery_suggestion=f"Ajuste la amplitud al rango seguro de {rule['min']} V a {rule['max']} V"
            )

        return None

    def _validate_sampling_rate(self, sampling_rate: int, context: Dict) -> Optional[BusinessRuleViolation]:
        """Validate sampling rate against practical constraints"""
        rule = self.business_rules["sampling_rate"]

        if sampling_rate < rule["min"]:
            return BusinessRuleViolation(
                rule_name="sampling_rate",
                rule_type=BusinessRuleType.PROCESSING_LIMITS,
                violated_constraint="minimum_sampling_rate",
                current_value=sampling_rate,
                expected_condition=f"sampling_rate >= {rule['min']} Hz",
                educational_explanation=(
                    "Frecuencias de muestreo menores a 1 Hz no son prácticas para la mayoría de aplicaciones "
                    "de procesamiento de señales en tiempo real. Esto resultaría en tiempos de adquisición "
                    "extremadamente largos para obtener datos suficientes."
                ),
                recovery_suggestion=f"Use una frecuencia de muestreo entre {rule['min']} Hz y {rule['max']:,} Hz"
            )

        elif sampling_rate > rule["max"]:
            return BusinessRuleViolation(
                rule_name="sampling_rate",
                rule_type=BusinessRuleType.PROCESSING_LIMITS,
                violated_constraint="maximum_sampling_rate",
                current_value=sampling_rate,
                expected_condition=f"sampling_rate <= {rule['max']} Hz",
                educational_explanation=(
                    f"Frecuencias de muestreo superiores a {rule['max']:,} Hz requieren hardware especializado "
                    "y generan volúmenes masivos de datos difíciles de procesar en tiempo real en equipos académicos. "
                    "Esto también puede exceder la capacidad de almacenamiento disponible."
                ),
                recovery_suggestion=f"Use una frecuencia de muestreo entre {rule['min']} Hz y {rule['max']:,} Hz"
            )

        return None

    def ensure_domain_invariant(self, invariant_name: str, current_state: Dict[str, Any]) -> Optional[DomainInvariantError]:
        """
        Educational domain invariant verification

        Args:
            invariant_name: Name of the invariant to check
            current_state: Current domain object state

        Returns:
            DomainInvariantError if invariant is violated, None if valid

        Examples:
            >>> boundary = DomainErrorBoundary()
            >>> state = {"frequency": 1000, "sampling_rate": 500}
            >>> error = boundary.ensure_domain_invariant("nyquist_criterion", state)
        """
        if invariant_name == "nyquist_criterion":
            return self._check_nyquist_criterion(current_state)
        elif invariant_name == "signal_consistency":
            return self._check_signal_consistency(current_state)
        else:
            self.logger.warning(f"Unknown domain invariant: {invariant_name}")
            return None

    def _check_nyquist_criterion(self, state: Dict[str, Any]) -> Optional[DomainInvariantError]:
        """Check Nyquist sampling criterion invariant"""
        frequency = state.get("frequency")
        sampling_rate = state.get("sampling_rate")

        if frequency is None or sampling_rate is None:
            return None

        # Nyquist criterion: sampling_rate >= 2 * max_frequency
        min_required_sampling = 2 * frequency

        if sampling_rate < min_required_sampling:
            return DomainInvariantError(
                invariant_name="nyquist_criterion",
                invariant_description="La frecuencia de muestreo debe ser al menos el doble de la frecuencia máxima de la señal",
                current_state={"frequency": frequency, "sampling_rate": sampling_rate},
                required_state={"min_sampling_rate": min_required_sampling},
                violation_details=f"Frecuencia de muestreo {sampling_rate} Hz < {min_required_sampling} Hz requeridos",
                educational_context=(
                    "El criterio de Nyquist es fundamental en procesamiento digital de señales. "
                    "Si no se cumple, ocurre 'aliasing' - las frecuencias altas se confunden con frecuencias bajas, "
                    "corrompiendo la señal original y haciendo imposible la reconstrucción correcta."
                )
            )

        return None

    def _check_signal_consistency(self, state: Dict[str, Any]) -> Optional[DomainInvariantError]:
        """Check signal data consistency invariant"""
        signal_data = state.get("signal_data", [])
        expected_length = state.get("expected_length")

        if not signal_data or expected_length is None:
            return None

        if len(signal_data) != expected_length:
            return DomainInvariantError(
                invariant_name="signal_consistency",
                invariant_description="Los datos de la señal deben tener la longitud esperada",
                current_state={"actual_length": len(signal_data), "signal_data_type": type(signal_data).__name__},
                required_state={"expected_length": expected_length},
                violation_details=f"Longitud actual {len(signal_data)} != longitud esperada {expected_length}",
                educational_context=(
                    "La consistencia en la longitud de datos es crucial para algoritmos de procesamiento de señales. "
                    "Longitudes incorrectas pueden causar errores en FFT, filtros digitales y análisis estadísticos. "
                    "Siempre verifique que los datos tengan la dimensión esperada antes del procesamiento."
                )
            )

        return None

    def handle_business_rule_violation(self, violation: BusinessRuleViolation) -> None:
        """
        Educational business rule violation handler

        This method demonstrates how to handle business rule violations
        in a clean architecture context with educational logging.

        Args:
            violation: The business rule violation to handle
        """
        self.logger.error(
            f"Business Rule Violation: {violation.rule_name} - {violation.violated_constraint}",
            extra={
                "rule_type": violation.rule_type.value,
                "current_value": violation.current_value,
                "expected_condition": violation.expected_condition,
                "educational_explanation": violation.educational_explanation
            }
        )

        # For academic purposes, we convert to domain exceptions
        if SSA23_AVAILABLE:
            raise BusinessRuleViolationException(
                f"{violation.rule_name}: {violation.violated_constraint}",
                details={
                    "violation": violation,
                    "educational_explanation": violation.educational_explanation,
                    "recovery_suggestion": violation.recovery_suggestion
                }
            )
        else:
            raise BusinessRuleViolationException(f"{violation.rule_name}: {violation.violated_constraint}")

    def handle_domain_invariant_error(self, error: DomainInvariantError) -> None:
        """
        Educational domain invariant error handler

        Args:
            error: The domain invariant error to handle
        """
        self.logger.error(
            f"Domain Invariant Violation: {error.invariant_name}",
            extra={
                "invariant_description": error.invariant_description,
                "current_state": error.current_state,
                "required_state": error.required_state,
                "educational_context": error.educational_context
            }
        )

        if SSA23_AVAILABLE:
            raise InvalidDomainStateException(
                f"Domain invariant violated: {error.invariant_name}",
                details={
                    "error": error,
                    "educational_context": error.educational_context
                }
            )
        else:
            raise InvalidDomainStateException(f"Domain invariant violated: {error.invariant_name}")

    def safe_execute(self, operation: Callable, operation_name: str,
                    context: Optional[Dict] = None) -> Any:
        """
        Educational safe execution wrapper with domain boundary protection

        This method demonstrates how to wrap domain operations with
        proper error boundary handling for educational purposes.

        Args:
            operation: The domain operation to execute safely
            operation_name: Name of the operation for logging
            context: Additional context for error handling

        Returns:
            Result of the operation if successful

        Raises:
            DomainException: If a domain-level error occurs

        Examples:
            >>> boundary = DomainErrorBoundary()
            >>> result = boundary.safe_execute(
            ...     lambda: validate_signal(signal_data),
            ...     "signal_validation",
            ...     {"signal_id": "test_001"}
            ... )
        """
        context = context or {}

        try:
            self.logger.info(f"Executing domain operation: {operation_name}", extra={"context": context})
            result = operation()
            self.logger.info(f"Domain operation completed successfully: {operation_name}")
            return result

        except (BusinessRuleViolationException, InvalidDomainStateException) as domain_error:
            # These are expected domain errors - re-raise with context
            self.logger.warning(
                f"Domain operation failed with business rule violation: {operation_name}",
                extra={"error": str(domain_error), "context": context}
            )
            raise

        except Exception as unexpected_error:
            # Unexpected errors should be wrapped in domain exceptions
            self.logger.error(
                f"Unexpected error in domain operation: {operation_name}",
                extra={"error": str(unexpected_error), "context": context},
                exc_info=True
            )

            if SSA23_AVAILABLE:
                raise DomainException(
                    f"Unexpected error in {operation_name}: {str(unexpected_error)}",
                    details={"original_error": unexpected_error, "context": context}
                )
            else:
                raise DomainException(f"Unexpected error in {operation_name}: {str(unexpected_error)}")