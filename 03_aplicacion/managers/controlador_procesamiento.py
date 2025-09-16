from contenedor.configurador import *
from modelo.senial import *
from config.logging_config import get_logger
from exceptions import ProcessingException, RepositoryException, ValidationException
from exceptions.exception_handler import handle_with_recovery, get_exception_handler

logger = get_logger(__name__)


class ControladorProcesamiento(object):

    def __init__(self):
        pass

    def procesar_senial(self, senial):
        """
        Procesar la senial
        """
        logger.info("Iniciando procesamiento de señal", extra={"senial_id": getattr(senial, 'id', 'unknown')})
        signal_id = getattr(senial, 'id', 'unknown')
        signal_count = getattr(senial, '_cantidad', 0)

        def _realizar_procesamiento():
            """Internal function for signal processing with recovery support"""
            p = Configurador.procesador
            p.procesar(senial)
            senial_procesada = p.obtener_senial_procesada()
            logger.info("Señal procesada exitosamente", extra={
                "senial_id": signal_id,
                "procesador_tipo": type(p).__name__,
                "valores_procesados": getattr(senial_procesada, '_cantidad', 0)
            })
            return senial_procesada

        try:
            return handle_with_recovery(
                operation=_realizar_procesamiento,
                operation_name="procesar_senial",
                context={
                    "senial_id": signal_id,
                    "valores_entrada": signal_count,
                    "procesador_tipo": type(Configurador.procesador).__name__
                },
                max_attempts=2  # Limited retries for processing
            )
        except ProcessingException:
            # Re-raise processing exceptions as-is (may include fallback processing)
            raise
        except Exception as ex:
            # Wrap unexpected exceptions
            raise ProcessingException(
                operation="procesar_senial",
                signal_id=signal_id,
                processing_stage="controller_managed",
                context={
                    "valores_entrada": signal_count,
                    "procesador_tipo": type(Configurador.procesador).__name__
                },
                cause=ex
            )

    def identificar_senial(self, senial, titulo):

        opcion = 'N'
        while opcion != 'S':
            logger.info("Solicitando identificación de señal procesada", extra={"titulo": titulo})
            while True:
                try:
                    senial.id = int(input('      > Identificación de la señal (numero): '))
                    break
                except ValueError as ve:
                    logger.warning("Error de entrada: se esperaba número entero para ID de señal procesada")
                    print("Error: Por favor ingrese un número entero válido para el ID.")
                    # Don't raise here, continue the loop for user input
            senial.comentario = input('      > Descripción: ')
            opcion = input('Acepta Ingreso (S/N): ')
            
    def obtener_senial(self, id_senial):
        logger.debug("Obteniendo señal procesada", extra={"id_senial": id_senial})
        def _obtener_desde_repo():
            """Internal function for repository access with recovery support"""
            rep = Configurador.rep_procesamiento
            senial = rep.obtener(Senial(), id_senial)
            logger.info("Señal procesada obtenida exitosamente", extra={"id_senial": id_senial})
            return senial

        try:
            return handle_with_recovery(
                operation=_obtener_desde_repo,
                operation_name="obtener_senial_procesada",
                context={
                    "id_senial": id_senial,
                    "repository_type": type(Configurador.rep_procesamiento).__name__
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
                entity_type="senial_procesada",
                entity_id=id_senial,
                context={"repository_type": type(Configurador.rep_procesamiento).__name__},
                cause=ex
            )
        
    def guardar_senial(self, senial):
        logger.info("Guardando señal procesada", extra={"senial_id": getattr(senial, 'id', 'unknown')})
        def _guardar_en_repo():
            """Internal function for repository save with recovery support"""
            rep = Configurador.rep_procesamiento
            rep.guardar(senial)
            logger.info("Señal procesada guardada exitosamente", extra={"senial_id": getattr(senial, 'id', 'unknown')})

        signal_id = getattr(senial, 'id', 'unknown')
        try:
            return handle_with_recovery(
                operation=_guardar_en_repo,
                operation_name="guardar_senial_procesada",
                context={
                    "senial_id": signal_id,
                    "repository_type": type(Configurador.rep_procesamiento).__name__,
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
                entity_type="senial_procesada",
                entity_id=signal_id,
                context={
                    "repository_type": type(Configurador.rep_procesamiento).__name__,
                    "senial_cantidad": getattr(senial, '_cantidad', 0)
                },
                cause=ex
            )

    def listar_seniales_procesadas(self):
        logger.debug("Listando señales procesadas")
        def _listar_desde_repo():
            """Internal function for repository listing with recovery support"""
            rep = Configurador.rep_procesamiento
            seniales = rep.listar()
            logger.info("Lista de señales procesadas obtenida", extra={"cantidad": len(seniales) if seniales else 0})
            return seniales

        try:
            return handle_with_recovery(
                operation=_listar_desde_repo,
                operation_name="listar_seniales_procesadas",
                context={"repository_type": type(Configurador.rep_procesamiento).__name__},
                max_attempts=3  # Allow retries for listing operations
            )
        except RepositoryException:
            # Re-raise repository exceptions as-is
            raise
        except Exception as ex:
            # Wrap unexpected exceptions
            raise RepositoryException(
                operation="listar",
                entity_type="senial_procesada",
                context={"repository_type": type(Configurador.rep_procesamiento).__name__},
                cause=ex
            )
