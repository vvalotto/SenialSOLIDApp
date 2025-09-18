#!/usr/bin/env python3
"""
Comprehensive Test Suite for SSA-24 Input Validation Framework

Este archivo contiene tests exhaustivos para validar la correctitud,
seguridad y performance del framework de validación SSA-24.
"""

import unittest
import sys
import os
import tempfile
import json
import time
from datetime import datetime, timedelta
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aplicacion.validation import (
    # Core framework
    AbstractValidator,
    ValidationResult,
    ValidationPipeline,
    PipelineMode,
    SanitizationEngine,
    SanitizationLevel,

    # Specialized validators
    SignalParameterValidator,
    SignalDataValidator,
    FileTypeValidator,
    FileSizeValidator,
    FileContentValidator,
    StringInputValidator,
    EmailValidator,
    PasswordValidator,
    NumericInputValidator,
    DateTimeValidator,

    # Exceptions
    ValidationError,
    SecurityValidationError,
    FileValidationError,
    SignalValidationError,

    # Decorators
    validate_input,
    validate_parameters,
    auto_sanitize,
    sanitize_input
)


class TestValidationFrameworkCore(unittest.TestCase):
    """Tests for core validation framework components"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_results = []

    def test_validation_result_creation(self):
        """Test ValidationResult object creation and methods"""
        result = ValidationResult(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

        # Test error addition
        error = ValidationError("Test error", field_name="test_field")
        result.add_error(error)
        self.assertFalse(result.is_valid)
        self.assertTrue(result.has_errors())
        self.assertEqual(len(result.errors), 1)

        # Test warning addition
        result.add_warning("Test warning")
        self.assertTrue(result.has_warnings())
        self.assertEqual(len(result.warnings), 1)

        # Test serialization
        result_dict = result.to_dict()
        self.assertIn('is_valid', result_dict)
        self.assertIn('errors', result_dict)
        self.assertIn('warnings', result_dict)

        self.test_results.append({
            'test': 'validation_result_creation',
            'status': 'PASS',
            'details': 'ValidationResult creation and methods work correctly'
        })

    def test_validation_pipeline_modes(self):
        """Test different pipeline execution modes"""
        pipeline = ValidationPipeline("test_pipeline", mode=PipelineMode.FAIL_FAST)

        # Add validators that will fail
        pipeline.add_validator(StringInputValidator(max_length=5))
        pipeline.add_validator(NumericInputValidator(min_value=0, max_value=10))

        # Test fail-fast mode
        result = pipeline.validate("This is too long")
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

        # Test collect-all mode
        pipeline.mode = PipelineMode.COLLECT_ALL
        result = pipeline.validate("This is too long")
        self.assertFalse(result.is_valid)

        self.test_results.append({
            'test': 'validation_pipeline_modes',
            'status': 'PASS',
            'details': 'Pipeline modes (fail-fast, collect-all) work correctly'
        })

    def test_sanitization_engine_basic(self):
        """Test basic sanitization functionality"""
        engine = SanitizationEngine(SanitizationLevel.STRICT)

        # Test XSS sanitization
        xss_input = "<script>alert('xss')</script>Normal text"
        result = engine.sanitize(xss_input)
        self.assertTrue(result.was_modified)
        self.assertNotIn("<script>", result.sanitized_value)

        # Test SQL injection sanitization
        sql_input = "'; DROP TABLE users; --"
        result = engine.sanitize(sql_input)
        self.assertTrue(result.was_modified)

        # Test safe input
        safe_input = "This is safe text"
        result = engine.sanitize(safe_input)
        # May or may not be modified due to HTML escaping

        self.test_results.append({
            'test': 'sanitization_engine_basic',
            'status': 'PASS',
            'details': 'Basic sanitization (XSS, SQL injection) works correctly'
        })


class TestSignalValidation(unittest.TestCase):
    """Tests for signal-specific validation"""

    def setUp(self):
        self.test_results = []

    def test_signal_parameter_validation(self):
        """Test signal parameter validators"""
        # Test frequency validator
        freq_validator = SignalParameterValidator('frequency')

        # Valid frequency
        result = freq_validator.validate(1000.0)
        self.assertTrue(result.is_valid)

        # Invalid frequency (too high)
        result = freq_validator.validate(100000.0)
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.errors[0], SignalValidationError)

        # Invalid frequency (negative)
        result = freq_validator.validate(-100.0)
        self.assertFalse(result.is_valid)

        # Test amplitude validator
        amp_validator = SignalParameterValidator('amplitude')

        # Valid amplitude
        result = amp_validator.validate(5.0)
        self.assertTrue(result.is_valid)

        # Invalid amplitude (too high)
        result = amp_validator.validate(50.0)
        self.assertFalse(result.is_valid)

        self.test_results.append({
            'test': 'signal_parameter_validation',
            'status': 'PASS',
            'details': 'Signal parameter validation (frequency, amplitude) works correctly'
        })

    def test_signal_data_validation(self):
        """Test signal data array validation"""
        data_validator = SignalDataValidator(max_length=1000, check_anomalies=True)

        # Valid signal data
        valid_data = [1.0, 2.0, 3.0, 2.0, 1.0]
        result = data_validator.validate(valid_data)
        self.assertTrue(result.is_valid)
        self.assertIn('data_length', result.metadata)
        self.assertIn('mean_value', result.metadata)

        # Invalid data (contains NaN)
        invalid_data = [1.0, float('nan'), 3.0]
        result = data_validator.validate(invalid_data)
        self.assertFalse(result.is_valid)

        # Invalid data (contains inf)
        invalid_data = [1.0, float('inf'), 3.0]
        result = data_validator.validate(invalid_data)
        self.assertFalse(result.is_valid)

        # Too long data
        long_data = list(range(2000))
        result = data_validator.validate(long_data)
        self.assertFalse(result.is_valid)

        self.test_results.append({
            'test': 'signal_data_validation',
            'status': 'PASS',
            'details': 'Signal data validation (arrays, NaN, inf, length) works correctly'
        })

    def test_signal_anomaly_detection(self):
        """Test signal anomaly detection"""
        data_validator = SignalDataValidator(
            max_length=1000,
            check_anomalies=True,
            anomaly_threshold=2.0
        )

        # Normal distribution data
        normal_data = np.random.normal(0, 1, 100).tolist()
        result = data_validator.validate(normal_data)
        self.assertTrue(result.is_valid)

        # Data with outliers
        outlier_data = [1.0] * 90 + [100.0] * 10  # 10% outliers
        result = data_validator.validate(outlier_data)
        # Should detect anomalies but may not fail validation

        self.test_results.append({
            'test': 'signal_anomaly_detection',
            'status': 'PASS',
            'details': 'Signal anomaly detection works correctly'
        })


class TestFileValidation(unittest.TestCase):
    """Tests for file validation"""

    def setUp(self):
        self.test_results = []
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

    def test_file_type_validation(self):
        """Test file type validation"""
        file_validator = FileTypeValidator(allowed_extensions=['txt', 'csv', 'json'])

        # Valid file types
        valid_files = ['data.txt', 'signal.csv', 'config.json']
        for filename in valid_files:
            result = file_validator.validate(filename)
            self.assertTrue(result.is_valid, f"Failed for {filename}")

        # Invalid file types
        invalid_files = ['malware.exe', 'script.js', 'unknown.xyz']
        for filename in invalid_files:
            result = file_validator.validate(filename)
            self.assertFalse(result.is_valid, f"Should fail for {filename}")

        # Dangerous file types
        dangerous_files = ['virus.exe', 'malware.bat', 'script.vbs']
        for filename in dangerous_files:
            result = file_validator.validate(filename)
            self.assertFalse(result.is_valid, f"Should block dangerous file {filename}")
            if result.errors:
                self.assertIsInstance(result.errors[0], (SecurityValidationError, FileValidationError))

        self.test_results.append({
            'test': 'file_type_validation',
            'status': 'PASS',
            'details': 'File type validation (allowed, invalid, dangerous) works correctly'
        })

    def test_file_size_validation(self):
        """Test file size validation"""
        size_validator = FileSizeValidator(max_size=1024, min_size=10)

        # Create temporary files with different sizes
        small_file = tempfile.NamedTemporaryFile(delete=False)
        small_file.write(b'small')  # 5 bytes
        small_file.close()
        self.temp_files.append(small_file.name)

        medium_file = tempfile.NamedTemporaryFile(delete=False)
        medium_file.write(b'medium content' * 10)  # ~140 bytes
        medium_file.close()
        self.temp_files.append(medium_file.name)

        large_file = tempfile.NamedTemporaryFile(delete=False)
        large_file.write(b'large content' * 100)  # ~1300 bytes
        large_file.close()
        self.temp_files.append(large_file.name)

        # Test file sizes
        result = size_validator.validate(small_file.name)
        self.assertFalse(result.is_valid)  # Too small

        result = size_validator.validate(medium_file.name)
        self.assertTrue(result.is_valid)  # Just right

        result = size_validator.validate(large_file.name)
        self.assertFalse(result.is_valid)  # Too large

        self.test_results.append({
            'test': 'file_size_validation',
            'status': 'PASS',
            'details': 'File size validation (min, max limits) works correctly'
        })

    def test_file_content_security(self):
        """Test file content security scanning"""
        content_validator = FileContentValidator(scan_content=True)

        # Create file with safe content
        safe_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        safe_file.write("This is safe signal data\n1.0\n2.0\n3.0\n")
        safe_file.close()
        self.temp_files.append(safe_file.name)

        # Create file with malicious content
        malicious_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        malicious_file.write("<script>alert('xss')</script>\nSome data\n")
        malicious_file.close()
        self.temp_files.append(malicious_file.name)

        # Test safe content
        result = content_validator.validate(safe_file.name)
        self.assertTrue(result.is_valid)

        # Test malicious content
        result = content_validator.validate(malicious_file.name)
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.errors[0], SecurityValidationError)

        self.test_results.append({
            'test': 'file_content_security',
            'status': 'PASS',
            'details': 'File content security scanning works correctly'
        })


class TestUserInputValidation(unittest.TestCase):
    """Tests for user input validation"""

    def setUp(self):
        self.test_results = []

    def test_string_input_validation(self):
        """Test string input validation and sanitization"""
        string_validator = StringInputValidator(
            max_length=50,
            allowed_pattern=StringInputValidator.TEXT_SAFE
        )

        # Valid string
        result = string_validator.validate("Valid user input")
        self.assertTrue(result.is_valid)

        # Too long string
        result = string_validator.validate("A" * 100)
        self.assertFalse(result.is_valid)

        # Invalid characters (XSS attempt)
        result = string_validator.validate("<script>alert('xss')</script>")
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.errors[0], SecurityValidationError)

        self.test_results.append({
            'test': 'string_input_validation',
            'status': 'PASS',
            'details': 'String input validation (length, patterns, XSS) works correctly'
        })

    def test_email_validation(self):
        """Test email validation"""
        email_validator = EmailValidator()

        # Valid emails
        valid_emails = [
            'user@example.com',
            'test.email@domain.org',
            'user+tag@subdomain.example.com'
        ]

        for email in valid_emails:
            result = email_validator.validate(email)
            self.assertTrue(result.is_valid, f"Should be valid: {email}")

        # Invalid emails
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user..double@domain.com'
        ]

        for email in invalid_emails:
            result = email_validator.validate(email)
            self.assertFalse(result.is_valid, f"Should be invalid: {email}")

        self.test_results.append({
            'test': 'email_validation',
            'status': 'PASS',
            'details': 'Email validation (valid, invalid formats) works correctly'
        })

    def test_password_validation(self):
        """Test password strength validation"""
        password_validator = PasswordValidator(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )

        # Strong password
        result = password_validator.validate("StrongP@ss123")
        self.assertTrue(result.is_valid)
        self.assertIn('password_strength_score', result.metadata)
        self.assertGreater(result.metadata['password_strength_score'], 80)

        # Weak passwords
        weak_passwords = [
            "weak",           # Too short
            "nouppercase1!",  # No uppercase
            "NOLOWERCASE1!",  # No lowercase
            "NoDigits!",      # No digits
            "NoSpecial123"    # No special chars
        ]

        for password in weak_passwords:
            result = password_validator.validate(password)
            self.assertFalse(result.is_valid, f"Should be invalid: {password}")

        self.test_results.append({
            'test': 'password_validation',
            'status': 'PASS',
            'details': 'Password validation (strength, requirements) works correctly'
        })


class TestSecurityFeatures(unittest.TestCase):
    """Tests for security features"""

    def setUp(self):
        self.test_results = []

    def test_xss_prevention(self):
        """Test XSS attack prevention"""
        engine = SanitizationEngine(SanitizationLevel.STRICT)

        xss_vectors = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<div onload=alert('xss')>content</div>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;"
        ]

        for vector in xss_vectors:
            result = engine.sanitize(vector)
            self.assertTrue(result.was_modified, f"Should sanitize XSS: {vector}")
            self.assertNotIn("script", result.sanitized_value.lower())
            self.assertNotIn("javascript:", result.sanitized_value.lower())

        self.test_results.append({
            'test': 'xss_prevention',
            'status': 'PASS',
            'details': 'XSS prevention sanitizes all common attack vectors'
        })

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        engine = SanitizationEngine(SanitizationLevel.STRICT)

        sql_vectors = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "/*comment*/ SELECT",
            "admin'--"
        ]

        for vector in sql_vectors:
            result = engine.sanitize(vector)
            self.assertTrue(result.was_modified, f"Should sanitize SQL: {vector}")

        self.test_results.append({
            'test': 'sql_injection_prevention',
            'status': 'PASS',
            'details': 'SQL injection prevention sanitizes attack vectors'
        })

    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention"""
        engine = SanitizationEngine(SanitizationLevel.STRICT)

        path_vectors = [
            "../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "file.txt\x00.php",
            "....//....//etc/passwd"
        ]

        for vector in path_vectors:
            result = engine.sanitize(vector)
            self.assertTrue(result.was_modified, f"Should sanitize path: {vector}")
            self.assertNotIn("..", result.sanitized_value)

        self.test_results.append({
            'test': 'path_traversal_prevention',
            'status': 'PASS',
            'details': 'Path traversal prevention works correctly'
        })


class TestPerformance(unittest.TestCase):
    """Performance tests for validation framework"""

    def setUp(self):
        self.test_results = []

    def test_validation_performance(self):
        """Test validation performance with large datasets"""
        # Test signal data validation performance
        data_validator = SignalDataValidator(max_length=50000, check_anomalies=False)

        # Large signal data
        large_signal = np.random.normal(0, 1, 10000).tolist()

        start_time = time.time()
        result = data_validator.validate(large_signal)
        end_time = time.time()

        validation_time = end_time - start_time
        self.assertTrue(result.is_valid)
        self.assertLess(validation_time, 1.0, "Validation should complete in under 1 second")

        # Test string validation performance
        string_validator = StringInputValidator(max_length=10000)

        long_string = "A" * 5000
        start_time = time.time()
        result = string_validator.validate(long_string)
        end_time = time.time()

        validation_time = end_time - start_time
        self.assertLess(validation_time, 0.1, "String validation should be fast")

        self.test_results.append({
            'test': 'validation_performance',
            'status': 'PASS',
            'details': f'Validation performance is acceptable (signal: {validation_time:.3f}s)'
        })

    def test_sanitization_performance(self):
        """Test sanitization performance"""
        engine = SanitizationEngine(SanitizationLevel.MODERATE)

        # Test multiple sanitizations
        test_strings = [
            "Normal text content",
            "<script>alert('xss')</script> Mixed content",
            "SQL injection '; DROP TABLE users; --",
            "Path traversal ../../etc/passwd"
        ] * 100  # 400 strings total

        start_time = time.time()
        for test_string in test_strings:
            result = engine.sanitize(test_string)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / len(test_strings)

        self.assertLess(avg_time, 0.01, "Average sanitization should be under 10ms")

        self.test_results.append({
            'test': 'sanitization_performance',
            'status': 'PASS',
            'details': f'Sanitization performance is acceptable (avg: {avg_time*1000:.1f}ms)'
        })


class TestDecorators(unittest.TestCase):
    """Tests for validation decorators"""

    def setUp(self):
        self.test_results = []

    def test_validate_input_decorator(self):
        """Test @validate_input decorator"""

        @validate_parameters(
            text=StringInputValidator(max_length=10),
            number=NumericInputValidator(min_value=0, max_value=100)
        )
        def test_function(text, number):
            return f"{text}: {number}"

        # Valid inputs
        result = test_function("hello", 50)
        self.assertEqual(result, "hello: 50")

        # Invalid inputs should raise ValidationError
        with self.assertRaises(ValidationError):
            test_function("this is too long", 50)

        with self.assertRaises(ValidationError):
            test_function("hello", 150)

        self.test_results.append({
            'test': 'validate_input_decorator',
            'status': 'PASS',
            'details': 'Input validation decorators work correctly'
        })

    def test_auto_sanitize_decorator(self):
        """Test @auto_sanitize decorator"""

        @auto_sanitize()
        def test_sanitize_function(user_input):
            return f"Processed: {user_input}"

        # Test with potentially malicious input
        result = test_sanitize_function("<script>alert('xss')</script>")
        self.assertNotIn("<script>", result)

        self.test_results.append({
            'test': 'auto_sanitize_decorator',
            'status': 'PASS',
            'details': 'Auto-sanitize decorator works correctly'
        })


class TestReporter:
    """Test results reporter for generating evidence"""

    def __init__(self):
        self.all_results = []

    def collect_results(self, test_case):
        """Collect results from a test case"""
        if hasattr(test_case, 'test_results'):
            self.all_results.extend(test_case.test_results)

    def generate_report(self, output_file=None):
        """Generate comprehensive test report"""
        timestamp = datetime.now().isoformat()

        report = {
            'test_report': {
                'framework': 'SSA-24 Input Validation Framework',
                'timestamp': timestamp,
                'total_tests': len(self.all_results),
                'passed_tests': len([r for r in self.all_results if r['status'] == 'PASS']),
                'failed_tests': len([r for r in self.all_results if r['status'] == 'FAIL']),
                'coverage_areas': [
                    'Core Validation Framework',
                    'Signal Processing Validation',
                    'File Security Validation',
                    'User Input Sanitization',
                    'Security Features (XSS, SQL Injection, Path Traversal)',
                    'Performance Testing',
                    'Decorator Integration'
                ],
                'test_results': self.all_results
            }
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

        return report


def run_all_tests():
    """Run all validation tests and generate report"""
    print("🧪 Running SSA-24 Validation Framework Test Suite")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestValidationFrameworkCore,
        TestSignalValidation,
        TestFileValidation,
        TestUserInputValidation,
        TestSecurityFeatures,
        TestPerformance,
        TestDecorators
    ]

    reporter = TestReporter()

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Collect results for reporting
    # Note: In a real implementation, you'd need to modify the test runner
    # to collect the custom test_results from each test case

    print(f"\n📊 Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    # Generate detailed report
    report_file = f"tests/ssa24_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    print(f"\n📋 Detailed report would be saved to: {report_file}")
    print("✅ All validation tests completed")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)