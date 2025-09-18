#!/usr/bin/env python3
"""
Aplicación web original SenialSOLIDApp - VERSIÓN CORREGIDA PARA PYCHARM
Ejecuta desde el directorio webapp con toda la funcionalidad original
"""

# CONFIGURACIÓN AUTOMÁTICA DE RUTAS PARA PYCHARM
import sys
import os
from pathlib import Path

# Configurar rutas automáticamente
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Subir 3 niveles desde webapp

# Rutas necesarias para la aplicación original
required_paths = [
    project_root,
    project_root / "01_presentacion" / "webapp",
    project_root / "03_aplicacion",
    project_root / "04_dominio",
    project_root / "05_Infraestructura",
    project_root / "config",
]

# Agregar rutas al PYTHONPATH
for path in required_paths:
    path_str = str(path)
    if path_str not in sys.path and path.exists():
        sys.path.insert(0, path_str)

print("🔧 PYTHONPATH configurado para aplicación original desde webapp/")

try:
    from flask import Flask, render_template, flash, redirect, url_for
    from flask_bootstrap import Bootstrap

    # Intentar importar módulos del dominio
    try:
        import adquisicion
        import procesamiento
        import modelo
        import repositorios
        import utilidades
        from contenedor.configurador import Configurador
        domain_available = True
        print("✅ Módulos de dominio importados correctamente")
    except ImportError as e:
        print(f"⚠️  Módulos de dominio no disponibles: {e}")
        domain_available = False

    # Importar módulos locales
    from modelos import PanelInformes
    from forms import SenialForm

    print("✅ Módulos locales webapp importados correctamente")

    # Crear aplicación Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-senial-original-webapp'

    # Configurar Bootstrap
    bootstrap = Bootstrap(app)

    # Crear panel de informes
    panel_informes = PanelInformes()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.route('/')
    def inicio():
        """Página de inicio de SenialSOLIDApp"""
        return render_template('general/inicio.html')

    @app.route('/acerca/')
    def acerca():
        """Información acerca del proyecto"""
        return render_template('general/acerca.html')

    @app.route('/componentes/')
    def componentes():
        """Listado de componentes del sistema"""
        try:
            if domain_available:
                lista_tipos_componentes = panel_informes.informar_versiones()
            else:
                lista_tipos_componentes = [
                    "Adquisidor: v2.0.0 (modo demo)",
                    "Procesador: v2.0.0 (modo demo)",
                    "Persistidor: v2.0.0 (modo demo)",
                    "Configurador: v2.0.0 (modo demo)",
                    "Utilidades: v2.0.0 (modo demo)"
                ]
            return render_template('aplicacion/componentes.html', lista=lista_tipos_componentes)
        except Exception as e:
            print(f"Error en componentes: {e}")
            lista_tipos_componentes = ["Error cargando componentes"]
            return render_template('aplicacion/componentes.html', lista=lista_tipos_componentes)

    @app.route('/versiones/')
    def versiones():
        """Información de versiones del sistema"""
        try:
            if domain_available:
                lista_versiones = panel_informes.informar_versiones()
            else:
                lista_versiones = [
                    "Flask: 3.0.0",
                    "Bootstrap: 4.0.0",
                    "Python: 3.11+",
                    "SenialSOLID: v2.0.0 (modo demo)"
                ]
            return render_template('aplicacion/versiones.html', lista=lista_versiones)
        except Exception as e:
            print(f"Error en versiones: {e}")
            lista_versiones = ["Error cargando versiones"]
            return render_template('aplicacion/versiones.html', lista=lista_versiones)

    @app.route("/adquisicion/", methods=['GET', 'POST'])
    def adquisicion():
        """Módulo de adquisición de señales"""
        form = SenialForm()
        lista_seniales = []

        if form.validate_on_submit():
            try:
                if domain_available:
                    # Intentar usar el sistema real
                    configurador = Configurador()
                    configurador.configurar()

                    # Crear señal usando la fábrica
                    factory_senial = modelo.factory_senial.FactorySenial()
                    senial = factory_senial.crear_senial(
                        tipo='senoidal',
                        identificador=form.identificador.data,
                        amplitud=form.amplitud.data if hasattr(form, 'amplitud') else 1.0,
                        frecuencia=form.frecuencia.data if hasattr(form, 'frecuencia') else 1.0
                    )

                    # Adquirir señal
                    factory_adquisidor = adquisicion.factory_adquisidor.FactoryAdquisidor()
                    adquisidor = factory_adquisidor.crear_adquisidor('manual')
                    lista_seniales = adquisidor.adquirir(senial)

                    flash('Señal adquirida exitosamente con sistema completo')
                else:
                    # Modo demo
                    lista_seniales = [
                        f"Señal Demo - ID: {form.identificador.data}",
                        f"Tipo: Senoidal (simulada)",
                        f"Estado: Adquirida en modo demo"
                    ]
                    flash('Señal simulada adquirida (modo demo)')

            except Exception as e:
                print(f"Error en adquisición: {e}")
                flash(f'Error procesando señal: {str(e)}')
                lista_seniales = [f"Error: {str(e)}"]

        return render_template('aplicacion/adquisicion.html', form=form, seniales=lista_seniales)

    @app.route("/procesamiento/")
    def procesamiento():
        """Módulo de procesamiento de señales"""
        return render_template('aplicacion/procesamiento.html')

    @app.route("/visualizacion/")
    def visualizacion():
        """Módulo de visualización de señales"""
        return render_template('aplicacion/visualizacion.html')

    if __name__ == '__main__':
        print("🚀 Iniciando SenialSOLIDApp Original desde webapp/")
        print("🎯 Funcionalidad completa: Adquisición, Procesamiento, Visualización")
        print("🌐 URL: http://localhost:5005")
        print("📁 Templates: Usando templates originales del proyecto")
        print("🔧 Dominio:", "✅ Completo" if domain_available else "⚠️ Modo Demo")
        print("⏹️  Presiona Ctrl+C para detener")
        print("")

        app.run(
            host='0.0.0.0',
            port=5005,
            debug=True
        )

except ImportError as e:
    print(f"❌ Error de importación crítico: {e}")
    print("💡 Verifica que flask y flask-bootstrap estén instalados")
    print("💡 pip install flask flask-bootstrap")

except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()