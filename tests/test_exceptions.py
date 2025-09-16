"""
Comprehensive Exception Handling Tests
SSA-23: Exception Handling Refactoring
"""

import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open
from datetime import datetime

# Add project root to path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '04_dominio'))

from exceptions import (
    SenialSOLIDException,
    DomainException, InfrastructureException, PresentationException,
    ValidationException, ProcessingException, AcquisitionException, RepositoryException,
    ConfigurationException, DataAccessException, NetworkException,
    WebException, ConsoleException
)
from exceptions.recovery_strategies import (
    RecoveryStrategy, FileIORecoveryStrategy, ProcessingFallbackStrategy, RetryStrategy
)
from exceptions.exception_handler import ExceptionHandler, handle_with_recovery


class TestBaseExceptions:
    """Test base exception classes and SSA-22 integration"""

    def test_senial_solid_exception_creation(self):
        """Test base exception creation and context"""
        exception = SenialSOLIDException(
            message="Test error",
            user_message="User friendly error",
            context={"test_key": "test_value"},
            recovery_suggestion="Try again"
        )

        assert exception.message == "Test error"
        assert exception.user_message == "User friendly error"
        assert exception.context["test_key"] == "test_value"
        assert exception.recovery_suggestion == "Try again"
        assert exception.error_code.startswith("SenialSOLIDException_")
        assert exception.timestamp is not None

    def test_exception_to_dict(self):
        """Test exception serialization"""
        exception = SenialSOLIDException("Test error", context={"key": "value"})
        exception_dict = exception.to_dict()

        expected_keys = {"error_code", "error_type", "message", "user_message",
                        "context", "recovery_suggestion", "timestamp"}
        assert set(exception_dict.keys()) == expected_keys
        assert exception_dict["error_type"] == "SenialSOLIDException"
        assert exception_dict["context"]["key"] == "value"

    def test_exception_string_representation(self):
        """Test string and repr methods"""
        exception = SenialSOLIDException("Test error")

        str_repr = str(exception)
        assert "SenialSOLIDException" in str_repr
        assert "Test error" in str_repr

        repr_str = repr(exception)
        assert "SenialSOLIDException(" in repr_str
        assert "error_code" in repr_str


class TestDomainExceptions:
    """Test domain-specific exceptions"""

    def test_validation_exception(self):
        """Test ValidationException with field context"""
        exception = ValidationException(
            field="signal_id",
            value="invalid_id",
            rule="must be numeric"
        )

        assert isinstance(exception, DomainException)
        assert exception.context["field"] == "signal_id"
        assert exception.context["invalid_value"] == "invalid_id"
        assert exception.context["validation_rule"] == "must be numeric"
        assert "signal_id" in exception.message
        assert "must be numeric" in exception.message

    def test_processing_exception(self):
        """Test ProcessingException with signal context"""
        exception = ProcessingException(
            operation="complex_filter",
            signal_id="signal_123",
            processing_stage="filtering"
        )

        assert isinstance(exception, DomainException)
        assert exception.context["operation"] == "complex_filter"
        assert exception.context["signal_id"] == "signal_123"
        assert exception.context["processing_stage"] == "filtering"
        assert "complex_filter" in exception.message

    def test_acquisition_exception(self):
        """Test AcquisitionException with source context"""
        exception = AcquisitionException(
            source="file.dat",
            source_type="file",
            acquisition_method="file_read"
        )

        assert isinstance(exception, DomainException)
        assert exception.context["source"] == "file.dat"
        assert exception.context["source_type"] == "file"
        assert exception.context["acquisition_method"] == "file_read"
        assert "file.dat" in exception.message

    def test_repository_exception(self):
        """Test RepositoryException with entity context"""
        exception = RepositoryException(
            operation="save",
            entity_type="signal",
            entity_id="123"
        )

        assert isinstance(exception, DomainException)
        assert exception.context["operation"] == "save"
        assert exception.context["entity_type"] == "signal"
        assert exception.context["entity_id"] == "123"
        assert "save" in exception.message


class TestInfrastructureExceptions:
    """Test infrastructure-specific exceptions"""

    def test_configuration_exception(self):
        """Test ConfigurationException"""
        exception = ConfigurationException(
            config_key="database_url",
            config_file="config.yaml"
        )

        assert isinstance(exception, InfrastructureException)
        assert exception.context["config_key"] == "database_url"
        assert exception.context["config_file"] == "config.yaml"
        assert "database_url" in exception.message

    def test_data_access_exception(self):
        """Test DataAccessException with file context"""
        exception = DataAccessException(
            file_path="/tmp/test.dat",
            operation="read",
            retry_count=1,
            max_retries=3
        )

        assert isinstance(exception, InfrastructureException)
        assert exception.context["file_path"] == "/tmp/test.dat"
        assert exception.context["operation"] == "read"
        assert exception.context["retry_count"] == 1
        assert exception.context["can_retry"] == True
        assert "/tmp/test.dat" in exception.message

    def test_network_exception(self):
        """Test NetworkException with endpoint context"""
        exception = NetworkException(
            endpoint="http://api.example.com",
            operation="GET",
            status_code=500,
            timeout_seconds=30.0
        )

        assert isinstance(exception, InfrastructureException)
        assert exception.context["endpoint"] == "http://api.example.com"
        assert exception.context["status_code"] == 500
        assert exception.context["timeout_seconds"] == 30.0
        assert "http://api.example.com" in exception.message


class TestPresentationExceptions:
    """Test presentation-specific exceptions"""

    def test_web_exception(self):
        """Test WebException with HTTP context"""
        exception = WebException(
            endpoint="/api/signals",
            http_status=400,
            request_method="POST"
        )

        assert isinstance(exception, PresentationException)
        assert exception.context["endpoint"] == "/api/signals"
        assert exception.context["http_status"] == 400
        assert exception.context["request_method"] == "POST"
        assert "400" in exception.message

    def test_console_exception(self):
        """Test ConsoleException with command context"""
        exception = ConsoleException(
            command="list_signals",
            command_args=["--all"],
            user_input="invalid input"
        )

        assert isinstance(exception, PresentationException)
        assert exception.context["command"] == "list_signals"
        assert exception.context["command_args"] == ["--all"]
        assert exception.context["user_input"] == "invalid input"
        assert "list_signals" in exception.message


class TestRecoveryStrategies:
    """Test recovery strategy implementations"""

    def test_retry_strategy_can_recover(self):
        """Test RetryStrategy can_recover logic"""
        strategy = RetryStrategy(max_retries=3)

        # Test with retryable exception
        exception = DataAccessException("/tmp/test.dat", "read", retry_count=1)
        assert strategy.can_recover(exception) == True

        # Test with max retries exceeded
        exception = DataAccessException("/tmp/test.dat", "read", retry_count=3)
        assert strategy.can_recover(exception) == False

        # Test with non-retryable exception
        exception = ValidationException("field", "value", "rule")
        assert strategy.can_recover(exception) == False

    def test_file_io_recovery_strategy(self):
        """Test FileIORecoveryStrategy"""
        fallback_paths = ["/backup/path1", "/backup/path2"]
        strategy = FileIORecoveryStrategy(fallback_paths=fallback_paths)

        # Test with recoverable exception
        exception = DataAccessException("/original/path", "read", retry_count=0)
        assert strategy.can_recover(exception) == True

        # Test with exhausted retries
        exception = DataAccessException("/original/path", "read", retry_count=5)
        assert strategy.can_recover(exception) == False

    def test_processing_fallback_strategy(self):
        """Test ProcessingFallbackStrategy"""
        fallback_ops = {"complex_filter": "simple_filter"}
        strategy = ProcessingFallbackStrategy(fallback_operations=fallback_ops)

        # Test with fallback available
        exception = ProcessingException("complex_filter", "signal_123")
        assert strategy.can_recover(exception) == True

        # Test with no fallback
        exception = ProcessingException("unknown_operation", "signal_123")
        assert strategy.can_recover(exception) == False

        # Test with already fallback
        exception = ProcessingException("simple_filter", "signal_123")
        exception.context["is_fallback"] = True
        assert strategy.can_recover(exception) == False


class TestExceptionHandler:
    """Test centralized exception handler"""

    def test_exception_handler_initialization(self):
        """Test ExceptionHandler initialization"""
        handler = ExceptionHandler()
        assert len(handler.recovery_strategies) > 0
        # Should have default strategies
        strategy_types = [type(s).__name__ for s in handler.recovery_strategies]
        assert "FileIORecoveryStrategy" in strategy_types
        assert "ProcessingFallbackStrategy" in strategy_types
        assert "RetryStrategy" in strategy_types

    def test_wrap_exception(self):
        """Test exception wrapping functionality"""
        handler = ExceptionHandler()

        # Test IOError wrapping
        io_error = IOError("File not found")
        wrapped = handler._wrap_exception(io_error, {"test": "context"}, "test_operation")

        assert isinstance(wrapped, DataAccessException)
        assert wrapped.cause == io_error
        assert wrapped.context["test"] == "context"

    def test_handle_with_recovery_function(self):
        """Test handle_with_recovery function"""
        def successful_operation():
            return "success"

        def failing_operation():
            raise ValueError("Test error")

        # Test successful operation
        result = handle_with_recovery(
            operation=successful_operation,
            operation_name="test_success",
            max_attempts=1
        )
        assert result == "success"

        # Test failing operation
        with pytest.raises(SenialSOLIDException):
            handle_with_recovery(
                operation=failing_operation,
                operation_name="test_failure",
                max_attempts=1
            )


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""

    def test_file_operation_with_recovery(self):
        """Test file operation with automatic recovery"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")

            def write_file_operation():
                with open(test_file, 'w') as f:
                    f.write("test content")
                return "written"

            # Should succeed without recovery
            result = handle_with_recovery(
                operation=write_file_operation,
                operation_name="write_test_file",
                context={"file_path": test_file},
                max_attempts=2
            )
            assert result == "written"
            assert os.path.exists(test_file)

    def test_signal_processing_with_fallback(self):
        """Test signal processing with fallback strategy"""
        def complex_processing():
            raise ProcessingException(
                operation="complex_filter",
                signal_id="test_signal"
            )

        def simple_processing():
            return "processed_simple"

        # Test that processing exception is raised (fallback would be handled by strategy)
        with pytest.raises(ProcessingException) as exc_info:
            handle_with_recovery(
                operation=complex_processing,
                operation_name="process_signal",
                max_attempts=1
            )

        assert exc_info.value.context["operation"] == "complex_filter"

    @patch('builtins.open', mock_open(read_data="config_data"))
    def test_configuration_loading_error(self):
        """Test configuration loading with proper exception handling"""
        def load_config():
            # Simulate configuration error
            raise ConfigurationException(
                config_key="missing_key",
                config_file="test_config.yaml"
            )

        with pytest.raises(ConfigurationException) as exc_info:
            handle_with_recovery(
                operation=load_config,
                operation_name="load_configuration",
                max_attempts=1
            )

        assert exc_info.value.context["config_key"] == "missing_key"
        assert exc_info.value.context["config_file"] == "test_config.yaml"


class TestSSA22Integration:
    """Test SSA-22 structured logging integration"""

    @patch('exceptions.base_exceptions.get_logger')
    def test_automatic_logging_on_exception_creation(self, mock_get_logger):
        """Test that exceptions automatically log with SSA-22"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        exception = ValidationException(
            field="test_field",
            value="invalid_value",
            rule="test_rule"
        )

        # Verify logger was called
        mock_get_logger.assert_called_once()
        mock_logger.error.assert_called_once()

        # Check the logging call
        args, kwargs = mock_logger.error.call_args
        assert "ValidationException" in args[0]
        assert "extra" in kwargs
        assert kwargs["extra"]["error_type"] == "ValidationException"
        assert kwargs["extra"]["context"]["field"] == "test_field"
        assert kwargs["exc_info"] == True

    def test_exception_context_enrichment(self):
        """Test that exceptions include rich context for debugging"""
        exception = ProcessingException(
            operation="test_operation",
            signal_id="signal_123",
            processing_stage="validation"
        )

        # Verify context enrichment
        assert exception.context["operation"] == "test_operation"
        assert exception.context["signal_id"] == "signal_123"
        assert exception.context["processing_stage"] == "validation"
        assert exception.context["operation_type"] == "signal_processing"

        # Verify user-friendly messages
        assert exception.user_message == "Error procesando señal"
        assert "parámetros de procesamiento" in exception.recovery_suggestion


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])