"""
SSA-26 Academic Simple Retry Pattern
Educational retry pattern implementation for transient failure recovery

This module demonstrates how to implement basic retry patterns for
educational purposes without the complexity of exponential backoff.
"""

from typing import Callable, Any, Optional, List, Type, Dict
from dataclasses import dataclass
from enum import Enum
import time
import logging
import random
from datetime import datetime, timedelta


class RetryReason(Enum):
    """Educational classification of retry reasons"""
    TRANSIENT_IO_ERROR = "transient_io_error"
    NETWORK_TIMEOUT = "network_timeout"
    DATABASE_CONNECTION = "database_connection"
    FILE_LOCK = "file_lock"
    RESOURCE_BUSY = "resource_busy"
    TEMPORARY_UNAVAILABLE = "temporary_unavailable"


@dataclass
class RetryConfiguration:
    """
    Educational retry configuration for simple retry pattern

    This configuration demonstrates the key parameters needed for
    retry logic without the complexity of enterprise patterns.
    """
    max_attempts: int = 3                    # Maximum number of retry attempts
    delay_seconds: float = 1.0               # Fixed delay between attempts
    timeout_seconds: Optional[float] = None   # Optional timeout per attempt
    retryable_exceptions: List[Type[Exception]] = None  # Exceptions that trigger retry
    educational_logging: bool = True          # Enhanced logging for learning

    def __post_init__(self):
        """Set default retryable exceptions if not provided"""
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                ConnectionError,
                TimeoutError,
                OSError,
                IOError,
                FileNotFoundError  # For file operations
            ]


@dataclass
class RetryAttempt:
    """Educational retry attempt information for learning purposes"""
    attempt_number: int
    start_time: datetime
    end_time: Optional[datetime]
    exception: Optional[Exception]
    success: bool
    duration_ms: Optional[float]


@dataclass
class RetryResult:
    """Educational retry operation result with learning context"""
    success: bool
    result: Any
    total_attempts: int
    total_duration_ms: float
    attempts: List[RetryAttempt]
    final_exception: Optional[Exception]
    retry_reason: Optional[RetryReason]


class RetryableOperation:
    """
    Educational wrapper for operations that can be retried

    This class demonstrates how to wrap operations with retry logic
    while maintaining clean separation of concerns for educational purposes.

    Examples:
        >>> config = RetryConfiguration(max_attempts=3, delay_seconds=1.0)
        >>> operation = RetryableOperation(
        ...     operation=lambda: read_signal_file("data.csv"),
        ...     operation_name="file_read",
        ...     config=config
        ... )
        >>> result = operation.execute()
    """

    def __init__(self, operation: Callable[[], Any], operation_name: str,
                 config: RetryConfiguration, logger: Optional[logging.Logger] = None):
        """
        Initialize retryable operation with educational configuration

        Args:
            operation: The operation to execute with retry logic
            operation_name: Descriptive name for educational logging
            config: Retry configuration parameters
            logger: Optional logger for educational debugging
        """
        self.operation = operation
        self.operation_name = operation_name
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

    def execute(self) -> RetryResult:
        """
        Execute operation with simple retry logic

        This method demonstrates a basic retry pattern suitable for
        educational purposes without complex exponential backoff.

        Returns:
            RetryResult with detailed information for learning
        """
        attempts = []
        start_time = datetime.now()
        final_exception = None

        if self.config.educational_logging:
            self.logger.info(
                f"Starting retryable operation: {self.operation_name}",
                extra={
                    "max_attempts": self.config.max_attempts,
                    "delay_seconds": self.config.delay_seconds,
                    "retryable_exceptions": [exc.__name__ for exc in self.config.retryable_exceptions]
                }
            )

        for attempt_num in range(1, self.config.max_attempts + 1):
            attempt_start = datetime.now()
            attempt = RetryAttempt(
                attempt_number=attempt_num,
                start_time=attempt_start,
                end_time=None,
                exception=None,
                success=False,
                duration_ms=None
            )

            try:
                if self.config.educational_logging:
                    self.logger.info(f"Attempt {attempt_num}/{self.config.max_attempts}: {self.operation_name}")

                # Execute the operation
                result = self.operation()

                # Success!
                attempt.end_time = datetime.now()
                attempt.success = True
                attempt.duration_ms = (attempt.end_time - attempt_start).total_seconds() * 1000
                attempts.append(attempt)

                total_duration = (datetime.now() - start_time).total_seconds() * 1000

                if self.config.educational_logging:
                    self.logger.info(
                        f"Operation succeeded on attempt {attempt_num}: {self.operation_name}",
                        extra={
                            "attempt_duration_ms": attempt.duration_ms,
                            "total_duration_ms": total_duration
                        }
                    )

                return RetryResult(
                    success=True,
                    result=result,
                    total_attempts=attempt_num,
                    total_duration_ms=total_duration,
                    attempts=attempts,
                    final_exception=None,
                    retry_reason=None
                )

            except Exception as exc:
                attempt.end_time = datetime.now()
                attempt.exception = exc
                attempt.duration_ms = (attempt.end_time - attempt_start).total_seconds() * 1000
                attempts.append(attempt)
                final_exception = exc

                # Check if this exception is retryable
                if not self._is_retryable_exception(exc):
                    if self.config.educational_logging:
                        self.logger.error(
                            f"Non-retryable exception in {self.operation_name}: {type(exc).__name__}",
                            extra={
                                "exception_message": str(exc),
                                "attempt_number": attempt_num,
                                "educational_note": "Esta excepción no es reintentar porque no es transitoria"
                            }
                        )
                    break

                if self.config.educational_logging:
                    self.logger.warning(
                        f"Attempt {attempt_num} failed: {self.operation_name}",
                        extra={
                            "exception_type": type(exc).__name__,
                            "exception_message": str(exc),
                            "will_retry": attempt_num < self.config.max_attempts,
                            "educational_note": "Error transitorio - reintentando operación"
                        }
                    )

                # If this is not the last attempt, wait before retrying
                if attempt_num < self.config.max_attempts:
                    self._educational_wait(attempt_num)

        # All attempts failed
        total_duration = (datetime.now() - start_time).total_seconds() * 1000

        if self.config.educational_logging:
            self.logger.error(
                f"All retry attempts failed for {self.operation_name}",
                extra={
                    "total_attempts": len(attempts),
                    "total_duration_ms": total_duration,
                    "final_exception": str(final_exception),
                    "educational_note": "Operación falló después de todos los reintentos"
                }
            )

        return RetryResult(
            success=False,
            result=None,
            total_attempts=len(attempts),
            total_duration_ms=total_duration,
            attempts=attempts,
            final_exception=final_exception,
            retry_reason=self._classify_retry_reason(final_exception)
        )

    def _is_retryable_exception(self, exception: Exception) -> bool:
        """
        Determine if an exception should trigger a retry

        This method demonstrates how to classify exceptions as retryable
        or non-retryable for educational purposes.

        Args:
            exception: The exception to classify

        Returns:
            True if the exception is retryable, False otherwise
        """
        return any(isinstance(exception, exc_type) for exc_type in self.config.retryable_exceptions)

    def _classify_retry_reason(self, exception: Exception) -> Optional[RetryReason]:
        """Classify the reason for retry for educational purposes"""
        if isinstance(exception, (ConnectionError, OSError)):
            return RetryReason.NETWORK_TIMEOUT
        elif isinstance(exception, TimeoutError):
            return RetryReason.NETWORK_TIMEOUT
        elif isinstance(exception, (IOError, FileNotFoundError)):
            return RetryReason.TRANSIENT_IO_ERROR
        elif "database" in str(exception).lower():
            return RetryReason.DATABASE_CONNECTION
        elif "resource busy" in str(exception).lower():
            return RetryReason.RESOURCE_BUSY
        else:
            return RetryReason.TEMPORARY_UNAVAILABLE

    def _educational_wait(self, attempt_number: int) -> None:
        """
        Educational wait between retry attempts

        This method demonstrates a simple fixed delay strategy
        suitable for academic purposes.

        Args:
            attempt_number: Current attempt number for logging
        """
        if self.config.educational_logging:
            self.logger.info(
                f"Waiting {self.config.delay_seconds}s before retry attempt {attempt_number + 1}",
                extra={
                    "delay_seconds": self.config.delay_seconds,
                    "educational_note": "Pausa fija entre reintentos - no exponencial para simplicidad académica"
                }
            )

        time.sleep(self.config.delay_seconds)


class SimpleRetryPattern:
    """
    Academic Simple Retry Pattern for SenialSOLIDApp

    This class provides a simplified retry pattern implementation suitable
    for educational purposes in signal processing applications.

    Educational Purposes:
    - Demonstrates basic retry concepts without enterprise complexity
    - Shows how to handle transient failures in I/O operations
    - Illustrates retry configuration and monitoring
    - Provides examples relevant to signal processing scenarios

    Examples:
        >>> retry_pattern = SimpleRetryPattern()
        >>>
        >>> # Retry file read operation
        >>> result = retry_pattern.retry_file_operation(
        ...     lambda: read_signal_data("sensors.csv"),
        ...     "read_sensor_data"
        ... )
        >>>
        >>> # Retry database connection
        >>> result = retry_pattern.retry_database_operation(
        ...     lambda: connect_to_database(),
        ...     "database_connection"
        ... )
    """

    def __init__(self, default_config: Optional[RetryConfiguration] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize simple retry pattern with educational configuration

        Args:
            default_config: Default retry configuration for operations
            logger: Optional logger for educational debugging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.default_config = default_config or RetryConfiguration()

        # Educational retry configurations for different operation types
        self.operation_configs = {
            "file_operations": RetryConfiguration(
                max_attempts=3,
                delay_seconds=1.0,
                retryable_exceptions=[IOError, OSError, FileNotFoundError, PermissionError],
                educational_logging=True
            ),
            "database_operations": RetryConfiguration(
                max_attempts=5,
                delay_seconds=2.0,
                retryable_exceptions=[ConnectionError, TimeoutError],
                educational_logging=True
            ),
            "signal_processing": RetryConfiguration(
                max_attempts=2,
                delay_seconds=0.5,
                retryable_exceptions=[RuntimeError, ValueError],  # For numerical errors
                educational_logging=True
            )
        }

    def retry_operation(self, operation: Callable[[], Any], operation_name: str,
                       config: Optional[RetryConfiguration] = None) -> RetryResult:
        """
        Generic retry method for any operation

        Args:
            operation: The operation to retry
            operation_name: Descriptive name for logging
            config: Optional specific configuration

        Returns:
            RetryResult with operation outcome and retry information
        """
        config = config or self.default_config
        retryable_op = RetryableOperation(operation, operation_name, config, self.logger)
        return retryable_op.execute()

    def retry_file_operation(self, operation: Callable[[], Any], operation_name: str) -> RetryResult:
        """
        Retry file I/O operations with appropriate configuration

        This method demonstrates retry patterns specific to file operations
        common in signal processing applications.

        Args:
            operation: File operation to retry
            operation_name: Descriptive name for educational logging

        Returns:
            RetryResult with file operation outcome

        Examples:
            >>> retry_pattern = SimpleRetryPattern()
            >>> result = retry_pattern.retry_file_operation(
            ...     lambda: pd.read_csv("signal_data.csv"),
            ...     "read_signal_csv"
            ... )
        """
        return self.retry_operation(operation, operation_name, self.operation_configs["file_operations"])

    def retry_database_operation(self, operation: Callable[[], Any], operation_name: str) -> RetryResult:
        """
        Retry database operations with appropriate configuration

        Args:
            operation: Database operation to retry
            operation_name: Descriptive name for educational logging

        Returns:
            RetryResult with database operation outcome
        """
        return self.retry_operation(operation, operation_name, self.operation_configs["database_operations"])

    def retry_signal_processing(self, operation: Callable[[], Any], operation_name: str) -> RetryResult:
        """
        Retry signal processing operations with appropriate configuration

        This method demonstrates retry patterns for numerical operations
        that might fail due to transient computational issues.

        Args:
            operation: Signal processing operation to retry
            operation_name: Descriptive name for educational logging

        Returns:
            RetryResult with signal processing outcome

        Examples:
            >>> retry_pattern = SimpleRetryPattern()
            >>> result = retry_pattern.retry_signal_processing(
            ...     lambda: scipy.signal.butter(4, 0.5, 'low'),
            ...     "butter_filter_design"
            ... )
        """
        return self.retry_operation(operation, operation_name, self.operation_configs["signal_processing"])

    def get_retry_statistics(self, results: List[RetryResult]) -> Dict[str, Any]:
        """
        Educational retry statistics for learning and monitoring

        This method demonstrates how to collect and analyze retry patterns
        for educational purposes and system monitoring.

        Args:
            results: List of RetryResult objects to analyze

        Returns:
            Dictionary with retry statistics and educational insights
        """
        if not results:
            return {"error": "No retry results provided"}

        total_operations = len(results)
        successful_operations = sum(1 for r in results if r.success)
        failed_operations = total_operations - successful_operations

        total_attempts = sum(r.total_attempts for r in results)
        avg_attempts_per_operation = total_attempts / total_operations

        retry_reasons = {}
        for result in results:
            if result.retry_reason:
                reason = result.retry_reason.value
                retry_reasons[reason] = retry_reasons.get(reason, 0) + 1

        educational_insights = []

        if failed_operations > 0:
            failure_rate = (failed_operations / total_operations) * 100
            educational_insights.append(
                f"Tasa de fallo: {failure_rate:.1f}% - "
                f"{'Alta' if failure_rate > 20 else 'Normal' if failure_rate > 5 else 'Baja'} "
                f"incidencia de errores"
            )

        if avg_attempts_per_operation > 1.5:
            educational_insights.append(
                f"Promedio de {avg_attempts_per_operation:.1f} intentos por operación - "
                "indica problemas transitorios frecuentes en el sistema"
            )

        most_common_reason = max(retry_reasons.items(), key=lambda x: x[1]) if retry_reasons else None
        if most_common_reason:
            educational_insights.append(
                f"Causa principal de reintentos: {most_common_reason[0]} "
                f"({most_common_reason[1]} ocurrencias)"
            )

        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate_percent": (successful_operations / total_operations) * 100,
            "total_attempts": total_attempts,
            "average_attempts_per_operation": avg_attempts_per_operation,
            "retry_reasons": retry_reasons,
            "educational_insights": educational_insights,
            "recommendation": self._generate_educational_recommendation(
                failed_operations, avg_attempts_per_operation, retry_reasons
            )
        }

    def _generate_educational_recommendation(self, failed_operations: int,
                                           avg_attempts: float,
                                           retry_reasons: Dict[str, int]) -> str:
        """Generate educational recommendations based on retry patterns"""
        if failed_operations == 0 and avg_attempts < 1.2:
            return "Sistema estable - los reintentos están funcionando correctamente"

        if avg_attempts > 2.0:
            return ("Alto número de reintentos detectado. Considere investigar las causas "
                   "raíz de los errores transitorios y mejorar la infraestructura.")

        if "transient_io_error" in retry_reasons:
            return ("Errores de I/O frecuentes detectados. Verifique el sistema de archivos "
                   "y considere usar almacenamiento más confiable.")

        if "database_connection" in retry_reasons:
            return ("Problemas de conexión a base de datos detectados. Verifique la "
                   "configuración de red y la capacidad del servidor de base de datos.")

        return "Patrón de reintentos normal - continúe monitoreando el sistema."