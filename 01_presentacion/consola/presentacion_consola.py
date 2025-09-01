#!/usr/bin/env python3

from abc import ABCMeta, abstractclassmethod
import os
import collections
import adquisicion
import procesamiento
import modelo
import repositorios
import utilidades
import contenedor
import acceso_datos

from modelo.senial import Senial
from contenedor.configurador import Configurador


class Pantalla(metaclass=ABCMeta):

    def __init__(self, titulo):
        self._titulo = titulo
        pass

    @abstractclassmethod
    def mostrar(self):
        pass

    def mostrar_titulo(self):
        os.system("clear")
        print(self._titulo)
        print('-' * len(self._titulo))
        print()

    @staticmethod
    def tecla():
        """
        Funcion que solicita un tecla para continuar
        """
        while True:
            if input('C para continuar> ') == "C":
                break
        return


class PantallaMenu(Pantalla):

    def __init__(self, titulo, opciones):
        super().__init__(titulo)
        self._opciones = opciones
        pass

    def mostrar_opciones(self):
        items_opciones = []
        for opcion in self._opciones:
            items_opciones.append(opcion)

        for i in range(0, len(items_opciones)):
            print("{0} > {1}".format(i + 1, items_opciones[i]))

    def mostrar(self):
        """
        Genera la pantalla de opciones
        """
        while True:
            self.mostrar_titulo()
            self.mostrar_opciones()

            items_opciones = []
            for opcion in self._opciones:
                items_opciones.append(opcion)

            lista_id_opciones = []
            for i in range(0, len(items_opciones)):
                lista_id_opciones.append(str(i + 1))

            opcion = input('Elija una opcion > ')
            if opcion in lista_id_opciones:
                if items_opciones[int(opcion) - 1] == "Volver":
                    break
                else:
                    self._opciones[items_opciones[int(opcion) - 1]].mostrar()


class PantallaInfo(Pantalla):

    def mostrar(self):
        self.mostrar_titulo()


class PantallaInfoAcercaDe(PantallaInfo):

    def mostrar(self):
        self.mostrar_titulo()
        try:
            with open('./presentacion/acerca.txt', 'r') as archivo_acerca:
                print(archivo_acerca.read())
        except IOError as eIO:
            print("Error al leer el archivo: ", eIO)


class PantallaInfoVersiones(PantallaInfo):

    def mostrar(self):
        super().mostrar()
        print("adquisidor: " + adquisicion.__version__)
        print("procesador: " + procesamiento.__version__)
        print("persistidor: " + repositorios.__version__)
        print("configurador: " + contenedor.__version__)
        print("modelo: " + modelo.__version__)
        print("utiles: " + utilidades.__version__)
        print()
        self.tecla()


class PantallaInfoComponentes(PantallaInfo):
    def mostrar(self):
        super().mostrar()
        print("Tipo adquisidor: ", Configurador.adquisidor.__class__)
        print("Tipo procesador: ", Configurador.procesador.__class__)
        print("Tipo contexto de datos para adquisidor: ", Configurador.ctx_datos_adquisicion.__class__)
        print("Tipo contexto de datos para procesador: ", Configurador.ctx_datos_procesamiento.__class__)
        print("Tipo repositorio de datos para señal adquirida", Configurador.rep_adquisicion.__class__)
        print("Tipo repositorio de datos para señal procesada", Configurador.rep_procesamiento.__class__)
        print("Tipo señal Adquirida: ", Configurador.adquisidor._senial.__class__)
        print("Tipo señal Procesada: ", Configurador.procesador._senial_procesada.__class__)
        print()
        self.tecla()


class PantallaAccion(Pantalla):

    def mostrar(self):
        super().mostrar_titulo()


class PantallaAccionFin(PantallaAccion):

    def mostrar(self):
        super().mostrar()
        print("Fin del programa")
        exit()

from managers.controlador_adquisicion import ControladorAdquisicion
from managers.controlador_procesamiento import ControladorProcesamiento


class PantallaAccionAdquisicion(PantallaAccion):

    def mostrar(self):
        super().mostrar()
        print("Incio - Paso 1 - Adquisición")
        ctrl_adq = ControladorAdquisicion()
        senial = ctrl_adq.adquirir_senial()
        print('Cantidad de valores obtenidos {0}'.format(senial.cantidad))

        ctrl_adq.identificar_senial(senial, "Idenfificar Señal Adquirida")

        print('Se persiste la señal adquirida')
        ctrl_adq.guardar_senial(senial)
        print('Señal Guardada')
        Pantalla.tecla()


class PantallaAccionProcesamiento(PantallaAccion):

    def mostrar(self):
        super().mostrar()
        ctrl_adq = ControladorAdquisicion()
        ctrl_pro = ControladorProcesamiento()
        print("Incio - Paso 2 - Procesamiento")
        id_senial = self.seleccionar_senial()
        senial_a_procesar = ctrl_adq.obtener_senial(id_senial)
        Pantalla.tecla()

        print('Se procesa la señal')
        sp = ctrl_pro.procesar_senial(senial_a_procesar)
        Pantalla.tecla()

        ctrl_pro.identificar_senial(sp, "Identificar señal procesada")
        print('Se persiste la señal procesada')
        ctrl_pro.guardar_senial(sp)
        print('Señal Guardada')
        Pantalla.tecla()

    def seleccionar_senial(self):
        print('Lista de seniales adquiridas')
        idx = 1
        ctrl_adq = ControladorAdquisicion()
        lista_seniales = ctrl_adq.listar_seniales_adquiridas()

        while True:
            for id_senial in lista_seniales:
                print('{0} > {1}'.format(idx, id_senial))
                idx += 1

            op_senial = int(input('Elija una senial (nro):'))
            if op_senial <= len(lista_seniales):
                return lista_seniales[op_senial - 1]


class PantallaAccionVisualizacion(PantallaAccion):

    def mostrar(self):
        super().mostrar()
        print("Incio - Paso 3 - Mostrar Senial")
        id_senial_adq = input("Ingresar el identificador de la señial adquirida:")
        id_senial_pro = input("Ingresar el identificador de la señial procesada:")
        rep_adq = Configurador.rep_adquisicion
        rep_pro = Configurador.rep_procesamiento
        adquirida = rep_adq.obtener(Senial(), id_senial_adq)
        procesada = rep_pro.obtener(Senial(), id_senial_pro)
        print("{0:20s}{1:s}".format("Adquirida", "Procesada"))
        for i in range(0, adquirida.cantidad):
            print("{0:f}{1:20f}".format(adquirida.obtener_valor(i), procesada.obtener_valor(i)))
        self.tecla()


class AplicacionSOLID(object):

    @classmethod
    def iniciar(cls):
        """
        Inicializa las pantallas y menus de la aplicacion
        """

        """
        Pantallas centrales de la aplicacion
        """
        p_adquisicion = PantallaAccionAdquisicion("Adquisicion de la Señal")
        p_procesamiento = PantallaAccionProcesamiento("Procesamiento de la Señal")
        p_visualizacion = PantallaAccionVisualizacion("Visualizacion de la Señal")

        """
        Configura el menu de Aplicacion
        """
        op_menu_aplicacion = collections.OrderedDict()
        op_menu_aplicacion["Adquidir Señal"] = p_adquisicion
        op_menu_aplicacion["Procesar Señal"] = p_procesamiento
        op_menu_aplicacion["Visualizar Señal"] = p_visualizacion
        op_menu_aplicacion["Volver"] = None

        """
        Pantallas Iniciales de la Aplicacion
        """
        p_configuracion = PantallaInfoComponentes("Configuracion de elementos")
        p_versiones = PantallaInfoVersiones("Versiones de los componentes")
        p_acerca_de = PantallaInfoAcercaDe("Acerca")
        p_menu_aplicacion = PantallaMenu("Aplicacion", op_menu_aplicacion)
        p_salir = PantallaAccionFin("Salir")

        """
        Configuración del menu principal
        """
        op_menu_principal = collections.OrderedDict()
        op_menu_principal["Configuracion"] = p_configuracion
        op_menu_principal["Versiones"] = p_versiones
        op_menu_principal["Aplicacion"] = p_menu_aplicacion
        op_menu_principal["Acerca de"] = p_acerca_de
        op_menu_principal["Salir"] = p_salir

        p_menu_principal = PantallaMenu("Principal", op_menu_principal)

        """
        Iniciar Aplicacion llamando al menu principal
        """
        p_menu_principal.mostrar()