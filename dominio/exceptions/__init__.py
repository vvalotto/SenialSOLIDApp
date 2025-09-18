"""
Custom Exception Classes for SenialSOLID Application
SSA-23: Exception Handling Refactoring
SSA-24: Input Validation Framework Integration

This module provides a comprehensive exception hierarchy with:
- Automatic SSA-22 structured logging integration
- Rich context information for debugging
- Recovery strategy support
- Layer-specific exception types
- SSA-24 validation framework exceptions
"""

import sys
import os

# Add validation framework to path for exception integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from .base_exceptions import (
    SenialSOLIDException,
    DomainException,
    InfrastructureException,
    PresentationException
)

from .domain_exceptions import (
    ValidationException,
    ProcessingException,
    AcquisitionException,
    RepositoryException
)

from .infrastructure_exceptions import (
    ConfigurationException,
    DataAccessException,
    NetworkException
)

from .presentation_exceptions import (
    WebException,
    ConsoleException
)

from .recovery_strategies import (
    RecoveryStrategy,
    FileIORecoveryStrategy,
    ProcessingFallbackStrategy,
    RetryStrategy
)

# Import SSA-24 validation exceptions for unified exception handling
try:
    from aplicacion.validation.exceptions.validation_exceptions import (
        ValidationError as SSA24ValidationError,
        SanitizationError,
        SecurityValidationError,
        FileValidationError,
        SignalValidationError,
        ConfigValidationError,
        APIValidationError,
        ValidationPipelineError
    )
    SSA24_AVAILABLE = True
except ImportError:
    # Fallback if SSA-24 is not available
    SSA24_AVAILABLE = False
    SSA24ValidationError = None
    SanitizationError = None
    SecurityValidationError = None
    FileValidationError = None
    SignalValidationError = None
    ConfigValidationError = None
    APIValidationError = None
    ValidationPipelineError = None

__all__ = [
    # Base exceptions
    'SenialSOLIDException',
    'DomainException',
    'InfrastructureException',
    'PresentationException',

    # Domain-specific exceptions
    'ValidationException',
    'ProcessingException',
    'AcquisitionException',
    'RepositoryException',

    # Infrastructure exceptions
    'ConfigurationException',
    'DataAccessException',
    'NetworkException',

    # Presentation exceptions
    'WebException',
    'ConsoleException',

    # Recovery strategies
    'RecoveryStrategy',
    'FileIORecoveryStrategy',
    'ProcessingFallbackStrategy',
    'RetryStrategy',

    # SSA-24 validation framework integration
    'SSA24_AVAILABLE',
]

# Add SSA-24 exceptions to exports if available
if SSA24_AVAILABLE:
    __all__.extend([
        'SSA24ValidationError',
        'SanitizationError',
        'SecurityValidationError',
        'FileValidationError',
        'SignalValidationError',
        'ConfigValidationError',
        'APIValidationError',
        'ValidationPipelineError'
    ])


def handle_ssa24_exception(validation_error):
    """
    Convert SSA-24 validation exceptions to SSA-23 domain exceptions

    This function provides a bridge between the validation framework (SSA-24)
    and the domain exception system (SSA-23) for consistent error handling.

    Args:
        validation_error: SSA-24 validation exception

    Returns:
        Corresponding SSA-23 domain exception
    """
    if not SSA24_AVAILABLE or validation_error is None:
        return validation_error

    try:
        # Map SSA-24 exceptions to SSA-23 exceptions
        if isinstance(validation_error, (SSA24ValidationError, SanitizationError)):
            return ValidationException(
                message=validation_error.message,
                user_message=validation_error.user_message,
                context=validation_error.context,
                recovery_suggestion=validation_error.recovery_suggestion,
                error_code=validation_error.error_code,
                cause=validation_error
            )

        elif isinstance(validation_error, FileValidationError):
            return ValidationException(
                message=f"File validation failed: {validation_error.message}",
                user_message="El archivo no cumple con los requisitos de seguridad",
                context={
                    **validation_error.context,
                    'validation_type': 'file_validation',
                    'original_error_code': validation_error.error_code
                },
                recovery_suggestion="Verifique el tipo y contenido del archivo",
                cause=validation_error
            )

        elif isinstance(validation_error, SignalValidationError):
            return ValidationException(
                message=f"Signal validation failed: {validation_error.message}",
                user_message="Los parámetros de la señal no son válidos",
                context={
                    **validation_error.context,
                    'validation_type': 'signal_validation',
                    'original_error_code': validation_error.error_code
                },
                recovery_suggestion="Verifique los parámetros de la señal",
                cause=validation_error
            )

        elif isinstance(validation_error, SecurityValidationError):
            return ValidationException(
                message=f"Security validation failed: {validation_error.message}",
                user_message="Contenido no permitido por políticas de seguridad",
                context={
                    **validation_error.context,
                    'validation_type': 'security_validation',
                    'threat_type': validation_error.context.get('threat_type'),
                    'original_error_code': validation_error.error_code
                },
                recovery_suggestion="Modifique el contenido para cumplir con las políticas de seguridad",
                cause=validation_error
            )

        elif isinstance(validation_error, APIValidationError):
            return WebException(
                endpoint=validation_error.context.get('endpoint', 'unknown'),
                http_status=400,
                request_method=validation_error.context.get('request_method', 'unknown'),
                user_message=validation_error.user_message,
                recovery_suggestion=validation_error.recovery_suggestion,
                context={
                    **validation_error.context,
                    'validation_type': 'api_validation',
                    'original_error_code': validation_error.error_code
                },
                cause=validation_error
            )

        elif isinstance(validation_error, ConfigValidationError):
            return ConfigurationException(
                message=f"Configuration validation failed: {validation_error.message}",
                user_message="Error en la configuración del sistema",
                context={
                    **validation_error.context,
                    'validation_type': 'config_validation',
                    'original_error_code': validation_error.error_code
                },
                recovery_suggestion="Verifique la configuración del sistema",
                cause=validation_error
            )

        else:
            # Default mapping for unknown SSA-24 exceptions
            return ValidationException(
                message=f"Validation error: {validation_error.message}",
                user_message=getattr(validation_error, 'user_message', 'Error de validación'),
                context=getattr(validation_error, 'context', {}),
                recovery_suggestion=getattr(validation_error, 'recovery_suggestion',
                                          'Verifique los datos de entrada'),
                error_code=getattr(validation_error, 'error_code', 'VALIDATION_ERROR'),
                cause=validation_error
            )

    except Exception as e:
        # Fallback if conversion fails
        return ValidationException(
            message=f"Exception conversion failed: {str(e)}",
            user_message="Error interno de validación",
            context={'conversion_error': str(e), 'original_error': str(validation_error)},
            recovery_suggestion="Contacte al administrador del sistema",
            cause=e
        )


def is_ssa24_exception(exception):
    """
    Check if an exception is from the SSA-24 validation framework

    Args:
        exception: Exception to check

    Returns:
        bool: True if exception is from SSA-24, False otherwise
    """
    if not SSA24_AVAILABLE:
        return False

    ssa24_exception_types = (
        SSA24ValidationError,
        SanitizationError,
        SecurityValidationError,
        FileValidationError,
        SignalValidationError,
        ConfigValidationError,
        APIValidationError,
        ValidationPipelineError
    )

    return isinstance(exception, ssa24_exception_types)


# Convenience function for exception handling in application code
def handle_validation_exception(exception):
    """
    Unified exception handler for both SSA-23 and SSA-24 exceptions

    Args:
        exception: Exception to handle

    Returns:
        SSA-23 compatible exception
    """
    if is_ssa24_exception(exception):
        return handle_ssa24_exception(exception)
    else:
        return exception