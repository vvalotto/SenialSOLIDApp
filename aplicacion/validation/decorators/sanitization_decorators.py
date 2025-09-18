"""
Sanitization Decorators for SSA-24 Input Validation Framework

Provides easy-to-use decorators for automatic data sanitization
"""

import functools
import inspect
from typing import Any, Dict, List, Optional, Union, Callable
import logging

from ..framework.sanitization_engine import SanitizationEngine, SanitizationLevel
from ..exceptions.validation_exceptions import SanitizationError


def sanitize_input(
    level: SanitizationLevel = SanitizationLevel.MODERATE,
    categories: List[str] = None,
    custom_engine: SanitizationEngine = None
):
    """
    Decorator to automatically sanitize function input parameters

    Args:
        level: Sanitization level to apply
        categories: Specific rule categories to apply
        custom_engine: Custom sanitization engine to use

    Usage:
        @sanitize_input(level=SanitizationLevel.STRICT)
        def process_user_input(text: str, html_content: str):
            return f"Processed: {text}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use custom engine or create default
            engine = custom_engine or SanitizationEngine(level)
            logger = logging.getLogger(f"{__name__}.sanitize_input")

            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Sanitize each parameter
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self':  # Skip self parameter
                    continue

                if isinstance(param_value, str):
                    try:
                        result = engine.sanitize(param_value, categories)
                        if result.was_modified:
                            bound_args.arguments[param_name] = result.sanitized_value
                            logger.info(f"Sanitized parameter '{param_name}' in function {func.__name__}")

                        if result.has_security_issues():
                            logger.warning(f"Security issues detected in parameter '{param_name}': {result.security_issues}")

                    except Exception as e:
                        raise SanitizationError(
                            message=f"Failed to sanitize parameter '{param_name}' in function {func.__name__}",
                            context={
                                'function_name': func.__name__,
                                'parameter_name': param_name,
                                'original_value': str(param_value)[:100]
                            },
                            cause=e
                        )

            # Call function with sanitized arguments
            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def sanitize_output(
    level: SanitizationLevel = SanitizationLevel.MODERATE,
    categories: List[str] = None
):
    """
    Decorator to sanitize function output

    Args:
        level: Sanitization level to apply
        categories: Specific rule categories to apply

    Usage:
        @sanitize_output(level=SanitizationLevel.STRICT)
        def generate_html_content() -> str:
            return "<script>alert('xss')</script>Safe content"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)

            # Sanitize output if it's a string
            if isinstance(result, str):
                engine = SanitizationEngine(level)
                try:
                    sanitization_result = engine.sanitize(result, categories)
                    if sanitization_result.was_modified:
                        logger = logging.getLogger(f"{__name__}.sanitize_output")
                        logger.info(f"Sanitized output from function {func.__name__}")

                    return sanitization_result.sanitized_value

                except Exception as e:
                    raise SanitizationError(
                        message=f"Failed to sanitize output from function {func.__name__}",
                        context={
                            'function_name': func.__name__,
                            'output_preview': str(result)[:100]
                        },
                        cause=e
                    )

            return result

        return wrapper
    return decorator


def auto_sanitize(
    string_params: bool = True,
    level: SanitizationLevel = SanitizationLevel.MODERATE,
    skip_params: List[str] = None
):
    """
    Decorator to automatically sanitize string parameters

    Args:
        string_params: Whether to sanitize string parameters
        level: Sanitization level to apply
        skip_params: Parameter names to skip sanitization

    Usage:
        @auto_sanitize(skip_params=['password'])
        def create_user(username: str, email: str, password: str):
            return f"Created user: {username}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not string_params:
                return func(*args, **kwargs)

            skip_params_set = set(skip_params or [])
            engine = SanitizationEngine(level)
            logger = logging.getLogger(f"{__name__}.auto_sanitize")

            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Auto-sanitize string parameters
            for param_name, param_value in bound_args.arguments.items():
                if (param_name == 'self' or
                    param_name in skip_params_set or
                    not isinstance(param_value, str)):
                    continue

                try:
                    result = engine.sanitize(param_value)
                    if result.was_modified:
                        bound_args.arguments[param_name] = result.sanitized_value
                        logger.debug(f"Auto-sanitized parameter '{param_name}' in function {func.__name__}")

                except Exception as e:
                    logger.warning(f"Auto-sanitization failed for parameter '{param_name}': {str(e)}")
                    # Continue with original value if sanitization fails

            # Call function with potentially sanitized arguments
            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def sanitize_filename_param(param_name: str = 'filename'):
    """
    Decorator to sanitize filename parameters

    Args:
        param_name: Name of the parameter containing the filename

    Usage:
        @sanitize_filename_param('file_name')
        def save_file(file_name: str, content: str):
            return f"Saved to {file_name}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Sanitize filename parameter
            if param_name in bound_args.arguments:
                filename = bound_args.arguments[param_name]
                if isinstance(filename, str):
                    engine = SanitizationEngine()
                    sanitized_filename = engine.sanitize_filename(filename)
                    bound_args.arguments[param_name] = sanitized_filename

                    if sanitized_filename != filename:
                        logger = logging.getLogger(f"{__name__}.sanitize_filename_param")
                        logger.info(f"Sanitized filename parameter '{param_name}' in function {func.__name__}")

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def sanitize_sql_params(*param_names: str):
    """
    Decorator to sanitize SQL identifier parameters

    Args:
        *param_names: Names of parameters containing SQL identifiers

    Usage:
        @sanitize_sql_params('table_name', 'column_name')
        def build_query(table_name: str, column_name: str):
            return f"SELECT {column_name} FROM {table_name}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            engine = SanitizationEngine()
            logger = logging.getLogger(f"{__name__}.sanitize_sql_params")

            # Sanitize SQL identifier parameters
            for param_name in param_names:
                if param_name in bound_args.arguments:
                    identifier = bound_args.arguments[param_name]
                    if isinstance(identifier, str):
                        sanitized_identifier = engine.sanitize_sql_identifier(identifier)
                        bound_args.arguments[param_name] = sanitized_identifier

                        if sanitized_identifier != identifier:
                            logger.info(f"Sanitized SQL identifier parameter '{param_name}' in function {func.__name__}")

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def sanitize_html_param(*param_names: str, escape_quotes: bool = True):
    """
    Decorator to sanitize HTML content in specific parameters

    Args:
        *param_names: Names of parameters containing HTML content
        escape_quotes: Whether to escape quotes

    Usage:
        @sanitize_html_param('content', 'description')
        def render_content(title: str, content: str, description: str):
            return f"<h1>{title}</h1><div>{content}</div><p>{description}</p>"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            engine = SanitizationEngine(SanitizationLevel.STRICT)
            logger = logging.getLogger(f"{__name__}.sanitize_html_param")

            # Sanitize HTML parameters
            for param_name in param_names:
                if param_name in bound_args.arguments:
                    html_content = bound_args.arguments[param_name]
                    if isinstance(html_content, str):
                        try:
                            result = engine.sanitize(html_content, categories=['html', 'xss'])
                            bound_args.arguments[param_name] = result.sanitized_value

                            if result.was_modified:
                                logger.info(f"Sanitized HTML parameter '{param_name}' in function {func.__name__}")

                        except Exception as e:
                            logger.warning(f"HTML sanitization failed for parameter '{param_name}': {str(e)}")

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def log_sanitization_events(log_level: str = 'INFO'):
    """
    Decorator to log sanitization events for monitoring

    Args:
        log_level: Logging level for sanitization events

    Usage:
        @log_sanitization_events(log_level='DEBUG')
        @auto_sanitize()
        def process_data(data: str):
            return data.upper()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"{__name__}.sanitization_monitor")

            # Log function entry
            logger.log(
                getattr(logging, log_level.upper(), logging.INFO),
                f"Starting sanitization monitoring for function {func.__name__}"
            )

            # Execute function (with sanitization from other decorators)
            result = func(*args, **kwargs)

            # Log function exit
            logger.log(
                getattr(logging, log_level.upper(), logging.INFO),
                f"Completed sanitization monitoring for function {func.__name__}"
            )

            return result

        return wrapper
    return decorator


def conditional_sanitize(condition_func: Callable, level: SanitizationLevel = SanitizationLevel.MODERATE):
    """
    Decorator to conditionally apply sanitization based on a condition function

    Args:
        condition_func: Function that returns True if sanitization should be applied
        level: Sanitization level to apply when condition is met

    Usage:
        def should_sanitize(user_role):
            return user_role != 'admin'

        @conditional_sanitize(lambda *args, **kwargs: should_sanitize(kwargs.get('user_role')))
        def process_input(data: str, user_role: str):
            return f"Processed: {data}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check condition
            should_sanitize = condition_func(*args, **kwargs)

            if should_sanitize:
                # Apply sanitization
                engine = SanitizationEngine(level)
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Sanitize string parameters
                for param_name, param_value in bound_args.arguments.items():
                    if param_name != 'self' and isinstance(param_value, str):
                        result = engine.sanitize(param_value)
                        if result.was_modified:
                            bound_args.arguments[param_name] = result.sanitized_value

                return func(*bound_args.args, **bound_args.kwargs)
            else:
                # Skip sanitization
                return func(*args, **kwargs)

        return wrapper
    return decorator