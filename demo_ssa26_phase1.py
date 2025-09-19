#!/usr/bin/env python3
"""
Demo SSA-26 Phase 1: Academic Error Message Formatter
Testing the user-friendly error messaging system
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dominio.patterns.messaging.user_message_formatter import (
        AcademicErrorMessageFormatter,
        format_error
    )
    print("✅ SSA-26 Phase 1 components loaded successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def demo_validation_errors():
    """Demo validation errors with academic messaging"""
    print("🧪 Demo: Validation Errors with Educational Context")
    print("=" * 60)

    formatter = AcademicErrorMessageFormatter(language="es", educational_mode=True)

    # Test frequency validation
    print("\n1️⃣ Frequency Validation Error:")
    print("-" * 30)
    freq_error = formatter.format_validation_error(
        field="frequency",
        value=75000,
        constraint="out_of_range"
    )
    print(f"👤 User Message: {freq_error.user_message}")
    print(f"🔧 Technical: {freq_error.technical_reason}")
    print(f"💡 Learning Tip: {freq_error.learning_tip}")
    print(f"✅ Action: {freq_error.suggested_action}")

    # Test amplitude validation
    print("\n2️⃣ Amplitude Validation Error:")
    print("-" * 30)
    amp_error = formatter.format_validation_error(
        field="amplitude",
        value=25.5,
        constraint="out_of_range"
    )
    print(f"👤 User Message: {amp_error.user_message}")
    print(f"🔧 Technical: {amp_error.technical_reason}")
    print(f"💡 Learning Tip: {amp_error.learning_tip}")
    print(f"✅ Action: {amp_error.suggested_action}")

    # Test description validation
    print("\n3️⃣ Description Validation Error:")
    print("-" * 30)
    desc_error = formatter.format_validation_error(
        field="description",
        value="AB",
        constraint="too_short"
    )
    print(f"👤 User Message: {desc_error.user_message}")
    print(f"🔧 Technical: {desc_error.technical_reason}")
    print(f"💡 Learning Tip: {desc_error.learning_tip}")
    print(f"✅ Action: {desc_error.suggested_action}")


def demo_security_errors():
    """Demo security errors with cybersecurity education"""
    print("\n\n🛡️ Demo: Security Errors with Educational Context")
    print("=" * 60)

    formatter = AcademicErrorMessageFormatter(language="es", educational_mode=True)

    # Test XSS attack detection
    print("\n1️⃣ XSS Attack Detection:")
    print("-" * 30)
    xss_error = formatter.format_security_error(
        attack_type="xss",
        blocked_content="<script>alert('malicious')</script>"
    )
    print(f"👤 User Message: {xss_error.user_message}")
    print(f"🔧 Technical: {xss_error.technical_reason}")
    print(f"💡 Learning Tip: {xss_error.learning_tip}")
    print(f"✅ Action: {xss_error.suggested_action}")

    # Test SQL injection detection
    print("\n2️⃣ SQL Injection Detection:")
    print("-" * 30)
    sql_error = formatter.format_security_error(
        attack_type="sql_injection",
        blocked_content="'; DROP TABLE signals; --"
    )
    print(f"👤 User Message: {sql_error.user_message}")
    print(f"🔧 Technical: {sql_error.technical_reason}")
    print(f"💡 Learning Tip: {sql_error.learning_tip}")
    print(f"✅ Action: {sql_error.suggested_action}")


def demo_system_errors():
    """Demo system errors with infrastructure education"""
    print("\n\n🖥️ Demo: System Errors with Infrastructure Education")
    print("=" * 60)

    formatter = AcademicErrorMessageFormatter(language="es", educational_mode=True)

    # Test database connection error
    print("\n1️⃣ Database Connection Error:")
    print("-" * 30)
    db_error = formatter.format_system_error(
        error_type="database_connection",
        component="SignalRepository",
        details="Connection timeout after 5 seconds"
    )
    print(f"👤 User Message: {db_error.user_message}")
    print(f"🔧 Technical: {db_error.technical_reason}")
    print(f"💡 Learning Tip: {db_error.learning_tip}")
    print(f"✅ Action: {db_error.suggested_action}")

    # Test file access error
    print("\n2️⃣ File Access Error:")
    print("-" * 30)
    file_error = formatter.format_system_error(
        error_type="file_access",
        component="SignalDataWriter",
        details="Permission denied: /data/signals/"
    )
    print(f"👤 User Message: {file_error.user_message}")
    print(f"🔧 Technical: {file_error.technical_reason}")
    print(f"💡 Learning Tip: {file_error.learning_tip}")
    print(f"✅ Action: {file_error.suggested_action}")


def demo_signal_processing_errors():
    """Demo signal processing errors with DSP education"""
    print("\n\n📊 Demo: Signal Processing Errors with DSP Education")
    print("=" * 60)

    formatter = AcademicErrorMessageFormatter(language="es", educational_mode=True)

    # Test acquisition error
    print("\n1️⃣ Signal Acquisition Error:")
    print("-" * 30)
    acq_error = formatter.format_signal_processing_error(
        operation="acquisition",
        signal_id="SIG_001",
        technical_details="Hardware timeout - no signal detected"
    )
    print(f"👤 User Message: {acq_error.user_message}")
    print(f"🔧 Technical: {acq_error.technical_reason}")
    print(f"💡 Learning Tip: {acq_error.learning_tip}")
    print(f"✅ Action: {acq_error.suggested_action}")

    # Test processing error
    print("\n2️⃣ Signal Processing Error:")
    print("-" * 30)
    proc_error = formatter.format_signal_processing_error(
        operation="processing",
        signal_id="SIG_002",
        technical_details="FFT computation failed - insufficient samples"
    )
    print(f"👤 User Message: {proc_error.user_message}")
    print(f"🔧 Technical: {proc_error.technical_reason}")
    print(f"💡 Learning Tip: {proc_error.learning_tip}")
    print(f"✅ Action: {proc_error.suggested_action}")


def demo_html_output():
    """Demo HTML output for web display"""
    print("\n\n🌐 Demo: HTML Output for Web Display")
    print("=" * 60)

    formatter = AcademicErrorMessageFormatter(language="es", educational_mode=True)

    # Create a validation error
    error = formatter.format_validation_error(
        field="frequency",
        value=100000,
        constraint="out_of_range"
    )

    # Convert to HTML
    html_output = formatter.to_html(error)
    print("HTML Output:")
    print(html_output)

    # Convert to dictionary
    dict_output = formatter.to_dict(error)
    print("\nJSON/Dictionary Output:")
    import json
    print(json.dumps(dict_output, indent=2, ensure_ascii=False))


def demo_convenience_function():
    """Demo convenience function for quick error formatting"""
    print("\n\n⚡ Demo: Convenience Function for Quick Formatting")
    print("=" * 60)

    # Quick validation error
    print("\n1️⃣ Quick Validation Error:")
    error1 = format_error("validation",
                         field="amplitude",
                         value=-15.0,
                         constraint="out_of_range")
    print(f"👤 {error1.user_message}")
    print(f"💡 {error1.learning_tip}")

    # Quick security error
    print("\n2️⃣ Quick Security Error:")
    error2 = format_error("security",
                         attack_type="xss",
                         blocked_content="<img src=x onerror=alert(1)>")
    print(f"👤 {error2.user_message}")
    print(f"💡 {error2.learning_tip}")

    # Quick system error
    print("\n3️⃣ Quick System Error:")
    error3 = format_error("system",
                         system_error_type="database_connection",
                         component="DataAccessLayer")
    print(f"👤 {error3.user_message}")
    print(f"💡 {error3.learning_tip}")


def main():
    """Main demo function"""
    print("🛡️ SSA-26 Phase 1: Academic Error Message Formatter Demo")
    print("📋 Testing User-Friendly Educational Error Messages")
    print("=" * 80)

    try:
        demo_validation_errors()
        demo_security_errors()
        demo_system_errors()
        demo_signal_processing_errors()
        demo_html_output()
        demo_convenience_function()

        print("\n" + "=" * 80)
        print("🎯 SSA-26 Phase 1 Demo Completed Successfully!")
        print("✅ Academic Error Message Formatter working correctly")
        print("📚 Educational error messages provide learning opportunities")
        print("🎓 Ready for integration with SSA-24 validation framework")

        return True

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)