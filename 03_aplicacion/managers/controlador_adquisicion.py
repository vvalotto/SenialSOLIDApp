from contenedor.configurador import *
from modelo.senial import *
from config.logging_config import get_logger

logger = get_logger(__name__)


class ControladorAdquisicion(object):

    def __init__(self):
        pass

    def adquirir_senial(self):
        """
        Adquirir la senial
        """
        logger.info("Iniciando adquisición de señal")
        try:
            a = Configurador.adquisidor
            a.leer_senial()
            senial = a.obtener_senial_adquirida()
            logger.info("Señal adquirida exitosamente", extra={"cantidad_valores": senial.cantidad if hasattr(senial, 'cantidad') else 'unknown'})
            return senial
        except Exception as exAdq:
            logger.error("Error durante adquisición de señal", exc_info=True)
            raise exAdq

    def identificar_senial(self, senial, titulo):

        opcion = 'N'
        while opcion != 'S':
            logger.info("Solicitando identificación de señal", extra={"titulo": titulo})
            while True:
                try:
                    senial.id = int(input('      > Identificación de la señal (numero): '))
                    break
                except ValueError:
                    logger.warning("Error de entrada: se esperaba número entero para ID de señal")
            senial.comentario = input('      > Descripción: ')
            opcion = input('Acepta Ingreso (S/N): ')

    def obtener_senial(self, id_senial):
        logger.debug("Obteniendo señal", extra={"id_senial": id_senial})
        try:
            rep = Configurador.rep_adquisicion
            senial = rep.obtener(Senial(), id_senial)
            logger.info("Señal obtenida exitosamente", extra={"id_senial": id_senial})
            return senial
        except Exception as ex:
            logger.error("Error obteniendo señal", extra={"id_senial": id_senial}, exc_info=True)
            raise ex

    def guardar_senial(self, senial):
        logger.info("Guardando señal", extra={"senial_id": getattr(senial, 'id', 'unknown')})
        try:
            rep = Configurador.rep_adquisicion
            rep.guardar(senial)
            logger.info("Señal guardada exitosamente", extra={"senial_id": getattr(senial, 'id', 'unknown')})
            return
        except Exception as ex:
            logger.error("Error guardando señal", extra={"senial_id": getattr(senial, 'id', 'unknown')}, exc_info=True)
            raise ex

    def listar_seniales_adquiridas(self):
        logger.debug("Listando señales adquiridas")
        try:
            rep = Configurador.rep_adquisicion
            seniales = rep.listar()
            logger.info("Lista de señales obtenida", extra={"cantidad": len(seniales) if seniales else 0})
            return seniales
        except Exception as ex:
            logger.error("Error listando señales adquiridas", exc_info=True)
            raise ex
