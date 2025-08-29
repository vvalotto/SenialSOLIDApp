from contenedor.configurador import *
from modelo.senial import *


class ControladorAdquisicion(object):

    def __init__(self):
        pass

    def adquirir_senial(self):
        """
        Adquirir la senial
        """
        try:
            a = Configurador.adquisidor
            a.leer_senial()
            return a.obtener_senial_adquirida()
        except Exception as exAdq:
            raise exAdq

    def identificar_senial(self, senial, titulo):

        opcion = 'N'
        while opcion != 'S':
            print('> ' + titulo)
            while True:
                try:
                    senial.id = int(input('      > Identificación de la señal (numero): '))
                    break
                except ValueError:
                    print("Error, debe ser un numero entero.")
            senial.comentario = input('      > Descripción: ')
            opcion = input('Acepta Ingreso (S/N): ')

    def obtener_senial(self, id_senial):
        try:
            rep = Configurador.rep_adquisicion
            return rep.obtener(Senial(), id_senial)
        except Exception as ex:
            raise ex

    def guardar_senial(self, senial):
        try:
            rep = Configurador.rep_adquisicion
            rep.guardar(senial)
            return
        except Exception as ex:
            raise ex

    def listar_seniales_adquiridas(self):
        try:
            rep = Configurador.rep_adquisicion
            return rep.listar()
        except Exception as ex:
            raise ex
