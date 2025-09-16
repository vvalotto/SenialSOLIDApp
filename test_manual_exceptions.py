#!/usr/bin/env python3
"""
Manual Exception Testing Script
SSA-23: Exception Handling Refactoring

Interactive script to manually test exception implementations
"""

import sys
import os
import tempfile
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / '04_dominio'))

def setup_imports():
    """Setup all necessary imports"""
    try:
        from exceptions import (
            SenialSOLIDException,
            ValidationException, ProcessingException, AcquisitionException, RepositoryException,
            ConfigurationException, DataAccessException, NetworkException,
            WebException, ConsoleException
        )
        from exceptions.recovery_strategies import (
            RetryStrategy, FileIORecoveryStrategy, ProcessingFallbackStrategy
        )
        from exceptions.exception_handler import ExceptionHandler, handle_with_recovery

        return {
            'SenialSOLIDException': SenialSOLIDException,
            'ValidationException': ValidationException,
            'ProcessingException': ProcessingException,
            'AcquisitionException': AcquisitionException,
            'RepositoryException': RepositoryException,
            'ConfigurationException': ConfigurationException,
            'DataAccessException': DataAccessException,
            'NetworkException': NetworkException,
            'WebException': WebException,
            'ConsoleException': ConsoleException,
            'RetryStrategy': RetryStrategy,
            'FileIORecoveryStrategy': FileIORecoveryStrategy,
            'ProcessingFallbackStrategy': ProcessingFallbackStrategy,
            'ExceptionHandler': ExceptionHandler,
            'handle_with_recovery': handle_with_recovery
        }
    except ImportError as e:
        print(f"❌ Error importando excepciones: {e}")
        print("Asegúrate de que el módulo exceptions esté disponible.")
        return None

def print_separator(title=""):
    """Print a visual separator"""
    print("\n" + "="*60)
    if title:
        print(f"🧪 {title}")
        print("="*60)

def test_base_exception(modules):
    """Test base exception functionality"""
    print_separator("Test Base Exception")

    print("Creando SenialSOLIDException básica...")
    try:
        exc = modules['SenialSOLIDException'](
            message="Test base exception",
            user_message="Mensaje amigable para usuario",
            context={"test_key": "test_value", "operation": "manual_test"},
            recovery_suggestion="Intente nuevamente"
        )

        print(f"✅ Excepción creada: {exc}")
        print(f"📝 Mensaje: {exc.message}")
        print(f"👤 Mensaje usuario: {exc.user_message}")
        print(f"🔧 Sugerencia: {exc.recovery_suggestion}")
        print(f"🏷️ Código error: {exc.error_code}")
        print(f"🕐 Timestamp: {exc.timestamp}")
        print(f"📊 Contexto: {exc.context}")

        print("\n📋 Serialización a diccionario:")
        print(exc.to_dict())

    except Exception as e:
        print(f"❌ Error creando base exception: {e}")
        return False

    return True

def test_domain_exceptions(modules):
    """Test domain-specific exceptions"""
    print_separator("Test Domain Exceptions")

    # Test ValidationException
    print("1️⃣ Probando ValidationException...")
    try:
        val_exc = modules['ValidationException'](
            field="signal_id",
            value="abc123",
            rule="debe ser numérico",
            context={"signal_length": 1000, "operation": "validation_test"}
        )
        print(f"✅ ValidationException: {val_exc.user_message}")
        print(f"   Campo: {val_exc.context['field']}")
        print(f"   Valor inválido: {val_exc.context['invalid_value']}")
        print(f"   Regla: {val_exc.context['validation_rule']}")
    except Exception as e:
        print(f"❌ Error ValidationException: {e}")

    # Test ProcessingException
    print("\n2️⃣ Probando ProcessingException...")
    try:
        proc_exc = modules['ProcessingException'](
            operation="complex_filter",
            signal_id="signal_test_123",
            processing_stage="filtering"
        )
        print(f"✅ ProcessingException: {proc_exc.user_message}")
        print(f"   Operación: {proc_exc.context['operation']}")
        print(f"   Signal ID: {proc_exc.context['signal_id']}")
        print(f"   Etapa: {proc_exc.context['processing_stage']}")
    except Exception as e:
        print(f"❌ Error ProcessingException: {e}")

    # Test AcquisitionException
    print("\n3️⃣ Probando AcquisitionException...")
    try:
        acq_exc = modules['AcquisitionException'](
            source="test_signal.dat",
            source_type="file",
            acquisition_method="file_read"
        )
        print(f"✅ AcquisitionException: {acq_exc.user_message}")
        print(f"   Fuente: {acq_exc.context['source']}")
        print(f"   Tipo fuente: {acq_exc.context['source_type']}")
        print(f"   Método: {acq_exc.context['acquisition_method']}")
    except Exception as e:
        print(f"❌ Error AcquisitionException: {e}")

def test_infrastructure_exceptions(modules):
    """Test infrastructure-specific exceptions"""
    print_separator("Test Infrastructure Exceptions")

    # Test DataAccessException
    print("1️⃣ Probando DataAccessException...")
    try:
        da_exc = modules['DataAccessException'](
            file_path="/tmp/test_signal.dat",
            operation="read",
            retry_count=1,
            max_retries=3
        )
        print(f"✅ DataAccessException: {da_exc.user_message}")
        print(f"   Archivo: {da_exc.context['file_path']}")
        print(f"   Operación: {da_exc.context['operation']}")
        print(f"   Reintentos: {da_exc.context['retry_count']}/{da_exc.context['max_retries']}")
        print(f"   Puede reintentar: {da_exc.context['can_retry']}")
    except Exception as e:
        print(f"❌ Error DataAccessException: {e}")

    # Test NetworkException
    print("\n2️⃣ Probando NetworkException...")
    try:
        net_exc = modules['NetworkException'](
            endpoint="http://api.example.com/signals",
            operation="GET",
            status_code=500,
            timeout_seconds=30.0
        )
        print(f"✅ NetworkException: {net_exc.user_message}")
        print(f"   Endpoint: {net_exc.context['endpoint']}")
        print(f"   Status: {net_exc.context['status_code']}")
        print(f"   Timeout: {net_exc.context['timeout_seconds']}s")
    except Exception as e:
        print(f"❌ Error NetworkException: {e}")

def test_presentation_exceptions(modules):
    """Test presentation-specific exceptions"""
    print_separator("Test Presentation Exceptions")

    # Test WebException
    print("1️⃣ Probando WebException...")
    try:
        web_exc = modules['WebException'](
            endpoint="/api/signals",
            http_status=400,
            request_method="POST",
            context={"user_id": "test_user", "form_errors": ["invalid_signal_id"]}
        )
        print(f"✅ WebException: {web_exc.user_message}")
        print(f"   Endpoint: {web_exc.context['endpoint']}")
        print(f"   Status HTTP: {web_exc.context['http_status']}")
        print(f"   Método: {web_exc.context['request_method']}")
    except Exception as e:
        print(f"❌ Error WebException: {e}")

    # Test ConsoleException
    print("\n2️⃣ Probando ConsoleException...")
    try:
        console_exc = modules['ConsoleException'](
            command="process_signal",
            command_args=["--input", "test.dat"],
            user_input="invalid_command"
        )
        print(f"✅ ConsoleException: {console_exc.user_message}")
        print(f"   Comando: {console_exc.context['command']}")
        print(f"   Argumentos: {console_exc.context['command_args']}")
        print(f"   Input usuario: {console_exc.context['user_input']}")
    except Exception as e:
        print(f"❌ Error ConsoleException: {e}")

def test_recovery_strategies(modules):
    """Test recovery strategies"""
    print_separator("Test Recovery Strategies")

    # Test RetryStrategy
    print("1️⃣ Probando RetryStrategy...")
    try:
        retry_strategy = modules['RetryStrategy'](max_retries=3, base_delay=0.1, max_delay=1.0)

        # Test with retryable exception
        retryable_exc = modules['DataAccessException']("/tmp/test.dat", "read", retry_count=1)
        can_recover = retry_strategy.can_recover(retryable_exc)
        print(f"✅ RetryStrategy creada - Puede recuperar DataAccessException: {can_recover}")

        # Test with non-retryable exception
        validation_exc = modules['ValidationException']("field", "value", "rule")
        can_recover_validation = retry_strategy.can_recover(validation_exc)
        print(f"   Puede recuperar ValidationException: {can_recover_validation}")

    except Exception as e:
        print(f"❌ Error RetryStrategy: {e}")

    # Test FileIORecoveryStrategy
    print("\n2️⃣ Probando FileIORecoveryStrategy...")
    try:
        file_strategy = modules['FileIORecoveryStrategy'](
            fallback_paths=["/backup/path1", "/backup/path2"],
            create_missing_dirs=True
        )

        file_exc = modules['DataAccessException']("/original/path.dat", "read", retry_count=0)
        can_recover = file_strategy.can_recover(file_exc)
        print(f"✅ FileIORecoveryStrategy creada - Puede recuperar: {can_recover}")
        print(f"   Paths de respaldo: {file_strategy.fallback_paths}")
        print(f"   Crear directorios: {file_strategy.create_missing_dirs}")

    except Exception as e:
        print(f"❌ Error FileIORecoveryStrategy: {e}")

    # Test ProcessingFallbackStrategy
    print("\n3️⃣ Probando ProcessingFallbackStrategy...")
    try:
        fallback_ops = {"complex_filter": "simple_filter", "advanced_transform": "basic_transform"}
        processing_strategy = modules['ProcessingFallbackStrategy'](fallback_operations=fallback_ops)

        # Test with available fallback
        proc_exc = modules['ProcessingException']("complex_filter", "signal_123")
        can_recover = processing_strategy.can_recover(proc_exc)
        print(f"✅ ProcessingFallbackStrategy creada - Puede recuperar: {can_recover}")
        print(f"   Operaciones de respaldo: {fallback_ops}")

        # Test with no fallback available
        proc_exc_no_fallback = modules['ProcessingException']("unknown_operation", "signal_123")
        can_recover_no_fallback = processing_strategy.can_recover(proc_exc_no_fallback)
        print(f"   Sin respaldo para 'unknown_operation': {can_recover_no_fallback}")

    except Exception as e:
        print(f"❌ Error ProcessingFallbackStrategy: {e}")

def test_exception_handler(modules):
    """Test exception handler and handle_with_recovery"""
    print_separator("Test Exception Handler")

    print("1️⃣ Probando ExceptionHandler...")
    try:
        handler = modules['ExceptionHandler']()
        print(f"✅ ExceptionHandler creado con {len(handler.recovery_strategies)} estrategias")

        strategy_names = [type(s).__name__ for s in handler.recovery_strategies]
        print(f"   Estrategias disponibles: {strategy_names}")

    except Exception as e:
        print(f"❌ Error ExceptionHandler: {e}")

    print("\n2️⃣ Probando handle_with_recovery con operación exitosa...")
    try:
        def successful_operation():
            time.sleep(0.1)  # Simular trabajo
            return "✅ Operación completada exitosamente"

        result = modules['handle_with_recovery'](
            operation=successful_operation,
            operation_name="test_successful_operation",
            context={"test": "success_scenario"},
            max_attempts=1
        )
        print(f"✅ Resultado: {result}")

    except Exception as e:
        print(f"❌ Error en operación exitosa: {e}")

    print("\n3️⃣ Probando handle_with_recovery con operación que falla...")
    try:
        def failing_operation():
            raise ValueError("Error simulado para testing")

        result = modules['handle_with_recovery'](
            operation=failing_operation,
            operation_name="test_failing_operation",
            context={"test": "failure_scenario"},
            max_attempts=1
        )
        print(f"❓ Resultado inesperado: {result}")

    except Exception as e:
        print(f"✅ Excepción manejada correctamente: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"   Mensaje usuario: {e.user_message}")
        if hasattr(e, 'context'):
            print(f"   Contexto: {e.context}")

def test_file_operations(modules):
    """Test real file operations with exception handling"""
    print_separator("Test File Operations")

    print("1️⃣ Probando operación de archivo exitosa...")
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.test') as temp_file:
            temp_path = temp_file.name
            temp_file.write("Test content for exception handling")

        def read_file_operation():
            with open(temp_path, 'r') as f:
                content = f.read()
            os.unlink(temp_path)  # Clean up
            return f"✅ Archivo leído: {len(content)} caracteres"

        result = modules['handle_with_recovery'](
            operation=read_file_operation,
            operation_name="read_test_file",
            context={"file_path": temp_path},
            max_attempts=2
        )
        print(f"✅ Resultado: {result}")

    except Exception as e:
        print(f"❌ Error en operación de archivo: {e}")

    print("\n2️⃣ Probando operación de archivo que falla...")
    try:
        def read_nonexistent_file():
            with open("/path/that/does/not/exist.txt", 'r') as f:
                return f.read()

        result = modules['handle_with_recovery'](
            operation=read_nonexistent_file,
            operation_name="read_nonexistent_file",
            context={"expected_file": "/path/that/does/not/exist.txt"},
            max_attempts=2
        )
        print(f"❓ Resultado inesperado: {result}")

    except Exception as e:
        print(f"✅ Excepción de archivo manejada: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"   Mensaje usuario: {e.user_message}")
        if hasattr(e, 'recovery_suggestion'):
            print(f"   Sugerencia: {e.recovery_suggestion}")

def main():
    """Main testing function"""
    print("🧪 Manual Exception Testing - SSA-23")
    print("="*60)
    print("Este script prueba manualmente todas las implementaciones de excepciones")
    print("Presiona Enter para continuar con cada test, o 'q' para salir...")

    # Setup imports
    modules = setup_imports()
    if not modules:
        return

    # Test sequence
    test_functions = [
        ("Base Exception", test_base_exception),
        ("Domain Exceptions", test_domain_exceptions),
        ("Infrastructure Exceptions", test_infrastructure_exceptions),
        ("Presentation Exceptions", test_presentation_exceptions),
        ("Recovery Strategies", test_recovery_strategies),
        ("Exception Handler", test_exception_handler),
        ("File Operations", test_file_operations),
    ]

    for test_name, test_func in test_functions:
        user_input = input(f"\n⏳ Presiona Enter para probar '{test_name}' (o 'q' para salir): ")
        if user_input.lower().strip() == 'q':
            print("👋 Saliendo del testing manual...")
            break

        try:
            test_func(modules)
        except Exception as e:
            print(f"❌ Error ejecutando test '{test_name}': {e}")

        print("\n" + "-"*40)

    print_separator("Testing Completado")
    print("✅ Testing manual completado!")
    print("📊 Has probado toda la jerarquía de excepciones SSA-23")
    print("🔧 Para más detalles, revisa: docs/SSA-23-EXCEPTION-HANDLING-GUIDELINES.md")

if __name__ == "__main__":
    main()