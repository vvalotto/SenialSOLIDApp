from flask import Flask, render_template, flash, redirect, url_for, request
from flask_bootstrap import Bootstrap
from webapp.modelos  import *
from webapp.forms import *
from config import config
import os
from exceptions import (
    ValidationException, AcquisitionException, ProcessingException,
    RepositoryException, WebException, ConfigurationException
)
from config.logging_config import get_logger

logger = get_logger(__name__)

# SECURITY FIX: Removed hardcoded SECRET_KEY "Victor" 
# Now using secure configuration management

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
def adquisicion():
    form = SenialForm()
    if form.validate():
        try:
            AccionSenial.adquirir(form)
            flash('Señal adquirida exitosamente', 'success')
            logger.info("Señal adquirida desde interfaz web", extra={
                "form_data": form.data if hasattr(form, 'data') else {},
                "endpoint": "adquisicion"
            })
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
                context={"form_data": form.data if hasattr(form, 'data') else {}},
                cause=ex
            )
            flash(f"Error: {web_error.user_message}", 'error')
            logger.error("Error inesperado en adquisición web", extra=web_error.context, exc_info=True)
        return redirect(url_for('adquisicion'))
    return render_template('aplicacion/adquisicion.html', form=form,
                           seniales=AccionSenial.listar_seniales_adquiridas())

@app.route("/procesamiento/")
def procesamiento():
    return render_template('aplicacion/procesamiento.html')


@app.route("/visualizacion/")
def visualizacion():
    return render_template('aplicacion/visualizacion.html')