from abc import ABCMeta, abstractmethod
from utilidades.auditor import *
from utilidades.trazador import *
import datetime
from exceptions import RepositoryException, DataAccessException
from config.logging_config import get_logger

logger = get_logger(__name__)


class BaseRepositorio(metaclass=ABCMeta):
    def _init__(self, contexto):
        self._contexto = contexto
    """
    Define la interfaz para el acceso a la persistencia de datos
    """
    @abstractmethod
    def guardar(self, entidad):
        """
        Persiste la entidad
        """
        pass

    @abstractmethod
    def obtener(self, entidad, id_entidad):
        """
        Rescata la entidad indica por id_entidad
        :param entidad: Tipo de entidad que debe rescatar
        :param id_entidad: identificador unico
        :return: retorna la instancia de la entidad indicada
        """
        pass

    @abstractmethod
    def listar(self):
        pass

class RepositorioSenial(BaseAuditor, BaseTrazador, BaseRepositorio):
    """
    Definicion del Repositorio de la Entidad Senial
    """
    def __init__(self, ctx):
        """
        Se le asocia el contexto correspondiente
        :param ctx: contexto para persistir la senial
        :return:
        """
        super()._init__(ctx)

    def guardar(self, senial):
        """
        Persiste la entidad senial
        :param senial:
        :return:
        """
        try:
            self.auditar(senial, "Antes de hacer la persistencia")
            self._contexto.persistir(senial, senial.id)
            self.auditar(senial, "Se realizó la persistencia")
            logger.info("Señal persistida exitosamente", extra={"signal_id": senial.id})
        except Exception as ex:
            self.auditar(senial, "Problema al persistir persistencia")
            self.trazar(senial, "guardar", str(ex))
            raise RepositoryException(
                operation="persistir",
                entity_type="senial",
                entity_id=getattr(senial, 'id', 'unknown'),
                context={
                    "senial_cantidad": getattr(senial, '_cantidad', 0),
                    "contexto_tipo": type(self._contexto).__name__
                },
                cause=ex
            )
        return

    def obtener(self, senial, id_senial):
        """
        Implementa la recuperacion de la entidad (senial)
        :param senial:
        :param id_senial:
        :return:
        """
        try:
            self.auditar(senial, "Antes de recuperar la senial")
            senial_recuperada = self._contexto.recuperar(senial, id_senial)
            self.auditar(senial, "Se realizó la recuperacion")
            logger.info("Señal recuperada exitosamente", extra={"signal_id": id_senial})
            return senial_recuperada
        except Exception as ex:
            self.auditar(senial, "Error al recuperar")
            msj = f'Error al leer una senial persistada - ID: {id_senial}'
            self.trazar(senial, "obtener", msj)
            raise RepositoryException(
                operation="recuperar",
                entity_type="senial",
                entity_id=id_senial,
                context={
                    "contexto_tipo": type(self._contexto).__name__,
                    "operacion_auditada": True
                },
                cause=ex
            )

    def auditar(self, senial, auditoria):
        """
        Implementacion de la auditoria de la señal
        :param senial:
        :param auditoria:
        :return:
        """
        nombre = 'auditor_senial.log'
        try:
            with open(nombre, 'a') as auditor:
                auditor.writelines('------->\n')
                auditor.writelines(str(senial) + '\n')
                auditor.writelines(str(datetime.datetime.now()) + '\n')
                auditor.writelines(str(auditoria) + '\n')
        except IOError as eIO:
            raise eIO

    def trazar(self, senial, accion, mensaje):
        """
        Implementacion del registro de eventos de la señal
        :param senial:
        :param accion:
        :param mensaje:
        :return:
        """
        nombre = 'logger_senial.log'
        try:
            with open(nombre, 'a') as logger:
                logger.writelines('------->\n')
                logger.writelines('Accion: ' + str(accion))
                logger.writelines(str(senial) + '\n')
                logger.writelines(str(datetime.datetime.now()) + '\n')
                logger.writelines(str(mensaje) + '\n')
        except IOError as eIO:
            raise eIO

    def listar(self):
        return self._contexto.listar()

class RepositorioUsuario(BaseRepositorio):

    def __init__(self, ctx):
        super()._init__(ctx)

    def guardar(self, usuario):
        try:
            self._contexto.persistir(usuario, usuario.id)
        except Exception:
            raise Exception
        return

    def obtener(self, usuario, id_usuario):
        try:
            return self._contexto.recuperar(usuario, id_usuario)
        except Exception:
            raise Exception