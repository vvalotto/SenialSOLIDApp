"""
Configuración centralizada del sistema de logging estructurado.
Proporciona logging con formato JSON y rotación automática.
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class StructuredFormatter(logging.Formatter):
    """Formatter que convierte logs a formato JSON estructurado"""

    def __init__(self, include_trace: bool = True):
        super().__init__()
        self.include_trace = include_trace

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Agregar información de contexto si está disponible
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation

        # Agregar información de excepción si está presente
        if record.exc_info and self.include_trace:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info) if record.exc_info else None
            }

        # Agregar campos extra si existen
        for key, value in record.__dict__.items():
            if key not in {'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message',
                          'user_id', 'session_id', 'request_id', 'operation'}:
                log_data['extra'] = log_data.get('extra', {})
                log_data['extra'][key] = value

        return json.dumps(log_data, ensure_ascii=False, separators=(',', ':'))


class LoggerFactory:
    """Factory para crear loggers configurados de manera consistente"""

    _configured = False
    _log_dir = None
    _log_level = logging.INFO

    @classmethod
    def setup(cls,
              log_dir: Optional[str] = None,
              log_level: str = 'INFO',
              max_file_size: int = 10 * 1024 * 1024,  # 10MB
              backup_count: int = 5,
              console_output: bool = True,
              config_dict: Optional[Dict[str, Any]] = None):
        """
        Configura el sistema de logging globalmente

        Args:
            log_dir: Directorio para archivos de log
            log_level: Nivel de logging
            max_file_size: Tamaño máximo de archivo antes de rotar
            backup_count: Número de archivos de backup a mantener
            console_output: Si mostrar logs en consola
            config_dict: Configuración desde YAML/config externo
        """
        if cls._configured:
            return

        # Usar configuración externa si está disponible
        if config_dict and 'logging' in config_dict:
            log_config = config_dict['logging']

            log_dir = log_config.get('directory', log_dir or 'logs')
            log_level = log_config.get('level', log_level)
            console_output = log_config.get('console_output', console_output)

            if 'rotation' in log_config:
                max_file_size = log_config['rotation'].get('max_file_size_mb', 10) * 1024 * 1024
                backup_count = log_config['rotation'].get('backup_count', 5)

        # Configurar directorio de logs
        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), 'logs')

        cls._log_dir = Path(log_dir)
        cls._log_dir.mkdir(parents=True, exist_ok=True)

        # Convertir nivel de string a constante
        cls._log_level = getattr(logging, log_level.upper(), logging.INFO)

        # Configurar root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(cls._log_level)

        # Limpiar handlers existentes
        root_logger.handlers.clear()

        # Handler para archivo principal con rotación
        main_log_file = cls._log_dir / 'app.log'
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(cls._log_level)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)

        # Handler para errores separado
        error_log_file = cls._log_dir / 'error.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)

        # Handler para consola (solo si está habilitado)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(cls._log_level)

            # Formatter más simple para consola
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str, extra_context: Optional[Dict[str, Any]] = None) -> logging.Logger:
        """
        Obtiene un logger configurado para el módulo especificado

        Args:
            name: Nombre del logger (generalmente __name__)
            extra_context: Contexto adicional para incluir en logs

        Returns:
            Logger configurado
        """
        if not cls._configured:
            cls.setup()

        logger = logging.getLogger(name)

        # Si hay contexto extra, crear un adapter
        if extra_context:
            logger = logging.LoggerAdapter(logger, extra_context)

        return logger

    @classmethod
    def get_module_logger(cls, module_name: str,
                         operation: Optional[str] = None) -> logging.Logger:
        """
        Obtiene un logger específico para un módulo con contexto de operación

        Args:
            module_name: Nombre del módulo
            operation: Operación que se está realizando

        Returns:
            Logger configurado con contexto del módulo
        """
        context = {'module': module_name}
        if operation:
            context['operation'] = operation

        return cls.get_logger(module_name, context)


def get_logger(name: str = None, **kwargs) -> logging.Logger:
    """
    Función de conveniencia para obtener un logger

    Args:
        name: Nombre del logger (si no se proporciona, usa el caller)
        **kwargs: Contexto adicional

    Returns:
        Logger configurado
    """
    if name is None:
        # Obtener el nombre del módulo que llamó esta función
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')

    return LoggerFactory.get_logger(name, kwargs if kwargs else None)


# Alias para compatibilidad
setup_logging = LoggerFactory.setup
get_module_logger = LoggerFactory.get_module_logger