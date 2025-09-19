"""
SSA-26 Validation Error Bridge
Integration bridge between SSA-24 validation and SSA-26 academic error messaging

This module bridges the SSA-24 ValidationResult with the SSA-26 AcademicErrorMessageFormatter
to provide seamless educational error messaging throughout the application.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    # Import SSA-24 validation components
    from aplicacion.validation.framework.validator_base import ValidationResult
    from aplicacion.validation.framework.security_validator import SecurityValidationResult
    SSA24_AVAILABLE = True
except ImportError:
    # Fallback for when SSA-24 is not available
    SSA24_AVAILABLE = False
    ValidationResult = None
    SecurityValidationResult = None

# Import SSA-26 error messaging
from dominio.patterns.messaging.user_message_formatter import (
    AcademicErrorMessageFormatter,
    AcademicErrorMessage,
    ErrorSeverity,
    ErrorCategory
)


@dataclass
class ValidationErrorContext:
    """Context information for validation errors"""
    field_name: str
    field_value: Any
    validation_type: str
    constraint_violated: str
    additional_details: Optional[Dict] = None


class SSA24ToSSA26Bridge:
    """
    Bridge between SSA-24 validation results and SSA-26 academic error messaging

    This class converts SSA-24 ValidationResult objects into SSA-26 AcademicErrorMessage
    objects, providing educational error messages for validation failures.

    Examples:
        >>> bridge = SSA24ToSSA26Bridge()
        >>> validation_result = some_validator.validate(value)
        >>> if not validation_result.is_valid:
        ...     error_message = bridge.convert_validation_result(
        ...         validation_result,
        ...         field_name="frequency",
        ...         field_value=75000
        ...     )
        ...     print(error_message.user_message)
    """

    def __init__(self, language: str = "es", educational_mode: bool = True):
        """
        Initialize the bridge

        Args:
            language: Language for error messages ("es" or "en")
            educational_mode: Whether to include educational tips
        """
        self.formatter = AcademicErrorMessageFormatter(
            language=language,
            educational_mode=educational_mode
        )
        self.ssa24_available = SSA24_AVAILABLE

    def convert_validation_result(
        self,
        validation_result: Any,  # ValidationResult when SSA24 available
        field_name: str,
        field_value: Any,
        context: Optional[ValidationErrorContext] = None
    ) -> Optional[AcademicErrorMessage]:
        """
        Convert SSA-24 ValidationResult to SSA-26 AcademicErrorMessage

        Args:
            validation_result: The SSA-24 ValidationResult object
            field_name: Name of the field that was validated
            field_value: The value that was validated
            context: Additional context for the validation error

        Returns:
            AcademicErrorMessage if validation failed, None if validation passed
        """
        if not self.ssa24_available or validation_result is None:
            return self._create_fallback_error(field_name, field_value, "SSA-24 not available")

        # If validation passed, no error message needed
        if hasattr(validation_result, 'is_valid') and validation_result.is_valid:
            return None

        # Extract error information from SSA-24 ValidationResult
        errors = getattr(validation_result, 'errors', [])
        if not errors:
            # Generic validation failure
            return self.formatter.format_validation_error(
                field=field_name,
                value=field_value,
                constraint="validation_failed",
                details={"message": "Unknown validation error"}
            )

        # Process the first error (most common case)
        primary_error = errors[0] if errors else {}
        error_type = primary_error.get('type', 'unknown')
        error_message = primary_error.get('message', 'Validation failed')

        # Map SSA-24 error types to constraint types
        constraint = self._map_error_type_to_constraint(error_type, field_name, field_value)

        # Create detailed context
        details = {
            'ssa24_error_type': error_type,
            'ssa24_error_message': error_message,
            'all_errors': errors,
            'field_context': context.__dict__ if context else {}
        }

        return self.formatter.format_validation_error(
            field=field_name,
            value=field_value,
            constraint=constraint,
            details=details
        )

    def convert_security_validation_result(
        self,
        security_result: Any,  # SecurityValidationResult when SSA24 available
        input_content: str,
        context: Optional[Dict] = None
    ) -> Optional[AcademicErrorMessage]:
        """
        Convert SSA-24 SecurityValidationResult to SSA-26 AcademicErrorMessage

        Args:
            security_result: The SSA-24 SecurityValidationResult object
            input_content: The content that was validated for security
            context: Additional context for the security validation

        Returns:
            AcademicErrorMessage if security threats detected, None if content is safe
        """
        if not self.ssa24_available or security_result is None:
            return self._create_fallback_security_error(input_content, "SSA-24 not available")

        # If security validation passed, no error message needed
        if hasattr(security_result, 'is_safe') and security_result.is_safe:
            return None

        # Extract security threat information
        threats = getattr(security_result, 'threats_detected', [])
        if not threats:
            # Generic security failure
            return self.formatter.format_security_error(
                attack_type="unknown",
                blocked_content=input_content[:50] + "..." if len(input_content) > 50 else input_content,
                context=context
            )

        # Process the primary threat
        primary_threat = threats[0] if threats else {}
        threat_type = primary_threat.get('type', 'unknown')

        # Map SSA-24 threat types to SSA-26 attack types
        attack_type = self._map_threat_type_to_attack_type(threat_type)

        return self.formatter.format_security_error(
            attack_type=attack_type,
            blocked_content=input_content[:100] + "..." if len(input_content) > 100 else input_content,
            context={
                'ssa24_threat_type': threat_type,
                'all_threats': threats,
                'additional_context': context or {}
            }
        )

    def convert_multiple_validation_results(
        self,
        validation_results: List[Dict[str, Any]],
        context: Optional[Dict] = None
    ) -> List[AcademicErrorMessage]:
        """
        Convert multiple SSA-24 validation results to SSA-26 error messages

        Args:
            validation_results: List of validation result dictionaries
            context: Additional context for all validations

        Returns:
            List of AcademicErrorMessage objects for all validation failures
        """
        error_messages = []

        for result_info in validation_results:
            validation_result = result_info.get('result')
            field_name = result_info.get('field_name', 'unknown')
            field_value = result_info.get('field_value', '')

            error_message = self.convert_validation_result(
                validation_result=validation_result,
                field_name=field_name,
                field_value=field_value,
                context=ValidationErrorContext(
                    field_name=field_name,
                    field_value=field_value,
                    validation_type=result_info.get('validation_type', 'unknown'),
                    constraint_violated=result_info.get('constraint', 'unknown'),
                    additional_details=context
                )
            )

            if error_message:
                error_messages.append(error_message)

        return error_messages

    def _map_error_type_to_constraint(self, error_type: str, field_name: str, field_value: Any) -> str:
        """
        Map SSA-24 error types to SSA-26 constraint types

        Args:
            error_type: The SSA-24 error type
            field_name: The field that failed validation
            field_value: The value that failed validation

        Returns:
            Constraint type string for SSA-26 formatting
        """
        # Common SSA-24 to SSA-26 error type mappings
        error_mappings = {
            'range_error': 'out_of_range',
            'length_error': 'too_short' if len(str(field_value)) < 5 else 'too_long',
            'type_error': 'invalid_type',
            'format_error': 'invalid_format',
            'required_error': 'required_field',
            'pattern_error': 'pattern_mismatch',
            'min_value_error': 'out_of_range',
            'max_value_error': 'out_of_range',
            'min_length_error': 'too_short',
            'max_length_error': 'too_long'
        }

        return error_mappings.get(error_type, 'validation_failed')

    def _map_threat_type_to_attack_type(self, threat_type: str) -> str:
        """
        Map SSA-24 threat types to SSA-26 attack types

        Args:
            threat_type: The SSA-24 security threat type

        Returns:
            Attack type string for SSA-26 security error formatting
        """
        # Common SSA-24 to SSA-26 threat type mappings
        threat_mappings = {
            'xss_threat': 'xss',
            'script_injection': 'xss',
            'sql_injection_threat': 'sql_injection',
            'path_traversal_threat': 'path_traversal',
            'command_injection': 'command_injection',
            'html_injection': 'xss',
            'javascript_injection': 'xss'
        }

        return threat_mappings.get(threat_type, 'unknown')

    def _create_fallback_error(self, field_name: str, field_value: Any, reason: str) -> AcademicErrorMessage:
        """
        Create a fallback error message when SSA-24 is not available

        Args:
            field_name: Name of the field
            field_value: Value that failed
            reason: Reason for fallback

        Returns:
            Basic AcademicErrorMessage
        """
        return self.formatter.format_validation_error(
            field=field_name,
            value=field_value,
            constraint="system_unavailable",
            details={"fallback_reason": reason}
        )

    def _create_fallback_security_error(self, content: str, reason: str) -> AcademicErrorMessage:
        """
        Create a fallback security error message when SSA-24 is not available

        Args:
            content: Content that was being validated
            reason: Reason for fallback

        Returns:
            Basic AcademicErrorMessage for security
        """
        return self.formatter.format_security_error(
            attack_type="unknown",
            blocked_content=content[:50] + "..." if len(content) > 50 else content,
            context={"fallback_reason": reason}
        )


class ValidationErrorCollector:
    """
    Utility class to collect and manage validation errors from multiple sources

    This class helps aggregate validation errors from different parts of the application
    and convert them all to educational error messages.
    """

    def __init__(self, language: str = "es", educational_mode: bool = True):
        """
        Initialize the error collector

        Args:
            language: Language for error messages
            educational_mode: Whether to include educational content
        """
        self.bridge = SSA24ToSSA26Bridge(language, educational_mode)
        self.collected_errors: List[AcademicErrorMessage] = []

    def add_validation_error(
        self,
        validation_result: Any,
        field_name: str,
        field_value: Any,
        context: Optional[ValidationErrorContext] = None
    ) -> None:
        """
        Add a validation error to the collection

        Args:
            validation_result: SSA-24 ValidationResult
            field_name: Name of the field that failed
            field_value: Value that failed validation
            context: Additional validation context
        """
        error_message = self.bridge.convert_validation_result(
            validation_result=validation_result,
            field_name=field_name,
            field_value=field_value,
            context=context
        )

        if error_message:
            self.collected_errors.append(error_message)

    def add_security_error(
        self,
        security_result: Any,
        input_content: str,
        context: Optional[Dict] = None
    ) -> None:
        """
        Add a security validation error to the collection

        Args:
            security_result: SSA-24 SecurityValidationResult
            input_content: Content that failed security validation
            context: Additional security context
        """
        error_message = self.bridge.convert_security_validation_result(
            security_result=security_result,
            input_content=input_content,
            context=context
        )

        if error_message:
            self.collected_errors.append(error_message)

    def add_direct_error(self, error_message: AcademicErrorMessage) -> None:
        """
        Add an already-formatted error message to the collection

        Args:
            error_message: Pre-formatted AcademicErrorMessage
        """
        self.collected_errors.append(error_message)

    def get_all_errors(self) -> List[AcademicErrorMessage]:
        """
        Get all collected error messages

        Returns:
            List of all collected AcademicErrorMessage objects
        """
        return self.collected_errors.copy()

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[AcademicErrorMessage]:
        """
        Get errors filtered by severity level

        Args:
            severity: Error severity to filter by

        Returns:
            List of errors matching the specified severity
        """
        return [error for error in self.collected_errors if error.severity == severity]

    def get_errors_by_category(self, category: ErrorCategory) -> List[AcademicErrorMessage]:
        """
        Get errors filtered by category

        Args:
            category: Error category to filter by

        Returns:
            List of errors matching the specified category
        """
        return [error for error in self.collected_errors if error.category == category]

    def has_critical_errors(self) -> bool:
        """
        Check if any collected errors are critical

        Returns:
            True if any critical errors exist
        """
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.collected_errors)

    def has_errors(self) -> bool:
        """
        Check if any errors have been collected

        Returns:
            True if any errors exist
        """
        return len(self.collected_errors) > 0

    def clear_errors(self) -> None:
        """Clear all collected errors"""
        self.collected_errors.clear()

    def get_html_formatted_errors(self) -> List[str]:
        """
        Get all errors formatted as HTML

        Returns:
            List of HTML-formatted error messages
        """
        return [
            self.bridge.formatter.to_html(error)
            for error in self.collected_errors
        ]

    def get_json_formatted_errors(self) -> List[Dict[str, Any]]:
        """
        Get all errors formatted as JSON-serializable dictionaries

        Returns:
            List of dictionary representations of error messages
        """
        return [
            self.bridge.formatter.to_dict(error)
            for error in self.collected_errors
        ]


# Convenience functions for quick error conversion
def convert_ssa24_validation_error(
    validation_result: Any,
    field_name: str,
    field_value: Any,
    language: str = "es"
) -> Optional[AcademicErrorMessage]:
    """
    Convenience function to quickly convert a single SSA-24 validation error

    Args:
        validation_result: SSA-24 ValidationResult object
        field_name: Name of the validated field
        field_value: Value that was validated
        language: Language for the error message

    Returns:
        AcademicErrorMessage if validation failed, None if validation passed
    """
    bridge = SSA24ToSSA26Bridge(language=language)
    return bridge.convert_validation_result(
        validation_result=validation_result,
        field_name=field_name,
        field_value=field_value
    )


def convert_ssa24_security_error(
    security_result: Any,
    input_content: str,
    language: str = "es"
) -> Optional[AcademicErrorMessage]:
    """
    Convenience function to quickly convert a single SSA-24 security error

    Args:
        security_result: SSA-24 SecurityValidationResult object
        input_content: Content that was validated
        language: Language for the error message

    Returns:
        AcademicErrorMessage if security threats detected, None if content is safe
    """
    bridge = SSA24ToSSA26Bridge(language=language)
    return bridge.convert_security_validation_result(
        security_result=security_result,
        input_content=input_content
    )


def create_validation_error_collector(language: str = "es") -> ValidationErrorCollector:
    """
    Convenience function to create a new ValidationErrorCollector

    Args:
        language: Language for error messages

    Returns:
        New ValidationErrorCollector instance
    """
    return ValidationErrorCollector(language=language, educational_mode=True)