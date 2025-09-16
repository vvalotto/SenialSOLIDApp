from contenedor.configurador import *
from modelo.senial import *
from config.logging_config import get_logger
from exceptions import AcquisitionException, RepositoryException, ValidationException
from exceptions.exception_handler import handle_with_recovery, get_exception_handler

logger = get_logger(__name__)


class ControladorAdquisicion(object):

    def __init__(self):
        pass

    def adquirir_senial(self):
        """
        Adquirir la senial
        """
        logger.info("Iniciando adquisición de señal")
        def _realizar_adquisicion():
            """Internal function for acquisition with recovery support"""
            a = Configurador.adquisidor
            a.leer_senial()
            senial = a.obtener_senial_adquirida()
            logger.info("Señal adquirida exitosamente", extra={
                "cantidad_valores": senial.cantidad if hasattr(senial, 'cantidad') else 'unknown',
                "signal_id": getattr(senial, 'id', 'unknown')
            })
            return senial

        try:
            return handle_with_recovery(
                operation=_realizar_adquisicion,
                operation_name="adquirir_senial",
                context={"adquisidor_tipo": type(Configurador.adquisidor).__name__},
                max_attempts=2  # Limited retries for acquisition
            )
        except (AcquisitionException, ValidationException):
            # Re-raise domain exceptions as-is
            raise
        except Exception as ex:
            # Wrap unexpected exceptions
            raise AcquisitionException(
                source="configurador_adquisidor",
                source_type="system",
                acquisition_method="controller_managed",
                context={"adquisidor_tipo": type(Configurador.adquisidor).__name__},
                cause=ex
            )

    def identificar_senial(self, senial, titulo):

        opcion = 'N'
        while opcion != 'S':
            logger.info("Solicitando identificación de señal", extra={"titulo": titulo})
            while True:
                try:
                    senial.id = int(input('      > Identificación de la señal (numero): '))
                    break
                except ValueError as ve:
                    logger.warning("Error de entrada: se esperaba número entero para ID de señal")
                    print("Error: Por favor ingrese un número entero válido para el ID.")
                    # Don't raise here, continue the loop for user input
            senial.comentario = input('      > Descripción: ')
            opcion = input('Acepta Ingreso (S/N): ')

    def obtener_senial(self, id_senial):
        logger.debug("Obteniendo señal", extra={"id_senial": id_senial})
        def _obtener_desde_repo():
            """Internal function for repository access with recovery support"""
            rep = Configurador.rep_adquisicion
            senial = rep.obtener(Senial(), id_senial)
            logger.info("Señal obtenida exitosamente", extra={"id_senial": id_senial})
            return senial

        try:
            return handle_with_recovery(
                operation=_obtener_desde_repo,
                operation_name="obtener_senial",
                context={
                    "id_senial": id_senial,
                    "repository_type": type(Configurador.rep_adquisicion).__name__
                },
                max_attempts=3  # Allow retries for repository operations
            )
        except RepositoryException:
            # Re-raise repository exceptions as-is
            raise
        except Exception as ex:
            # Wrap unexpected exceptions
            raise RepositoryException(
                operation="obtener",
                entity_type="senial",
                entity_id=id_senial,
                context={"repository_type": type(Configurador.rep_adquisicion).__name__},
                cause=ex
            )

    def guardar_senial(self, senial):
        logger.info("Guardando señal", extra={"senial_id": getattr(senial, 'id', 'unknown')})
        def _guardar_en_repo():
            """Internal function for repository save with recovery support"""
            rep = Configurador.rep_adquisicion
            rep.guardar(senial)
            logger.info("Señal guardada exitosamente", extra={"senial_id": getattr(senial, 'id', 'unknown')})

        signal_id = getattr(senial, 'id', 'unknown')
        try:
            return handle_with_recovery(
                operation=_guardar_en_repo,
                operation_name="guardar_senial",
                context={
                    "senial_id": signal_id,
                    "repository_type": type(Configurador.rep_adquisicion).__name__,
                    "senial_cantidad": getattr(senial, '_cantidad', 0)
                },
                max_attempts=3  # Allow retries for save operations
            )
        except RepositoryException:
            # Re-raise repository exceptions as-is
            raise
        except Exception as ex:
            # Wrap unexpected exceptions
            raise RepositoryException(
                operation="guardar",
                entity_type="senial",
                entity_id=signal_id,
                context={
                    "repository_type": type(Configurador.rep_adquisicion).__name__,
                    "senial_cantidad": getattr(senial, '_cantidad', 0)
                },
                cause=ex
            )

    def listar_seniales_adquiridas(self):
        logger.debug("Listando señales adquiridas")
        def _listar_desde_repo():
            """Internal function for repository listing with recovery support"""
            rep = Configurador.rep_adquisicion
            seniales = rep.listar()
            logger.info("Lista de señales obtenida", extra={"cantidad": len(seniales) if seniales else 0})
            return seniales

        try:
            return handle_with_recovery(
                operation=_listar_desde_repo,
                operation_name="listar_seniales",
                context={"repository_type": type(Configurador.rep_adquisicion).__name__},
                max_attempts=3  # Allow retries for listing operations
            )
        except RepositoryException:
            # Re-raise repository exceptions as-is
            raise
        except Exception as ex:
            # Wrap unexpected exceptions
            raise RepositoryException(
                operation="listar",
                entity_type="senial",
                context={"repository_type": type(Configurador.rep_adquisicion).__name__},
                cause=ex
            )
