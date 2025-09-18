"""
Validation Exceptions for SSA-24 Input Validation Framework
Integrates with SSA-23 Exception Handling System
"""

from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dominio.exceptions.base_exceptions import DomainException, PresentationException


class ValidationError(DomainException):
    """
    Base exception for validation errors

    Raised when input data fails validation rules
    """

    def __init__(
        self,
        message: str,
        field_name: str = None,
        invalid_value: Any = None,
        validation_rule: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'field_name': field_name,
            'invalid_value': str(invalid_value) if invalid_value is not None else None,
            'validation_rule': validation_rule,
            'validation_type': 'input_validation'
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'Los datos proporcionados no son válidos')
        kwargs.setdefault('recovery_suggestion', 'Verifique el formato y valores de los datos ingresados')
        kwargs.setdefault('error_code', f'VALIDATION_ERROR_{field_name or "UNKNOWN"}')

        super().__init__(message, **kwargs)


class SanitizationError(ValidationError):
    """
    Exception raised when data sanitization fails

    Indicates that input data could not be safely sanitized
    """

    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('user_message', 'Error al procesar los datos de entrada')
        kwargs.setdefault('recovery_suggestion', 'Los datos contienen caracteres no válidos')
        kwargs.setdefault('error_code', 'SANITIZATION_ERROR')
        super().__init__(message, **kwargs)


class SecurityValidationError(ValidationError):
    """
    Exception for security-related validation failures

    Raised when input data contains potential security threats
    """

    def __init__(
        self,
        message: str,
        threat_type: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'threat_type': threat_type,
            'security_level': 'HIGH',
            'requires_immediate_attention': True
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'Los datos contienen contenido no permitido')
        kwargs.setdefault('recovery_suggestion', 'Modifique los datos para cumplir con los requisitos de seguridad')
        kwargs.setdefault('error_code', f'SECURITY_VALIDATION_{threat_type or "UNKNOWN"}')

        super().__init__(message, **kwargs)


class FileValidationError(ValidationError):
    """
    Exception for file validation failures

    Raised when uploaded files fail validation checks
    """

    def __init__(
        self,
        message: str,
        filename: str = None,
        file_size: int = None,
        file_type: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'filename': filename,
            'file_size': file_size,
            'file_type': file_type,
            'validation_category': 'file_upload'
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'El archivo no cumple con los requisitos')
        kwargs.setdefault('recovery_suggestion', 'Verifique el tipo, tamaño y contenido del archivo')
        kwargs.setdefault('error_code', f'FILE_VALIDATION_{filename or "UNKNOWN"}')

        super().__init__(message, **kwargs)


class SignalValidationError(ValidationError):
    """
    Exception for signal data validation failures

    Raised when signal data doesn't meet technical specifications
    """

    def __init__(
        self,
        message: str,
        signal_parameter: str = None,
        expected_range: tuple = None,
        actual_value: Any = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'signal_parameter': signal_parameter,
            'expected_range': expected_range,
            'actual_value': actual_value,
            'validation_category': 'signal_processing'
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'Los parámetros de la señal están fuera de rango')
        kwargs.setdefault('recovery_suggestion', 'Ajuste los parámetros de la señal a los rangos válidos')
        kwargs.setdefault('error_code', f'SIGNAL_VALIDATION_{signal_parameter or "UNKNOWN"}')

        super().__init__(message, **kwargs)


class ConfigValidationError(ValidationError):
    """
    Exception for configuration validation failures

    Raised when configuration parameters are invalid
    """

    def __init__(
        self,
        message: str,
        config_key: str = None,
        config_section: str = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'config_key': config_key,
            'config_section': config_section,
            'validation_category': 'configuration'
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'Error en la configuración del sistema')
        kwargs.setdefault('recovery_suggestion', 'Verifique la configuración del sistema')
        kwargs.setdefault('error_code', f'CONFIG_VALIDATION_{config_key or "UNKNOWN"}')

        super().__init__(message, **kwargs)


class APIValidationError(PresentationException):
    """
    Exception for API input validation failures

    Raised when API requests contain invalid data
    """

    def __init__(
        self,
        message: str,
        endpoint: str = None,
        request_method: str = None,
        invalid_parameters: list = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'endpoint': endpoint,
            'request_method': request_method,
            'invalid_parameters': invalid_parameters or [],
            'validation_category': 'api_request'
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'Parámetros de solicitud inválidos')
        kwargs.setdefault('recovery_suggestion', 'Verifique la documentación de la API y los parámetros enviados')
        kwargs.setdefault('error_code', f'API_VALIDATION_{endpoint or "UNKNOWN"}')

        super().__init__(message, **kwargs)


class ValidationPipelineError(ValidationError):
    """
    Exception for validation pipeline failures

    Raised when the validation pipeline encounters an error
    """

    def __init__(
        self,
        message: str,
        pipeline_stage: str = None,
        failed_validators: list = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        context.update({
            'pipeline_stage': pipeline_stage,
            'failed_validators': failed_validators or [],
            'validation_category': 'pipeline_execution'
        })

        kwargs['context'] = context
        kwargs.setdefault('user_message', 'Error en el proceso de validación')
        kwargs.setdefault('recovery_suggestion', 'Contacte al administrador del sistema')
        kwargs.setdefault('error_code', f'PIPELINE_ERROR_{pipeline_stage or "UNKNOWN"}')

        super().__init__(message, **kwargs)