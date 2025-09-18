import adquisicion
import procesamiento
import modelo
import repositorios
import utilidades
from contenedor.configurador import *


class PanelInformes(object):
    '''
    Clase que genera los informacion general a mostrar
    '''
    def informar_versiones(self):
        lista_componentes = []
        lista_componentes.append('Adquisidor: ' + adquisicion.__version__)
        lista_componentes.append('Procesador: ' + procesamiento.__version__)
        lista_componentes.append('Persistidor: ' + repositorios.__version__)
        lista_componentes.append('Configurador: ' + modelo.__version__)
        lista_componentes.append('Utilidades: ' + utilidades.__version__)
        return lista_componentes

    def informar_componentes(self):
        lista_tipos_componentes = []
        lista_tipos_componentes.append("Tipo Adquisidor: " + str(Configurador.adquisidor.__class__))
        lista_tipos_componentes.append("Tipo Procesador: " + str(Configurador.procesador.__class__))
        lista_tipos_componentes.append("Tipo Señal (Adquisidor): " +
                                   str(Configurador.adquisidor._senial.__class__))
        lista_tipos_componentes.append("Tipo Señal (Procesador): " +
                                   str(Configurador.procesador._senial_procesada.__class__))
        lista_tipos_componentes.append("Tipo Repositorio (Adquisidor): " +
                                   str(Configurador.rep_adquisicion.__class__))
        lista_tipos_componentes.append("Tipo Repositorio (Procesador): " +
                                   str(Configurador.rep_procesamiento.__class__))
        lista_tipos_componentes.append("Tipo Contexto de Repositorio (Adquisidor): " +
                                   str(Configurador.ctx_datos_adquisicion.__class__))
        lista_tipos_componentes.append("Tipo Contexto de Repositorio (Procesador): " +
                                   str(Configurador.ctx_datos_procesamiento.__class__))
        return lista_tipos_componentes

class AccionSenial(object):

    @staticmethod
    def adquirir(form):
        ad = Configurador.adquisidor
        ra = Configurador.rep_adquisicion
        ad.leer_senial()
        sa = ad.obtener_senial_adquirida()
        sa.id = form.identificador.data
        sa.comentario = form.descripcion.data
        sa.fecha_adquisicion = form.fecha.data
        ra.guardar(sa)

    @staticmethod
    def listar_seniales_adquiridas():
        ra = Configurador.rep_adquisicion
        return ra.listar()