from contenedor.configurador import *
from modelo.senial import *
from config.logging_config import get_logger

logger = get_logger(__name__)


class ControladorProcesamiento(object):

    def __init__(self):
        pass

    def procesar_senial(self, senial):
        """
        Procesar la senial
        """
        logger.info("Iniciando procesamiento de señal", extra={"senial_id": getattr(senial, 'id', 'unknown')})
        try:
            p = Configurador.procesador
            p.procesar(senial)
            senial_procesada = p.obtener_senial_procesada()
            logger.info("Señal procesada exitosamente", extra={"senial_id": getattr(senial, 'id', 'unknown')})
            return senial_procesada
        except Exception as exAdq:
            logger.error("Error durante procesamiento de señal", extra={"senial_id": getattr(senial, 'id', 'unknown')}, exc_info=True)
            raise exAdq

    def identificar_senial(self, senial, titulo):

        opcion = 'N'
        while opcion != 'S':
            logger.info("Solicitando identificación de señal procesada", extra={"titulo": titulo})
            while True:
                try:
                    senial.id = int(input('      > Identificación de la señal (numero): '))
                    break
                except ValueError:
                    logger.warning("Error de entrada: se esperaba número entero para ID de señal procesada")
            senial.comentario = input('      > Descripción: ')
            opcion = input('Acepta Ingreso (S/N): ')
            
    def obtener_senial(self, id_senial):
        logger.debug("Obteniendo señal procesada", extra={"id_senial": id_senial})
        try:
            rep = Configurador.rep_procesamiento
            senial = rep.obtener(Senial(), id_senial)
            logger.info("Señal procesada obtenida exitosamente", extra={"id_senial": id_senial})
            return senial
        except Exception as ex:
            logger.error("Error obteniendo señal procesada", extra={"id_senial": id_senial}, exc_info=True)
            raise ex
        
    def guardar_senial(self, senial):
        logger.info("Guardando señal procesada", extra={"senial_id": getattr(senial, 'id', 'unknown')})
        try:
            rep = Configurador.rep_procesamiento
            rep.guardar(senial)
            logger.info("Señal procesada guardada exitosamente", extra={"senial_id": getattr(senial, 'id', 'unknown')})
            return
        except Exception as ex:
            logger.error("Error guardando señal procesada", extra={"senial_id": getattr(senial, 'id', 'unknown')}, exc_info=True)
            raise ex

    def listar_seniales_procesadas(self):
        logger.debug("Listando señales procesadas")
        try:
            rep = Configurador.rep_procesamiento
            seniales = rep.listar()
            logger.info("Lista de señales procesadas obtenida", extra={"cantidad": len(seniales) if seniales else 0})
            return seniales
        except Exception as ex:
            logger.error("Error listando señales procesadas", exc_info=True)
            raise ex
