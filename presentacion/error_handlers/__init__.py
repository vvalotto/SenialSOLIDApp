"""
SSA-26 Academic Presentation Layer Error Handlers
Educational error handling for web interface and APIs
"""

from .flask_error_handler import FlaskErrorHandler, WebErrorBoundary

__all__ = [
    'FlaskErrorHandler',
    'WebErrorBoundary'
]