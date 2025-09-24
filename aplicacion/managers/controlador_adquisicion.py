"""Application service for signal acquisition operations.

This module contains the ControladorAdquisicion application service that orchestrates
signal acquisition use cases by coordinating domain entities, repositories, and
external acquisition sources. Implements transaction boundaries and comprehensive
error handling with recovery strategies from SSA-26.

The controller follows the Application Service pattern from DDD, providing
a facade for signal acquisition operations while maintaining separation
between domain logic and infrastructure concerns.
"""

from typing import Optional, List, Any
from contenedor.configurador import *
from modelo.senial import *
from config.logging_config import get_logger
from exceptions import AcquisitionException, RepositoryException, ValidationException
from exceptions.exception_handler import handle_with_recovery, get_exception_handler

logger = get_logger(__name__)


class ControladorAdquisicion:
    """Application service for signal acquisition and management operations.

    Orchestrates signal acquisition use cases by coordinating domain objects,
    repositories, and external acquisition sources. Implements transaction
    boundaries and error handling with recovery strategies from SSA-26.

    This service handles the complete signal acquisition workflow:
        - Signal acquisition from configured sources
        - Signal identification and metadata management
        - Signal persistence and retrieval operations
        - Signal listing and search operations

    The controller integrates with:
        - Configurador: DI container providing acquisition and repository services
        - Exception handlers: SSA-26 error handling with recovery patterns
        - Logging: Structured logging for operations monitoring
        - Domain entities: Senial and its variants for signal representation

    Dependencies:
        All dependencies are injected through the Configurador DI container:
        - adquisidor: Signal acquisition implementation
        - rep_adquisicion: Repository for signal persistence

    Example:
        Basic signal acquisition workflow:

        >>> controller = ControladorAdquisicion()
        >>> signal = controller.adquirir_senial()
        >>> controller.identificar_senial(signal, "Temperature Sensor")
        >>> controller.guardar_senial(signal)
        >>> signals = controller.listar_seniales_adquiridas()
        >>> print(f"Total signals: {len(signals)}")
        Total signals: 1
    """

    def __init__(self) -> None:
        """Initialize the acquisition controller.

        No explicit dependencies required as all services are obtained
        through the Configurador dependency injection container.

        Note:
            The controller relies on Configurador being properly configured
            with adquisidor and rep_adquisicion services before use.
        """
        pass

    def adquirir_senial(self) -> Senial:
        """Acquire a signal from the configured acquisition source.

        Coordinates the signal acquisition process using the configured
        adquisidor from the DI container and applies exception handling
        with automatic recovery strategies from SSA-26.

        Use Case Flow:
            1. Get configured adquisidor from DI container
            2. Execute signal reading operation
            3. Retrieve acquired signal with metadata
            4. Apply error handling and recovery if needed

        Returns:
            Senial: Newly acquired signal with basic metadata

        Raises:
            AcquisitionException: When signal acquisition fails after retries
            ValidationException: When acquired signal doesn't meet constraints
            ConfigurationException: When adquisidor is not properly configured

        Example:
            >>> controller = ControladorAdquisicion()
            >>> signal = controller.adquirir_senial()
            >>> print(f"Acquired signal with {signal.cantidad} values")
            Acquired signal with 50 values

        Note:
            This method uses automatic retry mechanisms. If acquisition fails
            temporarily, it will be retried up to 2 times with recovery strategies.
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

    def identificar_senial(self, senial: Senial, titulo: str) -> None:
        """Interactively identify and set signal metadata.

        Prompts the user to provide identification and description for the signal.
        Continues prompting until the user confirms the entered information.
        Updates the signal's ID and comentario properties directly.

        Args:
            senial: Signal entity to be identified and updated
            titulo: Title/context to display during identification process

        Raises:
            ValueError: When user enters invalid ID format (handled internally)

        Example:
            >>> signal = Senial()
            >>> controller.identificar_senial(signal, "New Temperature Signal")
            # User interaction follows...
            >>> print(f"Signal ID: {signal.id}, Description: {signal.comentario}")
            Signal ID: 123, Description: Temperature from sensor A

        Note:
            This method contains blocking user interaction. It will continue
            prompting until valid input is provided and confirmed.
        """

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

    def obtener_senial(self, id_senial: Any) -> Senial:
        """Retrieve signal by ID from the acquisition repository.

        Fetches a previously stored signal from the configured acquisition
        repository using the provided identifier. Applies SSA-26 recovery
        strategies for transient repository failures.

        Args:
            id_senial: Unique identifier for the signal to retrieve

        Returns:
            Senial: The signal entity with the specified ID

        Raises:
            RepositoryException: When signal cannot be retrieved after retries
            ValidationException: When signal ID is invalid or not found

        Example:
            >>> signal = controller.obtener_senial("SIG_001")
            >>> print(f"Retrieved signal: {signal.comentario}")
            Retrieved signal: Temperature readings from sensor A

        Note:
            Uses automatic retry mechanism with up to 3 attempts for
            repository operations with exponential backoff.
        """
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

    def guardar_senial(self, senial: Senial) -> None:
        """Persist signal to the configured acquisition repository.

        Saves the provided signal using the repository pattern while
        applying SSA-26 exception handling and recovery strategies.
        Maintains transaction boundaries for data consistency.

        Args:
            senial: Domain entity to persist, must have valid ID and data

        Raises:
            RepositoryException: When persistence operation fails after retries
            ValidationException: When signal state is invalid for persistence
            DataAccessException: When underlying storage is unavailable

        Example:
            >>> signal = Senial()
            >>> signal.id = "SIG_001"
            >>> signal.poner_valor(25.5)
            >>> controller.guardar_senial(signal)

        Note:
            The signal must have a valid ID before saving. Uses automatic
            retry with up to 3 attempts for transient storage failures.
        """
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

    def listar_seniales_adquiridas(self) -> List[Senial]:
        """List all signals from the acquisition repository.

        Retrieves a list of all signals previously stored in the acquisition
        repository. Applies SSA-26 recovery strategies for repository access.

        Returns:
            List[Senial]: List of all acquired signals, empty list if none exist

        Raises:
            RepositoryException: When listing operation fails after retries
            DataAccessException: When repository is unavailable

        Example:
            >>> signals = controller.listar_seniales_adquiridas()
            >>> print(f"Found {len(signals)} acquired signals")
            Found 5 acquired signals
            >>> for signal in signals:
            ...     print(f"- {signal.id}: {signal.comentario}")
            - SIG_001: Temperature sensor A
            - SIG_002: Pressure sensor B

        Note:
            Returns empty list if no signals are found. Uses automatic retry
            mechanisms for transient repository access failures.
        """
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
