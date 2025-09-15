"""
Modulo que define la entidad Senial.
Es considerada una entidad del dominio

Modificacion: Se crea un clase abstracta que define todas las interfaces de las
estructuras de las seniales y resuelve la violacion de los principio OCP y LSP
"""


from abc import ABCMeta, abstractmethod
from collections import deque
import datetime
from config.logging_config import get_logger

logger = get_logger(__name__)


class SenialBase(metaclass=ABCMeta):
    """
    Definición de la entidad tipo Senial.
    En este caso es una definicion de una clase concreta.
    Tiene las funciones:
    -> poner_valor(valor)
    -> obtener_valot(indice)
    -> obtener_tamanio()
    """
    def __init__(self, tamanio=10):
        """
        Constructor: Inicializa la lista de valores vacia
        :return:
        """
        self._id = ''
        self._comentario = ''
        self._fecha_adquisicion = None
        self._tamanio = tamanio
        self._cantidad = 0
        self._valores = []
        return

    # Propiedades
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor):
        self._id = valor

    @property
    def comentario(self):
        return self._comentario

    @comentario.setter
    def comentario(self, valor):
        self._comentario = valor

    @property
    def fecha_adquisicion(self):
        return self._fecha_adquisicion

    @fecha_adquisicion.setter
    def fecha_adquisicion(self, valor):
        self._fecha_adquisicion = valor

    @fecha_adquisicion.deleter
    def fecha_adquisicion(self):
        del self._fecha_adquisicion

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        self._cantidad = valor

    @property
    def tamanio(self):
        return self._tamanio

    @tamanio.setter
    def tamanio(self, valor):
        self._tamanio = valor

    @property
    def valores(self):
        return self._valores

    @valores.setter
    def valores(self, datos):
        self._valores = datos

    @abstractmethod
    def poner_valor(self, valor):
        pass

    @abstractmethod
    def sacar_valor(self, *valor):
        pass

    def limpiar(self):
        """
        Deja a la senial sin valores
        """
        self._valores.clear()
        self._cantidad = 0

    def obtener_valor(self, indice):
        """
        Devuelve el valor contenido en la lista de acuerdo a al indice
        :param indice:
        :return: valor
        """
        try:
            valor = self._valores[indice]
            return valor
        except Exception as e:
            logger.error("Error obteniendo valor por índice", extra={"indice": indice, "cantidad": self._cantidad}, exc_info=True)
            return None

    def __str__(self):
        """
        Sobreescritura de la funcion str
        """
        cad = ""
        cad += 'Tipo: ' + str(type(self)) + '\r\n'
        cad += 'Id: ' + str(self._id) + '\r\n'
        cad += 'Descripcion: ' + str(self._comentario) + '\r\n'
        cad += 'fecha_adquisicion: ' + str(self._fecha_adquisicion)
        return cad


class Senial(SenialBase):
    """
    Clase tipo lista que implementa los metodos de manipulacion de datos
    dentro de la estructura
    """
    def poner_valor(self, valor):
        """
        Agrega dato a la lista de la senial
        :param valor: dato de la senial obtenida
        """
        if self._cantidad < self._tamanio:
            self._valores.append(valor)
            self._cantidad += 1
        else:
            logger.warning("Capacidad de señal excedida", extra={"cantidad_actual": self._cantidad, "tamanio_maximo": self._tamanio})
        return

    def sacar_valor(self, indice):
        """
        Retira un elemento de la lista ubicado en indice
        :return: dato extraido
        """
        valor = None
        if self._cantidad > 0:
            valor = self.obtener_valor(indice)
            self._valores.remove(valor)
            self._cantidad -= 1

            return valor
        else:
            logger.warning("Intento de extraer valor de señal vacía", extra={"cantidad": self._cantidad})
        return valor


class SenialPila(Senial):

    def sacar_valor(self):
        """
        Retira un elemento de la lista ubicado en indice
        :return: dato extraido
        """
        valor = None
        try:
            valor = self._valores.pop()
            self._cantidad -= 1
            return valor
        except Exception as e:
            logger.warning("No hay elementos en la pila para extraer", extra={"cantidad": self._cantidad})
        return valor


class SenialCola(Senial):
    def __init__(self, tamanio):
        super().__init__(tamanio)
        self._valores = deque([])

    def sacar_valor(self):
        """
        Retira un elemento de la lista ubicado en indice
        :return: dato extraido
        """
        valor = 0
        try:
            valor = self._valores.popleft()
            self._cantidad -= 1
        except Exception as e:
            logger.warning("No hay elementos en la cola para extraer", extra={"cantidad": self._cantidad})
        return valor


if __name__ == "__main__":
    # Configurar logging para prueba
    from config.logging_config import setup_logging
    setup_logging()

    s = SenialPila()
    s.id = '100'
    s._fecha_adquisicion = datetime.datetime.now()
    logger.info("Prueba de señal creada", extra={"senial_info": str(s)})