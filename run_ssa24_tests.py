#!/usr/bin/env python3
"""
SSA-24 Test Execution Script
Convenient script to run all SSA-24 validation tests and generate comprehensive evidence
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root and tests to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tests"))

def run_ssa24_tests():
    """Run SSA-24 validation tests and generate evidence"""
    print("🛡️ SSA-24 Input Validation Framework - Test Execution")
    print("=" * 60)

    try:
        # Change to tests directory
        tests_dir = project_root / "tests"
        os.chdir(tests_dir)

        # Run the test reporter which executes all tests
        print("🚀 Executing comprehensive test suite...")
        result = subprocess.run([
            sys.executable, "ssa24_test_reporter.py"
        ], capture_output=True, text=True)

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        # Check for test reports
        reports_dir = tests_dir / "test_reports"
        if reports_dir.exists():
            html_files = list(reports_dir.glob("*.html"))
            json_files = list(reports_dir.glob("*.json"))
            txt_files = list(reports_dir.glob("*.txt"))

            if html_files or json_files or txt_files:
                print("\n📊 Generated Reports:")
                for html_file in html_files:
                    print(f"   📄 HTML Report: {html_file}")
                for json_file in json_files:
                    print(f"   📊 JSON Report: {json_file}")
                for txt_file in txt_files:
                    print(f"   📋 Evidence Doc: {txt_file}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_ssa24_tests()
    sys.exit(0 if success else 1)