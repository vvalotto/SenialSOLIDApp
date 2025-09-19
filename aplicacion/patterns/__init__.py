"""
SSA-26 Application Layer Error Handling Patterns
Educational patterns for use case error handling and validation error bridging
"""

from .validation_error_bridge import SSA24ToSSA26Bridge
from .use_case_error_handler import (
    UseCaseErrorHandler,
    GracefulDegradation,
    UseCaseExecutionMode,
    FallbackStrategy
)

__all__ = [
    'SSA24ToSSA26Bridge',
    'UseCaseErrorHandler',
    'GracefulDegradation',
    'UseCaseExecutionMode',
    'FallbackStrategy'
]