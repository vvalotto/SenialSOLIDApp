"""
Modulo que contiene la responsabilidad de guardar las seniales, adquiridas y procesadas
en algun tipo de almacen de persistencia (archivo plano, xml, serializa, base de dato)
"""
import os
import pickle
import glob
import datetime
from acceso_datos.mapeador import *
from utilidades.trazador import *
from utilidades.auditor import *
from config.logging_config import get_logger
from exceptions import DataAccessException, ConfigurationException
from exceptions.exception_handler import handle_with_recovery

logger = get_logger(__name__)


class BaseContexto(BaseTrazador, BaseAuditor, metaclass=ABCMeta):
    """
    Clase abstract que define la interfaz de la persistencia de datos
    """
    def __init__(self, recurso):
        """
        Se crea el contexto, donde el nombre es el recurso fisico donde residen los datos
        junto con esto se crea el recurso fisico con el nombre
        :param recurso:
        :return:
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
    def recurso(self):
        return self._recurso

    @abstractmethod
    def persistir(self, entidad, nombre_entidad):
        """
        Se identifica a la instancia de la entidad con nombre_entidad y en entidad es el tipo a persistir
        """
        pass

    @abstractmethod
    def recuperar(self, id_entidad, entidad):
        """
        Se identifica a la instancia de la entidad con nombre_entidad y en entidad es devuelta por el metodo
        """
        pass

    @abstractmethod
    def listar(self):
        lista = [f[len(self._recurso) + 1:] for f in glob.glob(self._recurso + '/*.dat')]
        logger.info("Lista de archivos obtenida", extra={"cantidad": len(lista), "archivos": lista[:5]})  # Solo primeros 5 para evitar logs muy largos
        return lista

    def auditar(self, contexto, auditoria):
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

    def trazar(self, contexto, accion, mensaje):
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
    """
    Clase de persistidor que persiste un tipo de objeto de manera serializada
    """
    def __init__(self, recurso):
        """
        Se crea el archivo con el path donde se guardarán los archivos
        de la entidades a persistir
        :param recurso: Path del repositorio de entidades
        :return:
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
