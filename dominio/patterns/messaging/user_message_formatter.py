"""
SSA-26 Academic User-Friendly Error Message Formatter
Educational error messaging system for SenialSOLIDApp

This module provides user-friendly, educational error messages that help students
understand both the error and the underlying concepts in signal processing.
"""

from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
import datetime


class ErrorSeverity(Enum):
    """Educational error severity classification"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Signal processing domain error categories"""
    VALIDATION = "validation"
    SIGNAL_ACQUISITION = "signal_acquisition"
    SIGNAL_PROCESSING = "signal_processing"
    DATA_ACCESS = "data_access"
    SECURITY = "security"
    SYSTEM = "system"


@dataclass
class AcademicErrorMessage:
    """
    Academic-focused error message with educational components

    This structure provides both user-friendly messages and learning opportunities
    """
    user_message: str          # Simple, clear message for the user
    technical_reason: str      # Technical explanation for learning
    learning_tip: str          # Educational insight about the concept
    suggested_action: str      # Clear next steps for the user
    severity: ErrorSeverity    # Error severity level
    category: ErrorCategory    # Domain category
    context: Dict[str, Any]    # Additional context for debugging
    timestamp: datetime.datetime


class AcademicErrorMessageFormatter:
    """
    Academic-focused error message formatter for SenialSOLIDApp

    Provides educational, context-aware error messages that help students
    learn about signal processing concepts while handling errors gracefully.

    Examples:
        >>> formatter = AcademicErrorMessageFormatter()
        >>> error_msg = formatter.format_validation_error(
        ...     field="frequency",
        ...     value=75000,
        ...     constraint="max_50000"
        ... )
        >>> print(error_msg.user_message)
        "La frecuencia ingresada (75000 Hz) excede el límite máximo permitido"
    """

    def __init__(self, language: str = "es", educational_mode: bool = True):
        """
        Initialize the academic error message formatter

        Args:
            language: Language for messages ("es" or "en")
            educational_mode: Whether to include educational tips
        """
        self.language = language
        self.educational_mode = educational_mode

        # Academic signal processing constraints for educational context
        self.signal_constraints = {
            "frequency_range": (0.1, 50000),  # 0.1Hz to 50kHz (audio + industrial)
            "amplitude_range": (-10.0, 10.0),  # ±10V typical industrial range
            "sample_rate_range": (1, 1000000),  # 1Hz to 1MHz sampling
            "description_length": (3, 200),     # Reasonable description length
        }

    def format_validation_error(self, field: str, value: Any, constraint: str,
                              details: Optional[Dict] = None) -> AcademicErrorMessage:
        """
        Format SSA-24 validation errors with educational context

        Args:
            field: Field name that failed validation
            value: The invalid value
            constraint: Type of constraint violated
            details: Additional validation details

        Returns:
            AcademicErrorMessage with educational content
        """
        context = {
            "field": field,
            "value": value,
            "constraint": constraint,
            "details": details or {}
        }

        if field == "frequency":
            return self._format_frequency_validation_error(value, constraint, context)
        elif field == "amplitude":
            return self._format_amplitude_validation_error(value, constraint, context)
        elif field == "description":
            return self._format_description_validation_error(value, constraint, context)
        elif field == "signal_id":
            return self._format_signal_id_validation_error(value, constraint, context)
        else:
            return self._format_generic_validation_error(field, value, constraint, context)

    def _format_frequency_validation_error(self, value: float, constraint: str,
                                         context: Dict) -> AcademicErrorMessage:
        """Format frequency validation errors with signal processing education"""
        min_freq, max_freq = self.signal_constraints["frequency_range"]

        if constraint == "out_of_range":
            if value > max_freq:
                user_message = f"La frecuencia ingresada ({value:,.1f} Hz) excede el límite máximo de {max_freq:,.0f} Hz"
                technical_reason = f"Frequency {value} Hz exceeds maximum sampling capability of {max_freq} Hz"
                learning_tip = "Las frecuencias superiores a 50kHz requieren equipos especializados de alta velocidad. En sistemas académicos usamos rangos de audio e industriales (0.1Hz-50kHz)."
                suggested_action = f"Ingrese una frecuencia entre {min_freq} Hz y {max_freq:,.0f} Hz"
            else:
                user_message = f"La frecuencia ingresada ({value:,.3f} Hz) es inferior al mínimo de {min_freq} Hz"
                technical_reason = f"Frequency {value} Hz is below minimum detectable frequency of {min_freq} Hz"
                learning_tip = "Las frecuencias muy bajas (< 0.1Hz) son difíciles de medir y procesar en tiempo real. En sistemas de adquisición se requiere un mínimo técnico."
                suggested_action = f"Ingrese una frecuencia entre {min_freq} Hz y {max_freq:,.0f} Hz"
        else:
            user_message = f"Error en la validación de frecuencia: {constraint}"
            technical_reason = f"Frequency validation failed: {constraint}"
            learning_tip = "La frecuencia debe ser un valor numérico positivo dentro del rango de operación del sistema."
            suggested_action = "Verifique que ingresó un número válido para la frecuencia"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def _format_amplitude_validation_error(self, value: float, constraint: str,
                                         context: Dict) -> AcademicErrorMessage:
        """Format amplitude validation errors with electrical engineering education"""
        min_amp, max_amp = self.signal_constraints["amplitude_range"]

        if constraint == "out_of_range":
            user_message = f"La amplitud ingresada ({value:+.2f} V) está fuera del rango permitido (±{max_amp} V)"
            technical_reason = f"Amplitude {value} V exceeds safe operating range of ±{max_amp} V"
            learning_tip = f"En sistemas industriales, ±{max_amp}V es un rango seguro que evita daños al hardware de adquisición. Amplitudes mayores requieren atenuadores o acondicionadores de señal."
            suggested_action = f"Ingrese una amplitud entre {min_amp:+.1f} V y {max_amp:+.1f} V"
        else:
            user_message = f"Error en la validación de amplitud: {constraint}"
            technical_reason = f"Amplitude validation failed: {constraint}"
            learning_tip = "La amplitud representa el nivel de voltaje de la señal. Debe ser un valor numérico que el hardware puede manejar de forma segura."
            suggested_action = "Verifique que ingresó un valor numérico válido para la amplitud"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def _format_description_validation_error(self, value: str, constraint: str,
                                           context: Dict) -> AcademicErrorMessage:
        """Format description validation errors with documentation best practices"""
        min_len, max_len = self.signal_constraints["description_length"]

        if constraint == "too_short":
            user_message = f"La descripción es muy corta ({len(value)} caracteres). Mínimo requerido: {min_len} caracteres"
            technical_reason = f"Description length {len(value)} is below minimum requirement of {min_len} characters"
            learning_tip = "Las descripciones claras son fundamentales en ingeniería. Ayudan a identificar señales, documentar experimentos y facilitar el mantenimiento del sistema."
            suggested_action = f"Proporcione una descripción más detallada (mínimo {min_len} caracteres)"
        elif constraint == "too_long":
            user_message = f"La descripción es muy larga ({len(value)} caracteres). Máximo permitido: {max_len} caracteres"
            technical_reason = f"Description length {len(value)} exceeds maximum limit of {max_len} characters"
            learning_tip = "Las descripciones deben ser concisas pero informativas. Muy largas pueden causar problemas de almacenamiento y visualización."
            suggested_action = f"Reduzca la descripción a máximo {max_len} caracteres"
        else:
            user_message = f"Error en la validación de descripción: {constraint}"
            technical_reason = f"Description validation failed: {constraint}"
            learning_tip = "La descripción debe contener solo caracteres válidos y tener una longitud apropiada para documentar la señal."
            suggested_action = "Verifique que la descripción no contenga caracteres especiales problemáticos"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def _format_signal_id_validation_error(self, value: Any, constraint: str,
                                         context: Dict) -> AcademicErrorMessage:
        """Format signal ID validation errors with data management education"""
        if constraint == "out_of_range":
            user_message = f"El ID de señal ({value}) debe estar entre 1 y 9999"
            technical_reason = f"Signal ID {value} is outside valid range (1-9999)"
            learning_tip = "Los IDs numéricos secuenciales facilitan la organización y búsqueda de datos. El rango 1-9999 es suficiente para proyectos académicos y permite indexación eficiente."
            suggested_action = "Ingrese un número entero entre 1 y 9999"
        else:
            user_message = f"Error en la validación del ID de señal: {constraint}"
            technical_reason = f"Signal ID validation failed: {constraint}"
            learning_tip = "El ID debe ser un identificador único y numérico para cada señal en el sistema."
            suggested_action = "Verifique que ingresó un número entero válido"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def _format_generic_validation_error(self, field: str, value: Any, constraint: str,
                                       context: Dict) -> AcademicErrorMessage:
        """Format generic validation errors with general educational context"""
        user_message = f"Error de validación en el campo '{field}': {constraint}"
        technical_reason = f"Field '{field}' with value '{value}' failed constraint '{constraint}'"
        learning_tip = "Las validaciones protegen la integridad del sistema y aseguran que los datos cumplan los requisitos técnicos necesarios."
        suggested_action = f"Revise el valor ingresado en '{field}' y corrija según los requisitos"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def format_security_error(self, attack_type: str, blocked_content: str = "",
                            context: Optional[Dict] = None) -> AcademicErrorMessage:
        """
        Format security errors with cybersecurity education

        Args:
            attack_type: Type of security attack detected
            blocked_content: The malicious content that was blocked
            context: Additional security context

        Returns:
            AcademicErrorMessage with security education
        """
        context = context or {}
        context.update({
            "attack_type": attack_type,
            "blocked_content": blocked_content,
            "security_framework": "SSA-24"
        })

        if attack_type == "xss":
            user_message = "Se detectó y bloqueó contenido potencialmente peligroso en su entrada"
            technical_reason = f"XSS attack detected and blocked: {blocked_content[:50]}..."
            learning_tip = "Los ataques XSS (Cross-Site Scripting) intentan inyectar código malicioso. El framework SSA-24 los detecta y bloquea automáticamente para proteger la aplicación."
            suggested_action = "Ingrese solo contenido de texto normal sin etiquetas HTML o JavaScript"
        elif attack_type == "sql_injection":
            user_message = "Se detectó un patrón de entrada no permitido que fue bloqueado por seguridad"
            technical_reason = f"SQL injection attempt detected: {blocked_content[:50]}..."
            learning_tip = "Las inyecciones SQL intentan manipular consultas a la base de datos. El framework SSA-24 sanitiza automáticamente las entradas para prevenir estos ataques."
            suggested_action = "Use solo caracteres alfanuméricos y evite símbolos especiales como comillas o punto y coma"
        else:
            user_message = f"Se detectó una amenaza de seguridad tipo '{attack_type}' que fue bloqueada"
            technical_reason = f"Security threat detected: {attack_type}"
            learning_tip = "El sistema incluye múltiples capas de protección que detectan y bloquean automáticamente intentos de ataque conocidos."
            suggested_action = "Revise su entrada y asegúrese de usar solo contenido legítimo"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def format_system_error(self, error_type: str, component: str,
                          details: Optional[str] = None) -> AcademicErrorMessage:
        """
        Format system errors with infrastructure education

        Args:
            error_type: Type of system error
            component: System component that failed
            details: Additional error details

        Returns:
            AcademicErrorMessage with system education
        """
        context = {
            "error_type": error_type,
            "component": component,
            "details": details,
            "system": "SenialSOLIDApp"
        }

        if error_type == "database_connection":
            user_message = "Temporalmente no se puede acceder a los datos. El sistema está intentando reconectar."
            technical_reason = f"Database connection failed in component: {component}"
            learning_tip = "Las conexiones a base de datos pueden fallar por problemas de red, sobrecarga o mantenimiento. Los sistemas robustos implementan reconexión automática y manejo de fallos."
            suggested_action = "Por favor, intente nuevamente en unos momentos. Si el problema persiste, contacte al administrador."
        elif error_type == "file_access":
            user_message = "No se pudo acceder a los archivos necesarios para procesar su solicitud"
            technical_reason = f"File access error in component: {component} - {details}"
            learning_tip = "Los errores de acceso a archivos pueden deberse a permisos, espacio en disco o archivos bloqueados. Es importante manejar estos errores graciosamente."
            suggested_action = "Verifique que tiene permisos adecuados y que hay espacio disponible en el sistema"
        else:
            user_message = f"Error interno del sistema en el componente '{component}'"
            technical_reason = f"System error: {error_type} in {component}"
            learning_tip = "Los sistemas complejos pueden experimentar errores internos. El manejo adecuado incluye logging, alertas y recuperación automática cuando es posible."
            suggested_action = "El error ha sido registrado. Intente la operación nuevamente o contacte soporte técnico"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def format_signal_processing_error(self, operation: str, signal_id: Optional[str] = None,
                                     technical_details: Optional[str] = None) -> AcademicErrorMessage:
        """
        Format signal processing errors with DSP education

        Args:
            operation: Signal processing operation that failed
            signal_id: ID of the signal being processed
            technical_details: Technical error details

        Returns:
            AcademicErrorMessage with signal processing education
        """
        context = {
            "operation": operation,
            "signal_id": signal_id,
            "technical_details": technical_details
        }

        if operation == "acquisition":
            user_message = f"Error durante la adquisición de la señal {signal_id or 'desconocida'}"
            technical_reason = f"Signal acquisition failed: {technical_details or 'Unknown error'}"
            learning_tip = "La adquisición de señales puede fallar por problemas de hardware, configuración incorrecta o interferencias. Es importante validar parámetros antes de iniciar la captura."
            suggested_action = "Verifique la configuración del hardware y los parámetros de la señal"
        elif operation == "processing":
            user_message = f"Error durante el procesamiento de la señal {signal_id or 'desconocida'}"
            technical_reason = f"Signal processing failed: {technical_details or 'Processing error'}"
            learning_tip = "El procesamiento de señales requiere algoritmos robustos que manejen casos extremos como señales corruptas o parámetros fuera de rango."
            suggested_action = "Revise los datos de entrada y los parámetros del procesamiento"
        else:
            user_message = f"Error en operación de señal: {operation}"
            technical_reason = f"Signal operation '{operation}' failed"
            learning_tip = "Las operaciones con señales deben incluir validación de entrada, manejo de errores y recuperación automática cuando sea posible."
            suggested_action = "Consulte la documentación de la operación e intente con diferentes parámetros"

        return AcademicErrorMessage(
            user_message=user_message,
            technical_reason=technical_reason,
            learning_tip=learning_tip,
            suggested_action=suggested_action,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SIGNAL_PROCESSING,
            context=context,
            timestamp=datetime.datetime.now()
        )

    def to_dict(self, error_message: AcademicErrorMessage) -> Dict[str, Any]:
        """
        Convert AcademicErrorMessage to dictionary for JSON serialization

        Args:
            error_message: The error message to convert

        Returns:
            Dictionary representation suitable for API responses
        """
        return {
            "user_message": error_message.user_message,
            "technical_reason": error_message.technical_reason,
            "learning_tip": error_message.learning_tip if self.educational_mode else None,
            "suggested_action": error_message.suggested_action,
            "severity": error_message.severity.value,
            "category": error_message.category.value,
            "context": error_message.context,
            "timestamp": error_message.timestamp.isoformat(),
            "educational_mode": self.educational_mode,
            "language": self.language
        }

    def to_html(self, error_message: AcademicErrorMessage) -> str:
        """
        Convert AcademicErrorMessage to HTML for web display

        Args:
            error_message: The error message to convert

        Returns:
            HTML string suitable for web display
        """
        severity_class = {
            ErrorSeverity.INFO: "alert-info",
            ErrorSeverity.WARNING: "alert-warning",
            ErrorSeverity.ERROR: "alert-danger",
            ErrorSeverity.CRITICAL: "alert-danger"
        }

        severity_icon = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }

        html = f'''
        <div class="alert {severity_class[error_message.severity]} alert-dismissible fade show" role="alert">
            <h6 class="alert-heading">
                {severity_icon[error_message.severity]} {error_message.user_message}
            </h6>
        '''

        if self.educational_mode and error_message.learning_tip:
            html += f'''
            <hr>
            <p class="mb-2"><strong>💡 Concepto:</strong> {error_message.learning_tip}</p>
            '''

        html += f'''
            <p class="mb-0"><strong>🔧 Acción sugerida:</strong> {error_message.suggested_action}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        '''

        return html


# Convenience function for quick error formatting
def format_error(error_type: str, **kwargs) -> AcademicErrorMessage:
    """
    Convenience function to quickly format common errors

    Args:
        error_type: Type of error to format
        **kwargs: Additional arguments for specific error types

    Returns:
        Formatted AcademicErrorMessage
    """
    formatter = AcademicErrorMessageFormatter()

    if error_type == "validation":
        return formatter.format_validation_error(
            field=kwargs.get("field", "unknown"),
            value=kwargs.get("value", ""),
            constraint=kwargs.get("constraint", "unknown"),
            details=kwargs.get("details")
        )
    elif error_type == "security":
        return formatter.format_security_error(
            attack_type=kwargs.get("attack_type", "unknown"),
            blocked_content=kwargs.get("blocked_content", ""),
            context=kwargs.get("context")
        )
    elif error_type == "system":
        return formatter.format_system_error(
            error_type=kwargs.get("system_error_type", "unknown"),
            component=kwargs.get("component", "unknown"),
            details=kwargs.get("details")
        )
    elif error_type == "signal_processing":
        return formatter.format_signal_processing_error(
            operation=kwargs.get("operation", "unknown"),
            signal_id=kwargs.get("signal_id"),
            technical_details=kwargs.get("technical_details")
        )
    else:
        # Generic error format
        context = kwargs.get("context", {})
        return AcademicErrorMessage(
            user_message=kwargs.get("user_message", f"Error desconocido: {error_type}"),
            technical_reason=kwargs.get("technical_reason", f"Unknown error type: {error_type}"),
            learning_tip=kwargs.get("learning_tip", "Este tipo de error requiere revisión del código fuente."),
            suggested_action=kwargs.get("suggested_action", "Contacte al administrador del sistema"),
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.datetime.now()
        )