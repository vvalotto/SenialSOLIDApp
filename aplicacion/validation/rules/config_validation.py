"""
Configuration Validation for SSA-24 Input Validation Framework

Specialized validators for system configuration parameters and settings
"""

import os
import json
import yaml
import configparser
from typing import Any, Dict, List, Optional, Union, Type
import logging
from pathlib import Path
import re

from ..framework.validator_base import AbstractValidator, ValidationResult
from ..exceptions.validation_exceptions import ConfigValidationError, SecurityValidationError


class ConfigParameterValidator(AbstractValidator):
    """
    Validator for individual configuration parameters
    """

    def __init__(
        self,
        param_name: str,
        param_type: Type,
        required: bool = True,
        default_value: Any = None,
        allowed_values: List[Any] = None,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        validation_func: callable = None
    ):
        super().__init__(f"config_param_{param_name}")
        self.param_name = param_name
        self.param_type = param_type
        self.required = required
        self.default_value = default_value
        self.allowed_values = allowed_values
        self.min_value = min_value
        self.max_value = max_value
        self.validation_func = validation_func

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate configuration parameter"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Handle missing values
        if value is None:
            if self.required:
                error = ConfigValidationError(
                    message=f"Required configuration parameter '{self.param_name}' is missing",
                    config_key=self.param_name,
                    context=context
                )
                result.add_error(error)
                return result
            elif self.default_value is not None:
                value = self.default_value
                result.sanitized_value = value
                result.add_warning(f"Using default value for '{self.param_name}': {value}")

        if value is None:
            return result

        # Type conversion and validation
        try:
            converted_value = self._convert_type(value)
        except (ValueError, TypeError) as e:
            error = ConfigValidationError(
                message=f"Configuration parameter '{self.param_name}' type error: {str(e)}",
                config_key=self.param_name,
                context={**context, 'expected_type': self.param_type.__name__}
            )
            result.add_error(error)
            return result

        # Value constraints validation
        self._validate_constraints(converted_value, result, context)

        # Custom validation function
        if self.validation_func:
            try:
                custom_valid = self.validation_func(converted_value)
                if not custom_valid:
                    error = ConfigValidationError(
                        message=f"Configuration parameter '{self.param_name}' failed custom validation",
                        config_key=self.param_name,
                        context=context
                    )
                    result.add_error(error)
            except Exception as e:
                error = ConfigValidationError(
                    message=f"Custom validation error for '{self.param_name}': {str(e)}",
                    config_key=self.param_name,
                    context=context
                )
                result.add_error(error)

        result.sanitized_value = converted_value
        return result

    def _convert_type(self, value: Any) -> Any:
        """Convert value to expected type"""
        if isinstance(value, self.param_type):
            return value

        if self.param_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
            return bool(value)
        elif self.param_type == int:
            return int(float(value))  # Handle strings like "10.0"
        elif self.param_type == float:
            return float(value)
        elif self.param_type == str:
            return str(value)
        elif self.param_type == list:
            if isinstance(value, str):
                # Try to parse as JSON array or comma-separated
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return [x.strip() for x in value.split(',') if x.strip()]
            return list(value)
        elif self.param_type == dict:
            if isinstance(value, str):
                return json.loads(value)
            return dict(value)
        else:
            return self.param_type(value)

    def _validate_constraints(self, value: Any, result: ValidationResult, context: Dict[str, Any]):
        """Validate value constraints"""
        # Allowed values check
        if self.allowed_values and value not in self.allowed_values:
            error = ConfigValidationError(
                message=f"Parameter '{self.param_name}' value '{value}' not in allowed values: {self.allowed_values}",
                config_key=self.param_name,
                context={**context, 'allowed_values': self.allowed_values}
            )
            result.add_error(error)

        # Numeric range checks
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                error = ConfigValidationError(
                    message=f"Parameter '{self.param_name}' value {value} below minimum {self.min_value}",
                    config_key=self.param_name,
                    context=context
                )
                result.add_error(error)

            if self.max_value is not None and value > self.max_value:
                error = ConfigValidationError(
                    message=f"Parameter '{self.param_name}' value {value} exceeds maximum {self.max_value}",
                    config_key=self.param_name,
                    context=context
                )
                result.add_error(error)


class ConfigFileValidator(AbstractValidator):
    """
    Validator for configuration files
    """

    SUPPORTED_FORMATS = ['json', 'yaml', 'yml', 'ini', 'conf', 'cfg']

    def __init__(self, required_sections: List[str] = None, format_type: str = None):
        super().__init__("config_file_validator")
        self.required_sections = required_sections or []
        self.format_type = format_type

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate configuration file"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Handle file path or content
        if isinstance(value, str):
            if os.path.exists(value):
                # File path
                config_data = self._load_config_file(value, result, context)
                if config_data is None:
                    return result
            else:
                # String content
                config_data = self._parse_config_content(value, result, context)
                if config_data is None:
                    return result
        elif isinstance(value, dict):
            # Already parsed configuration
            config_data = value
        else:
            error = ConfigValidationError(
                message="Configuration must be file path, content string, or dictionary",
                context=context
            )
            result.add_error(error)
            return result

        # Validate configuration structure
        self._validate_config_structure(config_data, result, context)

        result.sanitized_value = config_data
        return result

    def _load_config_file(self, file_path: str, result: ValidationResult, context: Dict[str, Any]) -> Optional[Dict]:
        """Load and parse configuration file"""
        try:
            path = Path(file_path)

            # Security check - ensure file is in allowed location
            if not self._is_safe_path(path):
                error = SecurityValidationError(
                    message=f"Configuration file path not allowed: {file_path}",
                    threat_type="path_traversal",
                    context={**context, 'file_path': file_path}
                )
                result.add_error(error)
                return None

            # Determine format from extension
            file_format = self.format_type or path.suffix.lower().lstrip('.')

            if file_format not in self.SUPPORTED_FORMATS:
                error = ConfigValidationError(
                    message=f"Unsupported configuration file format: {file_format}",
                    context={**context, 'file_format': file_format}
                )
                result.add_error(error)
                return None

            # Load file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self._parse_config_content(content, result, context, file_format)

        except PermissionError:
            error = ConfigValidationError(
                message=f"Permission denied reading configuration file: {file_path}",
                context={**context, 'file_path': file_path}
            )
            result.add_error(error)
            return None
        except Exception as e:
            error = ConfigValidationError(
                message=f"Error reading configuration file: {str(e)}",
                context={**context, 'file_path': file_path}
            )
            result.add_error(error)
            return None

    def _parse_config_content(
        self,
        content: str,
        result: ValidationResult,
        context: Dict[str, Any],
        format_type: str = None
    ) -> Optional[Dict]:
        """Parse configuration content based on format"""
        format_type = format_type or self.format_type or 'json'

        try:
            if format_type == 'json':
                return json.loads(content)
            elif format_type in ['yaml', 'yml']:
                return yaml.safe_load(content)
            elif format_type in ['ini', 'conf', 'cfg']:
                parser = configparser.ConfigParser()
                parser.read_string(content)
                # Convert to dict
                return {section: dict(parser[section]) for section in parser.sections()}
            else:
                error = ConfigValidationError(
                    message=f"Unknown configuration format: {format_type}",
                    context={**context, 'format': format_type}
                )
                result.add_error(error)
                return None

        except json.JSONDecodeError as e:
            error = ConfigValidationError(
                message=f"Invalid JSON configuration: {str(e)}",
                context={**context, 'format': 'json'}
            )
            result.add_error(error)
            return None
        except yaml.YAMLError as e:
            error = ConfigValidationError(
                message=f"Invalid YAML configuration: {str(e)}",
                context={**context, 'format': 'yaml'}
            )
            result.add_error(error)
            return None
        except configparser.Error as e:
            error = ConfigValidationError(
                message=f"Invalid INI configuration: {str(e)}",
                context={**context, 'format': 'ini'}
            )
            result.add_error(error)
            return None

    def _validate_config_structure(self, config_data: Dict, result: ValidationResult, context: Dict[str, Any]):
        """Validate configuration structure and required sections"""
        if not isinstance(config_data, dict):
            error = ConfigValidationError(
                message="Configuration must be a dictionary/object",
                context=context
            )
            result.add_error(error)
            return

        # Check required sections
        for section in self.required_sections:
            if section not in config_data:
                error = ConfigValidationError(
                    message=f"Required configuration section '{section}' is missing",
                    config_section=section,
                    context=context
                )
                result.add_error(error)

        # Store metadata
        result.metadata.update({
            'sections': list(config_data.keys()),
            'total_parameters': sum(len(v) if isinstance(v, dict) else 1 for v in config_data.values())
        })

    def _is_safe_path(self, path: Path) -> bool:
        """Check if file path is safe (no path traversal)"""
        try:
            # Resolve path and check for traversal
            resolved = path.resolve()

            # Check for common unsafe patterns
            path_str = str(resolved)
            if '..' in path_str or path_str.startswith('/etc/') or path_str.startswith('/proc/'):
                return False

            return True
        except Exception:
            return False


class DatabaseConfigValidator(AbstractValidator):
    """
    Specialized validator for database configuration
    """

    def __init__(self):
        super().__init__("database_config_validator")

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate database configuration"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not isinstance(value, dict):
            error = ConfigValidationError(
                message="Database configuration must be a dictionary",
                config_section="database",
                context=context
            )
            result.add_error(error)
            return result

        # Required fields
        required_fields = ['host', 'port', 'database', 'username']
        for field in required_fields:
            if field not in value:
                error = ConfigValidationError(
                    message=f"Missing required database parameter: {field}",
                    config_key=field,
                    config_section="database",
                    context=context
                )
                result.add_error(error)

        # Validate specific fields
        self._validate_db_fields(value, result, context)

        return result

    def _validate_db_fields(self, config: Dict, result: ValidationResult, context: Dict[str, Any]):
        """Validate specific database configuration fields"""
        # Port validation
        if 'port' in config:
            try:
                port = int(config['port'])
                if port < 1 or port > 65535:
                    error = ConfigValidationError(
                        message=f"Invalid database port: {port} (must be 1-65535)",
                        config_key="port",
                        config_section="database",
                        context=context
                    )
                    result.add_error(error)
            except (ValueError, TypeError):
                error = ConfigValidationError(
                    message=f"Database port must be a number: {config['port']}",
                    config_key="port",
                    config_section="database",
                    context=context
                )
                result.add_error(error)

        # Host validation
        if 'host' in config:
            host = config['host']
            if not isinstance(host, str) or not host.strip():
                error = ConfigValidationError(
                    message="Database host cannot be empty",
                    config_key="host",
                    config_section="database",
                    context=context
                )
                result.add_error(error)

        # Security checks
        if 'password' in config:
            password = config['password']
            if isinstance(password, str) and len(password) < 8:
                result.add_warning("Database password is less than 8 characters")

        # SSL validation
        if 'ssl_mode' in config:
            ssl_mode = config['ssl_mode']
            valid_ssl_modes = ['disable', 'require', 'verify-ca', 'verify-full']
            if ssl_mode not in valid_ssl_modes:
                error = ConfigValidationError(
                    message=f"Invalid SSL mode: {ssl_mode} (valid: {valid_ssl_modes})",
                    config_key="ssl_mode",
                    config_section="database",
                    context=context
                )
                result.add_error(error)


class LoggingConfigValidator(AbstractValidator):
    """
    Specialized validator for logging configuration
    """

    def __init__(self):
        super().__init__("logging_config_validator")

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate logging configuration"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not isinstance(value, dict):
            error = ConfigValidationError(
                message="Logging configuration must be a dictionary",
                config_section="logging",
                context=context
            )
            result.add_error(error)
            return result

        # Validate log levels
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        if 'level' in value:
            level = value['level'].upper()
            if level not in valid_levels:
                error = ConfigValidationError(
                    message=f"Invalid log level: {level} (valid: {valid_levels})",
                    config_key="level",
                    config_section="logging",
                    context=context
                )
                result.add_error(error)

        # Validate log file path
        if 'file' in value:
            log_file = value['file']
            if log_file:
                log_path = Path(log_file)
                if not log_path.parent.exists():
                    result.add_warning(f"Log directory does not exist: {log_path.parent}")

        # Validate format string
        if 'format' in value:
            log_format = value['format']
            required_fields = ['%(levelname)s', '%(message)s']
            for field in required_fields:
                if field not in log_format:
                    result.add_warning(f"Log format missing recommended field: {field}")

        return result


class SecurityConfigValidator(AbstractValidator):
    """
    Specialized validator for security configuration
    """

    def __init__(self):
        super().__init__("security_config_validator")

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate security configuration"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not isinstance(value, dict):
            error = ConfigValidationError(
                message="Security configuration must be a dictionary",
                config_section="security",
                context=context
            )
            result.add_error(error)
            return result

        # Check for weak security settings
        self._check_security_settings(value, result, context)

        return result

    def _check_security_settings(self, config: Dict, result: ValidationResult, context: Dict[str, Any]):
        """Check for weak security configurations"""
        # Check for debug mode in production
        if config.get('debug', False):
            result.add_warning("Debug mode is enabled - should be disabled in production")

        # Check secret key strength
        if 'secret_key' in config:
            secret = config['secret_key']
            if isinstance(secret, str):
                if len(secret) < 32:
                    error = SecurityValidationError(
                        message="Secret key is too short (minimum 32 characters)",
                        threat_type="weak_secret",
                        context={**context, 'secret_length': len(secret)}
                    )
                    result.add_error(error)

                if secret in ['secret', 'password', 'admin', 'default']:
                    error = SecurityValidationError(
                        message="Secret key uses common/weak value",
                        threat_type="weak_secret",
                        context=context
                    )
                    result.add_error(error)

        # Check encryption settings
        if 'encryption' in config:
            encryption = config['encryption']
            if isinstance(encryption, dict):
                algorithm = encryption.get('algorithm', '').upper()
                weak_algorithms = ['MD5', 'SHA1', 'DES', 'RC4']
                if algorithm in weak_algorithms:
                    error = SecurityValidationError(
                        message=f"Weak encryption algorithm: {algorithm}",
                        threat_type="weak_encryption",
                        context={**context, 'algorithm': algorithm}
                    )
                    result.add_error(error)


# Factory function for creating configuration validation pipeline
def create_config_validation_pipeline(config_type: str = "general") -> 'ValidationPipeline':
    """
    Create a pre-configured validation pipeline for configuration

    Args:
        config_type: Type of configuration (general, database, security, logging)

    Returns:
        Configured ValidationPipeline
    """
    from ..framework.validation_pipeline import ValidationPipeline, PipelineStage

    pipeline = ValidationPipeline(f"config_validation_{config_type}")

    # Basic file validation
    pipeline.add_validator(
        ConfigFileValidator(),
        PipelineStage.TYPE_VALIDATION
    )

    # Specific validators based on type
    if config_type == "database":
        pipeline.add_validator(
            DatabaseConfigValidator(),
            PipelineStage.BUSINESS_VALIDATION
        )
    elif config_type == "logging":
        pipeline.add_validator(
            LoggingConfigValidator(),
            PipelineStage.BUSINESS_VALIDATION
        )
    elif config_type == "security":
        pipeline.add_validator(
            SecurityConfigValidator(),
            PipelineStage.SECURITY_VALIDATION
        )

    return pipeline