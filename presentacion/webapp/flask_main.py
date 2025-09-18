from flask import Flask, render_template, session, redirect, url_for, flash, request, g
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
import time
import uuid
from config import config
from config.logging_config import get_logger, LoggerFactory

# Configurar logging
LoggerFactory.setup(console_output=True)
logger = get_logger(__name__)
# SSA-21 Performance Integration (DISABLED due to CSS loading compatibility issues)
PERFORMANCE_AVAILABLE = False  # Temporarily disabled for CSS compatibility

# SECURITY FIX: Removed hardcoded SECRET_KEY "Victor" 
# Now using secure configuration management

basedir = os.path.abspath(os.path.dirname(__file__))

# Get configuration environment (default: development)
config_name = os.environ.get('FLASK_ENV', 'development')

app = Flask(__name__)
# SECURITY: Load configuration from secure config module
app.config.from_object(config[config_name])
# SECURITY: Initialize and validate configuration
config[config_name].init_app(app)

# SSA-21: Performance optimizations temporarily disabled for CSS compatibility
if PERFORMANCE_AVAILABLE:
    logger.info("SSA-21 Performance optimizations available but disabled", extra={"reason": "CSS loading compatibility issues"})
else:
    logger.warning("SSA-21 Performance middleware disabled", extra={"reason": "CSS compatibility"})

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# Middleware de logging para requests
@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

    # Log del request entrante
    logger.info("Request iniciado", extra={
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "ip": request.remote_addr,
        "user_agent": request.user_agent.string,
        "args": dict(request.args),
        "form_data": dict(request.form) if request.method == 'POST' else None,
        "session_id": session.get('_id', 'no_session')
    })

@app.after_request
def after_request(response):
    # Calcular tiempo de procesamiento
    processing_time = time.time() - g.start_time

    # Log del response
    logger.info("Request completado", extra={
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
        "processing_time_ms": round(processing_time * 1000, 2),
        "response_size": len(response.get_data()) if response.get_data() else 0
    })

    return response

@app.errorhandler(404)
def page_not_found(e):
    logger.warning("Página no encontrada", extra={
        "path": request.path,
        "method": request.method,
        "ip": request.remote_addr,
        "user_agent": request.user_agent.string
    })
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    logger.error("Error interno del servidor", extra={
        "path": request.path,
        "method": request.method,
        "ip": request.remote_addr,
        "user_agent": request.user_agent.string
    }, exc_info=True)
    return render_template('500.html'), 500


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submi')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Parace que cambiaste el nombre')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# Add basic routes for menu functionality
@app.route('/acerca/')
def acerca():
    return render_template('general/acerca.html')


@app.route('/componentes/')
def componentes():
    lista_tipos_componentes = [
        "Demo: Componentes del sistema",
        "Esta página requiere integración completa con el sistema DDD"
    ]
    return render_template('aplicacion/componentes.html', lista=lista_tipos_componentes)


@app.route('/versiones/')
def versiones():
    lista_versiones = [
        "Flask: 3.0.0",
        "Bootstrap: 4.0.0",
        "Python: 3.11+"
    ]
    return render_template('aplicacion/versiones.html', lista=lista_versiones)


@app.route("/adquisicion/", methods=['GET', 'POST'])
def adquisicion():
    from forms import SenialForm
    form = SenialForm()
    seniales_demo = []

    if form.validate_on_submit():
        logger.info("Señal demo adquirida", extra={
            "request_id": getattr(g, 'request_id', 'unknown'),
            "identificador": form.identificador.data,
            "session_id": session.get('_id', 'no_session')
        })
        flash('Señal demo adquirida exitosamente')
        seniales_demo.append(f"ID: {form.identificador.data}")
        return redirect(url_for('adquisicion'))

    return render_template('aplicacion/adquisicion.html', form=form, seniales=seniales_demo)


@app.route("/procesamiento/")
def procesamiento():
    return render_template('aplicacion/procesamiento.html')


@app.route("/visualizacion/")
def visualizacion():
    return render_template('aplicacion/visualizacion.html')


if __name__ == '__main__':
    # SECURITY: Debug mode now controlled by environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    logger.info("Iniciando aplicación Flask", extra={
        "debug_mode": debug_mode,
        "port": 5001,
        "config_env": config_name
    })
    app.run(debug=debug_mode, port=5001)