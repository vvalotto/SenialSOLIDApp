#!/usr/bin/env python3
"""
Automated Exception Demo Script
SSA-23: Exception Handling Refactoring

Demonstrates all exception implementations automatically
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
    print("\n" + "="*70)
    if title:
        print(f"🧪 {title}")
        print("="*70)

def demo_base_exception(modules):
    """Demo base exception functionality"""
    print_separator("DEMO: Base Exception")

    print("Creando SenialSOLIDException básica...")
    try:
        exc = modules['SenialSOLIDException'](
            message="Test base exception",
            user_message="Mensaje amigable para usuario",
            context={"test_key": "test_value", "operation": "manual_test"},
            recovery_suggestion="Intente nuevamente"
        )

        print(f"✅ Excepción creada exitosamente!")
        print(f"📝 Mensaje técnico: {exc.message}")
        print(f"👤 Mensaje usuario: {exc.user_message}")
        print(f"🔧 Sugerencia: {exc.recovery_suggestion}")
        print(f"🏷️ Código error: {exc.error_code}")
        print(f"🕐 Timestamp: {exc.timestamp}")
        print(f"📊 Contexto: {exc.context}")

        print(f"\n📋 String representation: {exc}")
        print(f"🔧 Repr: {repr(exc)}")

        return True

    except Exception as e:
        print(f"❌ Error creando base exception: {e}")
        return False

def demo_domain_exceptions(modules):
    """Demo domain-specific exceptions"""
    print_separator("DEMO: Domain Exceptions")

    print("🔍 1. ValidationException - Error de validación de entrada")
    try:
        val_exc = modules['ValidationException'](
            field="signal_id",
            value="abc123",
            rule="debe ser numérico",
            context={"signal_length": 1000, "operation": "validation_test"}
        )
        print(f"✅ Creada: {val_exc.user_message}")
        print(f"   🏷️ Error Code: {val_exc.error_code}")
        print(f"   📊 Context - Campo: {val_exc.context['field']}")
        print(f"   📊 Context - Valor inválido: {val_exc.context['invalid_value']}")
        print(f"   📊 Context - Regla: {val_exc.context['validation_rule']}")
        print(f"   💡 Sugerencia: {val_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error ValidationException: {e}")

    print("\n⚙️ 2. ProcessingException - Error en procesamiento de señal")
    try:
        proc_exc = modules['ProcessingException'](
            operation="complex_filter",
            signal_id="signal_test_123",
            processing_stage="filtering",
            context={"cpu_usage": 85.2, "memory_mb": 1024}
        )
        print(f"✅ Creada: {proc_exc.user_message}")
        print(f"   🏷️ Error Code: {proc_exc.error_code}")
        print(f"   📊 Context - Operación: {proc_exc.context['operation']}")
        print(f"   📊 Context - Signal ID: {proc_exc.context['signal_id']}")
        print(f"   📊 Context - Etapa: {proc_exc.context['processing_stage']}")
        print(f"   💡 Sugerencia: {proc_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error ProcessingException: {e}")

    print("\n📥 3. AcquisitionException - Error en adquisición de datos")
    try:
        acq_exc = modules['AcquisitionException'](
            source="test_signal.dat",
            source_type="file",
            acquisition_method="file_read"
        )
        print(f"✅ Creada: {acq_exc.user_message}")
        print(f"   🏷️ Error Code: {acq_exc.error_code}")
        print(f"   📊 Context - Fuente: {acq_exc.context['source']}")
        print(f"   📊 Context - Tipo: {acq_exc.context['source_type']}")
        print(f"   📊 Context - Método: {acq_exc.context['acquisition_method']}")
        print(f"   💡 Sugerencia: {acq_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error AcquisitionException: {e}")

    print("\n💾 4. RepositoryException - Error en persistencia")
    try:
        repo_exc = modules['RepositoryException'](
            operation="save",
            entity_type="signal",
            entity_id="signal_123",
            context={"file_size_mb": 45.6, "available_space_mb": 12.3}
        )
        print(f"✅ Creada: {repo_exc.user_message}")
        print(f"   🏷️ Error Code: {repo_exc.error_code}")
        print(f"   📊 Context - Operación: {repo_exc.context['operation']}")
        print(f"   📊 Context - Tipo entidad: {repo_exc.context['entity_type']}")
        print(f"   📊 Context - ID entidad: {repo_exc.context['entity_id']}")
        print(f"   💡 Sugerencia: {repo_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error RepositoryException: {e}")

def demo_infrastructure_exceptions(modules):
    """Demo infrastructure-specific exceptions"""
    print_separator("DEMO: Infrastructure Exceptions")

    print("💾 1. DataAccessException - Error de acceso a archivos")
    try:
        da_exc = modules['DataAccessException'](
            file_path="/tmp/test_signal.dat",
            operation="read",
            retry_count=1,
            max_retries=3,
            context={"file_exists": False, "permissions": "644"}
        )
        print(f"✅ Creada: {da_exc.user_message}")
        print(f"   🏷️ Error Code: {da_exc.error_code}")
        print(f"   📊 Context - Archivo: {da_exc.context['file_path']}")
        print(f"   📊 Context - Operación: {da_exc.context['operation']}")
        print(f"   📊 Context - Reintentos: {da_exc.context['retry_count']}/{da_exc.context['max_retries']}")
        print(f"   📊 Context - Puede reintentar: {da_exc.context['can_retry']}")
        print(f"   💡 Sugerencia: {da_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error DataAccessException: {e}")

    print("\n🌐 2. NetworkException - Error de conectividad")
    try:
        net_exc = modules['NetworkException'](
            endpoint="http://api.example.com/signals",
            operation="GET",
            status_code=500,
            timeout_seconds=30.0,
            context={"response_time_ms": 5000, "retry_after": 60}
        )
        print(f"✅ Creada: {net_exc.user_message}")
        print(f"   🏷️ Error Code: {net_exc.error_code}")
        print(f"   📊 Context - Endpoint: {net_exc.context['endpoint']}")
        print(f"   📊 Context - Status: {net_exc.context['status_code']}")
        print(f"   📊 Context - Timeout: {net_exc.context['timeout_seconds']}s")
        print(f"   💡 Sugerencia: {net_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error NetworkException: {e}")

    print("\n⚙️ 3. ConfigurationException - Error de configuración")
    try:
        config_exc = modules['ConfigurationException'](
            config_key="database_url",
            config_file="config.yaml",
            context={"config_exists": True, "key_missing": True}
        )
        print(f"✅ Creada: {config_exc.user_message}")
        print(f"   🏷️ Error Code: {config_exc.error_code}")
        print(f"   📊 Context - Clave: {config_exc.context['config_key']}")
        print(f"   📊 Context - Archivo: {config_exc.context['config_file']}")
        print(f"   💡 Sugerencia: {config_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error ConfigurationException: {e}")

def demo_presentation_exceptions(modules):
    """Demo presentation-specific exceptions"""
    print_separator("DEMO: Presentation Exceptions")

    print("🌐 1. WebException - Error en interfaz web")
    try:
        web_exc = modules['WebException'](
            endpoint="/api/signals",
            http_status=400,
            request_method="POST",
            context={
                "user_id": "test_user",
                "form_errors": ["invalid_signal_id"],
                "session_id": "abc123"
            }
        )
        print(f"✅ Creada: {web_exc.user_message}")
        print(f"   🏷️ Error Code: {web_exc.error_code}")
        print(f"   📊 Context - Endpoint: {web_exc.context['endpoint']}")
        print(f"   📊 Context - Status HTTP: {web_exc.context['http_status']}")
        print(f"   📊 Context - Método: {web_exc.context['request_method']}")
        print(f"   💡 Sugerencia: {web_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error WebException: {e}")

    print("\n💻 2. ConsoleException - Error en interfaz de consola")
    try:
        console_exc = modules['ConsoleException'](
            command="process_signal",
            command_args=["--input", "test.dat", "--filter", "complex"],
            user_input="invalid_command_syntax",
            context={"terminal": "bash", "working_dir": "/tmp"}
        )
        print(f"✅ Creada: {console_exc.user_message}")
        print(f"   🏷️ Error Code: {console_exc.error_code}")
        print(f"   📊 Context - Comando: {console_exc.context['command']}")
        print(f"   📊 Context - Argumentos: {console_exc.context['command_args']}")
        print(f"   📊 Context - Input usuario: {console_exc.context['user_input']}")
        print(f"   💡 Sugerencia: {console_exc.recovery_suggestion}")
    except Exception as e:
        print(f"❌ Error ConsoleException: {e}")

def demo_recovery_strategies(modules):
    """Demo recovery strategies"""
    print_separator("DEMO: Recovery Strategies")

    print("🔄 1. RetryStrategy - Reintento con backoff exponencial")
    try:
        retry_strategy = modules['RetryStrategy'](max_retries=3, base_delay=0.1, max_delay=2.0)

        # Test with retryable exception
        retryable_exc = modules['DataAccessException']("/tmp/test.dat", "read", retry_count=1)
        can_recover = retry_strategy.can_recover(retryable_exc)
        print(f"✅ RetryStrategy creada exitosamente")
        print(f"   📊 Max reintentos: {retry_strategy.max_retries}")
        print(f"   📊 Delay base: {retry_strategy.base_delay}s")
        print(f"   📊 Max delay: {retry_strategy.max_delay}s")
        print(f"   🔍 Puede recuperar DataAccessException (retry=1): {can_recover}")

        # Test with maxed out retries
        maxed_exc = modules['DataAccessException']("/tmp/test.dat", "read", retry_count=3)
        can_recover_maxed = retry_strategy.can_recover(maxed_exc)
        print(f"   🔍 Puede recuperar DataAccessException (retry=3): {can_recover_maxed}")

        # Test with non-retryable
        validation_exc = modules['ValidationException']("field", "value", "rule")
        can_recover_validation = retry_strategy.can_recover(validation_exc)
        print(f"   🔍 Puede recuperar ValidationException: {can_recover_validation}")

    except Exception as e:
        print(f"❌ Error RetryStrategy: {e}")

    print("\n💾 2. FileIORecoveryStrategy - Recuperación de archivos")
    try:
        file_strategy = modules['FileIORecoveryStrategy'](
            fallback_paths=["/backup/signals", "/tmp/signals", "/home/user/backup"],
            create_missing_dirs=True
        )

        file_exc = modules['DataAccessException']("/original/path.dat", "read", retry_count=0)
        can_recover = file_strategy.can_recover(file_exc)
        print(f"✅ FileIORecoveryStrategy creada exitosamente")
        print(f"   📊 Paths de respaldo: {file_strategy.fallback_paths}")
        print(f"   📊 Crear directorios: {file_strategy.create_missing_dirs}")
        print(f"   🔍 Puede recuperar error de archivo: {can_recover}")

        # Test exhausted retries
        exhausted_exc = modules['DataAccessException']("/path.dat", "read", retry_count=10)
        can_recover_exhausted = file_strategy.can_recover(exhausted_exc)
        print(f"   🔍 Puede recuperar con reintentos agotados: {can_recover_exhausted}")

    except Exception as e:
        print(f"❌ Error FileIORecoveryStrategy: {e}")

    print("\n⚙️ 3. ProcessingFallbackStrategy - Degradación de procesamiento")
    try:
        fallback_ops = {
            "complex_filter": "simple_filter",
            "advanced_transform": "basic_transform",
            "ml_processing": "statistical_processing",
            "neural_network": "linear_regression"
        }
        processing_strategy = modules['ProcessingFallbackStrategy'](fallback_operations=fallback_ops)

        # Test with available fallback
        proc_exc = modules['ProcessingException']("complex_filter", "signal_123")
        can_recover = processing_strategy.can_recover(proc_exc)
        print(f"✅ ProcessingFallbackStrategy creada exitosamente")
        print(f"   📊 Operaciones de respaldo: {len(fallback_ops)} disponibles")
        for original, fallback in fallback_ops.items():
            print(f"      {original} → {fallback}")
        print(f"   🔍 Puede recuperar 'complex_filter': {can_recover}")

        # Test with no fallback available
        proc_exc_no_fallback = modules['ProcessingException']("unknown_operation", "signal_123")
        can_recover_no_fallback = processing_strategy.can_recover(proc_exc_no_fallback)
        print(f"   🔍 Puede recuperar 'unknown_operation': {can_recover_no_fallback}")

        # Test already fallback
        proc_exc_fallback = modules['ProcessingException']("simple_filter", "signal_123")
        proc_exc_fallback.context["is_fallback"] = True
        can_recover_already_fallback = processing_strategy.can_recover(proc_exc_fallback)
        print(f"   🔍 Puede recuperar operación ya de respaldo: {can_recover_already_fallback}")

    except Exception as e:
        print(f"❌ Error ProcessingFallbackStrategy: {e}")

def demo_exception_handler(modules):
    """Demo exception handler and handle_with_recovery"""
    print_separator("DEMO: Exception Handler & Recovery")

    print("🎯 1. Inicializando ExceptionHandler")
    try:
        handler = modules['ExceptionHandler']()
        strategy_names = [type(s).__name__ for s in handler.recovery_strategies]
        print(f"✅ ExceptionHandler creado exitosamente")
        print(f"   📊 Estrategias cargadas: {len(handler.recovery_strategies)}")
        for i, name in enumerate(strategy_names, 1):
            print(f"      {i}. {name}")

    except Exception as e:
        print(f"❌ Error creando ExceptionHandler: {e}")

    print("\n✅ 2. Operación exitosa con handle_with_recovery")
    try:
        def successful_operation():
            time.sleep(0.05)  # Simular trabajo
            return "🎉 Operación completada exitosamente"

        start_time = time.time()
        result = modules['handle_with_recovery'](
            operation=successful_operation,
            operation_name="demo_successful_operation",
            context={"demo": "success_scenario", "user": "demo_user"},
            max_attempts=1
        )
        duration = (time.time() - start_time) * 1000
        print(f"✅ Operación completada en {duration:.2f}ms")
        print(f"   📊 Resultado: {result}")

    except Exception as e:
        print(f"❌ Error en operación exitosa: {e}")

    print("\n❌ 3. Operación que falla - Manejo automático")
    try:
        def failing_operation():
            raise IOError("Error simulado de I/O - archivo no accesible")

        start_time = time.time()
        result = modules['handle_with_recovery'](
            operation=failing_operation,
            operation_name="demo_failing_operation",
            context={"demo": "failure_scenario", "expected_error": True},
            max_attempts=2
        )
        duration = (time.time() - start_time) * 1000
        print(f"❓ Resultado inesperado: {result}")

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        print(f"✅ Excepción manejada correctamente en {duration:.2f}ms")
        print(f"   🏷️ Tipo: {type(e).__name__}")
        print(f"   📝 Mensaje técnico: {e}")
        if hasattr(e, 'user_message'):
            print(f"   👤 Mensaje usuario: {e.user_message}")
        if hasattr(e, 'recovery_suggestion'):
            print(f"   💡 Sugerencia: {e.recovery_suggestion}")
        if hasattr(e, 'context'):
            print(f"   📊 Contexto: {e.context}")

    print("\n🔄 4. Operación con reintento - Simula recuperación")
    try:
        attempt_count = 0
        def eventually_successful_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError(f"Error de conexión - intento {attempt_count}")
            return f"✅ Éxito en intento {attempt_count}"

        start_time = time.time()
        result = modules['handle_with_recovery'](
            operation=eventually_successful_operation,
            operation_name="demo_retry_operation",
            context={"demo": "retry_scenario", "max_expected_attempts": 3},
            max_attempts=4
        )
        duration = (time.time() - start_time) * 1000
        print(f"✅ Recuperación exitosa en {duration:.2f}ms")
        print(f"   📊 Resultado: {result}")
        print(f"   🔄 Intentos realizados: {attempt_count}")

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        print(f"❌ Falló después de reintentos en {duration:.2f}ms")
        print(f"   🏷️ Tipo: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"   👤 Mensaje: {e.user_message}")

def demo_real_scenarios(modules):
    """Demo real-world scenarios"""
    print_separator("DEMO: Escenarios Reales")

    print("📄 1. Escenario: Lectura de archivo de configuración")
    try:
        def read_config_file():
            # Simular lectura de archivo que puede fallar
            config_file = "/nonexistent/config.yaml"
            with open(config_file, 'r') as f:
                return f.read()

        result = modules['handle_with_recovery'](
            operation=read_config_file,
            operation_name="read_configuration",
            context={
                "config_file": "/nonexistent/config.yaml",
                "fallback_config": "/etc/default/config.yaml",
                "operation_type": "system_initialization"
            },
            max_attempts=2
        )
        print(f"❓ Resultado inesperado: {result}")

    except Exception as e:
        print(f"✅ Error de configuración manejado correctamente")
        print(f"   🏷️ Tipo: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"   👤 Mensaje: {e.user_message}")
        if hasattr(e, 'recovery_suggestion'):
            print(f"   💡 Sugerencia: {e.recovery_suggestion}")

    print("\n📊 2. Escenario: Procesamiento de señal compleja")
    try:
        def process_complex_signal():
            # Simular procesamiento que requiere recursos
            signal_data = list(range(10000))  # Señal grande
            if len(signal_data) > 5000:
                raise MemoryError("Memoria insuficiente para procesamiento complejo")
            return f"Procesada señal de {len(signal_data)} puntos"

        result = modules['handle_with_recovery'](
            operation=process_complex_signal,
            operation_name="process_large_signal",
            context={
                "signal_size": 10000,
                "algorithm": "complex_filter",
                "memory_limit_mb": 100,
                "cpu_cores": 4
            },
            max_attempts=2
        )
        print(f"❓ Resultado inesperado: {result}")

    except Exception as e:
        print(f"✅ Error de procesamiento manejado correctamente")
        print(f"   🏷️ Tipo: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"   👤 Mensaje: {e.user_message}")
        if hasattr(e, 'context') and 'signal_size' in e.context:
            print(f"   📊 Señal de {e.context['signal_size']} puntos")

    print("\n💾 3. Escenario: Guardado con archivo temporal")
    try:
        def save_with_temp_file():
            # Crear archivo temporal exitosamente
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.demo') as temp_file:
                temp_path = temp_file.name
                temp_file.write("Demo data: SSA-23 Exception Handling\n")
                temp_file.write(f"Timestamp: {time.time()}\n")
                temp_file.write("Context: Real scenario demo\n")

            # Leer para verificar
            with open(temp_path, 'r') as f:
                content = f.read()

            # Limpiar
            os.unlink(temp_path)

            return f"✅ Archivo guardado y verificado: {len(content)} caracteres"

        result = modules['handle_with_recovery'](
            operation=save_with_temp_file,
            operation_name="save_signal_data",
            context={
                "data_type": "processed_signal",
                "format": "demo_format",
                "compression": False,
                "backup_enabled": True
            },
            max_attempts=2
        )
        print(f"✅ Guardado exitoso: {result}")

    except Exception as e:
        print(f"❌ Error de guardado: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"   👤 Mensaje: {e.user_message}")

def main():
    """Main demo function"""
    print("🚀 DEMO AUTOMÁTICO - SSA-23 Exception Handling")
    print("="*70)
    print("Demostrando todas las implementaciones de excepciones automáticamente...")
    print("Este demo ejecuta ejemplos de cada tipo de excepción y estrategia de recuperación")
    print("")

    # Setup imports
    print("📦 Importando módulos de excepciones...")
    modules = setup_imports()
    if not modules:
        print("❌ No se pudieron importar los módulos. Saliendo.")
        return

    print("✅ Módulos importados exitosamente!")

    # Run all demos
    demos = [
        ("Base Exception", demo_base_exception),
        ("Domain Exceptions", demo_domain_exceptions),
        ("Infrastructure Exceptions", demo_infrastructure_exceptions),
        ("Presentation Exceptions", demo_presentation_exceptions),
        ("Recovery Strategies", demo_recovery_strategies),
        ("Exception Handler", demo_exception_handler),
        ("Real Scenarios", demo_real_scenarios),
    ]

    for demo_name, demo_func in demos:
        print(f"\n⏳ Ejecutando demo: {demo_name}...")
        try:
            demo_func(modules)
        except Exception as e:
            print(f"❌ Error ejecutando demo '{demo_name}': {e}")
            import traceback
            traceback.print_exc()

        print(f"✅ Demo '{demo_name}' completado")
        time.sleep(0.5)  # Pequeña pausa para legibilidad

    print_separator("DEMO COMPLETADO")
    print("🎉 ¡Demo automático completado exitosamente!")
    print("")
    print("📊 Resumen de lo demostrado:")
    print("   ✅ Jerarquía completa de excepciones personalizadas")
    print("   ✅ Integración automática con SSA-22 structured logging")
    print("   ✅ Context enrichment y error codes únicos")
    print("   ✅ Estrategias de recuperación inteligentes")
    print("   ✅ Manejo centralizado con handle_with_recovery()")
    print("   ✅ Escenarios de uso real y casos edge")
    print("")
    print("📚 Para más información:")
    print("   🔗 docs/SSA-23-EXCEPTION-HANDLING-GUIDELINES.md")
    print("   🔗 tests/test_exceptions.py")
    print("   🔗 run_exception_tests.py")
    print("")
    print("🛠️ Para testing interactivo: python3 test_manual_exceptions.py")

if __name__ == "__main__":
    main()