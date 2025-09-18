"""
Validation Decorators for SSA-24 Input Validation Framework

Provides easy-to-use decorators for function and method validation
"""

import functools
import inspect
from typing import Any, Dict, List, Optional, Union, Callable, get_type_hints
import logging

from ..framework.validator_base import AbstractValidator, ValidationResult
from ..framework.validation_pipeline import ValidationPipeline, PipelineMode
from ..exceptions.validation_exceptions import ValidationError, APIValidationError


def validate_input(*validators: AbstractValidator, pipeline_mode: PipelineMode = PipelineMode.COLLECT_ALL):
    """
    Decorator to validate function input parameters

    Args:
        *validators: Validators to apply to parameters
        pipeline_mode: How to handle multiple validation errors

    Usage:
        @validate_input(StringLengthValidator(max_length=100))
        def process_text(text: str):
            return text.upper()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Create validation pipeline
            pipeline = ValidationPipeline(
                name=f"{func.__name__}_input_validation",
                mode=pipeline_mode
            )

            # Add validators to pipeline
            for validator in validators:
                pipeline.add_validator(validator)

            # Validate each parameter
            validation_errors = []
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self':  # Skip self parameter
                    continue

                context = {
                    'function_name': func.__name__,
                    'parameter_name': param_name,
                    'parameter_type': sig.parameters[param_name].annotation
                }

                result = pipeline.validate(param_value, context)
                if not result.is_valid:
                    validation_errors.extend(result.errors)

                # Update parameter with sanitized value if available
                if result.sanitized_value is not None:
                    bound_args.arguments[param_name] = result.sanitized_value

            # Raise validation errors if any
            if validation_errors:
                raise APIValidationError(
                    message=f"Input validation failed for function {func.__name__}",
                    endpoint=func.__name__,
                    invalid_parameters=[error.context.get('parameter_name') for error in validation_errors],
                    context={'validation_errors': [error.to_dict() for error in validation_errors]}
                )

            # Call function with potentially sanitized arguments
            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def validate_output(validator: AbstractValidator, strict: bool = True):
    """
    Decorator to validate function output

    Args:
        validator: Validator to apply to return value
        strict: Whether to raise exception on validation failure

    Usage:
        @validate_output(StringLengthValidator(max_length=1000))
        def generate_report() -> str:
            return "Generated report content"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)

            # Validate output
            context = {
                'function_name': func.__name__,
                'output_validation': True
            }

            validation_result = validator.validate(result, context)

            if not validation_result.is_valid:
                if strict:
                    raise ValidationError(
                        message=f"Output validation failed for function {func.__name__}",
                        context={
                            'function_name': func.__name__,
                            'validation_errors': [error.to_dict() for error in validation_result.errors]
                        }
                    )
                else:
                    # Log warning but return original result
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Output validation failed for {func.__name__}: {validation_result.get_error_messages()}")

            # Return sanitized value if available and valid
            if validation_result.is_valid and validation_result.sanitized_value is not None:
                return validation_result.sanitized_value

            return result

        return wrapper
    return decorator


def validate_type(expected_type: Union[type, tuple], allow_none: bool = False):
    """
    Decorator to validate parameter types

    Args:
        expected_type: Expected type or tuple of types
        allow_none: Whether to allow None values

    Usage:
        @validate_type(str)
        def process_string(text):
            return text.lower()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate parameter types
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self':
                    continue

                if param_value is None and not allow_none:
                    raise ValidationError(
                        message=f"Parameter '{param_name}' cannot be None",
                        field_name=param_name,
                        validation_rule="not_none"
                    )

                if param_value is not None and not isinstance(param_value, expected_type):
                    expected_name = (
                        expected_type.__name__ if hasattr(expected_type, '__name__')
                        else str(expected_type)
                    )
                    raise ValidationError(
                        message=f"Parameter '{param_name}' must be of type {expected_name}, got {type(param_value).__name__}",
                        field_name=param_name,
                        invalid_value=param_value,
                        validation_rule="type_check"
                    )

            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_range(min_value: Optional[Union[int, float]] = None,
                  max_value: Optional[Union[int, float]] = None,
                  inclusive: bool = True):
    """
    Decorator to validate numeric parameter ranges

    Args:
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        inclusive: Whether bounds are inclusive

    Usage:
        @validate_range(min_value=0, max_value=100)
        def set_percentage(value):
            return f"Percentage: {value}%"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate parameter ranges
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self' or param_value is None:
                    continue

                if not isinstance(param_value, (int, float)):
                    continue  # Skip non-numeric parameters

                if min_value is not None:
                    if inclusive and param_value < min_value:
                        raise ValidationError(
                            message=f"Parameter '{param_name}' value {param_value} is below minimum {min_value}",
                            field_name=param_name,
                            invalid_value=param_value,
                            validation_rule="min_value"
                        )
                    elif not inclusive and param_value <= min_value:
                        raise ValidationError(
                            message=f"Parameter '{param_name}' value {param_value} must be greater than {min_value}",
                            field_name=param_name,
                            invalid_value=param_value,
                            validation_rule="min_value_exclusive"
                        )

                if max_value is not None:
                    if inclusive and param_value > max_value:
                        raise ValidationError(
                            message=f"Parameter '{param_name}' value {param_value} exceeds maximum {max_value}",
                            field_name=param_name,
                            invalid_value=param_value,
                            validation_rule="max_value"
                        )
                    elif not inclusive and param_value >= max_value:
                        raise ValidationError(
                            message=f"Parameter '{param_name}' value {param_value} must be less than {max_value}",
                            field_name=param_name,
                            invalid_value=param_value,
                            validation_rule="max_value_exclusive"
                        )

            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_length(min_length: Optional[int] = None,
                   max_length: Optional[int] = None):
    """
    Decorator to validate string/sequence parameter lengths

    Args:
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Usage:
        @validate_length(min_length=1, max_length=100)
        def process_name(name):
            return f"Hello, {name}!"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate parameter lengths
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self' or param_value is None:
                    continue

                if not hasattr(param_value, '__len__'):
                    continue  # Skip non-sequence parameters

                length = len(param_value)

                if min_length is not None and length < min_length:
                    raise ValidationError(
                        message=f"Parameter '{param_name}' length {length} is below minimum {min_length}",
                        field_name=param_name,
                        invalid_value=param_value,
                        validation_rule="min_length"
                    )

                if max_length is not None and length > max_length:
                    raise ValidationError(
                        message=f"Parameter '{param_name}' length {length} exceeds maximum {max_length}",
                        field_name=param_name,
                        invalid_value=param_value,
                        validation_rule="max_length"
                    )

            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_parameters(**param_validators):
    """
    Decorator to apply specific validators to specific parameters

    Args:
        **param_validators: Mapping of parameter names to validators

    Usage:
        @validate_parameters(
            email=EmailValidator(),
            age=RangeValidator(min_value=0, max_value=150)
        )
        def register_user(email, age, name):
            return f"Registered {name} with email {email}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate specific parameters
            validation_errors = []
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self':
                    continue

                if param_name in param_validators:
                    validator = param_validators[param_name]
                    context = {
                        'function_name': func.__name__,
                        'parameter_name': param_name
                    }

                    result = validator.validate(param_value, context)
                    if not result.is_valid:
                        validation_errors.extend(result.errors)

                    # Update parameter with sanitized value if available
                    if result.sanitized_value is not None:
                        bound_args.arguments[param_name] = result.sanitized_value

            # Raise validation errors if any
            if validation_errors:
                raise APIValidationError(
                    message=f"Parameter validation failed for function {func.__name__}",
                    endpoint=func.__name__,
                    invalid_parameters=[error.context.get('parameter_name') for error in validation_errors],
                    context={'validation_errors': [error.to_dict() for error in validation_errors]}
                )

            # Call function with potentially sanitized arguments
            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper
    return decorator


def auto_validate_types(func: Callable) -> Callable:
    """
    Decorator to automatically validate parameter types based on type hints

    Usage:
        @auto_validate_types
        def process_data(name: str, age: int, scores: List[float]):
            return f"{name} (age {age}) has scores: {scores}"
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Validate parameter types based on hints
        for param_name, param_value in bound_args.arguments.items():
            if param_name == 'self' or param_name not in type_hints:
                continue

            expected_type = type_hints[param_name]

            # Handle Optional types (Union with None)
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:
                # Check if it's Optional (Union with None)
                if type(None) in expected_type.__args__:
                    if param_value is None:
                        continue  # None is allowed
                    # Get the non-None type
                    non_none_types = [arg for arg in expected_type.__args__ if arg is not type(None)]
                    if len(non_none_types) == 1:
                        expected_type = non_none_types[0]

            # Basic type checking (can be extended for complex types)
            if not isinstance(param_value, expected_type):
                expected_name = getattr(expected_type, '__name__', str(expected_type))
                raise ValidationError(
                    message=f"Parameter '{param_name}' must be of type {expected_name}, got {type(param_value).__name__}",
                    field_name=param_name,
                    invalid_value=param_value,
                    validation_rule="auto_type_check"
                )

        return func(*args, **kwargs)

    return wrapper