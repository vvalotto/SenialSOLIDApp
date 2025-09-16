"""
Exception Handler with Recovery Strategy Integration
SSA-23: Exception Handling Refactoring
"""

from typing import Any, Dict, List, Optional, Callable
from .base_exceptions import SenialSOLIDException
from .recovery_strategies import RecoveryStrategy, RetryStrategy, FileIORecoveryStrategy, ProcessingFallbackStrategy

try:
    from config.logging_config import get_logger
except ImportError:
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger(__name__)


class ExceptionHandler:
    """
    Centralized exception handler with recovery strategy support

    Provides a unified way to handle exceptions across the application
    with automatic recovery attempts and consistent logging.
    """

    def __init__(self):
        self.recovery_strategies: List[RecoveryStrategy] = []
        self._setup_default_strategies()

    def _setup_default_strategies(self):
        """Setup default recovery strategies"""
        self.recovery_strategies = [
            FileIORecoveryStrategy(),
            ProcessingFallbackStrategy(),
            RetryStrategy(max_retries=3, base_delay=1.0)  # Generic retry as last resort
        ]

    def add_recovery_strategy(self, strategy: RecoveryStrategy):
        """Add a custom recovery strategy"""
        self.recovery_strategies.insert(-1, strategy)  # Insert before generic retry

    def handle_exception(
        self,
        exception: Exception,
        context: Dict = None,
        operation_name: str = None,
        max_recovery_attempts: int = 3
    ) -> Any:
        """
        Handle exception with recovery strategies

        Args:
            exception: The exception to handle
            context: Additional context information
            operation_name: Name of the operation that failed
            max_recovery_attempts: Maximum number of recovery attempts

        Returns:
            Result from successful recovery, or raises the exception

        Raises:
            The original or transformed exception if recovery fails
        """
        # Convert to SenialSOLIDException if needed
        if not isinstance(exception, SenialSOLIDException):
            exception = self._wrap_exception(exception, context, operation_name)

        original_exception = exception
        recovery_attempts = 0

        logger.info(
            "Starting exception handling",
            extra={
                "error_code": exception.error_code,
                "operation_name": operation_name,
                "max_recovery_attempts": max_recovery_attempts,
                "available_strategies": len(self.recovery_strategies)
            }
        )

        while recovery_attempts < max_recovery_attempts:
            # Try each recovery strategy
            for strategy in self.recovery_strategies:
                if strategy.can_recover(exception):
                    recovery_attempts += 1

                    logger.info(
                        "Attempting recovery",
                        extra={
                            "strategy": strategy.get_strategy_name(),
                            "attempt": recovery_attempts,
                            "error_code": exception.error_code
                        }
                    )

                    try:
                        result = strategy.recover(exception, context)

                        logger.info(
                            "Recovery successful",
                            extra={
                                "strategy": strategy.get_strategy_name(),
                                "attempt": recovery_attempts,
                                "error_code": exception.error_code
                            }
                        )

                        return result

                    except SenialSOLIDException as recovery_exception:
                        # Strategy modified the exception (e.g., for retry)
                        exception = recovery_exception
                        logger.debug(
                            "Recovery strategy updated exception",
                            extra={
                                "strategy": strategy.get_strategy_name(),
                                "new_error_code": exception.error_code
                            }
                        )
                        break  # Try strategies again with updated exception

                    except Exception as recovery_error:
                        logger.warning(
                            "Recovery strategy failed",
                            extra={
                                "strategy": strategy.get_strategy_name(),
                                "recovery_error": str(recovery_error),
                                "original_error_code": exception.error_code
                            },
                            exc_info=True
                        )
                        continue  # Try next strategy

            else:
                # No strategy could handle the exception
                break

        # All recovery attempts exhausted
        logger.error(
            "Exception handling failed - all recovery attempts exhausted",
            extra={
                "original_error_code": original_exception.error_code,
                "final_error_code": exception.error_code,
                "recovery_attempts": recovery_attempts,
                "operation_name": operation_name
            }
        )

        raise exception

    def _wrap_exception(
        self,
        exception: Exception,
        context: Dict = None,
        operation_name: str = None
    ) -> SenialSOLIDException:
        """Wrap a regular exception in SenialSOLIDException"""
        from .infrastructure_exceptions import DataAccessException
        from .domain_exceptions import ProcessingException

        # Try to map to appropriate exception type based on exception type
        if isinstance(exception, (IOError, OSError, FileNotFoundError, PermissionError)):
            return DataAccessException(
                file_path=str(getattr(exception, 'filename', 'unknown')),
                operation=operation_name or 'file_operation',
                context=context,
                cause=exception
            )

        elif isinstance(exception, (ValueError, TypeError)) and operation_name:
            if 'process' in operation_name.lower():
                return ProcessingException(
                    operation=operation_name,
                    context=context,
                    cause=exception
                )

        # Generic wrapping as last resort
        return SenialSOLIDException(
            message=str(exception),
            context=context or {},
            cause=exception
        )


# Global exception handler instance
_global_handler = ExceptionHandler()


def handle_with_recovery(
    operation: Callable,
    operation_name: str = None,
    context: Dict = None,
    max_attempts: int = 3,
    **operation_kwargs
) -> Any:
    """
    Decorator-like function to handle operations with automatic exception recovery

    Usage:
        result = handle_with_recovery(
            operation=lambda: risky_file_operation(file_path),
            operation_name="file_read",
            context={"file_path": file_path},
            max_attempts=3
        )
    """
    try:
        return operation(**operation_kwargs)
    except Exception as e:
        return _global_handler.handle_exception(
            exception=e,
            context=context,
            operation_name=operation_name,
            max_recovery_attempts=max_attempts
        )


def get_exception_handler() -> ExceptionHandler:
    """Get the global exception handler instance"""
    return _global_handler