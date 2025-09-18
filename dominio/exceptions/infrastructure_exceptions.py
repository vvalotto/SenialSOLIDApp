"""
Infrastructure Layer Specific Exceptions
SSA-23: Exception Handling Refactoring
"""

from typing import Any, Dict, Optional
from .base_exceptions import InfrastructureException


class ConfigurationException(InfrastructureException):
    """
    Configuration loading and validation errors

    Used when configuration files are missing, malformed,
    or contain invalid values that prevent system initialization.
    """

    def __init__(
        self,
        config_key: str,
        config_file: str = None,
        config_type: str = "yaml",
        **kwargs
    ):
        # Enrich context with configuration-specific information
        config_context = {
            "config_key": config_key,
            "config_file": config_file,
            "config_type": config_type,
            "operation_type": "configuration_loading"
        }

        context = kwargs.get('context', {})
        context.update(config_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', 'Error en configuración del sistema')
        kwargs.setdefault(
            'recovery_suggestion',
            f'Verifique el archivo de configuración {config_file or "principal"} y la clave {config_key}'
        )

        file_info = f" in {config_file}" if config_file else ""
        super().__init__(
            f"Configuration error: '{config_key}'{file_info}",
            **kwargs
        )


class DataAccessException(InfrastructureException):
    """
    File I/O and data access errors with retry context

    Used when file operations, database access, or external
    data sources fail due to I/O issues or connectivity problems.
    """

    def __init__(
        self,
        file_path: str,
        operation: str,
        retry_count: int = 0,
        max_retries: int = 3,
        **kwargs
    ):
        # Enrich context with data access-specific information
        data_access_context = {
            "file_path": file_path,
            "operation": operation,
            "retry_count": retry_count,
            "max_retries": max_retries,
            "operation_type": "data_access",
            "can_retry": retry_count < max_retries
        }

        # Add file system information if available
        try:
            import os
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                data_access_context.update({
                    "file_exists": True,
                    "file_size_bytes": stat_info.st_size,
                    "file_readable": os.access(file_path, os.R_OK),
                    "file_writable": os.access(file_path, os.W_OK)
                })
            else:
                data_access_context["file_exists"] = False
        except Exception:
            # Don't let file stat errors break exception creation
            pass

        context = kwargs.get('context', {})
        context.update(data_access_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', 'Error accediendo a archivo')
        kwargs.setdefault(
            'recovery_suggestion',
            'Verifique que el archivo existe, tiene permisos correctos y hay espacio en disco'
        )

        retry_info = f" (retry {retry_count}/{max_retries})" if retry_count > 0 else ""
        super().__init__(
            f"Data access failed: {operation} on '{file_path}'{retry_info}",
            **kwargs
        )


class NetworkException(InfrastructureException):
    """
    Network connectivity and communication errors

    Used when external service calls, API requests,
    or network operations fail due to connectivity issues.
    """

    def __init__(
        self,
        endpoint: str,
        operation: str,
        status_code: int = None,
        timeout_seconds: float = None,
        **kwargs
    ):
        # Enrich context with network-specific information
        network_context = {
            "endpoint": endpoint,
            "operation": operation,
            "status_code": status_code,
            "timeout_seconds": timeout_seconds,
            "operation_type": "network_communication"
        }

        # Add timing information if available
        if 'response_time_ms' in kwargs:
            network_context['response_time_ms'] = kwargs.pop('response_time_ms')

        context = kwargs.get('context', {})
        context.update(network_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', 'Error de conectividad')
        kwargs.setdefault(
            'recovery_suggestion',
            'Verifique la conexión a internet y disponibilidad del servicio'
        )

        status_info = f" (HTTP {status_code})" if status_code else ""
        timeout_info = f" after {timeout_seconds}s" if timeout_seconds else ""

        super().__init__(
            f"Network operation '{operation}' failed for {endpoint}{status_info}{timeout_info}",
            **kwargs
        )