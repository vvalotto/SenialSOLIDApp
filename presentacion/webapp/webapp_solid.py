from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, validators
import datetime
import adquisicion
import procesamiento
import modelo
import repositorios
import utilidades
from contenedor.configurador import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "dev-key-change-in-production"  # Should use environment variable
bootstrap = Bootstrap(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/general/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('/general/500.html'), 500


@app.route('/')
def inicio():
    return render_template('/general/inicio.html',)

@app.route('/versiones/')
def versiones():
    lista_componentes = []
    lista_componentes.append('Adquisidor: ' + adquisicion.__version__)
    lista_componentes.append('Procesador: ' + procesamiento.__version__)
    lista_componentes.append('Persistidor: ' + repositorios.__version__)
    lista_componentes.append('Configurador: ' + modelo.__version__)
    lista_componentes.append('Utilidades: ' + utilidades.__version__)
    return render_template('/aplicacion/versiones.html', lista=lista_componentes)


@app.route('/acerca/')
def acerca():
    return render_template('/general/acerca.html')


@app.route('/componentes/')
def componentes():
    lista_tipos_componentes = []
    lista_tipos_componentes.append("Tipo Adquisidor: " + str(Configurador.adquisidor.__class__))
    lista_tipos_componentes.append("Tipo Procesador: " + str(Configurador.procesador.__class__))
    lista_tipos_componentes.append("Tipo Señal (Adquisidor): " +
                                   str(Configurador.adquisidor._senial.__class__))
    lista_tipos_componentes.append("Tipo Señal (Procesador): " +
                                   str(Configurador.procesador._senial_procesada.__class__))
    lista_tipos_componentes.append("Tipo Repositorio (Adquisidor): " +
                                   str(Configurador.rep_adquisicion.__class__))
    lista_tipos_componentes.append("Tipo Repositorio (Procesador): " +
                                   str(Configurador.rep_procesamiento.__class__))
    lista_tipos_componentes.append("Tipo Contexto de Repositorio (Adquisidor): " +
                                   str(Configurador.ctx_datos_adquisicion.__class__))
    lista_tipos_componentes.append("Tipo Contexto de Repositorio (Procesador): " +
                                   str(Configurador.ctx_datos_procesamiento.__class__))
    return render_template('/aplicacion/componentes.html', lista=lista_tipos_componentes)


class SenialForm(FlaskForm):
    identificador = IntegerField('Identificador', [validators.DataRequired(),
                                                   validators.NumberRange(min=1, max=9999,
                                                                          message='Fuera de Rango')])
    descripcion = StringField('Descripcion', [validators.DataRequired()])
    fecha = DateField('Fecha Adquiscion', [validators.DataRequired()],
                      format='%d-%m-%Y', default=datetime.date.today())

    adquirir = SubmitField('Adquirir')

@app.route("/adquisicion/", methods=['GET', 'POST'])
def adquisicion():
    form = SenialForm()
    ad = Configurador.adquisidor
    ra = Configurador.rep_adquisicion
    valores = []
    bandera = False
    if form.validate_on_submit():
        try:
            ad.leer_senial()
            sa = ad.obtener_senial_adquirida()
            sa.id = form.identificador.data
            sa.comentario = form.descripcion.data
            sa.fecha_adquisicion = form.fecha.data
            ra.guardar(sa)
            valores = sa.valores
            bandera = True
            flash('Se Adquirio la señal')
        except Exception as ex:
            flash("Error: " + str(ex))
        # return redirect(url_for('adquisicion'))
    return render_template('aplicacion/adquisicion.html', form=form,
                           senial=valores, hay_valores=bandera)


@app.route("/procesamiento/")
def procesamiento():
    return render_template('aplicacion/procesamiento.html')


@app.route("/visualizacion/")
def visualizacion():
    return render_template('aplicacion/visualizacion.html')