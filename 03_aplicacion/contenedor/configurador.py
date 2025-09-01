"""
Configura la clase que se usara
"""
import os
from xml.dom import minidom
from modelo.factory_senial import *
from procesamiento.factory_procesador import *
from adquisicion.factory_adquisidor import *
from repositorios.repositorio import *
from acceso_datos.factory_context import *


def _obtener_ruta_config():
    """Obtiene la ruta absoluta al archivo de configuración"""
    # Obtener directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Subir dos niveles para llegar a la raíz del proyecto
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # Construir path al archivo de configuración
    config_path = os.path.join(project_root, "03_aplicacion", "datos", "configuracion.xml")
    
    # Si no existe, buscar desde el directorio actual
    if not os.path.exists(config_path):
        config_path = "03_aplicacion/datos/configuracion.xml"
        if not os.path.exists(config_path):
            # Último intento: buscar en el directorio donde está este archivo
            config_path = os.path.join(os.path.dirname(__file__), "..", "datos", "configuracion.xml")
            config_path = os.path.normpath(config_path)
    
    return config_path


def obtener_dir_datos():
    try:
        config_path = _obtener_ruta_config()
        conf = minidom.parse(config_path)
        dir_datos = conf.getElementsByTagName("dir_recurso_datos")[0]
        path_datos = dir_datos.firstChild.data
        
        # Si es path relativo, hacerlo absoluto desde la raíz del proyecto
        if not os.path.isabs(path_datos):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            path_datos = os.path.join(project_root, path_datos)
            path_datos = os.path.normpath(path_datos)
        
        return path_datos
    except IOError as ex:
        raise ex


def obtener_senial_config(senial_config):
    try:
        # Parsea el xml de configuracion
        config_path = _obtener_ruta_config()
        conf_procesador = minidom.parse(config_path)
        # Busca el nodo de la senial para adquirir
        item_senial_adquirida = conf_procesador.getElementsByTagName(senial_config)[0]
        # Obtiene el nombre del tipo de senial
        senial = item_senial_adquirida.firstChild.data.strip()
        # Busca los nodos de los parametros
        item_tamanio = item_senial_adquirida.getElementsByTagName("tamanio")[0]
        # Llena la lista con los parametros asociados a la senial
        tamanio = item_tamanio.firstChild.data.strip()
        return senial, tamanio
    except Exception as ex:
        raise ex


def obtener_fltros_config(filtro_config):
    """
    Recupera desde la configuración el tipo de procesador y los
    parametros asociado
    Luego llama la factory para que devuelva el tipo de procesador creado
    """
    try:
        # Parsea el xml de configuracion
        config_path = _obtener_ruta_config()
        conf_filtro = minidom.parse(config_path)
        # Busca el nodo del procesador
        item_filtro = conf_filtro.getElementsByTagName(filtro_config)[0]
        # Obtiene el nombre del tipo de procesador definido
        filtro = item_filtro.firstChild.data.strip()
        # Busca los nodos de los parametros
        item_params = item_filtro.getElementsByTagName("param")
        # Llena la lista con los parametros asociados al procesador
        params = []
        for param in item_params:
            params.append(param.firstChild.data)
        return filtro, params
    except Exception as ex:
        raise ex


def definir_senial_adquirir():
    try:
        senial, tamanio = obtener_senial_config("senial_adq")
        return FactorySenial.obtener_senial(senial, tamanio)
    except Exception as ex:
        raise ex


def definir_senial_procesar():
    try:
        senial, tamanio = obtener_senial_config("senial_pro")
        return FactorySenial.obtener_senial(senial, tamanio)
    except Exception as ex:
        raise ex


def definir_procesador():
    """
    Recupera desde la configuración el tipo de procesador y los
    parametros asociado
    Luego llama la factory para que devuelva el tipo de procesador creado
    """
    try:
        procesador, params = obtener_fltros_config("procesador")
        # Crea el procesador
        return FactoryProcesador.obtener_procesador(procesador,
                                                    definir_senial_procesar(),
                                                    params)
    except Exception as ex:
        raise ex


def definir_adquisidor():
    """
    Recupera desde la configuración el tipo de adquisidor y los
    parametros asociado
    Luego llama la factory para que devuelva el tipo de adquisidor creado
    """
    try:
        adquisidor, params = obtener_fltros_config("adquisidor")
        # Crea el procesador
        return FactoryAdquisidor.obtener_adquisidor(adquisidor,
                                                    definir_senial_adquirir(),
                                                    params)
    except Exception as ex:
        raise ex


def definir_contexto(recurso):
    """
    Recupera desde la configuración el tipo de adquisidor y los
    parametros asociado
    Luego llama la factory para que devuelva el tipo de adquisidor creado
    """
    try:
        # Parsea el xml de configuracion
        config_path = _obtener_ruta_config()
        conf_adquisidor = minidom.parse(config_path)
        # Busca el nodo del contexto
        item_contexto = conf_adquisidor.getElementsByTagName("contexto")[0]
        contexto = item_contexto.firstChild.data.strip()
        # Crea el contexto
        return FactoryContexto.obtener_contexto(contexto, recurso)
    except Exception as ex:
        raise ex


def definir_repositorio(contexto):
    return RepositorioSenial(contexto)


class Configurador(object):
    """
    El Configurador es un contenedor de objetos que participan de la solucion
    """

    ctx_datos_adquisicion = definir_contexto(obtener_dir_datos() + '/adq')
    ctx_datos_procesamiento = definir_contexto(obtener_dir_datos() + '/pro')

    rep_adquisicion = definir_repositorio(ctx_datos_adquisicion)
    rep_procesamiento = definir_repositorio(ctx_datos_procesamiento)

    adquisidor = definir_adquisidor()  # Se configura el tipo de adquisidor
    procesador = definir_procesador()  # Se configura el tipo de procesador


    def __init__(self):
        Configurador.rep_adquisicion.listar()
        Configurador.rep_procesamiento.listar()
        pass

