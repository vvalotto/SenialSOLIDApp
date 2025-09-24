"""Infrastructure module for signal data persistence contexts.

This module implements the Repository pattern for signal persistence using different
storage strategies. Provides abstract base context and concrete implementations
for file-based and pickle-based persistence with comprehensive error handling
and recovery strategies from SSA-26.

Classes:
    BaseContexto: Abstract base class defining persistence interface
    ContextoPickle: Pickle-based serialization persistence implementation
    ContextoArchivo: File-based persistence with custom mapping

The module supports:
    - Signal entity persistence and retrieval
    - Audit trail and tracing capabilities
    - Error handling with automatic recovery
    - Multiple storage backend strategies

This module is part of the infrastructure layer and implements the
Repository pattern from DDD for signal persistence operations.
"""
import os
import pickle
import glob
import datetime
from typing import Any, List, Optional, Union
from abc import ABCMeta, abstractmethod
from acceso_datos.mapeador import *
from utilidades.trazador import *
from utilidades.auditor import *
from config.logging_config import get_logger
from exceptions import DataAccessException, ConfigurationException
from exceptions.exception_handler import handle_with_recovery

logger = get_logger(__name__)


class BaseContexto(BaseTrazador, BaseAuditor, metaclass=ABCMeta):
    """Abstract base class for signal persistence contexts.

    Defines the interface for signal data persistence operations following
    the Repository pattern from DDD. Integrates audit trail and tracing
    capabilities through multiple inheritance from utility base classes.

    This class enforces consistent behavior across different storage backends
    while providing comprehensive error handling and recovery mechanisms
    from SSA-26 implementation.

    Attributes:
        _recurso: Physical resource location (file path, database connection, etc.)

    Abstract Methods:
        persistir: Store an entity with specified identifier
        recuperar: Retrieve an entity by identifier
        listar: List all available entities in the context

    Concrete Methods:
        auditar: Write audit trail entry with recovery support
        trazar: Write trace entry with recovery support

    Business Rules:
        - Resource name cannot be None or empty string
        - All persistence operations must support recovery mechanisms
        - Audit and trace entries are written to separate log files
        - Error conditions are logged with structured context

    Example:
        Cannot be instantiated directly, use concrete implementations:

        >>> context = ContextoPickle('/path/to/signals')
        >>> context.persistir(signal, 'SIG_001')
        >>> retrieved = context.recuperar(Senial(), 'SIG_001')
        >>> all_signals = context.listar()
    """
    def __init__(self, recurso: str) -> None:
        """Initialize the persistence context with resource location.

        Sets up the context with the physical resource location where data will
        be stored and retrieved. Validates resource name for business constraints.

        Args:
            recurso: Physical resource location (path, connection string, etc.)

        Raises:
            ConfigurationException: When recurso is None, empty, or invalid

        Example:
            >>> context = ConcreteContext('/data/signals')
            >>> print(context.recurso)
            /data/signals

        Note:
            Resource validation ensures data integrity and prevents
            accidental data loss from invalid storage locations.
        """
        if recurso is None or recurso == "":
            raise ConfigurationException(
                config_key="recurso",
                config_type="contexto_persistencia",
                context={
                    "provided_value": str(recurso),
                    "validation_rule": "nombre_recurso_requerido"
                }
            )
        self._recurso = recurso
        return

    @property
    def recurso(self) -> str:
        """Get the physical resource location for this context.

        Returns:
            str: The resource location where entities are persisted

        Note:
            This is the physical location (file path, database name, etc.)
            where all persistence operations for this context occur.
        """
        return self._recurso

    @abstractmethod
    def persistir(self, entidad: Any, nombre_entidad: str) -> None:
        """Store an entity in the persistence context.

        Abstract method that must be implemented by concrete context classes.
        Each implementation defines specific storage strategy while maintaining
        consistent interface for entity persistence.

        Args:
            entidad: Domain entity instance to be persisted
            nombre_entidad: Unique identifier for the entity instance

        Raises:
            DataAccessException: When persistence operation fails
            ConfigurationException: When context is not properly configured
            NotImplementedError: If not implemented by concrete class

        Note:
            Implementations must ensure data consistency and provide
            appropriate error handling with recovery mechanisms.
        """
        pass

    @abstractmethod
    def recuperar(self, entidad: Any, id_entidad: str) -> Optional[Any]:
        """Retrieve an entity from the persistence context.

        Abstract method that must be implemented by concrete context classes.
        Each implementation defines specific retrieval strategy while maintaining
        consistent interface for entity recovery.

        Args:
            entidad: Template entity instance indicating the expected type
            id_entidad: Unique identifier for the entity to retrieve

        Returns:
            Optional[Any]: The retrieved entity instance, None if not found

        Raises:
            DataAccessException: When retrieval operation fails
            NotImplementedError: If not implemented by concrete class

        Note:
            Implementations should return None for missing entities rather
            than raising exceptions to support optional retrieval patterns.
        """
        pass

    @abstractmethod
    def listar(self) -> List[str]:
        """List all available entities in the persistence context.

        Abstract method with default file-based implementation that can be
        overridden by concrete classes for specific storage backends.

        Returns:
            List[str]: List of entity identifiers available in the context

        Raises:
            DataAccessException: When listing operation fails
            NotImplementedError: If not implemented by concrete class

        Example:
            >>> entities = context.listar()
            >>> print(f"Found {len(entities)} entities")
            Found 5 entities
            >>> for entity_id in entities:
            ...     print(f"- {entity_id}")
            - SIG_001
            - SIG_002

        Note:
            Default implementation assumes .dat file extension.
            Concrete classes should override for specific storage formats.
        """
        lista = [f[len(self._recurso) + 1:] for f in glob.glob(self._recurso + '/*.dat')]
        logger.info("Lista de archivos obtenida", extra={"cantidad": len(lista), "archivos": lista[:5]})  # Solo primeros 5 para evitar logs muy largos
        return lista

    def auditar(self, contexto: Any, auditoria: str) -> None:
        """Write audit trail entry for persistence operations.

        Records audit information about persistence context operations
        for compliance and debugging purposes. Uses SSA-26 recovery
        mechanisms for reliable audit trail maintenance.

        Args:
            contexto: Context object or information to be audited
            auditoria: Audit message describing the operation

        Raises:
            DataAccessException: When audit writing fails after retries

        Example:
            >>> context.auditar(self, "Entity persisted successfully")
            # Writes audit entry to auditor_contexto.log

        Note:
            Audit entries include timestamp, context, and operation details.
            Critical for compliance and operational monitoring.
        """
        nombre = 'auditor_contexto.log'
        def _escribir_auditoria():
            """Internal function for audit writing with recovery support"""
            with open(nombre, 'a') as auditor:
                auditor.writelines('------->\n')
                auditor.writelines(str(contexto) + '\n')
                auditor.writelines(str(datetime.datetime.now()) + '\n')
                auditor.writelines(str(auditoria) + '\n')
            logger.debug("Auditoría escrita exitosamente", extra={"archivo": nombre, "contexto": str(contexto)})

        try:
            handle_with_recovery(
                operation=_escribir_auditoria,
                operation_name="escribir_auditoria",
                context={
                    "archivo_auditoria": nombre,
                    "contexto": str(contexto),
                    "auditoria": str(auditoria)
                },
                max_attempts=2
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is
            raise
        except Exception as ex:
            raise DataAccessException(
                file_path=nombre,
                operation="auditar",
                context={
                    "archivo_auditoria": nombre,
                    "contexto": str(contexto),
                    "auditoria": str(auditoria)
                },
                cause=ex
            )

    def trazar(self, contexto: Any, accion: str, mensaje: str) -> None:
        """Write trace entry for debugging and monitoring purposes.

        Records detailed trace information about persistence operations
        for debugging and operational monitoring. Uses SSA-26 recovery
        mechanisms for reliable trace information.

        Args:
            contexto: Context object or information to be traced
            accion: Action being performed (create, read, update, delete)
            mensaje: Detailed message about the operation

        Raises:
            DataAccessException: When trace writing fails after retries

        Example:
            >>> context.trazar("ContextoPickle", "persistir", "Signal SIG_001 saved")
            # Writes trace entry to logger_contexto.log

        Note:
            Trace entries include timestamp, action, context, and detailed message.
            Essential for debugging persistence issues.
        """
        nombre = 'logger_contexto.log'
        def _escribir_traza():
            """Internal function for trace writing with recovery support"""
            with open(nombre, 'a') as trazador:
                trazador.writelines('------->\n')
                trazador.writelines('Accion: ' + str(accion) + '\n')
                trazador.writelines('Contexto: ' + str(contexto) + '\n')
                trazador.writelines(str(datetime.datetime.now()) + '\n')
                trazador.writelines(str(mensaje) + '\n')
            logger.debug("Traza escrita exitosamente", extra={"archivo": nombre, "accion": str(accion)})

        try:
            handle_with_recovery(
                operation=_escribir_traza,
                operation_name="escribir_traza",
                context={
                    "archivo_traza": nombre,
                    "contexto": str(contexto),
                    "accion": str(accion),
                    "mensaje": str(mensaje)
                },
                max_attempts=2
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is
            raise
        except Exception as ex:
            raise DataAccessException(
                file_path=nombre,
                operation="trazar",
                context={
                    "archivo_traza": nombre,
                    "contexto": str(contexto),
                    "accion": str(accion),
                    "mensaje": str(mensaje)
                },
                cause=ex
            )


class ContextoPickle(BaseContexto):
    """Pickle-based serialization persistence implementation.

    Concrete implementation of BaseContexto that uses Python's pickle module
    for object serialization and deserialization. Provides efficient binary
    storage of Python objects while maintaining object structure and relationships.

    This implementation is ideal for:
        - Fast serialization/deserialization of Python objects
        - Preserving complete object state including private attributes
        - Development and testing scenarios
        - Small to medium-sized datasets

    Storage Format:
        - Binary pickle files with .pickle extension
        - One file per entity using entity ID as filename
        - Complete object graph serialization
        - Automatic directory creation if needed

    Performance Characteristics:
        - Fast serialization and deserialization
        - Compact binary storage format
        - O(1) access by entity ID
        - Directory-based organization

    Example:
        Using pickle-based persistence:

        >>> context = ContextoPickle('/data/signals')
        >>> signal = Senial()
        >>> signal.id = 'SIG_001'
        >>> signal.poner_valor(25.5)
        >>> context.persistir(signal, signal.id)
        >>> retrieved = context.recuperar(Senial(), 'SIG_001')
        >>> print(f"Retrieved signal with {retrieved.cantidad} values")
        Retrieved signal with 1 values

    Warning:
        Pickle files are Python-specific and not portable to other languages.
        Only unpickle data from trusted sources due to security implications.
    """
    def __init__(self, recurso: str) -> None:
        """Initialize pickle-based persistence context.

        Creates the persistence context with the specified directory path
        for storing pickle files. Creates the directory if it doesn't exist
        and initializes audit trail.

        Args:
            recurso: Directory path where pickle files will be stored

        Raises:
            IOError: When directory creation fails or path is inaccessible
            ConfigurationException: When recurso is invalid (handled by parent)

        Example:
            >>> context = ContextoPickle('/data/signals')
            # Creates /data/signals directory if it doesn't exist

        Note:
            Automatically creates the storage directory and writes initial
            audit entry for context creation.
        """
        try:
            super().__init__(recurso)
            if not os.path.isdir(recurso):
                os.mkdir(recurso)
            self.auditar(self, "Se creo el contexto")
        except IOError as eIO:
            self.trazar("Pickle", "Crear contexto", eIO)
            raise eIO

    def persistir(self, entidad, id_entidad):
        """
        Se persiste el objeto (entidad) y se indica el tipo de entidad
        :param: entidad (object)
        :param: id_entidad (string)
        """
        archivo = str(id_entidad) + '.pickle'
        ubicacion = self._recurso + "/" + archivo
        def _persistir_entidad():
            """Internal function for entity persistence with recovery support"""
            with open(ubicacion, "wb") as a:
                pickle.dump(entidad, a)
            logger.info("Entidad persistida exitosamente", extra={"id_entidad": id_entidad, "archivo": ubicacion})

        try:
            handle_with_recovery(
                operation=_persistir_entidad,
                operation_name="persistir_pickle",
                context={
                    "id_entidad": id_entidad,
                    "archivo": ubicacion,
                    "contexto_tipo": "ContextoPickle",
                    "entity_type": type(entidad).__name__
                },
                max_attempts=3
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is
            raise
        except Exception as ex:
            raise DataAccessException(
                file_path=ubicacion,
                operation="persistir",
                context={
                    "id_entidad": id_entidad,
                    "entity_type": type(entidad).__name__,
                    "contexto_tipo": "ContextoPickle"
                },
                cause=ex
            )
        return

    def recuperar(self, entidad, id_entidad):
        """
        Se lee el entidad a tratar
        :param id_entidad
        :return: entidad (object)
        """
        archivo = str(id_entidad) + '.pickle'
        ubicacion = self._recurso + "/" + archivo
        e = None
        def _recuperar_entidad():
            """Internal function for entity recovery with recovery support"""
            with open(ubicacion, "rb") as a:
                entidad_recuperada = pickle.load(a)
            logger.info("Entidad recuperada exitosamente", extra={"id_entidad": id_entidad, "archivo": ubicacion})
            return entidad_recuperada

        try:
            e = handle_with_recovery(
                operation=_recuperar_entidad,
                operation_name="recuperar_pickle",
                context={
                    "id_entidad": id_entidad,
                    "archivo": ubicacion,
                    "contexto_tipo": "ContextoPickle",
                    "entity_type": type(entidad).__name__
                },
                max_attempts=3
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is but return None for compatibility
            logger.error("Error de acceso a datos recuperando entidad", extra={"id_entidad": id_entidad, "archivo": ubicacion}, exc_info=True)
            e = None
        except Exception as ex:
            logger.error("Error inesperado recuperando entidad", extra={"id_entidad": id_entidad, "archivo": ubicacion}, exc_info=True)
            e = None
        return e

    def listar(self):
        return [f[len(self._recurso) + 1:] for f in glob.glob(self._recurso + '/*.pickle')]


class ContextoArchivo(BaseContexto):
    """
    Contexto del recurso de persistencia de tipo archivo
    """
    def __init__(self, recurso):
        """
        Se crea el archivo con el path donde se guardarán los archivos
        de la entidades a persistir
        :param recurso: Path del repositorio de entidades
        :return:
        """
        def _crear_contexto_archivo():
            """Internal function for context creation with recovery support"""
            super(ContextoArchivo, self).__init__(recurso)
            if not os.path.isdir(recurso):
                os.mkdir(recurso)
            self.auditar(self, "Se creo el contexto")
            logger.info("Contexto de archivo creado exitosamente", extra={"recurso": recurso})

        try:
            handle_with_recovery(
                operation=_crear_contexto_archivo,
                operation_name="crear_contexto_archivo",
                context={
                    "recurso": recurso,
                    "contexto_tipo": "ContextoArchivo",
                    "operation_type": "initialization"
                },
                max_attempts=2
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is
            raise
        except Exception as ex:
            raise DataAccessException(
                file_path=recurso,
                operation="crear_contexto",
                context={
                    "recurso": recurso,
                    "contexto_tipo": "ContextoArchivo",
                    "operation_type": "initialization"
                },
                cause=ex
            )

    def persistir(self, entidad, nombre_entidad):
        """
        Agregar un objeto(entidad) para persistirlo.
        :param entidad: Tipo de entidad
        :param nombre_entidad: identificacion de la instancia de la entidad
        :return:
        """
        archivo = str(nombre_entidad) + '.dat'
        ubicacion = self._recurso + "/" + archivo

        def _persistir_entidad_archivo():
            """Internal function for file entity persistence with recovery support"""
            mapeador = MapeadorArchivo()
            contenido = mapeador.ir_a_persistidor(entidad)
            with open(ubicacion, "w") as a:
                a.write(contenido)
            logger.info("Entidad archivo persistida exitosamente", extra={
                "id_entidad": nombre_entidad,
                "archivo": ubicacion,
                "contenido_length": len(contenido)
            })

        try:
            handle_with_recovery(
                operation=_persistir_entidad_archivo,
                operation_name="persistir_archivo",
                context={
                    "id_entidad": nombre_entidad,
                    "archivo": ubicacion,
                    "contexto_tipo": "ContextoArchivo",
                    "entity_type": type(entidad).__name__
                },
                max_attempts=3
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is
            raise
        except Exception as ex:
            raise DataAccessException(
                file_path=ubicacion,
                operation="persistir",
                context={
                    "id_entidad": nombre_entidad,
                    "entity_type": type(entidad).__name__,
                    "contexto_tipo": "ContextoArchivo"
                },
                cause=ex
            )
        return

    def recuperar(self, entidad, id_entidad):
        """
        Obtiene la entidad guardada
        :param entidad:
        :param id_entidad:
        :return:
        """
        archivo = str(id_entidad) + '.dat'
        ubicacion = self._recurso + "/" + archivo

        def _recuperar_entidad_archivo():
            """Internal function for file entity recovery with recovery support"""
            contenido = ''
            with open(ubicacion) as persistidor:
                linea = persistidor.readline()
                while linea != '':
                    contenido += linea
                    linea = persistidor.readline()
            mapeador = MapeadorArchivo()
            entidad_recuperada = mapeador.venir_desde_persistidor(entidad, contenido)
            logger.info("Entidad archivo recuperada exitosamente", extra={
                "id_entidad": id_entidad,
                "archivo": ubicacion,
                "contenido_length": len(contenido)
            })
            return entidad_recuperada

        try:
            return handle_with_recovery(
                operation=_recuperar_entidad_archivo,
                operation_name="recuperar_archivo",
                context={
                    "id_entidad": id_entidad,
                    "archivo": ubicacion,
                    "contexto_tipo": "ContextoArchivo",
                    "entity_type": type(entidad).__name__,
                    "file_exists": os.path.exists(ubicacion)
                },
                max_attempts=3
            )
        except DataAccessException:
            # Re-raise data access exceptions as-is but return None for compatibility
            logger.error("Error de acceso a datos recuperando entidad archivo", extra={
                "id_entidad": id_entidad,
                "archivo": ubicacion,
                "file_exists": os.path.exists(ubicacion)
            }, exc_info=True)
            return None
        except Exception as ex:
            logger.error("Error inesperado recuperando entidad archivo", extra={
                "id_entidad": id_entidad,
                "archivo": ubicacion
            }, exc_info=True)
            # Wrap unexpected exceptions
            raise DataAccessException(
                file_path=ubicacion,
                operation="recuperar",
                context={
                    "id_entidad": id_entidad,
                    "entity_type": type(entidad).__name__,
                    "contexto_tipo": "ContextoArchivo",
                    "file_exists": os.path.exists(ubicacion)
                },
                cause=ex
            )

    def listar(self):
        return [f[len(self._recurso) + 1:len(f) - 4] for f in glob.glob(self._recurso + '/*.dat')]
