"""
Módulo de configuración segura para SenialSOLID App
Maneja variables de entorno y configuración de aplicación de forma segura

SECURITY CRITICAL: Este módulo maneja SECRET_KEY y otros valores sensibles
Nunca hardcodear valores de seguridad en este archivo
"""

import os
import secrets
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """
    Configuración base de la aplicación
    Utiliza variables de entorno para valores sensibles
    
    SECURITY: SECRET_KEY debe estar en variables de entorno, NUNCA hardcodeada
    """
    
    # SECRET_KEY: Clave secreta para sesiones y CSRF protection
    # CRITICAL: Nunca hardcodear este valor
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite'))
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """
        Inicialización de la aplicación con validación de configuración
        Valida que todos los valores críticos de seguridad estén configurados
        """
        # Validar que SECRET_KEY está configurada
        if not Config.SECRET_KEY:
            raise ValueError(
                "🚨 SECURITY ERROR: SECRET_KEY environment variable is required but not set.\n"
                "Please set SECRET_KEY in your .env file or environment variables.\n"
                "Example: SECRET_KEY=your-super-secure-random-key-here"
            )
        
        # Validar que SECRET_KEY tiene una longitud mínima segura
        if len(Config.SECRET_KEY) < 32:
            raise ValueError(
                f"🚨 SECURITY ERROR: SECRET_KEY must be at least 32 characters long for security.\n"
                f"Current length: {len(Config.SECRET_KEY)}\n"
                f"Use: python -c \"import secrets; print(secrets.token_urlsafe(32))\" to generate a secure key"
            )
        
        # Verificar que no sea un valor por defecto inseguro
        insecure_defaults = ['Victor', 'secret', 'key', 'password', '123', 'test', 'dev', 'default']
        if Config.SECRET_KEY.lower() in [x.lower() for x in insecure_defaults]:
            raise ValueError(
                f"🚨 SECURITY ERROR: SECRET_KEY contains an insecure default value: '{Config.SECRET_KEY}'\n"
                f"This is a known weak secret. Please use a cryptographically secure random key."
            )
        
        # Log de configuración exitosa (sin exponer el secret)
        print("✅ Configuration loaded successfully")
        print(f"📊 Database: {Config.SQLALCHEMY_DATABASE_URI}")
        print(f"🐛 Debug mode: {Config.DEBUG}")
        print(f"🔐 SECRET_KEY: [CONFIGURED SECURELY - {len(Config.SECRET_KEY)} characters]")

class DevelopmentConfig(Config):
    """
    Configuración para desarrollo
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data-dev.sqlite'))

class ProductionConfig(Config):
    """
    Configuración para producción
    Validaciones de seguridad adicionales
    """
    DEBUG = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Validaciones adicionales para producción
        if Config.SECRET_KEY in ['default-dev-key-change-in-production', 'dev-key', 'development']:
            raise ValueError(
                "🚨 PRODUCTION SECURITY ALERT: Development SECRET_KEY detected in production!\n"
                "You MUST set a unique, secure SECRET_KEY for production environment."
            )
        
        # En producción, verificar que DEBUG esté desactivado
        if Config.DEBUG:
            raise ValueError(
                "🚨 PRODUCTION SECURITY ALERT: DEBUG mode is enabled in production!\n"
                "Set FLASK_DEBUG=false in your production environment."
            )

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def generate_secret_key():
    """
    Genera una clave secreta segura para usar en SECRET_KEY
    Útil para setup inicial y rotación de keys
    """
    return secrets.token_urlsafe(32)

if __name__ == '__main__':
    # Ejecutar para generar una nueva SECRET_KEY
    print("🔐 Generated secure SECRET_KEY:")
    print(generate_secret_key())
    print("\n💡 Add this to your .env file as:")
    print(f"SECRET_KEY={generate_secret_key()}")
