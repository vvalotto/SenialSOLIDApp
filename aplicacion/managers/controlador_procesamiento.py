"""Application service for signal processing operations.

This module contains the ControladorProcesamiento application service that orchestrates
signal processing use cases by coordinating domain entities, signal processors, and
repositories. Implements transaction boundaries and comprehensive error handling
with recovery strategies from SSA-26.

The controller follows the Application Service pattern from DDD, providing
a facade for signal processing operations while maintaining separation between
domain logic and infrastructure concerns.
"""

from typing import Optional, List, Any
from contenedor.configurador import *
from modelo.senial import *
from config.logging_config import get_logger
from exceptions import ProcessingException, RepositoryException, ValidationException
from exceptions.exception_handler import handle_with_recovery, get_exception_handler

logger = get_logger(__name__)


class ControladorProcesamiento:
    """Application service for signal processing and management operations.

    Orchestrates signal processing use cases by coordinating domain objects,
    signal processors, and repositories. Implements transaction boundaries
    and error handling with recovery strategies from SSA-26.

    This service handles the complete signal processing workflow:
        - Signal processing using configured processors
        - Processed signal identification and metadata management
        - Processed signal persistence and retrieval operations
        - Processed signal listing and search operations

    The controller integrates with:
        - Configurador: DI container providing processing and repository services
        - Exception handlers: SSA-26 error handling with recovery patterns
        - Logging: Structured logging for operations monitoring
        - Domain entities: Senial for signal representation

    Dependencies:
        All dependencies are injected through the Configurador DI container:
        - procesador: Signal processing implementation
        - rep_procesamiento: Repository for processed signal persistence

    Example:
        Basic signal processing workflow:

        >>> controller = ControladorProcesamiento()
        >>> raw_signal = acquire_signal()  # From acquisition controller
        >>> processed = controller.procesar_senial(raw_signal)
        >>> controller.identificar_senial(processed, "Filtered Signal")
        >>> controller.guardar_senial(processed)
        >>> signals = controller.listar_seniales_procesadas()
        >>> print(f"Total processed signals: {len(signals)}")
        Total processed signals: 1
    """

    def __init__(self) -> None:
        """Initialize the processing controller.

        No explicit dependencies required as all services are obtained
        through the Configurador dependency injection container.

        Note:
            The controller relies on Configurador being properly configured
            with procesador and rep_procesamiento services before use.
        """
        pass

    def procesar_senial(self, senial: Senial) -> Senial:
        """Process a signal using the configured processor.

        Coordinates the signal processing operation using the configured
        procesador from the DI container and applies exception handling
        with automatic recovery strategies from SSA-26.

        Use Case Flow:
            1. Get configured procesador from DI container
            2. Execute signal processing operation
            3. Retrieve processed signal with results
            4. Apply error handling and recovery if needed

        Args:
            senial: Input signal to be processed

        Returns:
            Senial: Processed signal with transformation results

        Raises:
            ProcessingException: When signal processing fails after retries
            ValidationException: When input signal doesn't meet processing constraints
            ConfigurationException: When procesador is not properly configured

        Example:
            >>> controller = ControladorProcesamiento()
            >>> raw_signal = get_acquired_signal()
            >>> processed = controller.procesar_senial(raw_signal)
            >>> print(f"Processed {processed.cantidad} values")
            Processed 100 values

        Note:
            This method uses automatic retry mechanisms. If processing fails
            temporarily, it will be retried up to 2 times with recovery strategies.
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

    def identificar_senial(self, senial: Senial, titulo: str) -> None:
        """Interactively identify and set processed signal metadata.

        Prompts the user to provide identification and description for the
        processed signal. Continues prompting until the user confirms the
        entered information. Updates the signal's ID and comentario properties.

        Args:
            senial: Processed signal entity to be identified and updated
            titulo: Title/context to display during identification process

        Raises:
            ValueError: When user enters invalid ID format (handled internally)

        Example:
            >>> processed_signal = controller.procesar_senial(raw_signal)
            >>> controller.identificar_senial(processed_signal, "Filtered Temperature")
            # User interaction follows...
            >>> print(f"Processed Signal: {processed_signal.comentario}")
            Processed Signal: Filtered temperature from sensor A

        Note:
            This method contains blocking user interaction for processed signals.
            Distinguished from raw signal identification by context and logging.
        """

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
            
    def obtener_senial(self, id_senial: Any) -> Senial:
        """Retrieve processed signal by ID from the processing repository.

        Fetches a previously stored processed signal from the configured processing
        repository using the provided identifier. Applies SSA-26 recovery
        strategies for transient repository failures.

        Args:
            id_senial: Unique identifier for the processed signal to retrieve

        Returns:
            Senial: The processed signal entity with the specified ID

        Raises:
            RepositoryException: When processed signal cannot be retrieved after retries
            ValidationException: When signal ID is invalid or not found

        Example:
            >>> signal = controller.obtener_senial("PROC_001")
            >>> print(f"Retrieved processed signal: {signal.comentario}")
            Retrieved processed signal: Filtered temperature readings

        Note:
            Uses automatic retry mechanism with up to 3 attempts for
            repository operations. Distinguished from raw signals by repository.
        """
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
        
    def guardar_senial(self, senial: Senial) -> None:
        """Persist processed signal to the configured processing repository.

        Saves the provided processed signal using the repository pattern while
        applying SSA-26 exception handling and recovery strategies.
        Maintains transaction boundaries for data consistency.

        Args:
            senial: Processed signal entity to persist, must have valid ID and data

        Raises:
            RepositoryException: When persistence operation fails after retries
            ValidationException: When processed signal state is invalid for persistence
            DataAccessException: When underlying storage is unavailable

        Example:
            >>> processed = controller.procesar_senial(raw_signal)
            >>> processed.id = "PROC_001"
            >>> controller.guardar_senial(processed)

        Note:
            The processed signal must have a valid ID before saving. Uses automatic
            retry with up to 3 attempts for transient storage failures.
        """
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

    def listar_seniales_procesadas(self) -> List[Senial]:
        """List all processed signals from the processing repository.

        Retrieves a list of all processed signals previously stored in the
        processing repository. Applies SSA-26 recovery strategies for repository access.

        Returns:
            List[Senial]: List of all processed signals, empty list if none exist

        Raises:
            RepositoryException: When listing operation fails after retries
            DataAccessException: When processing repository is unavailable

        Example:
            >>> signals = controller.listar_seniales_procesadas()
            >>> print(f"Found {len(signals)} processed signals")
            Found 3 processed signals
            >>> for signal in signals:
            ...     print(f"- {signal.id}: {signal.comentario}")
            - PROC_001: Filtered temperature
            - PROC_002: Smoothed pressure

        Note:
            Returns empty list if no processed signals are found. Distinguished
            from raw signals by processing repository.
        """
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
