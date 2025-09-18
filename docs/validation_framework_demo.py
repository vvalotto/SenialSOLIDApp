#!/usr/bin/env python3
"""
Demo de uso del SSA-24 Input Validation Framework

Este archivo demuestra cómo usar el framework de validación de entradas
implementado en la Fase 1.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aplicacion.validation import (
    # Core framework
    ValidationPipeline,
    PipelineMode,
    RangeValidator,
    LengthValidator,
    SanitizationEngine,
    SanitizationLevel,

    # Decorators
    validate_input,
    validate_range,
    validate_length,
    auto_sanitize,
    sanitize_input,

    # Exceptions
    ValidationError,
    SecurityValidationError
)


def demo_basic_validation():
    """Demuestra validación básica usando validators individuales"""
    print("=== Demo: Validación Básica ===")

    # Crear validadores
    range_validator = RangeValidator("frequency_range", min_value=0.1, max_value=50000.0)
    length_validator = LengthValidator("description_length", min_length=1, max_length=100)

    # Probar validación exitosa
    print("1. Validando frecuencia válida (1000 Hz):")
    result = range_validator.validate(1000.0)
    print(f"   Válido: {result.is_valid}")

    # Probar validación fallida
    print("2. Validando frecuencia inválida (100000 Hz):")
    result = range_validator.validate(100000.0)
    print(f"   Válido: {result.is_valid}")
    if result.errors:
        print(f"   Error: {result.errors[0].message}")

    print()


def demo_pipeline_validation():
    """Demuestra validación usando pipeline"""
    print("=== Demo: Pipeline de Validación ===")

    # Crear pipeline
    pipeline = ValidationPipeline("signal_validation", mode=PipelineMode.COLLECT_ALL)
    pipeline.add_validator(RangeValidator("frequency", min_value=0.1, max_value=50000.0))
    pipeline.add_validator(LengthValidator("identifier", min_length=1, max_length=50))

    # Datos de prueba
    test_data = {
        'frequency': 1000.0,
        'identifier': 'SIG_001'
    }

    print("1. Validando datos de señal:")
    for key, value in test_data.items():
        result = pipeline.validate(value, context={'field': key})
        print(f"   {key}: {value} -> Válido: {result.is_valid}")

    print()


def demo_sanitization():
    """Demuestra sanitización de datos"""
    print("=== Demo: Sanitización de Datos ===")

    # Crear motor de sanitización
    sanitizer = SanitizationEngine(SanitizationLevel.STRICT)

    # Datos de prueba con contenido malicioso
    test_inputs = [
        "<script>alert('XSS')</script>Texto normal",
        "SELECT * FROM users; DROP TABLE users;",
        "../../etc/passwd",
        "Texto normal sin problemas"
    ]

    print("Sanitizando entradas maliciosas:")
    for i, input_data in enumerate(test_inputs, 1):
        result = sanitizer.sanitize(input_data)
        print(f"   {i}. Original: {input_data[:30]}...")
        print(f"      Sanitizado: {result.sanitized_value[:30]}...")
        print(f"      Modificado: {result.was_modified}")
        if result.security_issues:
            print(f"      Problemas: {result.security_issues}")
        print()


@validate_range(min_value=0, max_value=100)
@validate_length(min_length=1, max_length=50)
def demo_validation_decorators(frequency: float, description: str):
    """Demuestra uso de decoradores de validación"""
    return f"Procesando señal {description} a {frequency} Hz"


@auto_sanitize()
def demo_sanitization_decorators(user_input: str, html_content: str):
    """Demuestra uso de decoradores de sanitización"""
    return f"Entrada: {user_input}, HTML: {html_content}"


def demo_decorators():
    """Demuestra uso de decoradores"""
    print("=== Demo: Decoradores ===")

    # Validación con decoradores
    print("1. Decoradores de validación:")
    try:
        result = demo_validation_decorators(50.0, "Señal de prueba")
        print(f"   Éxito: {result}")
    except ValidationError as e:
        print(f"   Error de validación: {e.user_message}")

    try:
        result = demo_validation_decorators(150.0, "")  # Fuera de rango y vacío
        print(f"   Éxito: {result}")
    except ValidationError as e:
        print(f"   Error de validación: {e.user_message}")

    # Sanitización con decoradores
    print("\n2. Decoradores de sanitización:")
    result = demo_sanitization_decorators(
        "Entrada normal",
        "<script>alert('hack')</script>Contenido HTML"
    )
    print(f"   Resultado: {result}")

    print()


def demo_security_features():
    """Demuestra características de seguridad"""
    print("=== Demo: Características de Seguridad ===")

    sanitizer = SanitizationEngine(SanitizationLevel.PARANOID)

    # Ataques comunes
    attack_vectors = [
        "'; DROP TABLE users; --",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "../../../etc/passwd",
        "$(rm -rf /)"
    ]

    print("Detectando vectores de ataque:")
    for attack in attack_vectors:
        try:
            result = sanitizer.sanitize(attack, strict_mode=True)
            print(f"   Sanitizado: {attack[:20]}... -> {result.sanitized_value[:20]}...")
            if result.security_issues:
                print(f"   Amenazas detectadas: {result.security_issues}")
        except SecurityValidationError as e:
            print(f"   RECHAZADO: {attack[:20]}... -> {e.user_message}")

    print()


if __name__ == "__main__":
    print("SSA-24 Input Validation Framework - Demo")
    print("=" * 50)
    print()

    try:
        demo_basic_validation()
        demo_pipeline_validation()
        demo_sanitization()
        demo_decorators()
        demo_security_features()

        print("✅ Demo completado exitosamente")
        print("El framework de validación SSA-24 Fase 1 está funcionando correctamente!")

    except Exception as e:
        print(f"❌ Error en demo: {str(e)}")
        import traceback
        traceback.print_exc()