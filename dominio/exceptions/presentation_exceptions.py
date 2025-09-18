"""
Presentation Layer Specific Exceptions
SSA-23: Exception Handling Refactoring
"""

from typing import Any, Dict, Optional
from .base_exceptions import PresentationException


class WebException(PresentationException):
    """
    Web layer errors with HTTP context and request information

    Used when web requests fail due to validation errors,
    authentication issues, or request processing problems.
    """

    def __init__(
        self,
        endpoint: str,
        http_status: int = 500,
        request_method: str = "unknown",
        request_id: str = None,
        user_id: str = None,
        **kwargs
    ):
        # Enrich context with web-specific information
        web_context = {
            "endpoint": endpoint,
            "http_status": http_status,
            "request_method": request_method,
            "request_id": request_id,
            "user_id": user_id,
            "operation_type": "web_request"
        }

        # Add request timing if available
        if 'request_duration_ms' in kwargs:
            web_context['request_duration_ms'] = kwargs.pop('request_duration_ms')

        context = kwargs.get('context', {})
        context.update(web_context)
        kwargs['context'] = context

        # Set user messages based on HTTP status
        if http_status == 400:
            kwargs.setdefault('user_message', 'Datos de entrada inválidos')
            kwargs.setdefault('recovery_suggestion', 'Verifique los datos ingresados')
        elif http_status == 401:
            kwargs.setdefault('user_message', 'Acceso no autorizado')
            kwargs.setdefault('recovery_suggestion', 'Inicie sesión para continuar')
        elif http_status == 403:
            kwargs.setdefault('user_message', 'Acceso prohibido')
            kwargs.setdefault('recovery_suggestion', 'No tiene permisos para esta operación')
        elif http_status == 404:
            kwargs.setdefault('user_message', 'Página no encontrada')
            kwargs.setdefault('recovery_suggestion', 'Verifique la URL o navegue desde el menú principal')
        elif http_status >= 500:
            kwargs.setdefault('user_message', 'Error interno del servidor')
            kwargs.setdefault('recovery_suggestion', 'Intente nuevamente en unos momentos')
        else:
            kwargs.setdefault('user_message', 'Error en la aplicación web')
            kwargs.setdefault('recovery_suggestion', 'Intente nuevamente o contacte soporte')

        request_info = f"{request_method} {endpoint}" if request_method != "unknown" else endpoint
        super().__init__(
            f"Web error: {request_info} (HTTP {http_status})",
            **kwargs
        )


class ConsoleException(PresentationException):
    """
    Console interface errors with command and user context

    Used when console commands fail due to invalid input,
    command parsing errors, or execution problems.
    """

    def __init__(
        self,
        command: str,
        command_args: list = None,
        user_input: str = None,
        **kwargs
    ):
        # Enrich context with console-specific information
        console_context = {
            "command": command,
            "command_args": command_args or [],
            "user_input": user_input[:100] if user_input else None,  # Limit length
            "operation_type": "console_command"
        }

        context = kwargs.get('context', {})
        context.update(console_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', f'Error ejecutando comando: {command}')
        kwargs.setdefault(
            'recovery_suggestion',
            f'Verifique la sintaxis del comando {command} y los parámetros'
        )

        args_info = f" with args {command_args}" if command_args else ""
        super().__init__(
            f"Console command failed: {command}{args_info}",
            **kwargs
        )