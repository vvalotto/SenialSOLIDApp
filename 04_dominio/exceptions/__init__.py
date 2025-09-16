"""
Custom Exception Classes for SenialSOLID Application
SSA-23: Exception Handling Refactoring

This module provides a comprehensive exception hierarchy with:
- Automatic SSA-22 structured logging integration
- Rich context information for debugging
- Recovery strategy support
- Layer-specific exception types
"""

from .base_exceptions import (
    SenialSOLIDException,
    DomainException,
    InfrastructureException,
    PresentationException
)

from .domain_exceptions import (
    ValidationException,
    ProcessingException,
    AcquisitionException,
    RepositoryException
)

from .infrastructure_exceptions import (
    ConfigurationException,
    DataAccessException,
    NetworkException
)

from .presentation_exceptions import (
    WebException,
    ConsoleException
)

from .recovery_strategies import (
    RecoveryStrategy,
    FileIORecoveryStrategy,
    ProcessingFallbackStrategy,
    RetryStrategy
)

__all__ = [
    # Base exceptions
    'SenialSOLIDException',
    'DomainException',
    'InfrastructureException',
    'PresentationException',

    # Domain-specific exceptions
    'ValidationException',
    'ProcessingException',
    'AcquisitionException',
    'RepositoryException',

    # Infrastructure exceptions
    'ConfigurationException',
    'DataAccessException',
    'NetworkException',

    # Presentation exceptions
    'WebException',
    'ConsoleException',

    # Recovery strategies
    'RecoveryStrategy',
    'FileIORecoveryStrategy',
    'ProcessingFallbackStrategy',
    'RetryStrategy'
]