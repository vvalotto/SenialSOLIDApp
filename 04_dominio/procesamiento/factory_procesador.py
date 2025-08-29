from procesamiento.procesador import *


class FactoryProcesador(object):

    def __int__(self):
        pass

    @staticmethod
    def obtener_procesador(tipo_procesador, senial, param):
        try:
            procesador = None
            if tipo_procesador == 'basico':
                procesador = Procesador(senial)

            elif tipo_procesador == 'umbral':
                umbral = int(param[0])
                procesador = ProcesadorConUmbral(senial, umbral)

            return procesador
        except Exception as ex:
            raise ex