from contenedor.configurador import *
from modelo.senial import *


class ControladorProcesamiento(object):

    def __init__(self):
        pass

    def procesar_senial(self, senial):
        """
        Adquirir la senial
        """
        try:
            p = Configurador.procesador
            p.procesar(senial)
            return p.obtener_senial_procesada()
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
            rep = Configurador.rep_procesamiento
            return rep.obtener(Senial(), id_senial)      
        except Exception as ex:
            raise ex
        
    def guardar_senial(self, senial):
        try:
            rep = Configurador.rep_procesamiento
            rep.guardar(senial)
            return
        except Exception as ex:
            raise ex

    def listar_seniales_procesadas(self):
        try:
            rep = Configurador.rep_procesamiento
            return rep.listar()
        except Exception as ex:
            raise ex
