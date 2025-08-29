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
            raise Exception("Nombre de recurso vacio")
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
        print(lista)

    def auditar(self, contexto, auditoria):
        nombre = 'auditor_contexto.log'
        try:
            with open(nombre, 'a') as auditor:
                auditor.writelines('------->\n')
                auditor.writelines(str(contexto) + '\n')
                auditor.writelines(str(datetime.datetime.now()) + '\n')
                auditor.writelines(str(auditoria) + '\n')
        except IOError as eIO:
            raise eIO

    def trazar(self, contexto, accion, mensaje):

        nombre = 'logger_contexto.log'
        try:
            with open(nombre, 'a') as logger:
                logger.writelines('------->\n')
                logger.writelines('Accion: ' + str(accion) + '\n')
                logger.writelines('Contexto: ' + str(contexto) + '\n')
                logger.writelines(str(datetime.datetime.now()) + '\n')
                logger.writelines(str(mensaje) + '\n')
        except IOError as eIO:
            raise eIO


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
        try:
            with open(ubicacion, "wb") as a:
                pickle.dump(entidad, a)
        except IOError as eIO:
            raise eIO
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
        try:
            with open(ubicacion, "rb") as a:
                e = pickle.load(a)
        except IOError as eIO:
            print(eIO)
        except ValueError as eVE:
            print(eVE)
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
        try:
            super().__init__(recurso)
            if not os.path.isdir(recurso):
                os.mkdir(recurso)
            self.auditar(self, "Se creo el contexto")
        except IOError as eIO:
            self.trazar("Archivo", "Crear contexto", eIO)
            raise eIO

    def persistir(self, entidad, nombre_entidad):
        """
        Agregar un objeto(entidad) para persistirlo.
        :param entidad: Tipo de entidad
        :param nombre_entidad: identificacion de la instancia de la entidad
        :return:
        """
        mapeador = MapeadorArchivo()
        archivo = str(nombre_entidad) + '.dat'
        contenido = mapeador.ir_a_persistidor(entidad)
        ubicacion = self._recurso + "/" + archivo

        try:
            with open(ubicacion, "w") as a:
                a.write(contenido)
        except IOError as eIO:
            raise eIO
        return

    def recuperar(self, entidad, id_entidad):
        """
        Obtiene la entidad guardada
        :param entidad:
        :param id_entidad:
        :return:
        """
        contenido = ''
        archivo = str(id_entidad) + '.dat'
        ubicacion = self._recurso + "/" + archivo
        try:
            with open(ubicacion) as persitidor:
                linea = persitidor.readline()
                while linea != '':
                    contenido += linea
                    linea = persitidor.readline()
            mapeador = MapeadorArchivo()
            return mapeador.venir_desde_persistidor(entidad, contenido)
        except IOError as eIO:
            raise eIO
        except ValueError:
            raise ValueError

    def listar(self):
        return [f[len(self._recurso) + 1:len(f) - 4] for f in glob.glob(self._recurso + '/*.dat')]
