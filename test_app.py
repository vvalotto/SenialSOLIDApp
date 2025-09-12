from flask import Flask, render_template
import os

# Create Flask app
app = Flask(__name__, 
           template_folder='01_presentacion/webapp/templates',
           static_folder='01_presentacion/webapp/static')
app.config['SECRET_KEY'] = "dev-key-for-testing"

# Mock data for testing
mock_seniales = ['SIGNAL_001', 'SIGNAL_002', 'SIGNAL_003', 'SIGNAL_004']
mock_componentes = [
    'Adquisidor: v1.5.0',
    'Procesador: v1.5.0', 
    'Persistidor: v1.5.0',
    'Configurador: v1.5.0',
    'Utilidades: v1.5.0'
]

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/acerca/')
def acerca():
    return render_template('general/acerca.html')

@app.route('/versiones/')
def versiones():
    return render_template('aplicacion/versiones.html', lista=mock_componentes)

@app.route('/componentes/')
def componentes():
    # Mock component types
    tipos_componentes = [
        'Adquisidor de señales',
        'Procesador de datos',
        'Visualizador de gráficos',
        'Persistidor de información',
        'Utilidades del sistema'
    ]
    return render_template('aplicacion/componentes.html', lista=tipos_componentes)

@app.route('/adquisicion/')
def adquisicion():
    return render_template('aplicacion/adquisicion.html', seniales=mock_seniales)

@app.route('/procesamiento/')
def procesamiento():
    return render_template('aplicacion/procesamiento.html', seniales=mock_seniales)

@app.route('/visualizacion/')
def visualizacion():
    return render_template('aplicacion/visualizacion.html', seniales=mock_seniales)

if __name__ == '__main__':
    print("🚀 Iniciando SenialSOLIDApp - Bootstrap 5 Testing Server")
    print("📍 URL: http://localhost:8080")
    print("🔧 Bootstrap 5.3.3 LTS implementado")
    print("✅ Templates modernizados y responsive")
    print("🎯 Testing manual disponible")
    print("-" * 50)
    app.run(debug=True, host='0.0.0.0', port=8080)