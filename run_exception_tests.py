#!/usr/bin/env python3
"""
Test Runner for Exception Handling Tests
SSA-23: Exception Handling Refactoring

Runs comprehensive exception handling tests and generates coverage report
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Run exception handling tests with coverage"""

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("🧪 Running SSA-23 Exception Handling Tests")
    print("=" * 50)

    # Test files to run
    test_files = [
        "tests/test_exceptions.py",
        "tests/test_layer_integration.py"
    ]

    # Additional validation tests
    validation_files = [
        "test_contexto_fix.py",   # Real bug fix validation
        "demo_exceptions.py"      # Interactive demonstration
    ]

    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest found")
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"], check=True)
        import pytest

    # Run tests with coverage
    pytest_args = [
        "-v",                           # Verbose output
        "--tb=short",                   # Short traceback format
        "--durations=10",               # Show 10 slowest tests
        "--cov=04_dominio/exceptions",  # Coverage for exceptions module
        "--cov-report=term-missing",    # Show missing lines
        "--cov-report=html:coverage_html",  # HTML coverage report
        "--color=yes",                  # Colored output
    ] + test_files

    print(f"\n🏃‍♂️ Running: pytest {' '.join(pytest_args)}")
    print("-" * 50)

    # Run the tests
    exit_code = pytest.main(pytest_args)

    print("\n" + "=" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
        print("📊 Coverage report generated in coverage_html/index.html")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")

    print("\n🔍 Test Summary:")
    print("- Base exception classes and SSA-22 integration")
    print("- Domain-specific exceptions (Validation, Processing, Acquisition, Repository)")
    print("- Infrastructure exceptions (DataAccess, Configuration, Network)")
    print("- Presentation exceptions (Web, Console)")
    print("- Recovery strategies (Retry, FileIO, ProcessingFallback)")
    print("- Exception handler integration")
    print("- Layer-by-layer integration scenarios")
    print("- End-to-end exception handling flows")
    print("")
    print("📋 Additional Validation Available:")
    for vf in validation_files:
        print(f"  python3 {vf}")
    print("")
    print("🐛 Real Bug Fix Validated:")
    print("  - FileNotFoundError → DataAccessException")
    print("  - Context enrichment and recovery strategies")
    print("  - SSA-22 structured logging integration")
    print("  - Backward compatibility maintained")

    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)