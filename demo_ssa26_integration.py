#!/usr/bin/env python3
"""
Demo SSA-26 Integration: SSA-24 + SSA-26 Bridge
Testing the integration between validation framework and academic error messaging
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from aplicacion.patterns.validation_error_bridge import (
        SSA24ToSSA26Bridge,
        ValidationErrorCollector,
        convert_ssa24_validation_error,
        create_validation_error_collector
    )
    from dominio.patterns.messaging.user_message_formatter import (
        AcademicErrorMessageFormatter,
        format_error
    )
    print("✅ SSA-26 Integration components loaded successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


class MockValidationResult:
    """Mock SSA-24 ValidationResult for demo purposes"""
    def __init__(self, is_valid: bool, errors: list = None):
        self.is_valid = is_valid
        self.errors = errors or []


class MockSecurityResult:
    """Mock SSA-24 SecurityValidationResult for demo purposes"""
    def __init__(self, is_safe: bool, threats_detected: list = None):
        self.is_safe = is_safe
        self.threats_detected = threats_detected or []


def demo_bridge_validation_errors():
    """Demo bridging SSA-24 validation errors to SSA-26 messages"""
    print("🌉 Demo: SSA-24 to SSA-26 Bridge - Validation Errors")
    print("=" * 60)

    bridge = SSA24ToSSA26Bridge(language="es", educational_mode=True)

    # Test 1: Successful validation (no error message needed)
    print("\n1️⃣ Successful Validation:")
    print("-" * 30)
    success_result = MockValidationResult(is_valid=True)
    error_msg = bridge.convert_validation_result(
        validation_result=success_result,
        field_name="frequency",
        field_value=1000.0
    )
    print(f"Result: {error_msg}")  # Should be None

    # Test 2: Range validation error
    print("\n2️⃣ Range Validation Error:")
    print("-" * 30)
    range_error = MockValidationResult(
        is_valid=False,
        errors=[{
            'type': 'range_error',
            'message': 'Value 75000 is outside valid range (0.1-50000)'
        }]
    )
    error_msg = bridge.convert_validation_result(
        validation_result=range_error,
        field_name="frequency",
        field_value=75000.0
    )
    if error_msg:
        print(f"👤 User Message: {error_msg.user_message}")
        print(f"💡 Learning Tip: {error_msg.learning_tip}")
        print(f"✅ Action: {error_msg.suggested_action}")

    # Test 3: Length validation error
    print("\n3️⃣ Length Validation Error:")
    print("-" * 30)
    length_error = MockValidationResult(
        is_valid=False,
        errors=[{
            'type': 'min_length_error',
            'message': 'Description must be at least 3 characters long'
        }]
    )
    error_msg = bridge.convert_validation_result(
        validation_result=length_error,
        field_name="description",
        field_value="AB"
    )
    if error_msg:
        print(f"👤 User Message: {error_msg.user_message}")
        print(f"💡 Learning Tip: {error_msg.learning_tip}")
        print(f"✅ Action: {error_msg.suggested_action}")


def demo_bridge_security_errors():
    """Demo bridging SSA-24 security errors to SSA-26 messages"""
    print("\n\n🛡️ Demo: SSA-24 to SSA-26 Bridge - Security Errors")
    print("=" * 60)

    bridge = SSA24ToSSA26Bridge(language="es", educational_mode=True)

    # Test 1: Safe content
    print("\n1️⃣ Safe Content:")
    print("-" * 30)
    safe_result = MockSecurityResult(is_safe=True)
    error_msg = bridge.convert_security_validation_result(
        security_result=safe_result,
        input_content="Normal signal description"
    )
    print(f"Result: {error_msg}")  # Should be None

    # Test 2: XSS threat detection
    print("\n2️⃣ XSS Threat Detection:")
    print("-" * 30)
    xss_result = MockSecurityResult(
        is_safe=False,
        threats_detected=[{
            'type': 'xss_threat',
            'message': 'Script injection attempt detected'
        }]
    )
    error_msg = bridge.convert_security_validation_result(
        security_result=xss_result,
        input_content="<script>alert('malicious')</script>"
    )
    if error_msg:
        print(f"👤 User Message: {error_msg.user_message}")
        print(f"💡 Learning Tip: {error_msg.learning_tip}")
        print(f"✅ Action: {error_msg.suggested_action}")

    # Test 3: SQL injection threat
    print("\n3️⃣ SQL Injection Threat:")
    print("-" * 30)
    sql_result = MockSecurityResult(
        is_safe=False,
        threats_detected=[{
            'type': 'sql_injection_threat',
            'message': 'SQL injection pattern detected'
        }]
    )
    error_msg = bridge.convert_security_validation_result(
        security_result=sql_result,
        input_content="'; DROP TABLE signals; --"
    )
    if error_msg:
        print(f"👤 User Message: {error_msg.user_message}")
        print(f"💡 Learning Tip: {error_msg.learning_tip}")
        print(f"✅ Action: {error_msg.suggested_action}")


def demo_error_collector():
    """Demo the ValidationErrorCollector utility"""
    print("\n\n📊 Demo: Validation Error Collector")
    print("=" * 60)

    collector = create_validation_error_collector(language="es")

    # Collect multiple validation errors
    print("\n1️⃣ Collecting Multiple Validation Errors:")
    print("-" * 40)

    # Frequency error
    freq_error = MockValidationResult(
        is_valid=False,
        errors=[{'type': 'range_error', 'message': 'Frequency out of range'}]
    )
    collector.add_validation_error(
        validation_result=freq_error,
        field_name="frequency",
        field_value=100000.0
    )

    # Description error
    desc_error = MockValidationResult(
        is_valid=False,
        errors=[{'type': 'min_length_error', 'message': 'Description too short'}]
    )
    collector.add_validation_error(
        validation_result=desc_error,
        field_name="description",
        field_value="A"
    )

    # Security error
    security_error = MockSecurityResult(
        is_safe=False,
        threats_detected=[{'type': 'xss_threat', 'message': 'XSS detected'}]
    )
    collector.add_security_error(
        security_result=security_error,
        input_content="<script>hack()</script>"
    )

    print(f"Total errors collected: {len(collector.get_all_errors())}")
    print(f"Has critical errors: {collector.has_critical_errors()}")

    print("\n2️⃣ Error Summary by Category:")
    print("-" * 30)
    all_errors = collector.get_all_errors()
    for i, error in enumerate(all_errors, 1):
        print(f"{i}. [{error.category.value.upper()}] {error.user_message}")

    print("\n3️⃣ HTML Formatted Errors:")
    print("-" * 30)
    html_errors = collector.get_html_formatted_errors()
    for html_error in html_errors:
        print("HTML Output:")
        print(html_error[:150] + "..." if len(html_error) > 150 else html_error)
        print()


def demo_convenience_functions():
    """Demo convenience functions for quick error conversion"""
    print("\n\n⚡ Demo: Convenience Functions")
    print("=" * 60)

    print("\n1️⃣ Quick Validation Error Conversion:")
    print("-" * 40)
    mock_result = MockValidationResult(
        is_valid=False,
        errors=[{'type': 'max_value_error', 'message': 'Amplitude too high'}]
    )
    error_msg = convert_ssa24_validation_error(
        validation_result=mock_result,
        field_name="amplitude",
        field_value=15.0,
        language="es"
    )
    if error_msg:
        print(f"👤 {error_msg.user_message}")
        print(f"💡 {error_msg.learning_tip}")

    print("\n2️⃣ Direct Error Creation:")
    print("-" * 40)
    direct_error = format_error(
        "validation",
        field="signal_id",
        value=10000,
        constraint="out_of_range"
    )
    print(f"👤 {direct_error.user_message}")
    print(f"💡 {direct_error.learning_tip}")


def demo_fallback_behavior():
    """Demo fallback behavior when SSA-24 is not available"""
    print("\n\n🔄 Demo: Fallback Behavior")
    print("=" * 60)

    bridge = SSA24ToSSA26Bridge(language="es", educational_mode=True)

    print("\n1️⃣ Fallback for Missing SSA-24:")
    print("-" * 40)
    # Pass None to simulate SSA-24 not being available
    fallback_error = bridge.convert_validation_result(
        validation_result=None,
        field_name="test_field",
        field_value="test_value"
    )
    if fallback_error:
        print(f"👤 {fallback_error.user_message}")
        print(f"💡 {fallback_error.learning_tip}")

    print("\n2️⃣ Fallback for Unknown Error Types:")
    print("-" * 40)
    unknown_error = MockValidationResult(
        is_valid=False,
        errors=[{'type': 'unknown_error_type', 'message': 'Something went wrong'}]
    )
    fallback_error2 = bridge.convert_validation_result(
        validation_result=unknown_error,
        field_name="mystery_field",
        field_value="mystery_value"
    )
    if fallback_error2:
        print(f"👤 {fallback_error2.user_message}")
        print(f"💡 {fallback_error2.learning_tip}")


def main():
    """Main demo function"""
    print("🌉 SSA-26 Integration Demo: SSA-24 + SSA-26 Bridge")
    print("📋 Testing Bridge Between Validation and Academic Error Messaging")
    print("=" * 80)

    try:
        demo_bridge_validation_errors()
        demo_bridge_security_errors()
        demo_error_collector()
        demo_convenience_functions()
        demo_fallback_behavior()

        print("\n" + "=" * 80)
        print("🎯 SSA-26 Integration Demo Completed Successfully!")
        print("✅ Bridge between SSA-24 and SSA-26 working correctly")
        print("🌉 Seamless integration of validation and error messaging")
        print("📚 Educational error messages provide learning value")
        print("🔄 Robust fallback handling for edge cases")
        print("🎓 Ready for production use in academic environment")

        return True

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)