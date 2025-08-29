"""
Fabrica de tipos de adquisidor
"""
from adquisicion.adquisidor import *

class FactoryAdquisidor(object):

    def __int__(self):
        pass

    @staticmethod
    def obtener_adquisidor(tipo_adquisidor, senial, params):

        adquisidor = None
        if tipo_adquisidor == 'simple':
            adquisidor = AdquisidorSimple(senial)

        elif tipo_adquisidor == 'archivo':
            ubicacion = str(params[0])
            adquisidor = AdquisidorArchivo(senial, ubicacion)

        elif tipo_adquisidor == 'senoidal':
            adquisidor = AdquisidorSenoidal(senial)

        return adquisidor