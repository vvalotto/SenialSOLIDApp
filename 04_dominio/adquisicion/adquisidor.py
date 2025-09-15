"""
Se modifica la clase base y se extiende con la clase abstracta trazador
"""
from abc import ABCMeta, abstractmethod
from modelo.senial import *
from utilidades.trazador import *
import math
from config.logging_config import get_logger

logger = get_logger(__name__)


class BaseAdquisidor(BaseTrazador, metaclass=ABCMeta):
    """
    Clase Abstracta Adquisidor
    """
    def __init__(self, senial):
        """
        Inicializa el adquisidor con una lista vacia de valores de la senial
        :valor: Tamanio de la coleccion de valores de la senial
        """
        self._senial = senial

    def obtener_senial_adquirida(self):
        """
        Devuelve la lista de valores de la senial adquirida
        :return: senial
        """
        return self._senial

    @abstractmethod
    def leer_senial(self):
        """
        Metodo abstracto. Cada adquisidor tiene su propia implementacion
        de la lectura de la senial
        """
        pass

    @abstractmethod
    def _leer_dato_entrada(self):
        pass

    def trazar(self, entidad, accion, mensaje):
        """
        Registra un evento asociado a la proceso de adquisicion
        entidad: clase que genera el evento
        accion: metodo o funcion en la que se genera el evento
        mensaje: Comentario
        """
        nombre = 'adquisidor_logger.log'
        try:
            with open(nombre, 'a') as logger:
                logger.writelines('------->\n')
                logger.writelines('Accion: ' + str(accion) + '\n')
                logger.writelines(str(entidad) + '\n')
                logger.writelines(str(datetime.datetime.now()) + '\n')
                logger.writelines(str(mensaje) + '\n')
        except IOError as eIO:
            raise eIO


class AdquisidorSimple(BaseAdquisidor):
    """
    Adquisidor de datos desde el teclado
    """
    def _leer_dato_entrada(self):
        """
        Lee un dato por teclaso
        :return: dato leido
        """
        dato = 0
        while True:
            try:
                dato = float(input('Valor:'))
                break
            except ValueError:
                logger.warning("Entrada inválida: se esperaba número")
            finally:
                return dato

    def leer_senial(self):
        """
        llena la coleccion de valores de la senial desde el teclado
        :return:
        """
        logger.info("Iniciando lectura de señal desde teclado", extra={"tamanio": self._senial.tamanio})
        for i in range(0, self._senial.tamanio):
            logger.debug("Leyendo dato", extra={"numero_dato": i})
            self._senial.poner_valor(self._leer_dato_entrada())
        logger.info("Lectura de señal desde teclado completada", extra={"valores_leidos": self._senial.cantidad})
        return


class AdquisidorArchivo(BaseAdquisidor):
    """
    Adquisidor de datos desde Archivo
    """
    @property
    def ubicacion(self):
        return self._ubicacion

    def __init__(self, senial, ubicacion):
        """
        Inicializa la instancia con la ubicacion del archivo a leer
        :param ubicacion:
        """
        BaseAdquisidor.__init__(self, senial)
        if isinstance(ubicacion, str):
            self._ubicacion = ubicacion
        else:
            super().trazar(AdquisidorArchivo,
                           'Inicializacion',
                           'El dato no es de una ubicacion valida, (No es un nombre de archivo')
            raise Exception('El dato no es de una ubicacion valida, (No es un nombre de archivo')
        return



    def _leer_dato_entrada(self):
        pass

    def leer_senial(self):
        logger.info("Iniciando lectura de señal desde archivo", extra={"archivo": self._ubicacion})
        try:
            with open(self._ubicacion, 'r') as a:
                for linea in a:
                    dato = float(linea)
                    self._senial.poner_valor(dato)
                    logger.debug("Valor leído desde archivo", extra={"valor": dato})
        except IOError as ex:
            super().trazar(AdquisidorArchivo,
                           'leer_senial',
                           'I/O Error: ' + str(ex))
            raise ex
        except ValueError as ex:
            super().trazar(AdquisidorArchivo,
                           'leer_senial',
                           'Dato de senial no detectado: ' + str(ex))
            logger.error("Dato de señal no detectado en archivo", extra={"archivo": self._ubicacion})
            raise ex
        except Exception as ex:
            super().trazar(AdquisidorArchivo,
                           'leer_senial',
                           'Error en la carga de datos: ' + str(ex))
            logger.error("Error en la carga de datos desde archivo", extra={"archivo": self._ubicacion})
            raise ex


class AdquisidorSenoidal(BaseAdquisidor):
    """
    Simulador de una entrada de senial senoidal
    """
    def __init__(self, senial):
        BaseAdquisidor.__init__(self, senial)
        self._valor = 0
        self._i = 0

    def _leer_dato_entrada(self):
        self._valor = math.sin((float(self._i) / (float(self._senial.tamanio))) * 2 * 3.14) * 10
        self._i += 1
        return self._valor

    def leer_senial(self):
        logger.info("Iniciando generación de señal senoidal", extra={"tamanio": self._senial.tamanio})
        i = 0
        try:
            while i < self._senial.tamanio:
                valor = self._leer_dato_entrada()
                self._senial.poner_valor(valor)
                i += 1
            logger.info("Señal senoidal generada exitosamente", extra={"valores_generados": i})
        except Exception as ex:
            super().trazar(AdquisidorSenoidal,
                           'leer_senial',
                           'Error en la carga de datos: ' + str(ex))
            logger.error("Error en la generación de señal senoidal", exc_info=True)