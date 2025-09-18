#!/usr/bin/env python3
"""
Demo de uso del SSA-24 Input Validation Framework - Fase 2

Este archivo demuestra las capacidades completas del framework de validación
incluyendo validadores especializados para señales, archivos, API, etc.
"""

import sys
import os
import tempfile
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aplicacion.validation import (
    # Core framework
    ValidationPipeline,
    PipelineMode,

    # Signal validation
    SignalParameterValidator,
    SignalDataValidator,
    create_signal_validation_pipeline,

    # File validation
    FileTypeValidator,
    FileSizeValidator,
    create_file_validation_pipeline,

    # User input validation
    StringInputValidator,
    EmailValidator,
    PasswordValidator,
    create_user_input_validation_pipeline,

    # API validation
    APIParameterValidator,
    JSONSchemaValidator,
    create_api_validation_pipeline,

    # Configuration validation
    ConfigFileValidator,
    DatabaseConfigValidator,
    create_config_validation_pipeline,

    # Exceptions
    ValidationError,
    SecurityValidationError
)


def demo_signal_validation():
    """Demuestra validación especializada para señales"""
    print("=== Demo: Validación de Señales ===")

    # Crear validadores de parámetros de señales
    freq_validator = SignalParameterValidator('frequency')
    amplitude_validator = SignalParameterValidator('amplitude')
    data_validator = SignalDataValidator(max_length=1000, check_anomalies=True)

    print("1. Validando parámetros de señal:")

    # Parámetros válidos
    test_params = [
        ('frequency', 1000.0),
        ('amplitude', 5.0),
        ('frequency', -10.0),  # Inválida
        ('amplitude', 15.0)    # Fuera de rango
    ]

    for param_type, value in test_params:
        if param_type == 'frequency':
            result = freq_validator.validate(value)
        else:
            result = amplitude_validator.validate(value)

        print(f"   {param_type} = {value}: {'✓ Válido' if result.is_valid else '✗ Inválido'}")
        if not result.is_valid:
            print(f"     Error: {result.errors[0].message}")

    print("\n2. Validando datos de señal:")

    # Datos de prueba
    test_signals = [
        [1.0, 2.0, 3.0, 2.0, 1.0],  # Válida
        list(range(2000)),            # Muy larga
        [1.0, float('nan'), 3.0],     # Con NaN
    ]

    for i, signal_data in enumerate(test_signals, 1):
        result = data_validator.validate(signal_data)
        print(f"   Señal {i}: {'✓ Válida' if result.is_valid else '✗ Inválida'}")
        if not result.is_valid:
            print(f"     Error: {result.errors[0].message}")
        if result.metadata:
            print(f"     Metadata: {result.metadata}")

    print()


def demo_file_validation():
    """Demuestra validación de archivos"""
    print("=== Demo: Validación de Archivos ===")

    # Crear validadores de archivos
    type_validator = FileTypeValidator(allowed_extensions=['wav', 'csv', 'json'])
    size_validator = FileSizeValidator(max_size=1024 * 1024)  # 1MB

    print("1. Validando tipos de archivo:")

    test_files = [
        'signal_data.wav',
        'signal_data.csv',
        'malware.exe',        # Tipo peligroso
        'unknown.xyz'         # Tipo no permitido
    ]

    for filename in test_files:
        result = type_validator.validate(filename)
        print(f"   {filename}: {'✓ Válido' if result.is_valid else '✗ Inválido'}")
        if not result.is_valid:
            print(f"     Error: {result.errors[0].message}")

    print("\n2. Creando archivo temporal para validación:")

    # Crear archivo temporal para probar validación de contenido
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("timestamp,amplitude\n")
        f.write("1.0,2.5\n")
        f.write("2.0,3.1\n")
        temp_file = f.name

    try:
        # Validar tamaño del archivo
        result = size_validator.validate(temp_file)
        print(f"   Archivo temporal: {'✓ Válido' if result.is_valid else '✗ Inválido'}")
        if result.metadata:
            print(f"     Tamaño: {result.metadata.get('file_size_formatted', 'unknown')}")
    finally:
        os.unlink(temp_file)

    print()


def demo_user_input_validation():
    """Demuestra validación de entradas de usuario"""
    print("=== Demo: Validación de Entradas de Usuario ===")

    # Crear validadores
    string_validator = StringInputValidator(
        max_length=50,
        allowed_pattern=StringInputValidator.ALPHANUMERIC_EXTENDED
    )
    email_validator = EmailValidator()
    password_validator = PasswordValidator(min_length=8)

    print("1. Validando entradas de texto:")

    test_strings = [
        "Usuario_123",
        "Texto normal con espacios",
        "<script>alert('xss')</script>",  # XSS
        "A" * 100                         # Muy largo
    ]

    for text in test_strings:
        result = string_validator.validate(text)
        status = '✓ Válido' if result.is_valid else '✗ Inválido'
        print(f"   '{text[:30]}...': {status}")
        if not result.is_valid:
            print(f"     Error: {result.errors[0].message}")

    print("\n2. Validando emails:")

    test_emails = [
        "usuario@dominio.com",
        "email.valido@empresa.org",
        "email-invalido",
        "test@"
    ]

    for email in test_emails:
        result = email_validator.validate(email)
        print(f"   {email}: {'✓ Válido' if result.is_valid else '✗ Inválido'}")

    print("\n3. Validando contraseñas:")

    test_passwords = [
        "MiPassword123!",  # Fuerte
        "password",        # Débil
        "12345",          # Muy débil
        "P@ssw0rd!"       # Fuerte
    ]

    for password in test_passwords:
        result = password_validator.validate(password)
        score = result.metadata.get('password_strength_score', 0)
        print(f"   [oculta]: Score {score}/100 - {'✓ Válida' if result.is_valid else '✗ Inválida'}")

    print()


def demo_api_validation():
    """Demuestra validación de APIs"""
    print("=== Demo: Validación de APIs ===")

    # Crear validadores de parámetros API
    param_validator = APIParameterValidator(
        'limit', int, required=False, default_value=10, min_value=1, max_value=100
    )

    # Validador de esquema JSON
    schema = {
        'type': 'object',
        'required': ['name', 'frequency'],
        'properties': {
            'name': {'type': 'string'},
            'frequency': {'type': 'number'},
            'description': {'type': 'string'}
        }
    }
    json_validator = JSONSchemaValidator(schema)

    print("1. Validando parámetros de API:")

    test_params = [
        ('limit', 25),      # Válido
        ('limit', 150),     # Fuera de rango
        ('limit', 'abc'),   # Tipo incorrecto
        ('limit', None)     # Usará default
    ]

    for param_name, value in test_params:
        result = param_validator.validate(value, context={'endpoint': '/api/signals'})
        print(f"   {param_name}={value}: {'✓ Válido' if result.is_valid else '✗ Inválido'}")
        if result.sanitized_value != value:
            print(f"     Valor sanitizado: {result.sanitized_value}")

    print("\n2. Validando JSON según esquema:")

    test_jsons = [
        {'name': 'Señal1', 'frequency': 1000.0, 'description': 'Señal de prueba'},  # Válido
        {'name': 'Señal2'},                                                          # Falta frequency
        {'frequency': 500.0},                                                        # Falta name
        {'name': 'Señal3', 'frequency': 'invalid'}                                  # Tipo incorrecto
    ]

    for i, json_data in enumerate(test_jsons, 1):
        result = json_validator.validate(json_data, context={'endpoint': '/api/signals'})
        print(f"   JSON {i}: {'✓ Válido' if result.is_valid else '✗ Inválido'}")
        if not result.is_valid:
            print(f"     Error: {result.errors[0].message}")

    print()


def demo_config_validation():
    """Demuestra validación de configuración"""
    print("=== Demo: Validación de Configuración ===")

    # Crear validador de archivos de configuración
    config_validator = ConfigFileValidator(required_sections=['database', 'logging'])
    db_validator = DatabaseConfigValidator()

    print("1. Validando configuración JSON:")

    # Configuración de prueba
    test_config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'database': 'senial_db',
            'username': 'user'
        },
        'logging': {
            'level': 'INFO',
            'file': '/var/log/app.log'
        }
    }

    result = config_validator.validate(test_config)
    print(f"   Configuración general: {'✓ Válida' if result.is_valid else '✗ Inválida'}")
    if result.metadata:
        print(f"     Secciones: {result.metadata['sections']}")

    print("\n2. Validando configuración de base de datos:")

    test_db_configs = [
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'username': 'user',
            'password': 'strong_password'
        },
        {
            'host': 'localhost',
            'port': 99999,  # Puerto inválido
            'database': 'test_db'
            # Falta username
        }
    ]

    for i, db_config in enumerate(test_db_configs, 1):
        result = db_validator.validate(db_config)
        print(f"   Config DB {i}: {'✓ Válida' if result.is_valid else '✗ Inválida'}")
        if not result.is_valid:
            print(f"     Error: {result.errors[0].message}")

    print()


def demo_pipeline_integration():
    """Demuestra pipelines de validación integrados"""
    print("=== Demo: Pipelines de Validación Integrados ===")

    print("1. Pipeline para validación de señales:")
    signal_pipeline = create_signal_validation_pipeline("audio")

    # Datos de señal de audio
    signal_context = {
        'signal_type': 'audio',
        'max_frequency': 20000
    }

    # Validar frecuencia de audio
    result = signal_pipeline.validate(1000.0, signal_context)
    print(f"   Frecuencia de audio (1kHz): {'✓ Válida' if result.is_valid else '✗ Inválida'}")

    print("\n2. Pipeline para validación de archivos:")
    file_pipeline = create_file_validation_pipeline("signal", max_size=1024*1024)

    # Simular archivo válido
    file_info = {
        'filename': 'audio_signal.wav',
        'size': 512 * 1024  # 512KB
    }

    result = file_pipeline.validate(file_info)
    print(f"   Archivo de señal: {'✓ Válido' if result.is_valid else '✗ Inválido'}")

    print("\n3. Pipeline para validación de API:")
    api_pipeline = create_api_validation_pipeline("public", rate_limit=50)

    # Simular request API
    api_request = {
        'client_ip': '192.168.1.100',
        'endpoint': '/api/signals',
        'data': {'name': 'test', 'frequency': 1000}
    }

    result = api_pipeline.validate(api_request, context={'endpoint': '/api/signals'})
    print(f"   Request API público: {'✓ Válido' if result.is_valid else '✗ Inválido'}")

    print()


if __name__ == "__main__":
    print("SSA-24 Input Validation Framework - Demo Fase 2")
    print("=" * 60)
    print("Demostrando validadores especializados y pipelines completos")
    print()

    try:
        demo_signal_validation()
        demo_file_validation()
        demo_user_input_validation()
        demo_api_validation()
        demo_config_validation()
        demo_pipeline_integration()

        print("✅ Demo Fase 2 completado exitosamente")
        print("El framework de validación SSA-24 está completamente funcional!")
        print("\nCaracterísticas implementadas:")
        print("• Validación de señales con análisis de calidad")
        print("• Validación de archivos con escaneo de seguridad")
        print("• Validación de inputs de usuario con protección XSS")
        print("• Validación de APIs con rate limiting y esquemas JSON")
        print("• Validación de configuración con validadores especializados")
        print("• Pipelines integrados para casos de uso específicos")

    except Exception as e:
        print(f"❌ Error en demo: {str(e)}")
        import traceback
        traceback.print_exc()