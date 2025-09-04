"""
Cargador de configuración flexible para SenialSOLID
==================================================
Soporta YAML/TOML con variables de entorno y validación de schema.
"""

import os
import re
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError


class ConfigLoader:
    """Cargador de configuración con soporte para variables de entorno y validación."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Inicializa el cargador de configuración.
        
        Args:
            config_dir: Directorio de configuración. Por defecto usa 'config' relativo al proyecto.
        """
        if config_dir is None:
            # Determinar directorio del proyecto
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self._config_cache: Optional[Dict[str, Any]] = None
        self._schema_cache: Optional[Dict[str, Any]] = None
    
    def load_config(self, environment: Optional[str] = None, 
                   validate_schema: bool = True) -> Dict[str, Any]:
        """
        Carga la configuración con soporte para entornos y variables de entorno.
        
        Args:
            environment: Entorno específico (development, testing, production).
                        Si no se especifica, usa la variable ENVIRONMENT.
            validate_schema: Si True, valida la configuración contra el schema.
            
        Returns:
            Diccionario con la configuración cargada y expandida.
            
        Raises:
            FileNotFoundError: Si no se encuentra el archivo de configuración.
            ValidationError: Si la configuración no es válida según el schema.
            ValueError: Si hay errores en variables de entorno o configuración.
        """
        if self._config_cache is None:
            self._config_cache = self._load_raw_config()
        
        # Expandir variables de entorno
        config = self._expand_environment_variables(self._config_cache)
        
        # Determinar entorno
        if environment is None:
            environment = os.getenv('ENVIRONMENT', config.get('app', {}).get('environment', 'development'))
        
        config['app']['environment'] = environment
        
        # Aplicar configuración específica del entorno
        if 'environments' in config and environment in config['environments']:
            env_config = config['environments'][environment]
            config = self._merge_config(config, env_config)
        
        # Validar configuración si se solicita
        if validate_schema:
            self._validate_config(config)
        
        # Calcular paths absolutos
        config = self._resolve_paths(config)
        
        return config
    
    def _load_raw_config(self) -> Dict[str, Any]:
        """Carga el archivo de configuración crudo desde YAML."""
        config_file = self.config_dir / "config.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_schema(self) -> Dict[str, Any]:
        """Carga el schema de validación."""
        if self._schema_cache is None:
            schema_file = self.config_dir / "config_schema.yaml"
            
            if not schema_file.exists():
                raise FileNotFoundError(f"Schema de configuración no encontrado: {schema_file}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                self._schema_cache = yaml.safe_load(f)
        
        return self._schema_cache
    
    def _expand_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expande variables de entorno en la configuración.
        Soporta el formato ${VAR_NAME:-default_value}.
        """
        def expand_value(value):
            if isinstance(value, str):
                # Patrón para ${VAR_NAME:-default}
                pattern = r'\$\{([^}]+)\}'
                
                def replace_var(match):
                    var_expr = match.group(1)
                    if ':-' in var_expr:
                        var_name, default_value = var_expr.split(':-', 1)
                        return os.getenv(var_name, default_value)
                    else:
                        var_name = var_expr
                        env_value = os.getenv(var_name)
                        if env_value is None:
                            raise ValueError(f"Variable de entorno requerida no encontrada: {var_name}")
                        return env_value
                
                return re.sub(pattern, replace_var, value)
            elif isinstance(value, dict):
                return {k: expand_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [expand_value(item) for item in value]
            else:
                return value
        
        return expand_value(config)
    
    def _merge_config(self, base_config: Dict[str, Any], 
                     env_config: Dict[str, Any]) -> Dict[str, Any]:
        """Combina configuración base con configuración específica del entorno."""
        result = base_config.copy()
        
        def deep_merge(base_dict, env_dict):
            for key, value in env_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_merge(result, env_config)
        return result
    
    def _validate_config(self, config: Dict[str, Any]):
        """Valida la configuración contra el schema."""
        try:
            schema = self._load_schema()
            validate(instance=config, schema=schema)
        except ValidationError as e:
            raise ValidationError(f"Configuración inválida: {e.message}")
    
    def _resolve_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve paths relativos a absolutos basados en el directorio del proyecto."""
        result = config.copy()
        
        # Determinar directorio base del proyecto
        project_root = Path(__file__).parent.parent
        
        paths_config = result.get('paths', {})
        base_data_dir = paths_config.get('base_data_dir', 'datos')
        
        # Si el path base no es absoluto, hacerlo relativo al proyecto
        if not Path(base_data_dir).is_absolute():
            base_data_dir = project_root / base_data_dir
        else:
            base_data_dir = Path(base_data_dir)
        
        # Calcular paths derivados
        result['computed_paths'] = {
            'project_root': str(project_root),
            'base_data_dir': str(base_data_dir),
            'input_dir': str(base_data_dir / paths_config.get('input_subdir', 'entrada')),
            'acquisition_dir': str(base_data_dir / paths_config.get('acquisition_subdir', 'adq')),
            'processing_dir': str(base_data_dir / paths_config.get('processing_subdir', 'pro')),
            'input_file_path': str(base_data_dir / paths_config.get('input_subdir', 'entrada') / 
                                 result.get('acquisition', {}).get('input_file', 'datos.txt'))
        }
        
        return result
    
    def get_config_value(self, key_path: str, default: Any = None, 
                        environment: Optional[str] = None) -> Any:
        """
        Obtiene un valor específico de la configuración usando notación de puntos.
        
        Args:
            key_path: Ruta de la clave usando notación de puntos (ej: 'processing.threshold').
            default: Valor por defecto si no se encuentra la clave.
            environment: Entorno específico para cargar la configuración.
            
        Returns:
            Valor de la configuración o default si no se encuentra.
        """
        config = self.load_config(environment=environment)
        
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def reload_config(self):
        """Fuerza la recarga de la configuración desde el archivo."""
        self._config_cache = None
        self._schema_cache = None


# Instancia global del cargador de configuración
_config_loader = ConfigLoader()

def load_config(environment: Optional[str] = None, validate_schema: bool = True) -> Dict[str, Any]:
    """
    Función de conveniencia para cargar la configuración.
    
    Args:
        environment: Entorno específico a cargar.
        validate_schema: Si validar contra el schema.
        
    Returns:
        Configuración cargada y procesada.
    """
    return _config_loader.load_config(environment=environment, validate_schema=validate_schema)

def get_config_value(key_path: str, default: Any = None, 
                    environment: Optional[str] = None) -> Any:
    """
    Función de conveniencia para obtener un valor específico de configuración.
    
    Args:
        key_path: Ruta de la clave usando notación de puntos.
        default: Valor por defecto.
        environment: Entorno específico.
        
    Returns:
        Valor de configuración o default.
    """
    return _config_loader.get_config_value(key_path, default, environment)