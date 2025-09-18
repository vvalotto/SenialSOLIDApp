#!/usr/bin/env python3
import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

try:
    from aplicacion.validation import ValidationResult
    print("✅ Import successful using 'aplicacion.validation'")
except ImportError as e:
    print(f"❌ Import failed with aplicacion: {e}")

try:
    # Direct path import
    validation_path = os.path.join(project_root, "03_aplicacion", "validation")
    sys.path.insert(0, validation_path)

    from framework.validator_base import ValidationResult
    print("✅ Direct path import successful")
except Exception as e:
    print(f"❌ Direct path failed: {e}")

try:
    # Alternative approach - rename directory temporarily
    old_name = "03_aplicacion"
    new_name = "aplicacion"
    print(f"Directory structure: {os.listdir('.')}")
except Exception as e:
    print(f"Directory check failed: {e}")