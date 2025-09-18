"""
Configurador modernizado para SenialSOLID
=========================================
Sistema de configuración flexible que soporta tanto YAML como XML (legacy).
Mantiene compatibilidad hacia atrás mientras migra al nuevo sistema.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Añadir el directorio raíz al path para imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modelo.factory_senial import *
from procesamiento.factory_procesador import *
from adquisicion.factory_adquisidor import *
from repositorios.repositorio import *
from acceso_datos.factory_context import *

# Intentar importar el nuevo sistema de configuración
try:
    from config.config_loader import load_config, get_config_value, ConfigLoader
    MODERN_CONFIG_AVAILABLE = True
except ImportError:
    MODERN_CONFIG_AVAILABLE = False
    print("⚠️  Advertencia: Sistema moderno de configuración no disponible. Usando configuración legacy.")

# Importar configurador legacy para fallback
try:
    from xml.dom import minidom
    XML_SUPPORT = True
except ImportError:
    XML_SUPPORT = False


class ConfiguradorModerno:
    """
    Configurador modernizado con soporte dual para YAML y XML.
    Prioriza YAML cuando está disponible, fallback a XML legacy.
    """
    
    def __init__(self, force_legacy: bool = False, environment: Optional[str] = None):
        """
        Inicializa el configurador.
        
        Args:
            force_legacy: Si True, fuerza el uso del sistema XML legacy.
            environment: Entorno específico para cargar (development/testing/production).
        """
        self.force_legacy = force_legacy
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self._config_cache: Optional[Dict[str, Any]] = None
        self._use_modern = MODERN_CONFIG_AVAILABLE and not force_legacy
        
        # Cargar configuración
        self._load_configuration()
    
    def _load_configuration(self):
        """Carga la configuración usando el sistema disponible."""
        if self._use_modern:
            try:
                self._config_cache = load_config(environment=self.environment, validate_schema=True)
                print(f"✅ Configuración moderna cargada (entorno: {self.environment})")
            except Exception as e:
                print(f"⚠️  Error cargando configuración moderna: {e}")
                print("🔄 Fallback a configuración legacy...")
                self._use_modern = False
                self._load_legacy_configuration()
        else:
            self._load_legacy_configuration()
    
    def _load_legacy_configuration(self):
        """Carga configuración desde XML legacy."""
        if not XML_SUPPORT:
            raise ImportError("Ni configuración moderna ni soporte XML disponible")
        
        # Usar lógica original para encontrar el archivo XML
        config_path = self._obtener_ruta_config_xml()
        
        try:
            # Convertir XML a estructura similar al YAML
            self._config_cache = self._parse_xml_to_dict(config_path)
            print(f"📄 Configuración legacy cargada desde: {config_path}")
        except Exception as e:
            raise RuntimeError(f"Error cargando configuración legacy: {e}")
    
    def _obtener_ruta_config_xml(self) -> str:
        """Obtiene la ruta al archivo XML legacy (lógica original)."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        config_path = os.path.join(project_root, "03_aplicacion", "datos", "configuracion.xml")
        
        if not os.path.exists(config_path):
            config_path = "03_aplicacion/datos/configuracion.xml"
            if not os.path.exists(config_path):
                config_path = os.path.join(os.path.dirname(__file__), "..", "datos", "configuracion.xml")
                config_path = os.path.normpath(config_path)
        
        return config_path
    
    def _parse_xml_to_dict(self, xml_path: str) -> Dict[str, Any]:
        """Convierte XML legacy a estructura de diccionario compatible."""
        conf = minidom.parse(xml_path)
        
        # Obtener valores del XML
        dir_datos = conf.getElementsByTagName("dir_recurso_datos")[0].firstChild.data
        
        # Adquisidor
        adq_node = conf.getElementsByTagName("adquisidor")[0]
        adq_type = adq_node.firstChild.data.strip()
        adq_params = [p.firstChild.data for p in adq_node.getElementsByTagName("param")]
        
        # Procesador
        proc_node = conf.getElementsByTagName("procesador")[0]
        proc_type = proc_node.firstChild.data.strip()
        proc_params = [p.firstChild.data for p in proc_node.getElementsByTagName("param")]
        
        # Señales
        senial_adq_node = conf.getElementsByTagName("senial_adq")[0]
        senial_adq_type = senial_adq_node.firstChild.data.strip()
        senial_adq_size = int(senial_adq_node.getElementsByTagName("tamanio")[0].firstChild.data.strip())
        
        senial_pro_node = conf.getElementsByTagName("senial_pro")[0]
        senial_pro_type = senial_pro_node.firstChild.data.strip()
        senial_pro_size = int(senial_pro_node.getElementsByTagName("tamanio")[0].firstChild.data.strip())
        
        # Contexto
        contexto = conf.getElementsByTagName("contexto")[0].firstChild.data.strip()
        
        # Crear estructura compatible
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_path = os.path.dirname(os.path.dirname(current_dir))
        
        # Paths absolutos computados
        if not os.path.isabs(dir_datos):
            base_data_path = os.path.join(project_root_path, dir_datos)
        else:
            base_data_path = dir_datos
        
        base_data_path = os.path.normpath(base_data_path)
        
        return {
            'app': {
                'name': 'SenialSOLID',
                'version': '2.0',
                'environment': 'legacy'
            },
            'paths': {
                'base_data_dir': dir_datos,
            },
            'acquisition': {
                'type': adq_type,
                'input_file': adq_params[0] if adq_params else 'datos.txt',
                'signal': {
                    'type': senial_adq_type,
                    'size': senial_adq_size
                }
            },
            'processing': {
                'type': proc_type,
                'threshold': int(proc_params[0]) if proc_params else 5,
                'signal': {
                    'type': senial_pro_type,
                    'size': senial_pro_size
                }
            },
            'storage': {
                'context_type': contexto
            },
            'computed_paths': {
                'project_root': project_root_path,
                'base_data_dir': base_data_path,
                'acquisition_dir': os.path.join(base_data_path, 'adq'),
                'processing_dir': os.path.join(base_data_path, 'pro'),
                'input_dir': os.path.join(base_data_path, 'entrada') if 'entrada' in (adq_params[0] if adq_params else 'datos.txt') else base_data_path,
                'input_file_path': os.path.join(base_data_path, adq_params[0] if adq_params else 'datos.txt')
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna la configuración completa cargada."""
        return self._config_cache or {}
    
    def get_base_data_dir(self) -> str:
        """Obtiene el directorio base de datos."""
        config = self.get_config()
        return config.get('computed_paths', {}).get('base_data_dir', 'datos')
    
    def get_acquisition_dir(self) -> str:
        """Obtiene el directorio de adquisición."""
        config = self.get_config()
        return config.get('computed_paths', {}).get('acquisition_dir', 'datos/adq')
    
    def get_processing_dir(self) -> str:
        """Obtiene el directorio de procesamiento."""
        config = self.get_config()
        return config.get('computed_paths', {}).get('processing_dir', 'datos/pro')
    
    def create_acquisition_signal(self):
        """Crea la señal para adquisición."""
        config = self.get_config()
        acquisition_config = config.get('acquisition', {})
        signal_config = acquisition_config.get('signal', {})
        
        signal_type = signal_config.get('type', 'pila')
        signal_size = signal_config.get('size', 20)
        
        return FactorySenial.obtener_senial(signal_type, signal_size)
    
    def create_processing_signal(self):
        """Crea la señal para procesamiento."""
        config = self.get_config()
        processing_config = config.get('processing', {})
        signal_config = processing_config.get('signal', {})
        
        signal_type = signal_config.get('type', 'pila')
        signal_size = signal_config.get('size', 20)
        
        return FactorySenial.obtener_senial(signal_type, signal_size)
    
    def create_processor(self):
        """Crea el procesador configurado."""
        config = self.get_config()
        processing_config = config.get('processing', {})
        
        processor_type = processing_config.get('type', 'umbral')
        threshold = processing_config.get('threshold', 5)
        
        # Preparar parámetros como lista para compatibilidad con factory
        params = [str(threshold)]
        
        return FactoryProcesador.obtener_procesador(
            processor_type,
            self.create_processing_signal(),
            params
        )
    
    def create_acquisitor(self):
        """Crea el adquisidor configurado."""
        config = self.get_config()
        acquisition_config = config.get('acquisition', {})
        
        acquisitor_type = acquisition_config.get('type', 'senoidal')
        input_file = acquisition_config.get('input_file', 'datos.txt')
        
        # Preparar parámetros como lista para compatibilidad con factory
        input_file_path = config.get('computed_paths', {}).get('input_file_path', input_file)
        params = [input_file_path]
        
        return FactoryAdquisidor.obtener_adquisidor(
            acquisitor_type,
            self.create_acquisition_signal(),
            params
        )
    
    def create_context(self, resource_path: str):
        """Crea el contexto de acceso a datos."""
        config = self.get_config()
        storage_config = config.get('storage', {})
        
        context_type = storage_config.get('context_type', 'archivo')
        
        return FactoryContexto.obtener_contexto(context_type, resource_path)
    
    def create_repository(self, context):
        """Crea el repositorio de señales."""
        return RepositorioSenial(context)


class ConfiguradorCompatible(object):
    """
    Contenedor de objetos compatible con la clase original.
    Mantiene la interfaz existente mientras usa el nuevo sistema internamente.
    """
    
    def __init__(self, force_legacy: bool = False, environment: Optional[str] = None):
        """
        Inicializa el configurador compatible.
        
        Args:
            force_legacy: Forzar uso del sistema legacy.
            environment: Entorno específico a cargar.
        """
        # Crear configurador interno
        self._modern_configurator = ConfiguradorModerno(force_legacy=force_legacy, environment=environment)
        
        # Crear contextos y repositorios (interfaz compatible)
        self.ctx_datos_adquisicion = self._modern_configurator.create_context(
            self._modern_configurator.get_acquisition_dir()
        )
        self.ctx_datos_procesamiento = self._modern_configurator.create_context(
            self._modern_configurator.get_processing_dir()
        )
        
        self.rep_adquisicion = self._modern_configurator.create_repository(self.ctx_datos_adquisicion)
        self.rep_procesamiento = self._modern_configurator.create_repository(self.ctx_datos_procesamiento)
        
        self.adquisidor = self._modern_configurator.create_acquisitor()
        self.procesador = self._modern_configurator.create_processor()
        
        # Inicializar repositorios (comportamiento original)
        try:
            self.rep_adquisicion.listar()
            self.rep_procesamiento.listar()
        except Exception as e:
            print(f"⚠️  Advertencia: Error inicializando repositorios: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Expone la configuración cargada (nueva funcionalidad)."""
        return self._modern_configurator.get_config()
    
    def is_using_modern_config(self) -> bool:
        """Indica si se está usando el sistema moderno de configuración."""
        return self._modern_configurator._use_modern


# Instancia global compatible (drop-in replacement)
Configurador = ConfiguradorCompatible

# Funciones legacy para máxima compatibilidad
def obtener_dir_datos():
    """Función legacy para obtener directorio de datos."""
    configurator = ConfiguradorModerno()
    return configurator.get_base_data_dir()

def definir_senial_adquirir():
    """Función legacy para crear señal de adquisición."""
    configurator = ConfiguradorModerno()
    return configurator.create_acquisition_signal()

def definir_senial_procesar():
    """Función legacy para crear señal de procesamiento."""
    configurator = ConfiguradorModerno()
    return configurator.create_processing_signal()

def definir_procesador():
    """Función legacy para crear procesador."""
    configurator = ConfiguradorModerno()
    return configurator.create_processor()

def definir_adquisidor():
    """Función legacy para crear adquisidor."""
    configurator = ConfiguradorModerno()
    return configurator.create_acquisitor()

def definir_contexto(resource_path: str):
    """Función legacy para crear contexto."""
    configurator = ConfiguradorModerno()
    return configurator.create_context(resource_path)

def definir_repositorio(context):
    """Función legacy para crear repositorio."""
    configurator = ConfiguradorModerno()
    return configurator.create_repository(context)