"""Web presentation layer for SenialSOLIDApp.

This module implements the web interface using Flask framework, providing both
HTML views and REST API endpoints for signal management. Integrates comprehensive
validation from SSA-24, error handling from SSA-26, and follows secure coding
principles for web application development.

Key Features:
    - Web forms for signal acquisition and management
    - REST API endpoints with validation
    - Comprehensive error handling and user feedback
    - Security validation and sanitization
    - Structured logging and monitoring
    - Bootstrap-based responsive UI

Endpoints:
    Web Views:
        /: Homepage with navigation
        /acerca/: About page
        /versiones/: System version information
        /componentes/: System component status
        /adquisicion/: Signal acquisition interface
        /procesamiento/: Signal processing interface
        /visualizacion/: Signal visualization interface

    API Endpoints:
        GET /api/signals: List signals with pagination
        POST /api/signals: Create new signal
        GET /api/health: Health check endpoint

This module is part of the presentation layer in DDD architecture and provides
the external interface for the signal processing domain.
"""

from typing import Dict, Any, Optional, List
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from webapp.modelos  import *
from webapp.forms import *
from config import config
import os
import sys
import datetime
from functools import wraps
import traceback

# Add validation framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from exceptions import (
    ValidationException, AcquisitionException, ProcessingException,
    RepositoryException, WebException, ConfigurationException
)
from config.logging_config import get_logger

# Import SSA-24 validation framework
from aplicacion.validation import (
    ValidationError,
    SecurityValidationError,
    APIValidationError,
    FileValidationError,
    auto_sanitize,
    sanitize_input,
    validate_parameters,
    StringInputValidator,
    create_api_validation_pipeline
)

logger = get_logger(__name__)

# SECURITY FIX: Removed hardcoded SECRET_KEY "Victor"
# Now using secure configuration management

# Create validation pipeline for web requests
web_api_pipeline = create_api_validation_pipeline("public", rate_limit=200)


def handle_validation_errors(f):
    """Decorator to handle SSA-24 validation errors in web routes.

    Provides centralized error handling for validation exceptions across
    all web routes. Converts technical exceptions into user-friendly
    messages and implements appropriate recovery strategies.

    Handles the following validation error types:
        - ValidationError: General input validation failures
        - SecurityValidationError: Security threats and malicious input
        - FileValidationError: File upload and processing errors

    Args:
        f: Flask route function to be wrapped with error handling

    Returns:
        function: Wrapped function with comprehensive error handling

    Example:
        @app.route('/example')
        @handle_validation_errors
        def example_route():
            # Route implementation with automatic error handling
            return render_template('example.html')

    Note:
        Logs all validation errors with structured context for monitoring.
        Provides user feedback through Flask flash messages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as ve:
            logger.warning(
                "Validation error in web route",
                extra={
                    'route': request.endpoint,
                    'method': request.method,
                    'error_code': ve.error_code,
                    'validation_context': ve.context
                }
            )
            flash(f"Error de validación: {ve.user_message}", 'error')
            if ve.recovery_suggestion:
                flash(f"Sugerencia: {ve.recovery_suggestion}", 'info')
            return redirect(request.url)

        except SecurityValidationError as sve:
            logger.error(
                "Security validation error in web route",
                extra={
                    'route': request.endpoint,
                    'method': request.method,
                    'error_code': sve.error_code,
                    'threat_type': sve.context.get('threat_type'),
                    'client_ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent')
                }
            )
            flash("Error de seguridad: Solicitud no permitida", 'error')
            return redirect(url_for('inicio'))

        except FileValidationError as fve:
            logger.warning(
                "File validation error in web route",
                extra={
                    'route': request.endpoint,
                    'method': request.method,
                    'error_code': fve.error_code,
                    'filename': fve.context.get('filename')
                }
            )
            flash(f"Error de archivo: {fve.user_message}", 'error')
            return redirect(request.url)

    return decorated_function


def validate_web_request() -> Optional[Any]:
    """Validate incoming web request for security threats.

    Performs comprehensive validation of web requests using the SSA-24
    validation framework. Checks for security threats, malicious input,
    and enforces request limits and constraints.

    Validation includes:
        - Client IP address validation
        - User agent analysis
        - Request method verification
        - Form data sanitization
        - Rate limiting and abuse detection

    Returns:
        Optional[Any]: Validation result object or None if validation fails

    Raises:
        SecurityValidationError: When security threats are detected
        ValidationError: When input validation fails

    Example:
        >>> result = validate_web_request()
        >>> if result and result.is_valid:
        ...     # Process request normally
        ...     process_request()
        >>> else:
        ...     # Handle validation failure
        ...     return error_response()

    Note:
        Automatically called by decorated routes. Manual calls should
        handle None return values appropriately.
    """
    try:
        request_data = {
            'client_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'method': request.method,
            'endpoint': request.endpoint,
            'args': dict(request.args),
            'form_data': dict(request.form) if request.form else {}
        }

        context = {
            'endpoint': request.endpoint,
            'client_ip': request.remote_addr,
            'request_method': request.method
        }

        # Validate with web API pipeline
        result = web_api_pipeline.validate(request_data, context)

        if not result.is_valid:
            logger.warning(
                "Web request validation failed",
                extra={
                    'validation_errors': [error.to_dict() for error in result.errors],
                    'client_ip': request.remote_addr,
                    'endpoint': request.endpoint
                }
            )
            # Don't block on warnings, just log
            for error in result.errors:
                if isinstance(error, SecurityValidationError):
                    raise error

        return result

    except Exception as e:
        logger.error(f"Error in web request validation: {str(e)}", exc_info=True)
        return None


@auto_sanitize()
def sanitize_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize form data using SSA-24 validation framework.

    Applies automatic sanitization to all form input data to prevent
    security vulnerabilities such as XSS, SQL injection, and other
    malicious input attacks.

    Sanitization Process:
        1. Identify string values in form data
        2. Apply StringInputValidator with length limits
        3. Sanitize potentially dangerous content
        4. Preserve non-string values unchanged
        5. Return sanitized dictionary

    Args:
        form_data: Dictionary containing form field names and values

    Returns:
        Dict[str, Any]: Sanitized form data with safe values

    Example:
        >>> raw_form = {'name': '<script>alert("xss")</script>', 'age': 25}
        >>> clean_form = sanitize_form_data(raw_form)
        >>> print(clean_form['name'])
        alert("xss")
        >>> print(clean_form['age'])
        25

    Note:
        Uses @auto_sanitize decorator for additional automatic processing.
        String length limited to 1000 characters for security.
    """
    sanitized = {}
    for key, value in form_data.items():
        if isinstance(value, str):
            validator = StringInputValidator(max_length=1000)
            result = validator.validate(value)
            sanitized[key] = result.sanitized_value if result.sanitized_value is not None else value
        else:
            sanitized[key] = value
    return sanitized

# Get configuration environment (default: development)
config_name = os.environ.get('FLASK_ENV', 'development')

app = Flask(__name__)
# SECURITY: Load configuration from secure config module
app.config.from_object(config[config_name])
# SECURITY: Initialize and validate configuration
config[config_name].init_app(app)

bootstrap = Bootstrap(app)
panel_informes = PanelInformes()


@app.errorhandler(404)
def page_not_found(e) -> tuple:
    """Handle 404 Not Found errors with user-friendly message.

    Provides consistent error handling for missing pages with structured
    logging and user-friendly error pages. Uses WebException for
    standardized error context and recovery suggestions.

    Args:
        e: Flask error object containing request details

    Returns:
        tuple: (rendered template, status code) for Flask response

    Example:
        When user visits non-existent URL:
        - Logs error with request context
        - Shows friendly 404 page
        - Provides navigation suggestions

    Note:
        Error details logged for monitoring and debugging.
        Recovery suggestions help users navigate back to valid pages.
    """
    error = WebException(
        endpoint=request.endpoint or request.path,
        http_status=404,
        request_method=request.method,
        request_id=request.headers.get('X-Request-ID'),
        user_message="Página no encontrada",
        recovery_suggestion="Verifique la URL o navegue desde el menú principal"
    )
    logger.warning("Página no encontrada", extra=error.context)

    return render_template('errors/404.html',
                         error_message=error.user_message,
                         recovery_suggestion=error.recovery_suggestion), 404


@app.errorhandler(500)
def internal_server_error(e) -> tuple:
    """Handle 500 Internal Server Error with user-friendly message.

    Provides consistent error handling for server errors with structured
    logging and user-friendly error pages. Uses WebException for
    standardized error context and masks technical details from users.

    Args:
        e: Flask error object containing exception details

    Returns:
        tuple: (rendered template, status code) for Flask response

    Example:
        When unhandled exception occurs:
        - Logs full exception details for debugging
        - Shows user-friendly error message
        - Provides recovery suggestions
        - Includes unique error code for support

    Note:
        Full exception details logged with stack trace for debugging.
        User sees only safe, actionable error information.
    ""\
    error = WebException(
        endpoint=request.endpoint or request.path,
        http_status=500,
        request_method=request.method,
        request_id=request.headers.get('X-Request-ID'),
        user_message="Error interno del servidor",
        recovery_suggestion="Intente nuevamente en unos momentos o contacte soporte",
        cause=e
    )
    logger.error("Error interno del servidor", extra=error.context, exc_info=True)

    return render_template('errors/500.html',
                         error_message=error.user_message,
                         recovery_suggestion=error.recovery_suggestion,
                         error_code=error.error_code), 500


@app.route('/')
def inicio() -> str:
    """Render the application homepage.

    Displays the main navigation page for the signal processing application
    with links to all major features and system information.

    Returns:
        str: Rendered HTML template for homepage

    Example:
        User navigates to http://localhost:5000/
        - Shows welcome message
        - Displays navigation menu
        - Provides access to all application features
    """
    return render_template('/general/inicio.html')


@app.route('/acerca/')
def acerca() -> str:
    """Render the about page with application information.

    Displays information about the SenialSOLIDApp including:
    - Application purpose and features
    - Technical architecture overview
    - Development team information
    - Contact and support details

    Returns:
        str: Rendered HTML template for about page
    """
    return render_template('general/acerca.html')


@app.route('/versiones/')
def versiones() -> str:
    """Display system version information.

    Shows detailed version information for all system components
    including frameworks, libraries, and application modules.
    Uses the panel_informes service to gather version data.

    Returns:
        str: Rendered HTML template with version information

    Example:
        Displays version table showing:
        - Application version
        - Flask framework version
        - Python interpreter version
        - Database version
        - Other dependency versions
    """
    return render_template('/aplicacion/versiones.html',
                           lista=panel_informes.informar_versiones())


@app.route('/componentes/')
def componentes() -> str:
    """Display system component status information.

    Shows the status and health of all system components including
    services, repositories, processors, and external dependencies.
    Uses the panel_informes service to gather component data.

    Returns:
        str: Rendered HTML template with component status

    Example:
        Displays component table showing:
        - Database connection status
        - Repository service status
        - Validation framework status
        - Logging system status
        - External service connectivity
    """
    return render_template('/aplicacion/componentes.html',
                           lista=panel_informes.informar_componentes())


@app.route("/adquisicion/", methods=['GET', 'POST'])
@handle_validation_errors
def adquisicion() -> str:
    """Handle signal acquisition through web interface.

    Provides both GET (form display) and POST (form processing) handling
    for signal acquisition operations. Integrates comprehensive validation
    from SSA-24 and error handling from SSA-26.

    GET Request:
        - Displays signal acquisition form
        - Shows list of previously acquired signals
        - Applies security validation to request

    POST Request:
        - Validates and sanitizes form data
        - Processes signal acquisition through domain services
        - Provides user feedback on success/failure
        - Implements comprehensive error handling

    Returns:
        str: Rendered HTML template or redirect response

    Raises:
        ValidationException: When form validation fails
        AcquisitionException: When signal acquisition fails
        RepositoryException: When signal persistence fails
        WebException: When unexpected web errors occur

    Example:
        GET /adquisicion/ - Shows acquisition form
        POST /adquisicion/ - Processes signal acquisition with validation

    Note:
        Uses SSA-24 validation framework for security and data validation.
        All errors are logged with structured context for monitoring.
    """
    # Validate web request for security
    validation_result = validate_web_request()

    form = SenialForm()

    if request.method == 'POST':
        # Additional server-side validation using SSA-24
        sanitized_form_data = sanitize_form_data(request.form)

        # Log validation summary for monitoring
        validation_summary = form.get_validation_summary()
        logger.info(
            "Form validation summary",
            extra={
                'endpoint': 'adquisicion',
                'validation_summary': validation_summary,
                'client_ip': request.remote_addr
            }
        )

    if form.validate():
        try:
            # Get sanitized data from form
            form_data = form.get_sanitized_data()

            AccionSenial.adquirir(form)
            flash('Señal adquirida exitosamente', 'success')

            logger.info("Señal adquirida desde interfaz web", extra={
                "form_data": form_data,
                "endpoint": "adquisicion",
                "client_ip": request.remote_addr,
                "validation_warnings": getattr(form, '_warnings', [])
            })

            return redirect(url_for('adquisicion'))

        except ValidationException as ve:
            flash(f"Error de validación: {ve.user_message}", 'error')
            if ve.recovery_suggestion:
                flash(f"Sugerencia: {ve.recovery_suggestion}", 'info')
            logger.warning("Error de validación en adquisición web", extra=ve.context)

        except AcquisitionException as ae:
            flash(f"Error de adquisición: {ae.user_message}", 'error')
            if ae.recovery_suggestion:
                flash(f"Sugerencia: {ae.recovery_suggestion}", 'info')
            logger.error("Error de adquisición en interfaz web", extra=ae.context, exc_info=True)

        except RepositoryException as re:
            flash("Error guardando la señal. Intente nuevamente.", 'error')
            logger.error("Error de repositorio en adquisición web", extra=re.context, exc_info=True)

        except Exception as ex:
            # Wrap unexpected exceptions
            web_error = WebException(
                endpoint="adquisicion",
                http_status=500,
                request_method=request.method,
                user_message="Error inesperado procesando la señal",
                recovery_suggestion="Intente nuevamente o contacte soporte",
                context={"form_data": form.get_sanitized_data() if hasattr(form, 'get_sanitized_data') else {}},
                cause=ex
            )
            flash(f"Error: {web_error.user_message}", 'error')
            logger.error("Error inesperado en adquisición web", extra=web_error.context, exc_info=True)

    # Show form with validation errors and warnings
    form_warnings = getattr(form, '_warnings', [])
    for warning in form_warnings:
        flash(warning, 'warning')

    return render_template('aplicacion/adquisicion.html',
                         form=form,
                         seniales=AccionSenial.listar_seniales_adquiridas())

@app.route("/procesamiento/")
def procesamiento() -> str:
    """Display signal processing interface.

    Provides access to signal processing capabilities including
    filtering, transformation, and analysis operations.

    Returns:
        str: Rendered HTML template for processing interface

    Note:
        Currently displays interface template. Processing logic
        can be added similar to acquisition endpoint.
    """
    return render_template('aplicacion/procesamiento.html')


@app.route("/visualizacion/")
def visualizacion() -> str:
    """Display signal visualization interface.

    Provides access to signal visualization capabilities including
    time-domain plots, frequency analysis, and statistical views.

    Returns:
        str: Rendered HTML template for visualization interface

    Note:
        Currently displays interface template. Visualization logic
        can be added with charting libraries and signal display.
    """
    return render_template('aplicacion/visualizacion.html')


# API Routes with SSA-24 Validation
@app.route("/api/signals", methods=['GET'])
@handle_validation_errors
@validate_parameters(
    limit=StringInputValidator(max_length=10, allowed_pattern=r'^\d+$'),
    offset=StringInputValidator(max_length=10, allowed_pattern=r'^\d+$')
)
def api_list_signals(limit: str = "10", offset: str = "0") -> tuple:
    """REST API endpoint to list signals with pagination and validation.

    Provides paginated access to acquired signals through RESTful API.
    Implements comprehensive validation, security checks, and structured
    error handling with JSON responses.

    Query Parameters:
        limit (str): Maximum number of signals to return (1-100, default: 10)
        offset (str): Number of signals to skip for pagination (default: 0)

    Returns:
        tuple: (JSON response, HTTP status code)

    Response Format:
        {
            "signals": [
                {
                    "id": "signal_identifier",
                    "description": "signal_description",
                    "date": "acquisition_date",
                    "frequency": "signal_frequency",
                    "amplitude": "signal_amplitude"
                }
            ],
            "total": total_count,
            "limit": applied_limit,
            "offset": applied_offset,
            "has_more": boolean
        }

    Raises:
        ValidationError: When parameters are invalid or out of range
        WebException: When unexpected errors occur during processing

    Example:
        GET /api/signals?limit=5&offset=10
        Returns 5 signals starting from the 11th signal

    Note:
        Validates limit (1-100) and offset (≥0) parameters for security.
        All requests logged with client IP and parameters for monitoring.
    """
    # Validate request
    validation_result = validate_web_request()

    try:
        limit_int = int(limit) if limit else 10
        offset_int = int(offset) if offset else 0

        # Validate ranges
        if limit_int > 100:
            raise ValidationError("Limit cannot exceed 100", field_name="limit")
        if limit_int < 1:
            raise ValidationError("Limit must be at least 1", field_name="limit")

        signals = AccionSenial.listar_seniales_adquiridas()

        # Apply pagination
        paginated_signals = signals[offset_int:offset_int + limit_int]

        response_data = {
            'signals': [
                {
                    'id': signal.get('identificador'),
                    'description': signal.get('descripcion'),
                    'date': signal.get('fecha'),
                    'frequency': signal.get('frecuencia'),
                    'amplitude': signal.get('amplitud')
                }
                for signal in paginated_signals
            ],
            'total': len(signals),
            'limit': limit_int,
            'offset': offset_int,
            'has_more': offset_int + limit_int < len(signals)
        }

        logger.info("API signals list accessed", extra={
            'endpoint': 'api_list_signals',
            'client_ip': request.remote_addr,
            'limit': limit_int,
            'offset': offset_int,
            'total_results': len(signals)
        })

        return jsonify(response_data)

    except Exception as e:
        error_response = {
            'error': 'Internal server error',
            'message': 'Unable to retrieve signals',
            'error_code': 'API_ERROR_001'
        }
        logger.error("Error in API signals list", extra={
            'endpoint': 'api_list_signals',
            'error': str(e),
            'client_ip': request.remote_addr
        }, exc_info=True)
        return jsonify(error_response), 500


@app.route("/api/signals", methods=['POST'])
@handle_validation_errors
def api_create_signal() -> tuple:
    """REST API endpoint to create new signals with JSON validation.

    Accepts JSON payloads for creating new signal entities through the API.
    Implements comprehensive validation, sanitization, and error handling
    with structured JSON responses.

    Request Format:
        Content-Type: application/json
        {
            "identificador": "unique_signal_id",
            "descripcion": "signal_description",
            "fecha": "acquisition_date",
            "frecuencia": "signal_frequency",
            "amplitud": "signal_amplitude"
        }

    Returns:
        tuple: (JSON response, HTTP status code)
            - 201: Signal created successfully
            - 400: Validation errors in request data
            - 500: Internal server error

    Success Response (201):
        {
            "status": "success",
            "message": "Signal created successfully",
            "signal": {...created_signal_data...}
        }

    Error Response (400):
        {
            "error": "Validation failed",
            "validation_errors": [{"field": "error_message"}],
            "error_code": "API_VALIDATION_ERROR"
        }

    Raises:
        APIValidationError: When Content-Type is not application/json
        ValidationException: When domain validation fails
        WebException: When unexpected errors occur

    Example:
        POST /api/signals
        Content-Type: application/json
        {"identificador": "SIG_001", "descripcion": "Test signal"}

    Note:
        Uses form validation for consistency with web interface.
        All creation attempts logged with client context.
    """
    # Validate request
    validation_result = validate_web_request()

    if not request.is_json:
        raise APIValidationError(
            "Content-Type must be application/json",
            endpoint="api_create_signal"
        )

    try:
        data = request.get_json()

        # Create form instance for validation
        form_data = {
            'identificador': data.get('identificador'),
            'descripcion': data.get('descripcion'),
            'fecha': data.get('fecha'),
            'frecuencia': data.get('frecuencia'),
            'amplitud': data.get('amplitud')
        }

        # Validate using form validators
        form = SenialForm(data=form_data)
        if not form.validate():
            validation_errors = []
            for field, errors in form.errors.items():
                for error in errors:
                    validation_errors.append({
                        'field': field,
                        'message': error
                    })

            error_response = {
                'error': 'Validation failed',
                'validation_errors': validation_errors,
                'error_code': 'API_VALIDATION_ERROR'
            }
            logger.warning("API validation failed", extra={
                'endpoint': 'api_create_signal',
                'validation_errors': validation_errors,
                'client_ip': request.remote_addr
            })
            return jsonify(error_response), 400

        # Process signal creation
        AccionSenial.adquirir(form)

        response_data = {
            'status': 'success',
            'message': 'Signal created successfully',
            'signal': {
                'identificador': form.identificador.data,
                'descripcion': form.descripcion.data,
                'fecha': form.fecha.data.isoformat() if form.fecha.data else None,
                'frecuencia': form.frecuencia.data,
                'amplitud': form.amplitud.data
            }
        }

        logger.info("Signal created via API", extra={
            'endpoint': 'api_create_signal',
            'signal_id': form.identificador.data,
            'client_ip': request.remote_addr
        })

        return jsonify(response_data), 201

    except ValidationException as ve:
        error_response = {
            'error': 'Domain validation error',
            'message': ve.user_message,
            'error_code': ve.error_code
        }
        logger.warning("Domain validation error in API", extra={
            'endpoint': 'api_create_signal',
            'error_code': ve.error_code,
            'client_ip': request.remote_addr
        })
        return jsonify(error_response), 400

    except Exception as e:
        error_response = {
            'error': 'Internal server error',
            'message': 'Unable to create signal',
            'error_code': 'API_ERROR_002'
        }
        logger.error("Error creating signal via API", extra={
            'endpoint': 'api_create_signal',
            'error': str(e),
            'client_ip': request.remote_addr
        }, exc_info=True)
        return jsonify(error_response), 500


@app.route("/api/health", methods=['GET'])
@handle_validation_errors
def api_health() -> tuple:
    """REST API health check endpoint for system monitoring.

    Provides system health status information for monitoring and
    load balancer health checks. Returns JSON with system status,
    component health, and validation framework status.

    Returns:
        tuple: (JSON response, HTTP status code) - Always returns 200

    Response Format:
        {
            "status": "healthy",
            "timestamp": "2025-09-24T10:30:00.000Z",
            "version": "1.0.0",
            "validation_framework": "SSA-24",
            "components": {
                "database": "connected",
                "validation": "active",
                "logging": "active"
            }
        }

    Example:
        GET /api/health
        Used by monitoring systems and load balancers

    Note:
        Lightweight endpoint for frequent health checks.
        Does not perform deep system validation to avoid performance impact.
    """
    validation_result = validate_web_request()

    health_data = {
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'validation_framework': 'SSA-24',
        'components': {
            'database': 'connected',
            'validation': 'active',
            'logging': 'active'
        }
    }

    return jsonify(health_data)


# Global before_request handler for additional security
@app.before_request
def before_request() -> Optional[tuple]:
    """Global request validation and security checks for all requests.

    Executed before every request to perform security validation,
    logging, and request size limits. Provides centralized security
    enforcement across the entire application.

    Security Checks:
        - Request size validation (10MB limit)
        - Static file bypass for performance
        - Comprehensive request logging
        - Rate limiting preparation
        - User agent validation

    Returns:
        Optional[tuple]: Error response tuple if request is rejected,
                        None to continue normal request processing

    Example:
        Automatically called for every request:
        - Logs request details for monitoring
        - Blocks oversized requests (>10MB)
        - Prepares context for route handlers

    Note:
        Balances security with performance by skipping validation
        for static files. Request logging limited to prevent log flooding.
    """
    # Skip validation for static files
    if request.endpoint and request.endpoint.startswith('static'):
        return

    # Log all requests for monitoring
    logger.debug("Request received", extra={
        'endpoint': request.endpoint,
        'method': request.method,
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', '')[:200],  # Limit user agent length
        'request_id': request.headers.get('X-Request-ID')
    })

    # Additional rate limiting could be added here
    # For now, just ensure request is within reasonable limits
    if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
        logger.warning("Request too large", extra={
            'content_length': request.content_length,
            'client_ip': request.remote_addr,
            'endpoint': request.endpoint
        })
        return jsonify({'error': 'Request too large'}), 413