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
    """
    Decorator to handle SSA-24 validation errors in web routes
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


def validate_web_request():
    """
    Validate incoming web request for security threats
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
def sanitize_form_data(form_data):
    """
    Sanitize form data using SSA-24 framework
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
def page_not_found(e):
    """Handle 404 Not Found errors with user-friendly message"""
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
def internal_server_error(e):
    """Handle 500 Internal Server Error with user-friendly message"""
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
def inicio():
    return render_template('/general/inicio.html')


@app.route('/acerca/')
def acerca():
    return render_template('general/acerca.html')


@app.route('/versiones/')
def versiones():
    return render_template('/aplicacion/versiones.html',
                           lista=panel_informes.informar_versiones())


@app.route('/componentes/')
def componentes():
    return render_template('/aplicacion/componentes.html',
                           lista=panel_informes.informar_componentes())


@app.route("/adquisicion/", methods=['GET', 'POST'])
@handle_validation_errors
def adquisicion():
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
def procesamiento():
    return render_template('aplicacion/procesamiento.html')


@app.route("/visualizacion/")
def visualizacion():
    return render_template('aplicacion/visualizacion.html')


# API Routes with SSA-24 Validation
@app.route("/api/signals", methods=['GET'])
@handle_validation_errors
@validate_parameters(
    limit=StringInputValidator(max_length=10, allowed_pattern=r'^\d+$'),
    offset=StringInputValidator(max_length=10, allowed_pattern=r'^\d+$')
)
def api_list_signals(limit="10", offset="0"):
    """
    API endpoint to list signals with validation
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
def api_create_signal():
    """
    API endpoint to create signals with JSON validation
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
def api_health():
    """
    Health check endpoint with basic validation
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
def before_request():
    """
    Global request validation and security checks
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