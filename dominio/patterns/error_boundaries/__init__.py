"""
SSA-26 Academic Error Boundaries
Domain layer error boundaries for clean architecture education
"""

from .domain_boundary import DomainErrorBoundary, BusinessRuleViolation, DomainInvariantError

__all__ = [
    'DomainErrorBoundary',
    'BusinessRuleViolation',
    'DomainInvariantError'
]