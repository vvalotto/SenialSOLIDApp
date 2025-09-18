#!/usr/bin/env python3
"""
Integration Tests for SSA-24 Input Validation Framework
Tests end-to-end validation workflows across layers and components
"""

import unittest
import tempfile
import os
import json
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aplicacion.validation import (
    ValidationPipeline,
    create_signal_validation_pipeline,
    create_file_validation_pipeline,
    create_api_validation_pipeline,
    SignalParameterValidator,
    FileTypeValidator,
    StringInputValidator,
    ValidationError,
    FileValidationError,
    SignalValidationError,
    SecurityValidationError
)

from dominio.exceptions import (
    handle_ssa24_exception,
    is_ssa24_exception,
    handle_validation_exception,
    SSA24_AVAILABLE
)


class TestSignalValidationPipeline(unittest.TestCase):
    """Test complete signal validation workflows"""

    def setUp(self):
        self.signal_pipeline = create_signal_validation_pipeline("audio")

    def test_complete_audio_signal_pipeline(self):
        """Test complete audio signal validation pipeline"""
        # Valid audio signal data
        valid_signal_data = {
            'frequency': 440.0,  # A4 note
            'amplitude': 1.0,
            'sample_rate': 44100,
            'duration': 1.0,
            'data': [0.1, 0.2, -0.1, -0.2] * 100
        }

        context = {
            'signal_type': 'audio',
            'source': 'integration_test'
        }

        result = self.signal_pipeline.validate(valid_signal_data, context)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertIsNotNone(result.metadata)

    def test_signal_pipeline_with_invalid_data(self):
        """Test signal pipeline with invalid parameters"""
        invalid_signal_data = {
            'frequency': 100000.0,  # Too high
            'amplitude': 20.0,      # Too high
            'sample_rate': 1000,    # Too low for audio
            'duration': -1.0,       # Invalid
            'data': []              # Empty
        }

        context = {'signal_type': 'audio'}
        result = self.signal_pipeline.validate(invalid_signal_data, context)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

    def test_rf_signal_pipeline(self):
        """Test RF signal validation pipeline"""
        rf_pipeline = create_signal_validation_pipeline("rf")

        rf_signal_data = {
            'frequency': 2400000000.0,  # 2.4 GHz
            'amplitude': 0.1,
            'modulation': 'FSK',
            'bandwidth': 1000000.0,     # 1 MHz
            'data': [0.05, -0.05, 0.08, -0.08] * 50
        }

        context = {'signal_type': 'rf', 'band': '2.4GHz'}
        result = rf_pipeline.validate(rf_signal_data, context)

        self.assertTrue(result.is_valid)


class TestFileValidationPipeline(unittest.TestCase):
    """Test complete file validation workflows"""

    def setUp(self):
        self.file_pipeline = create_file_validation_pipeline("signal", max_size=1024*1024)

    def test_valid_signal_file_pipeline(self):
        """Test complete signal file validation"""
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("1.0\n2.0\n3.0\n4.0\n5.0\n")
            test_file = f.name

        try:
            context = {
                'file_type': 'signal',
                'expected_format': 'numeric'
            }

            result = self.file_pipeline.validate(test_file, context)

            self.assertTrue(result.is_valid)
            self.assertIsNotNone(result.metadata)
            self.assertIn('file_size', result.metadata)
            self.assertIn('extension', result.metadata)

        finally:
            os.unlink(test_file)

    def test_malicious_file_detection(self):
        """Test detection of potentially malicious files"""
        # Create file with suspicious content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("#!/bin/bash\nrm -rf /\n")  # Dangerous script
            malicious_file = f.name

        try:
            context = {'file_type': 'signal'}
            result = self.file_pipeline.validate(malicious_file, context)

            # Should detect malicious content
            self.assertFalse(result.is_valid)
            self.assertTrue(any('security' in error.message.lower() for error in result.errors))

        finally:
            os.unlink(malicious_file)

    def test_oversized_file_rejection(self):
        """Test rejection of oversized files"""
        # Create large file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("1.0\n" * 100000)  # Large file
            large_file = f.name

        try:
            small_pipeline = create_file_validation_pipeline("signal", max_size=1024)  # 1KB limit

            context = {'file_type': 'signal'}
            result = small_pipeline.validate(large_file, context)

            self.assertFalse(result.is_valid)
            self.assertTrue(any('size' in error.message.lower() for error in result.errors))

        finally:
            os.unlink(large_file)


class TestAPIValidationPipeline(unittest.TestCase):
    """Test API validation pipeline integration"""

    def setUp(self):
        self.api_pipeline = create_api_validation_pipeline("public", rate_limit=100)

    def test_valid_api_request(self):
        """Test valid API request validation"""
        request_data = {
            'method': 'POST',
            'endpoint': '/api/signals',
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': 'TestClient/1.0'
            },
            'body': {
                'identificador': 1234,
                'descripcion': 'Test signal',
                'frecuencia': 1000.0,
                'amplitud': 5.0
            }
        }

        context = {
            'client_ip': '192.168.1.100',
            'api_key': 'test_key_123'
        }

        result = self.api_pipeline.validate(request_data, context)

        self.assertTrue(result.is_valid)

    def test_malicious_api_request_detection(self):
        """Test detection of malicious API requests"""
        malicious_request = {
            'method': 'POST',
            'endpoint': '/api/signals',
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': '<script>alert("xss")</script>'
            },
            'body': {
                'identificador': 1234,
                'descripcion': "'; DROP TABLE signals; --",  # SQL injection
                'frecuencia': 1000.0,
                'amplitud': 5.0
            }
        }

        context = {'client_ip': '192.168.1.100'}
        result = self.api_pipeline.validate(malicious_request, context)

        self.assertFalse(result.is_valid)
        self.assertTrue(any('security' in error.message.lower() for error in result.errors))


class TestExceptionIntegration(unittest.TestCase):
    """Test integration between SSA-24 and SSA-23 exception systems"""

    @unittest.skipUnless(SSA24_AVAILABLE, "SSA-24 framework not available")
    def test_validation_error_conversion(self):
        """Test conversion of SSA-24 ValidationError to SSA-23"""
        ssa24_error = ValidationError(
            message="Invalid input data",
            field_name="test_field",
            invalid_value="bad_value",
            context={'test': True}
        )

        ssa23_error = handle_ssa24_exception(ssa24_error)

        self.assertIsNotNone(ssa23_error)
        self.assertEqual(ssa23_error.message, "Invalid input data")
        self.assertIn('test', ssa23_error.context)

    @unittest.skipUnless(SSA24_AVAILABLE, "SSA-24 framework not available")
    def test_security_error_conversion(self):
        """Test conversion of SSA-24 SecurityValidationError to SSA-23"""
        security_error = SecurityValidationError(
            message="XSS attempt detected",
            threat_type="xss_injection",
            context={'pattern': '<script>'}
        )

        ssa23_error = handle_ssa24_exception(security_error)

        self.assertIsNotNone(ssa23_error)
        self.assertIn('security', ssa23_error.message.lower())
        self.assertEqual(ssa23_error.context.get('threat_type'), 'xss_injection')

    @unittest.skipUnless(SSA24_AVAILABLE, "SSA-24 framework not available")
    def test_file_error_conversion(self):
        """Test conversion of SSA-24 FileValidationError to SSA-23"""
        file_error = FileValidationError(
            message="Invalid file type",
            filename="test.exe",
            context={'expected_types': ['txt', 'csv']}
        )

        ssa23_error = handle_ssa24_exception(file_error)

        self.assertIsNotNone(ssa23_error)
        self.assertIn('file', ssa23_error.message.lower())

    def test_exception_type_detection(self):
        """Test SSA-24 exception type detection"""
        if SSA24_AVAILABLE:
            ssa24_error = ValidationError("test", field_name="test")
            self.assertTrue(is_ssa24_exception(ssa24_error))

        standard_error = ValueError("standard error")
        self.assertFalse(is_ssa24_exception(standard_error))

    def test_unified_exception_handling(self):
        """Test unified exception handling for mixed exception types"""
        exceptions = [
            ValueError("Standard Python exception"),
            RuntimeError("Another standard exception")
        ]

        if SSA24_AVAILABLE:
            exceptions.extend([
                ValidationError("SSA-24 validation error", field_name="test"),
                SecurityValidationError("SSA-24 security error", threat_type="xss")
            ])

        for exc in exceptions:
            handled = handle_validation_exception(exc)
            self.assertIsNotNone(handled)


class TestCrossLayerIntegration(unittest.TestCase):
    """Test integration across presentation, domain, and application layers"""

    def test_form_to_domain_validation_flow(self):
        """Test validation flow from web form to domain layer"""
        # Simulate form data
        form_data = {
            'identificador': 1234,
            'descripcion': 'Integration test signal',
            'fecha': '2024-01-15',
            'frecuencia': 1000.0,
            'amplitud': 5.0,
            'archivo_configuracion': 'config.json'
        }

        # Test string validation (presentation layer)
        string_validator = StringInputValidator(max_length=200)
        desc_result = string_validator.validate(form_data['descripcion'])

        self.assertTrue(desc_result.is_valid)

        # Test signal parameter validation (domain layer)
        freq_validator = SignalParameterValidator('frequency')
        freq_result = freq_validator.validate(form_data['frecuencia'])

        self.assertTrue(freq_result.is_valid)

        # Test file validation (infrastructure layer)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'setting': 'value'}, f)
            config_file = f.name

        try:
            file_validator = FileTypeValidator(allowed_extensions=['json'])
            file_result = file_validator.validate(config_file)

            self.assertTrue(file_result.is_valid)

        finally:
            os.unlink(config_file)

    def test_error_propagation_across_layers(self):
        """Test error propagation from domain to presentation layer"""
        # Create invalid signal parameters
        invalid_data = {
            'frequency': -1000.0,  # Invalid frequency
            'amplitude': 50.0      # Too high amplitude
        }

        # Domain layer validation should fail
        freq_validator = SignalParameterValidator('frequency')
        freq_result = freq_validator.validate(invalid_data['frequency'])

        self.assertFalse(freq_result.is_valid)

        # Convert to SSA-23 exception for presentation layer
        if freq_result.errors:
            ssa24_error = SignalValidationError(
                message=freq_result.errors[0].message,
                signal_parameter='frequency',
                actual_value=invalid_data['frequency']
            )

            if SSA24_AVAILABLE:
                ssa23_error = handle_ssa24_exception(ssa24_error)
                self.assertIsNotNone(ssa23_error)
                self.assertIsNotNone(ssa23_error.user_message)

    @patch('04_dominio.adquisicion.adquisidor.logger')
    def test_adquisidor_integration(self, mock_logger):
        """Test AdquisidorArchivo integration with SSA-24 validation"""
        # Create test signal file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(10):
                f.write(f"{i * 0.1}\n")
            test_file = f.name

        try:
            # Mock signal object
            mock_signal = Mock()
            mock_signal.tamanio = 10
            mock_signal.poner_valor = Mock()

            # Test file path validation
            path_validator = StringInputValidator(
                max_length=500,
                allowed_pattern=r'^[a-zA-Z0-9\s\-_.\\/]+$'
            )
            path_result = path_validator.validate(test_file)

            self.assertTrue(path_result.is_valid)

            # Test file type validation
            file_validator = FileTypeValidator(
                allowed_extensions=['txt', 'csv', 'dat'],
                strict_mime_check=False
            )
            file_result = file_validator.validate(test_file)

            self.assertTrue(file_result.is_valid)

        finally:
            os.unlink(test_file)


class TestValidationPipelineOrchestration(unittest.TestCase):
    """Test orchestration of multiple validation pipelines"""

    def test_sequential_pipeline_execution(self):
        """Test sequential execution of multiple validation stages"""
        # Create multi-stage pipeline
        pipeline = ValidationPipeline(
            execution_mode="fail_fast",
            stage_config={
                'PRE_VALIDATION': True,
                'TYPE_VALIDATION': True,
                'BUSINESS_VALIDATION': True,
                'POST_VALIDATION': True
            }
        )

        # Add validators to different stages
        string_validator = StringInputValidator(max_length=100)
        signal_validator = SignalParameterValidator('frequency')

        pipeline.add_validator(string_validator, stage='PRE_VALIDATION')
        pipeline.add_validator(signal_validator, stage='BUSINESS_VALIDATION')

        # Test with valid data
        test_data = {
            'description': 'Test signal',
            'frequency': 1000.0
        }

        context = {'validation_type': 'sequential_test'}
        result = pipeline.validate(test_data, context)

        self.assertTrue(result.is_valid)

    def test_parallel_pipeline_execution(self):
        """Test parallel execution of validation pipelines"""
        # Create parallel pipeline
        pipeline = ValidationPipeline(
            execution_mode="collect_all",
            parallel_execution=True
        )

        # Add multiple validators
        validators = [
            StringInputValidator(max_length=50),
            StringInputValidator(min_length=5),
            StringInputValidator(allowed_pattern=r'^[a-zA-Z0-9\s]+$')
        ]

        for validator in validators:
            pipeline.add_validator(validator)

        # Test with data that should pass all validators
        test_data = "Valid test string 123"
        context = {'test_type': 'parallel'}

        result = pipeline.validate(test_data, context)

        self.assertTrue(result.is_valid)

    def test_pipeline_with_mixed_results(self):
        """Test pipeline with some passing and some failing validators"""
        pipeline = ValidationPipeline(execution_mode="collect_all")

        # Add validators with different requirements
        pipeline.add_validator(StringInputValidator(max_length=100))  # Should pass
        pipeline.add_validator(StringInputValidator(min_length=200))  # Should fail

        test_data = "Medium length string for testing"
        result = pipeline.validate(test_data, {})

        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)  # One validator should fail


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestSignalValidationPipeline,
        TestFileValidationPipeline,
        TestAPIValidationPipeline,
        TestExceptionIntegration,
        TestCrossLayerIntegration,
        TestValidationPipelineOrchestration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )

    print("=" * 70)
    print("SSA-24 Input Validation Framework - Integration Tests")
    print("=" * 70)
    print("Testing cross-layer validation workflows and component integration")
    print()

    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("Integration Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print(f"\nFailures: {len(result.failures)}")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split(chr(10))[-2]}")

    if result.errors:
        print(f"\nErrors: {len(result.errors)}")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(chr(10))[-2]}")

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)