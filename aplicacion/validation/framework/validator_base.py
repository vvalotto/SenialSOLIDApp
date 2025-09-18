"""
Base Validator Classes for SSA-24 Input Validation Framework
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
import logging

from ..exceptions.validation_exceptions import ValidationError, SecurityValidationError


class ValidationResult:
    """
    Result of a validation operation

    Contains information about validation success/failure and any errors found
    """

    def __init__(
        self,
        is_valid: bool,
        errors: List[ValidationError] = None,
        warnings: List[str] = None,
        sanitized_value: Any = None,
        metadata: Dict[str, Any] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.sanitized_value = sanitized_value
        self.metadata = metadata or {}

    def add_error(self, error: ValidationError):
        """Add a validation error"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a validation warning"""
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return len(self.warnings) > 0

    def get_error_messages(self) -> List[str]:
        """Get list of error messages"""
        return [error.message for error in self.errors]

    def get_user_error_messages(self) -> List[str]:
        """Get list of user-friendly error messages"""
        return [error.user_message for error in self.errors]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'is_valid': self.is_valid,
            'errors': [error.to_dict() for error in self.errors],
            'warnings': self.warnings,
            'metadata': self.metadata
        }


class ValidationSeverity(Enum):
    """Severity levels for validation rules"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationRule:
    """
    Represents a single validation rule
    """

    def __init__(
        self,
        name: str,
        description: str,
        severity: ValidationSeverity = ValidationSeverity.MEDIUM,
        enabled: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.severity = severity
        self.enabled = enabled
        self.metadata = metadata or {}


class AbstractValidator(ABC):
    """
    Abstract base class for all validators

    Defines the contract that all validators must implement
    """

    def __init__(
        self,
        name: str,
        description: str = None,
        enabled: bool = True,
        rules: List[ValidationRule] = None
    ):
        self.name = name
        self.description = description or f"Validator: {name}"
        self.enabled = enabled
        self.rules = rules or []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """
        Validate a value according to the validator's rules

        Args:
            value: The value to validate
            context: Optional context information for validation

        Returns:
            ValidationResult object with validation outcome
        """
        pass

    def is_enabled(self) -> bool:
        """Check if validator is enabled"""
        return self.enabled

    def enable(self):
        """Enable the validator"""
        self.enabled = True

    def disable(self):
        """Disable the validator"""
        self.enabled = False

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a validation rule by name"""
        initial_count = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        return len(self.rules) < initial_count

    def get_rule(self, rule_name: str) -> Optional[ValidationRule]:
        """Get a validation rule by name"""
        return next((rule for rule in self.rules if rule.name == rule_name), None)

    def get_enabled_rules(self) -> List[ValidationRule]:
        """Get list of enabled validation rules"""
        return [rule for rule in self.rules if rule.enabled]

    def _create_validation_error(
        self,
        message: str,
        field_name: str = None,
        invalid_value: Any = None,
        validation_rule: str = None,
        **kwargs
    ) -> ValidationError:
        """Helper method to create validation errors"""
        return ValidationError(
            message=message,
            field_name=field_name,
            invalid_value=invalid_value,
            validation_rule=validation_rule,
            **kwargs
        )

    def _create_security_error(
        self,
        message: str,
        threat_type: str = None,
        **kwargs
    ) -> SecurityValidationError:
        """Helper method to create security validation errors"""
        return SecurityValidationError(
            message=message,
            threat_type=threat_type,
            **kwargs
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"enabled={self.enabled}, "
            f"rules_count={len(self.rules)})"
        )


class DataTypeValidator(AbstractValidator):
    """
    Base class for data type specific validators
    """

    def __init__(
        self,
        name: str,
        expected_type: Union[type, Tuple[type, ...]],
        allow_none: bool = False,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.expected_type = expected_type
        self.allow_none = allow_none

    def _validate_type(self, value: Any) -> ValidationResult:
        """Validate that value is of expected type"""
        result = ValidationResult(is_valid=True)

        if value is None:
            if not self.allow_none:
                error = self._create_validation_error(
                    message=f"Value cannot be None",
                    validation_rule="type_check"
                )
                result.add_error(error)
            return result

        if not isinstance(value, self.expected_type):
            expected_type_name = (
                self.expected_type.__name__
                if hasattr(self.expected_type, '__name__')
                else str(self.expected_type)
            )
            error = self._create_validation_error(
                message=f"Expected {expected_type_name}, got {type(value).__name__}",
                invalid_value=value,
                validation_rule="type_check"
            )
            result.add_error(error)

        return result


class RangeValidator(AbstractValidator):
    """
    Validator for numeric ranges
    """

    def __init__(
        self,
        name: str,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        inclusive: bool = True,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.inclusive = inclusive

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate that value is within specified range"""
        result = ValidationResult(is_valid=True, sanitized_value=value)

        if not isinstance(value, (int, float)):
            error = self._create_validation_error(
                message=f"Value must be numeric, got {type(value).__name__}",
                invalid_value=value,
                validation_rule="numeric_type"
            )
            result.add_error(error)
            return result

        if self.min_value is not None:
            if self.inclusive and value < self.min_value:
                error = self._create_validation_error(
                    message=f"Value {value} is below minimum {self.min_value}",
                    invalid_value=value,
                    validation_rule="min_value"
                )
                result.add_error(error)
            elif not self.inclusive and value <= self.min_value:
                error = self._create_validation_error(
                    message=f"Value {value} must be greater than {self.min_value}",
                    invalid_value=value,
                    validation_rule="min_value_exclusive"
                )
                result.add_error(error)

        if self.max_value is not None:
            if self.inclusive and value > self.max_value:
                error = self._create_validation_error(
                    message=f"Value {value} exceeds maximum {self.max_value}",
                    invalid_value=value,
                    validation_rule="max_value"
                )
                result.add_error(error)
            elif not self.inclusive and value >= self.max_value:
                error = self._create_validation_error(
                    message=f"Value {value} must be less than {self.max_value}",
                    invalid_value=value,
                    validation_rule="max_value_exclusive"
                )
                result.add_error(error)

        return result


class LengthValidator(AbstractValidator):
    """
    Validator for string/sequence length
    """

    def __init__(
        self,
        name: str,
        min_length: int = None,
        max_length: int = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate that value length is within specified bounds"""
        result = ValidationResult(is_valid=True, sanitized_value=value)

        if not hasattr(value, '__len__'):
            error = self._create_validation_error(
                message=f"Value must have length property, got {type(value).__name__}",
                invalid_value=value,
                validation_rule="length_capability"
            )
            result.add_error(error)
            return result

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            error = self._create_validation_error(
                message=f"Length {length} is below minimum {self.min_length}",
                invalid_value=value,
                validation_rule="min_length"
            )
            result.add_error(error)

        if self.max_length is not None and length > self.max_length:
            error = self._create_validation_error(
                message=f"Length {length} exceeds maximum {self.max_length}",
                invalid_value=value,
                validation_rule="max_length"
            )
            result.add_error(error)

        return result