"""
Recovery Strategies for Exception Handling
SSA-23: Exception Handling Refactoring
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from .base_exceptions import SenialSOLIDException

try:
    from config.logging_config import get_logger
except ImportError:
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger(__name__)


class RecoveryStrategy(ABC):
    """
    Abstract base class for recovery strategies

    Recovery strategies implement specific logic to handle
    and potentially recover from different types of exceptions.
    """

    @abstractmethod
    def can_recover(self, exception: SenialSOLIDException) -> bool:
        """Check if this strategy can handle the given exception"""
        pass

    @abstractmethod
    def recover(self, exception: SenialSOLIDException, context: Dict = None) -> Any:
        """Attempt recovery and return result or raise exception"""
        pass

    def get_strategy_name(self) -> str:
        """Get human-readable name for this strategy"""
        return self.__class__.__name__


class RetryStrategy(RecoveryStrategy):
    """
    Generic retry strategy with exponential backoff

    Implements configurable retry logic with exponential backoff
    for transient failures that may succeed on retry.
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def can_recover(self, exception: SenialSOLIDException) -> bool:
        """Check if exception is retryable"""
        retry_count = exception.context.get('retry_count', 0)
        return retry_count < self.max_retries and self._is_retryable_exception(exception)

    def _is_retryable_exception(self, exception: SenialSOLIDException) -> bool:
        """Determine if exception type is suitable for retry"""
        # Import here to avoid circular imports
        from .infrastructure_exceptions import DataAccessException, NetworkException

        return isinstance(exception, (DataAccessException, NetworkException))

    def recover(self, exception: SenialSOLIDException, context: Dict = None) -> Any:
        """Implement retry with exponential backoff"""
        retry_count = exception.context.get('retry_count', 0)

        if retry_count >= self.max_retries:
            logger.error(
                "Max retries exceeded",
                extra={
                    "strategy": self.get_strategy_name(),
                    "max_retries": self.max_retries,
                    "exception_type": type(exception).__name__,
                    "error_code": exception.error_code
                }
            )
            raise exception

        # Calculate delay with exponential backoff
        delay = min(self.base_delay * (2 ** retry_count), self.max_delay)

        logger.info(
            "Attempting retry",
            extra={
                "strategy": self.get_strategy_name(),
                "retry_count": retry_count + 1,
                "max_retries": self.max_retries,
                "delay_seconds": delay,
                "error_code": exception.error_code
            }
        )

        time.sleep(delay)

        # Update retry count in exception context
        exception.context['retry_count'] = retry_count + 1
        exception.context['last_retry_delay'] = delay

        # Re-raise to trigger retry in calling code
        raise exception


class FileIORecoveryStrategy(RecoveryStrategy):
    """
    Recovery strategy for file I/O operations

    Implements specific recovery logic for file access issues,
    including permission fixes and alternative file paths.
    """

    def __init__(self, fallback_paths: list = None, create_missing_dirs: bool = True):
        self.fallback_paths = fallback_paths or []
        self.create_missing_dirs = create_missing_dirs

    def can_recover(self, exception: SenialSOLIDException) -> bool:
        """Check if this is a recoverable file I/O exception"""
        from .infrastructure_exceptions import DataAccessException

        if not isinstance(exception, DataAccessException):
            return False

        # Check if we have fallback options
        retry_count = exception.context.get('retry_count', 0)
        return retry_count < len(self.fallback_paths) + 2  # Original + fallbacks + create dir attempt

    def recover(self, exception, context: Dict = None) -> Any:
        """Attempt file I/O recovery strategies"""
        from .infrastructure_exceptions import DataAccessException
        import os

        if not isinstance(exception, DataAccessException):
            raise exception

        file_path = exception.context.get('file_path')
        operation = exception.context.get('operation')
        retry_count = exception.context.get('retry_count', 0)

        logger.info(
            "Attempting file I/O recovery",
            extra={
                "strategy": self.get_strategy_name(),
                "file_path": file_path,
                "operation": operation,
                "retry_count": retry_count
            }
        )

        # Strategy 1: Create missing directories
        if retry_count == 0 and self.create_missing_dirs:
            try:
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    logger.info("Created missing directory", extra={"directory": directory})
                    exception.context['retry_count'] = retry_count + 1
                    raise exception  # Retry with created directory
            except Exception as e:
                logger.warning("Failed to create directory", extra={"error": str(e)})

        # Strategy 2: Try fallback paths
        fallback_index = retry_count - 1
        if 0 <= fallback_index < len(self.fallback_paths):
            fallback_path = self.fallback_paths[fallback_index]
            logger.info("Trying fallback path", extra={"fallback_path": fallback_path})

            # Create new exception with fallback path
            new_exception = DataAccessException(
                file_path=fallback_path,
                operation=operation,
                retry_count=retry_count + 1,
                cause=exception
            )
            raise new_exception

        # No more recovery options
        logger.error("File I/O recovery exhausted", extra={"file_path": file_path})
        raise exception


class ProcessingFallbackStrategy(RecoveryStrategy):
    """
    Graceful degradation strategy for signal processing

    Implements fallback to simpler processing algorithms
    when complex operations fail.
    """

    def __init__(self, fallback_operations: Dict[str, str] = None):
        self.fallback_operations = fallback_operations or {
            'complex_filter': 'simple_filter',
            'advanced_transform': 'basic_transform',
            'ml_processing': 'statistical_processing'
        }

    def can_recover(self, exception: SenialSOLIDException) -> bool:
        """Check if processing operation has a fallback"""
        from .domain_exceptions import ProcessingException

        if not isinstance(exception, ProcessingException):
            return False

        operation = exception.context.get('operation')
        has_fallback = operation in self.fallback_operations
        already_fallback = exception.context.get('is_fallback', False)

        return has_fallback and not already_fallback

    def recover(self, exception, context: Dict = None) -> Any:
        """Implement graceful processing degradation"""
        from .domain_exceptions import ProcessingException

        if not isinstance(exception, ProcessingException):
            raise exception

        operation = exception.context.get('operation')
        fallback_operation = self.fallback_operations.get(operation)

        if not fallback_operation:
            raise exception

        logger.warning(
            "Falling back to simpler processing",
            extra={
                "strategy": self.get_strategy_name(),
                "original_operation": operation,
                "fallback_operation": fallback_operation,
                "signal_id": exception.context.get('signal_id')
            }
        )

        # Create fallback exception with simplified operation
        fallback_context = exception.context.copy()
        fallback_context.update({
            'operation': fallback_operation,
            'is_fallback': True,
            'original_operation': operation
        })

        fallback_exception = ProcessingException(
            operation=fallback_operation,
            signal_id=exception.context.get('signal_id'),
            processing_stage=exception.context.get('processing_stage'),
            context=fallback_context,
            cause=exception
        )

        raise fallback_exception