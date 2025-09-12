from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from config import config
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
    print("✅ SSA-21 Performance optimizations would be available")
    print("⚠️ Currently disabled to resolve CSS loading issues")
else:
    print("⚠️ SSA-21 Performance middleware disabled for CSS compatibility")

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
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
    app.run(debug=debug_mode, port=5001)