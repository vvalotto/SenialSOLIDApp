"""
Base Exception Classes with SSA-22 Integration
SSA-23: Exception Handling Refactoring
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from config.logging_config import get_logger
except ImportError:
    # Fallback for testing or when logging not available
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)


class SenialSOLIDException(Exception):
    """
    Base exception class for SenialSOLID application

    Features:
    - Automatic SSA-22 structured logging integration
    - Rich context information for debugging
    - Recovery strategy support
    - User-friendly error messages
    - Unique error codes for tracking
    """

    def __init__(
        self,
        message: str,
        user_message: str = None,
        context: Optional[Dict[str, Any]] = None,
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
        """Generate unique error code for tracking and correlation"""
        return f"{self.__class__.__name__}_{int(time.time() * 1000)}"

    def _log_exception(self):
        """Automatic SSA-22 structured logging with rich context"""
        try:
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
                    "timestamp": self.timestamp.isoformat(),
                    "exception_module": self.__class__.__module__
                },
                exc_info=True
            )
        except Exception:
            # Fallback if logging fails - don't let logging errors break the application
            pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization and API responses"""
        return {
            "error_code": self.error_code,
            "error_type": self.__class__.__name__,
            "message": self.message,
            "user_message": self.user_message,
            "context": self.context,
            "recovery_suggestion": self.recovery_suggestion,
            "timestamp": self.timestamp.isoformat()
        }

    def __str__(self) -> str:
        """String representation for debugging"""
        return f"{self.__class__.__name__}({self.error_code}): {self.message}"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (
            f"{self.__class__.__name__}("
            f"error_code='{self.error_code}', "
            f"message='{self.message}', "
            f"context={self.context})"
        )


class DomainException(SenialSOLIDException):
    """
    Base class for domain layer exceptions

    Domain exceptions represent violations of business rules,
    validation failures, and errors in core business logic.
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('user_message', 'Error en la lógica de negocio')
        kwargs.setdefault('recovery_suggestion', 'Verifique los datos de entrada y las reglas de negocio')
        super().__init__(message, **kwargs)


class InfrastructureException(SenialSOLIDException):
    """
    Base class for infrastructure layer exceptions

    Infrastructure exceptions represent failures in external systems,
    I/O operations, configuration, and technical infrastructure.
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('user_message', 'Error técnico del sistema')
        kwargs.setdefault('recovery_suggestion', 'Contacte al administrador del sistema')
        super().__init__(message, **kwargs)


class PresentationException(SenialSOLIDException):
    """
    Base class for presentation layer exceptions

    Presentation exceptions represent errors in user interfaces,
    request processing, and user interaction handling.
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('user_message', 'Error en la interfaz de usuario')
        kwargs.setdefault('recovery_suggestion', 'Intente nuevamente o contacte soporte')
        super().__init__(message, **kwargs)