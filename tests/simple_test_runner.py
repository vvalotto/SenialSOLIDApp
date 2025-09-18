#!/usr/bin/env python3
"""
Simple SSA-24 Test Runner (sin dependencias externas)
Versión simplificada que solo usa bibliotecas estándar de Python
"""

import os
import sys
import time
import unittest
import platform
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def run_simple_tests():
    """Ejecuta tests SSA-24 de manera simple"""
    print("🛡️ SSA-24 Input Validation Framework - Simple Test Runner")
    print("=" * 60)

    # Información básica del sistema
    print(f"🖥️ Sistema: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Tests a ejecutar
    test_modules = [
        ('test_ssa24_validation_framework', '🧪 Core Framework Tests'),
        ('test_ssa24_integration', '🔗 Integration Tests'),
        ('test_ssa24_security', '🛡️ Security Tests'),
        ('test_ssa24_performance', '⚡ Performance Tests')
    ]

    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    start_time = time.time()

    # Ejecutar cada módulo de tests
    for module_name, description in test_modules:
        print(f"\n{description}")
        print("-" * 40)

        try:
            # Importar y ejecutar el módulo
            module = __import__(module_name)
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)

            # Ejecutar tests
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)

            # Acumular resultados
            tests_run = result.testsRun
            passed = tests_run - len(result.failures) - len(result.errors)
            failed = len(result.failures)
            errors = len(result.errors)

            total_tests += tests_run
            total_passed += passed
            total_failed += failed
            total_errors += errors

            # Mostrar resultado del módulo
            print(f"📊 Resultado: {passed}/{tests_run} pasaron")
            if failed > 0:
                print(f"❌ Fallos: {failed}")
            if errors > 0:
                print(f"💥 Errores: {errors}")

        except Exception as e:
            print(f"❌ Error ejecutando {module_name}: {e}")
            total_errors += 1

    # Resumen final
    end_time = time.time()
    execution_time = end_time - start_time
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print("\n" + "=" * 60)
    print("📈 RESUMEN FINAL")
    print("=" * 60)
    print(f"⏱️ Tiempo total: {execution_time:.2f} segundos")
    print(f"🧪 Tests totales: {total_tests}")
    print(f"✅ Pasaron: {total_passed}")
    print(f"❌ Fallaron: {total_failed}")
    print(f"💥 Errores: {total_errors}")
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")

    # Estado del framework
    if success_rate >= 95:
        status = "✅ FRAMEWORK VALIDADO"
    elif success_rate >= 80:
        status = "⚠️ FRAMEWORK NECESITA ATENCIÓN"
    else:
        status = "❌ FRAMEWORK TIENE PROBLEMAS CRÍTICOS"

    print(f"🎯 Estado: {status}")

    # Guardar resumen simple
    try:
        reports_dir = Path("test_reports")
        reports_dir.mkdir(exist_ok=True)

        summary_file = reports_dir / f"simple_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(summary_file, 'w') as f:
            f.write(f"SSA-24 Test Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"System: {platform.system()} {platform.release()}\n")
            f.write(f"Python: {platform.python_version()}\n\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {total_passed}\n")
            f.write(f"Failed: {total_failed}\n")
            f.write(f"Errors: {total_errors}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Execution Time: {execution_time:.2f}s\n")
            f.write(f"Status: {status}\n")

        print(f"📄 Resumen guardado en: {summary_file}")

    except Exception as e:
        print(f"⚠️ No se pudo guardar resumen: {e}")

    return success_rate >= 80

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)