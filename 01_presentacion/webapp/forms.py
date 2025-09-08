
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, validators
import datetime


class SenialForm(FlaskForm):
    identificador = IntegerField('Identificador', [validators.DataRequired(),
                                                   validators.NumberRange(min=1, max=9999,
                                                                          message='Fuera de Rango')])
    descripcion = StringField('Descripción', [validators.DataRequired()])
    fecha = DateField('Fecha Adquisción', [validators.DataRequired()],
                      format='%d-%m-%Y', default=datetime.date.today())

    adquirir = SubmitField('Adquirir')
