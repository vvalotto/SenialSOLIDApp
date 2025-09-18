"""
SSA-24 Input Validation Framework

A comprehensive validation and sanitization framework for the SenialSOLID application.
Integrates with SSA-23 exception handling system and provides security-focused input validation.
"""

# Framework core
from .framework import (
    AbstractValidator,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    DataTypeValidator,
    RangeValidator,
    LengthValidator,
    ValidationPipeline,
    PipelineMode,
    PipelineStage,
    SanitizationEngine,
    SanitizationLevel,
    SanitizationStrategy,
    SanitizationRule,
    SanitizationResult
)

# Decorators
from .decorators import (
    validate_input,
    validate_output,
    validate_type,
    validate_range,
    validate_length,
    validate_parameters,
    auto_validate_types,
    sanitize_input,
    sanitize_output,
    auto_sanitize,
    sanitize_filename_param,
    sanitize_sql_params,
    sanitize_html_param,
    log_sanitization_events,
    conditional_sanitize
)

# Specialized validators
from .rules import (
    # Signal validation
    SignalParameterValidator,
    SignalDataValidator,
    SignalFormatValidator,
    SignalQualityValidator,
    create_signal_validation_pipeline,

    # File validation
    FileTypeValidator,
    FileSizeValidator,
    FileContentValidator,
    SignalFileValidator,
    create_file_validation_pipeline,

    # User input validation
    StringInputValidator,
    SQLInjectionValidator,
    EmailValidator,
    NumericInputValidator,
    DateTimeValidator,
    PasswordValidator,
    create_user_input_validation_pipeline,

    # File path validation
    FilePathValidator,

    # API validation
    APIParameterValidator,
    JSONSchemaValidator,
    RateLimitValidator,
    IPWhitelistValidator,
    APISecurityValidator,
    create_api_validation_pipeline,

    # Configuration validation
    ConfigParameterValidator,
    ConfigFileValidator,
    DatabaseConfigValidator,
    LoggingConfigValidator,
    SecurityConfigValidator,
    create_config_validation_pipeline
)

# Exceptions
from .exceptions import (
    ValidationError,
    SanitizationError,
    SecurityValidationError,
    FileValidationError,
    SignalValidationError,
    ConfigValidationError,
    APIValidationError,
    ValidationPipelineError
)

__version__ = "1.0.0"
__author__ = "SenialSOLID Team"
__description__ = "Input Validation Framework with Security Focus"

__all__ = [
    # Core framework
    'AbstractValidator',
    'ValidationResult',
    'ValidationRule',
    'ValidationSeverity',
    'DataTypeValidator',
    'RangeValidator',
    'LengthValidator',
    'ValidationPipeline',
    'PipelineMode',
    'PipelineStage',
    'SanitizationEngine',
    'SanitizationLevel',
    'SanitizationStrategy',
    'SanitizationRule',
    'SanitizationResult',

    # Decorators
    'validate_input',
    'validate_output',
    'validate_type',
    'validate_range',
    'validate_length',
    'validate_parameters',
    'auto_validate_types',
    'sanitize_input',
    'sanitize_output',
    'auto_sanitize',
    'sanitize_filename_param',
    'sanitize_sql_params',
    'sanitize_html_param',
    'log_sanitization_events',
    'conditional_sanitize',

    # Signal validation
    'SignalParameterValidator',
    'SignalDataValidator',
    'SignalFormatValidator',
    'SignalQualityValidator',
    'create_signal_validation_pipeline',

    # File validation
    'FileTypeValidator',
    'FileSizeValidator',
    'FileContentValidator',
    'SignalFileValidator',
    'create_file_validation_pipeline',

    # User input validation
    'StringInputValidator',
    'SQLInjectionValidator',
    'EmailValidator',
    'NumericInputValidator',
    'DateTimeValidator',
    'PasswordValidator',
    'create_user_input_validation_pipeline',

    # File path validation
    'FilePathValidator',

    # API validation
    'APIParameterValidator',
    'JSONSchemaValidator',
    'RateLimitValidator',
    'IPWhitelistValidator',
    'APISecurityValidator',
    'create_api_validation_pipeline',

    # Configuration validation
    'ConfigParameterValidator',
    'ConfigFileValidator',
    'DatabaseConfigValidator',
    'LoggingConfigValidator',
    'SecurityConfigValidator',
    'create_config_validation_pipeline',

    # Exceptions
    'ValidationError',
    'SanitizationError',
    'SecurityValidationError',
    'FileValidationError',
    'SignalValidationError',
    'ConfigValidationError',
    'APIValidationError',
    'ValidationPipelineError'
]


def create_default_pipeline(name: str = "default") -> ValidationPipeline:
    """
    Create a default validation pipeline with common validators

    Args:
        name: Name for the pipeline

    Returns:
        Configured ValidationPipeline
    """
    pipeline = ValidationPipeline(name=name, mode=PipelineMode.COLLECT_ALL)
    return pipeline


def create_strict_sanitizer() -> SanitizationEngine:
    """
    Create a strict sanitization engine for security-critical operations

    Returns:
        SanitizationEngine configured for strict security
    """
    return SanitizationEngine(level=SanitizationLevel.STRICT)


def create_moderate_sanitizer() -> SanitizationEngine:
    """
    Create a moderate sanitization engine for general use

    Returns:
        SanitizationEngine configured for moderate security
    """
    return SanitizationEngine(level=SanitizationLevel.MODERATE)