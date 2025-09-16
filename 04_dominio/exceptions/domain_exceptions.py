"""
Domain Layer Specific Exceptions
SSA-23: Exception Handling Refactoring
"""

from typing import Any, Dict, Optional
from .base_exceptions import DomainException


class ValidationException(DomainException):
    """
    Input validation and business rule violations

    Used when data doesn't meet business rules or validation criteria.
    Provides specific field-level validation information.
    """

    def __init__(
        self,
        field: str,
        value: Any,
        rule: str,
        expected: str = None,
        **kwargs
    ):
        # Enrich context with validation-specific information
        validation_context = {
            "field": field,
            "invalid_value": str(value)[:100],  # Limit length for logging
            "validation_rule": rule,
            "expected_format": expected,
            "validation_type": "business_rule"
        }

        # Merge with any additional context
        context = kwargs.get('context', {})
        context.update(validation_context)
        kwargs['context'] = context

        # Set user-friendly messages
        kwargs.setdefault('user_message', f"Valor inválido para {field}")
        kwargs.setdefault('recovery_suggestion', f"Verifique que {field} cumple con: {rule}")

        super().__init__(
            f"Validation failed for '{field}': {rule}",
            **kwargs
        )


class ProcessingException(DomainException):
    """
    Signal processing errors with performance and operation context

    Used when signal processing operations fail due to data issues,
    algorithm limitations, or processing constraints.
    """

    def __init__(
        self,
        operation: str,
        signal_id: str = None,
        processing_stage: str = None,
        **kwargs
    ):
        # Enrich context with processing-specific information
        processing_context = {
            "operation": operation,
            "signal_id": signal_id,
            "processing_stage": processing_stage or "unknown",
            "operation_type": "signal_processing"
        }

        # Add performance metrics if available
        if 'processing_time_ms' in kwargs:
            processing_context['processing_time_ms'] = kwargs.pop('processing_time_ms')
        if 'memory_usage_mb' in kwargs:
            processing_context['memory_usage_mb'] = kwargs.pop('memory_usage_mb')

        context = kwargs.get('context', {})
        context.update(processing_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', 'Error procesando señal')
        kwargs.setdefault(
            'recovery_suggestion',
            'Verifique los parámetros de procesamiento o intente con datos diferentes'
        )

        super().__init__(
            f"Processing failed: {operation}" + (f" for signal {signal_id}" if signal_id else ""),
            **kwargs
        )


class AcquisitionException(DomainException):
    """
    Signal acquisition errors with source and method context

    Used when signal acquisition fails due to source issues,
    connectivity problems, or data format errors.
    """

    def __init__(
        self,
        source: str,
        source_type: str = "unknown",
        acquisition_method: str = "unknown",
        **kwargs
    ):
        # Enrich context with acquisition-specific information
        acquisition_context = {
            "source": source,
            "source_type": source_type,
            "acquisition_method": acquisition_method,
            "operation_type": "signal_acquisition"
        }

        context = kwargs.get('context', {})
        context.update(acquisition_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', 'Error adquiriendo señal')
        kwargs.setdefault(
            'recovery_suggestion',
            'Verifique la fuente de datos, conectividad y formato de archivo'
        )

        super().__init__(
            f"Acquisition failed from {source} ({source_type})",
            **kwargs
        )


class RepositoryException(DomainException):
    """
    Repository and persistence errors with entity context

    Used when data persistence operations fail due to storage issues,
    entity validation, or repository constraints.
    """

    def __init__(
        self,
        operation: str,
        entity_type: str = None,
        entity_id: str = None,
        **kwargs
    ):
        # Enrich context with repository-specific information
        repository_context = {
            "operation": operation,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "repository_type": "file_based",
            "operation_type": "data_persistence"
        }

        context = kwargs.get('context', {})
        context.update(repository_context)
        kwargs['context'] = context

        kwargs.setdefault('user_message', 'Error accediendo a datos almacenados')
        kwargs.setdefault(
            'recovery_suggestion',
            'Verifique permisos de archivo, espacio en disco y integridad de datos'
        )

        entity_info = f" for {entity_type}" if entity_type else ""
        entity_info += f" (ID: {entity_id})" if entity_id else ""

        super().__init__(
            f"Repository operation '{operation}' failed{entity_info}",
            **kwargs
        )