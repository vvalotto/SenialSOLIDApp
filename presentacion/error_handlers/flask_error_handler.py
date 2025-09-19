"""
SSA-26 Academic Flask Error Handler
Educational web error boundary implementation for Flask applications

This module demonstrates how to implement web-layer error boundaries
in clean architecture with educational error messaging.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import traceback
from datetime import datetime

try:
    from flask import Flask, request, jsonify, render_template, session
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None

# Import SSA-23 exception hierarchy
try:
    from dominio.exceptions.custom_exceptions import (
        DomainException,
        BusinessRuleViolationException,
        ValidationException,
        SecurityException
    )
    SSA23_AVAILABLE = True
except ImportError:
    SSA23_AVAILABLE = False
    # Fallback classes
    class DomainException(Exception):
        pass
    class BusinessRuleViolationException(DomainException):
        pass
    class ValidationException(Exception):
        pass
    class SecurityException(Exception):
        pass

# Import SSA-26 patterns
from dominio.patterns.messaging.user_message_formatter import (
    AcademicErrorMessageFormatter,
    ErrorSeverity,
    ErrorCategory
)

try:
    from aplicacion.patterns.validation_error_bridge import SSA24ToSSA26Bridge
    VALIDATION_BRIDGE_AVAILABLE = True
except ImportError:
    VALIDATION_BRIDGE_AVAILABLE = False
    SSA24ToSSA26Bridge = None


class HTTPErrorCode(Enum):
    """Educational HTTP error code mapping"""
    BAD_REQUEST = 400          # Client error - invalid input
    UNAUTHORIZED = 401         # Authentication required
    FORBIDDEN = 403           # Access denied
    NOT_FOUND = 404           # Resource not found
    METHOD_NOT_ALLOWED = 405  # HTTP method not supported
    CONFLICT = 409            # Resource conflict
    UNPROCESSABLE_ENTITY = 422  # Validation errors
    TOO_MANY_REQUESTS = 429   # Rate limiting
    INTERNAL_SERVER_ERROR = 500  # Server error
    SERVICE_UNAVAILABLE = 503    # Service temporarily down


@dataclass
class WebErrorContext:
    """Educational web error context for debugging and learning"""
    request_url: str
    request_method: str
    user_agent: Optional[str]
    client_ip: Optional[str]
    user_session_id: Optional[str]
    timestamp: datetime
    additional_context: Dict[str, Any]


@dataclass
class WebErrorResponse:
    """Educational web error response structure"""
    error_code: int
    user_message: str
    technical_details: Optional[str]
    educational_tip: Optional[str]
    suggested_actions: list
    error_id: str
    context: WebErrorContext


class WebErrorBoundary:
    """
    Academic Web Error Boundary for Flask applications

    This class demonstrates how to implement presentation layer error
    boundaries in clean architecture with educational error handling.

    Educational Purposes:
    - Shows separation between web errors and domain errors
    - Demonstrates proper HTTP status code mapping
    - Illustrates user session preservation during errors
    - Provides examples of educational error pages

    Examples:
        >>> boundary = WebErrorBoundary()
        >>> error_response = boundary.handle_domain_error(
        ...     domain_error,
        ...     request_context
        ... )
    """

    def __init__(self, educational_mode: bool = True, logger: Optional[logging.Logger] = None):
        """
        Initialize web error boundary with educational configuration

        Args:
            educational_mode: Whether to include educational tips in errors
            logger: Optional logger for error tracking
        """
        self.educational_mode = educational_mode
        self.logger = logger or logging.getLogger(__name__)
        self.formatter = AcademicErrorMessageFormatter(educational_mode=educational_mode)

        if VALIDATION_BRIDGE_AVAILABLE:
            self.validation_bridge = SSA24ToSSA26Bridge()
        else:
            self.validation_bridge = None

        # Educational error page templates
        self.error_templates = {
            400: "errors/400_validation_error.html",
            401: "errors/401_unauthorized.html",
            403: "errors/403_forbidden.html",
            404: "errors/404_not_found.html",
            422: "errors/422_validation_error.html",
            500: "errors/500_server_error.html",
            503: "errors/503_service_unavailable.html"
        }

    def create_error_context(self, request_obj=None) -> WebErrorContext:
        """
        Create educational web error context from Flask request

        Args:
            request_obj: Flask request object (if available)

        Returns:
            WebErrorContext with request information
        """
        if not FLASK_AVAILABLE or not request_obj:
            return WebErrorContext(
                request_url="unknown",
                request_method="unknown",
                user_agent=None,
                client_ip=None,
                user_session_id=None,
                timestamp=datetime.now(),
                additional_context={}
            )

        return WebErrorContext(
            request_url=request_obj.url,
            request_method=request_obj.method,
            user_agent=request_obj.headers.get('User-Agent'),
            client_ip=request_obj.remote_addr,
            user_session_id=session.get('session_id') if session else None,
            timestamp=datetime.now(),
            additional_context={
                "endpoint": request_obj.endpoint,
                "args": dict(request_obj.args),
                "form_data": dict(request_obj.form) if request_obj.form else {}
            }
        )

    def map_exception_to_http_code(self, exception: Exception) -> int:
        """
        Educational exception to HTTP status code mapping

        This method demonstrates how to properly map domain exceptions
        to appropriate HTTP status codes for educational purposes.

        Args:
            exception: The exception to map

        Returns:
            Appropriate HTTP status code

        Examples:
            >>> boundary = WebErrorBoundary()
            >>> code = boundary.map_exception_to_http_code(ValidationException("Invalid input"))
            >>> assert code == 422  # Unprocessable Entity
        """
        if isinstance(exception, ValidationException):
            return HTTPErrorCode.UNPROCESSABLE_ENTITY.value
        elif isinstance(exception, BusinessRuleViolationException):
            return HTTPErrorCode.BAD_REQUEST.value
        elif isinstance(exception, SecurityException):
            return HTTPErrorCode.FORBIDDEN.value
        elif isinstance(exception, DomainException):
            return HTTPErrorCode.BAD_REQUEST.value
        elif isinstance(exception, FileNotFoundError):
            return HTTPErrorCode.NOT_FOUND.value
        elif isinstance(exception, PermissionError):
            return HTTPErrorCode.FORBIDDEN.value
        elif isinstance(exception, TimeoutError):
            return HTTPErrorCode.SERVICE_UNAVAILABLE.value
        else:
            # Unknown errors default to 500
            return HTTPErrorCode.INTERNAL_SERVER_ERROR.value

    def handle_domain_error(self, exception: Exception, context: WebErrorContext) -> WebErrorResponse:
        """
        Educational domain error handling for web layer

        This method demonstrates how to convert domain exceptions into
        appropriate web responses with educational content.

        Args:
            exception: Domain exception to handle
            context: Web request context

        Returns:
            WebErrorResponse with educational content
        """
        error_code = self.map_exception_to_http_code(exception)
        error_id = f"ERR_{context.timestamp.strftime('%Y%m%d_%H%M%S')}_{id(exception)}"

        # Log error for educational debugging
        self.logger.error(
            f"Web layer handling domain error: {type(exception).__name__}",
            extra={
                "error_id": error_id,
                "error_code": error_code,
                "context": context.__dict__,
                "exception_details": str(exception)
            },
            exc_info=True
        )

        if isinstance(exception, ValidationException):
            return self._handle_validation_error(exception, error_code, error_id, context)
        elif isinstance(exception, BusinessRuleViolationException):
            return self._handle_business_rule_error(exception, error_code, error_id, context)
        elif isinstance(exception, SecurityException):
            return self._handle_security_error(exception, error_code, error_id, context)
        else:
            return self._handle_generic_error(exception, error_code, error_id, context)

    def _handle_validation_error(self, exception: ValidationException, error_code: int,
                                error_id: str, context: WebErrorContext) -> WebErrorResponse:
        """Handle validation errors with educational content"""
        user_message = "Los datos ingresados no cumplen con los requisitos de validación"
        educational_tip = (
            "Las validaciones protegen la integridad de los datos y aseguran que "
            "los parámetros de entrada sean seguros para el procesamiento de señales. "
            "Revise que todos los campos tengan el formato correcto."
        )
        suggested_actions = [
            "Verifique que todos los campos requeridos estén completos",
            "Asegúrese de que los valores numéricos estén en el rango permitido",
            "Revise el formato de los datos ingresados",
            "Consulte la documentación para conocer los límites permitidos"
        ]

        return WebErrorResponse(
            error_code=error_code,
            user_message=user_message,
            technical_details=str(exception) if self.educational_mode else None,
            educational_tip=educational_tip if self.educational_mode else None,
            suggested_actions=suggested_actions,
            error_id=error_id,
            context=context
        )

    def _handle_business_rule_error(self, exception: BusinessRuleViolationException,
                                   error_code: int, error_id: str,
                                   context: WebErrorContext) -> WebErrorResponse:
        """Handle business rule violations with educational content"""
        user_message = "La operación viola una regla de negocio del sistema"
        educational_tip = (
            "Las reglas de negocio aseguran que las operaciones mantengan la "
            "consistencia del dominio de procesamiento de señales. Estas reglas "
            "reflejan las limitaciones físicas y prácticas del mundo real."
        )
        suggested_actions = [
            "Revise los parámetros de entrada",
            "Verifique que la operación sea válida en el contexto actual",
            "Consulte la documentación de limitaciones del sistema",
            "Considere ajustar los parámetros a rangos permitidos"
        ]

        return WebErrorResponse(
            error_code=error_code,
            user_message=user_message,
            technical_details=str(exception) if self.educational_mode else None,
            educational_tip=educational_tip if self.educational_mode else None,
            suggested_actions=suggested_actions,
            error_id=error_id,
            context=context
        )

    def _handle_security_error(self, exception: SecurityException, error_code: int,
                              error_id: str, context: WebErrorContext) -> WebErrorResponse:
        """Handle security errors with educational content"""
        user_message = "Acceso denegado por motivos de seguridad"
        educational_tip = (
            "La seguridad en sistemas de procesamiento de señales es crítica "
            "para proteger datos sensibles y prevenir accesos no autorizados "
            "a configuraciones del sistema."
        )
        suggested_actions = [
            "Verifique que tiene los permisos necesarios",
            "Asegúrese de estar autenticado correctamente",
            "Contacte al administrador si necesita acceso adicional"
        ]

        return WebErrorResponse(
            error_code=error_code,
            user_message=user_message,
            technical_details=None,  # Never expose security details
            educational_tip=educational_tip if self.educational_mode else None,
            suggested_actions=suggested_actions,
            error_id=error_id,
            context=context
        )

    def _handle_generic_error(self, exception: Exception, error_code: int,
                             error_id: str, context: WebErrorContext) -> WebErrorResponse:
        """Handle generic errors with educational content"""
        user_message = "Ha ocurrido un error inesperado en el sistema"
        educational_tip = (
            "Los errores inesperados pueden deberse a condiciones excepcionales "
            "no previstas en el diseño. En sistemas reales, estos errores se "
            "registran para análisis y mejora continua del software."
        )
        suggested_actions = [
            "Intente la operación nuevamente",
            "Verifique que todos los datos sean correctos",
            "Si el problema persiste, contacte al soporte técnico",
            f"Proporcione el ID de error: {error_id}"
        ]

        return WebErrorResponse(
            error_code=error_code,
            user_message=user_message,
            technical_details=str(exception) if self.educational_mode else None,
            educational_tip=educational_tip if self.educational_mode else None,
            suggested_actions=suggested_actions,
            error_id=error_id,
            context=context
        )


class FlaskErrorHandler:
    """
    Academic Flask Error Handler for SenialSOLIDApp

    This class provides educational Flask error handlers that demonstrate
    proper web error boundary implementation in clean architecture.

    Educational Purposes:
    - Shows how to register Flask error handlers
    - Demonstrates JSON vs HTML error responses
    - Illustrates user session preservation
    - Provides examples of educational error pages

    Examples:
        >>> app = Flask(__name__)
        >>> error_handler = FlaskErrorHandler(app, educational_mode=True)
        >>> error_handler.register_handlers()
    """

    def __init__(self, app: Optional[Flask] = None, educational_mode: bool = True):
        """
        Initialize Flask error handler with educational configuration

        Args:
            app: Flask application instance
            educational_mode: Whether to include educational content in errors
        """
        self.app = app
        self.educational_mode = educational_mode
        self.logger = logging.getLogger(__name__)
        self.boundary = WebErrorBoundary(educational_mode=educational_mode, logger=self.logger)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize error handlers for Flask app"""
        self.app = app
        self.register_handlers()

    def register_handlers(self) -> None:
        """
        Register educational Flask error handlers

        This method demonstrates how to properly register error handlers
        for different types of exceptions in Flask applications.
        """
        if not self.app or not FLASK_AVAILABLE:
            self.logger.warning("Flask not available or app not initialized")
            return

        # Domain-specific error handlers
        self.app.errorhandler(ValidationException)(self.handle_validation_error)
        self.app.errorhandler(BusinessRuleViolationException)(self.handle_business_rule_error)
        self.app.errorhandler(SecurityException)(self.handle_security_error)
        self.app.errorhandler(DomainException)(self.handle_domain_error)

        # HTTP error handlers
        self.app.errorhandler(400)(self.handle_bad_request)
        self.app.errorhandler(401)(self.handle_unauthorized)
        self.app.errorhandler(403)(self.handle_forbidden)
        self.app.errorhandler(404)(self.handle_not_found)
        self.app.errorhandler(422)(self.handle_unprocessable_entity)
        self.app.errorhandler(500)(self.handle_internal_server_error)
        self.app.errorhandler(503)(self.handle_service_unavailable)

        # Generic exception handler
        self.app.errorhandler(Exception)(self.handle_generic_exception)

        self.logger.info("Educational Flask error handlers registered successfully")

    def handle_validation_error(self, error: ValidationException) -> Tuple[Any, int]:
        """Handle SSA-24 validation errors with educational content"""
        context = self.boundary.create_error_context(request if FLASK_AVAILABLE else None)
        response = self.boundary.handle_domain_error(error, context)
        return self._create_response(response)

    def handle_business_rule_error(self, error: BusinessRuleViolationException) -> Tuple[Any, int]:
        """Handle business rule violations with educational content"""
        context = self.boundary.create_error_context(request if FLASK_AVAILABLE else None)
        response = self.boundary.handle_domain_error(error, context)
        return self._create_response(response)

    def handle_security_error(self, error: SecurityException) -> Tuple[Any, int]:
        """Handle security errors with educational content"""
        context = self.boundary.create_error_context(request if FLASK_AVAILABLE else None)
        response = self.boundary.handle_domain_error(error, context)
        return self._create_response(response)

    def handle_domain_error(self, error: DomainException) -> Tuple[Any, int]:
        """Handle generic domain errors with educational content"""
        context = self.boundary.create_error_context(request if FLASK_AVAILABLE else None)
        response = self.boundary.handle_domain_error(error, context)
        return self._create_response(response)

    def handle_bad_request(self, error) -> Tuple[Any, int]:
        """Handle 400 Bad Request errors"""
        return self._handle_http_error(error, 400, "Solicitud inválida")

    def handle_unauthorized(self, error) -> Tuple[Any, int]:
        """Handle 401 Unauthorized errors"""
        return self._handle_http_error(error, 401, "Autenticación requerida")

    def handle_forbidden(self, error) -> Tuple[Any, int]:
        """Handle 403 Forbidden errors"""
        return self._handle_http_error(error, 403, "Acceso denegado")

    def handle_not_found(self, error) -> Tuple[Any, int]:
        """Handle 404 Not Found errors"""
        return self._handle_http_error(error, 404, "Recurso no encontrado")

    def handle_unprocessable_entity(self, error) -> Tuple[Any, int]:
        """Handle 422 Unprocessable Entity errors"""
        return self._handle_http_error(error, 422, "Datos no procesables")

    def handle_internal_server_error(self, error) -> Tuple[Any, int]:
        """Handle 500 Internal Server Error"""
        return self._handle_http_error(error, 500, "Error interno del servidor")

    def handle_service_unavailable(self, error) -> Tuple[Any, int]:
        """Handle 503 Service Unavailable errors"""
        return self._handle_http_error(error, 503, "Servicio no disponible")

    def handle_generic_exception(self, error: Exception) -> Tuple[Any, int]:
        """Handle any unhandled exception"""
        context = self.boundary.create_error_context(request if FLASK_AVAILABLE else None)
        response = self.boundary.handle_domain_error(error, context)
        return self._create_response(response)

    def _handle_http_error(self, error, status_code: int, user_message: str) -> Tuple[Any, int]:
        """Handle HTTP errors with educational content"""
        context = self.boundary.create_error_context(request if FLASK_AVAILABLE else None)
        error_id = f"HTTP_{status_code}_{context.timestamp.strftime('%Y%m%d_%H%M%S')}"

        response = WebErrorResponse(
            error_code=status_code,
            user_message=user_message,
            technical_details=str(error) if self.educational_mode else None,
            educational_tip=f"Error HTTP {status_code}: {self._get_educational_tip(status_code)}",
            suggested_actions=self._get_suggested_actions(status_code),
            error_id=error_id,
            context=context
        )

        return self._create_response(response)

    def _get_educational_tip(self, status_code: int) -> str:
        """Get educational tip for HTTP status codes"""
        tips = {
            400: "Los errores 400 indican que la solicitud del cliente contiene datos inválidos o malformados.",
            401: "Los errores 401 requieren autenticación. El cliente debe proporcionar credenciales válidas.",
            403: "Los errores 403 indican que el cliente no tiene permisos para acceder al recurso solicitado.",
            404: "Los errores 404 indican que el recurso solicitado no existe en el servidor.",
            422: "Los errores 422 indican que los datos están bien formados pero contienen errores semánticos.",
            500: "Los errores 500 indican problemas internos del servidor que deben ser investigados.",
            503: "Los errores 503 indican que el servicio está temporalmente no disponible."
        }
        return tips.get(status_code, "Error HTTP no común que requiere investigación específica.")

    def _get_suggested_actions(self, status_code: int) -> list:
        """Get suggested actions for HTTP status codes"""
        actions = {
            400: ["Verifique los datos enviados", "Revise el formato de la solicitud"],
            401: ["Inicie sesión", "Verifique sus credenciales"],
            403: ["Contacte al administrador", "Verifique sus permisos"],
            404: ["Verifique la URL", "Consulte la documentación"],
            422: ["Revise los datos ingresados", "Corrija los errores de validación"],
            500: ["Intente nuevamente más tarde", "Contacte al soporte técnico"],
            503: ["Espere unos minutos", "Intente nuevamente más tarde"]
        }
        return actions.get(status_code, ["Intente nuevamente", "Contacte al soporte técnico"])

    def _create_response(self, response: WebErrorResponse) -> Tuple[Any, int]:
        """
        Create Flask response from WebErrorResponse

        This method demonstrates how to create appropriate responses
        for both JSON API calls and HTML page requests.
        """
        if not FLASK_AVAILABLE:
            return {"error": response.user_message}, response.error_code

        # Check if request wants JSON response
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                "error": {
                    "code": response.error_code,
                    "message": response.user_message,
                    "technical_details": response.technical_details,
                    "educational_tip": response.educational_tip,
                    "suggested_actions": response.suggested_actions,
                    "error_id": response.error_id,
                    "timestamp": response.context.timestamp.isoformat()
                }
            }), response.error_code

        # HTML response for web pages
        template = self.boundary.error_templates.get(response.error_code, "errors/generic_error.html")

        try:
            return render_template(template,
                                 error=response,
                                 educational_mode=self.educational_mode), response.error_code
        except Exception:
            # Fallback to simple error page if template not found
            return render_template("errors/generic_error.html",
                                 error=response,
                                 educational_mode=self.educational_mode), response.error_code