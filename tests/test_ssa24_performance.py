#!/usr/bin/env python3
"""
Performance Tests for SSA-24 Input Validation Framework
Tests performance characteristics, scalability, and resource usage
"""

import unittest
import time
import sys
import os
import tempfile
import threading
import memory_profiler
import gc
import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from unittest.mock import Mock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aplicacion.validation import (
    ValidationPipeline,
    StringInputValidator,
    SignalParameterValidator,
    SignalDataValidator,
    FileTypeValidator,
    FileContentValidator,
    SanitizationEngine,
    SanitizationLevel,
    create_signal_validation_pipeline,
    create_file_validation_pipeline,
    create_api_validation_pipeline
)


class PerformanceTestCase(unittest.TestCase):
    """Base class for performance tests with timing utilities"""

    def setUp(self):
        self.performance_data = {}
        gc.collect()  # Clean up before tests

    def time_operation(self, operation, iterations=1000, name="operation"):
        """Time an operation and record statistics"""
        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            operation()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        self.performance_data[name] = {
            'min': min(times),
            'max': max(times),
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'total_time': sum(times),
            'iterations': iterations,
            'ops_per_second': iterations / sum(times)
        }

        return self.performance_data[name]

    def assert_performance_threshold(self, operation_name, max_mean_time=None, min_ops_per_second=None):
        """Assert performance meets thresholds"""
        data = self.performance_data.get(operation_name)
        self.assertIsNotNone(data, f"No performance data for {operation_name}")

        if max_mean_time:
            self.assertLessEqual(data['mean'], max_mean_time,
                               f"{operation_name} mean time {data['mean']:.6f}s exceeds threshold {max_mean_time}s")

        if min_ops_per_second:
            self.assertGreaterEqual(data['ops_per_second'], min_ops_per_second,
                                  f"{operation_name} {data['ops_per_second']:.0f} ops/s below threshold {min_ops_per_second}")


class TestValidatorPerformance(PerformanceTestCase):
    """Test individual validator performance"""

    def test_string_validator_performance(self):
        """Test StringInputValidator performance with various input sizes"""
        validator = StringInputValidator(max_length=10000)

        # Test different input sizes
        test_inputs = [
            ("small", "Hello World"),
            ("medium", "A" * 1000),
            ("large", "B" * 5000),
            ("max_size", "C" * 10000)
        ]

        for size_name, test_input in test_inputs:
            operation = lambda: validator.validate(test_input)
            self.time_operation(operation, iterations=1000, name=f"string_validation_{size_name}")

        # Performance assertions
        self.assert_performance_threshold("string_validation_small", max_mean_time=0.001)
        self.assert_performance_threshold("string_validation_medium", max_mean_time=0.005)
        self.assert_performance_threshold("string_validation_large", max_mean_time=0.01)

    def test_signal_parameter_validator_performance(self):
        """Test SignalParameterValidator performance"""
        validator = SignalParameterValidator('frequency')

        # Test with valid frequency
        operation = lambda: validator.validate(1000.0)
        self.time_operation(operation, iterations=5000, name="signal_param_validation")

        self.assert_performance_threshold("signal_param_validation", max_mean_time=0.0005)

    def test_signal_data_validator_performance(self):
        """Test SignalDataValidator performance with large datasets"""
        validator = SignalDataValidator(max_length=100000, check_anomalies=True)

        # Test different data sizes
        data_sizes = [100, 1000, 10000, 50000]

        for size in data_sizes:
            test_data = [float(i % 100) for i in range(size)]
            operation = lambda: validator.validate(test_data)
            self.time_operation(operation, iterations=10, name=f"signal_data_{size}")

        # Ensure linear or sub-linear scaling
        small_time = self.performance_data['signal_data_100']['mean']
        large_time = self.performance_data['signal_data_10000']['mean']

        # Should not scale worse than O(n²)
        scaling_factor = large_time / small_time
        size_ratio = 10000 / 100
        self.assertLess(scaling_factor, size_ratio * size_ratio,
                       "Signal data validation scaling is worse than O(n²)")

    def test_file_validator_performance(self):
        """Test file validation performance"""
        file_validator = FileTypeValidator(allowed_extensions=['txt'])
        content_validator = FileContentValidator(scan_content=True)

        # Create test files of different sizes
        file_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB

        for size in file_sizes:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("A" * size)
                test_file = f.name

            try:
                # Test file type validation
                operation = lambda: file_validator.validate(test_file)
                self.time_operation(operation, iterations=100, name=f"file_type_{size}")

                # Test content validation
                operation = lambda: content_validator.validate(test_file)
                self.time_operation(operation, iterations=10, name=f"file_content_{size}")

            finally:
                os.unlink(test_file)

        # File type validation should be very fast
        self.assert_performance_threshold("file_type_1024", max_mean_time=0.001)


class TestSanitizationPerformance(PerformanceTestCase):
    """Test sanitization engine performance"""

    def test_sanitization_performance_by_level(self):
        """Test sanitization performance at different security levels"""
        test_input = "<script>alert('xss')</script>" + "Safe content " * 100

        levels = [
            (SanitizationLevel.BASIC, "basic"),
            (SanitizationLevel.STANDARD, "standard"),
            (SanitizationLevel.STRICT, "strict")
        ]

        for level, level_name in levels:
            sanitizer = SanitizationEngine(level)
            operation = lambda: sanitizer.sanitize(test_input)
            self.time_operation(operation, iterations=1000, name=f"sanitization_{level_name}")

        # Basic should be fastest, strict should still be reasonable
        self.assert_performance_threshold("sanitization_basic", max_mean_time=0.001)
        self.assert_performance_threshold("sanitization_strict", max_mean_time=0.005)

    def test_sanitization_scaling(self):
        """Test how sanitization scales with input size"""
        sanitizer = SanitizationEngine(SanitizationLevel.STANDARD)

        input_sizes = [100, 1000, 10000]
        base_content = "<script>alert('test')</script>Normal content with numbers 123 and symbols !@#$%"

        for size in input_sizes:
            # Create input of specified size
            multiplier = size // len(base_content) + 1
            test_input = base_content * multiplier
            test_input = test_input[:size]  # Trim to exact size

            operation = lambda: sanitizer.sanitize(test_input)
            self.time_operation(operation, iterations=100, name=f"sanitization_scale_{size}")

        # Should scale reasonably (not worse than quadratic)
        small_time = self.performance_data['sanitization_scale_100']['mean']
        large_time = self.performance_data['sanitization_scale_10000']['mean']

        scaling_factor = large_time / small_time
        size_ratio = 10000 / 100

        self.assertLess(scaling_factor, size_ratio * 2,
                       "Sanitization scaling is worse than expected")


class TestPipelinePerformance(PerformanceTestCase):
    """Test validation pipeline performance"""

    def test_sequential_pipeline_performance(self):
        """Test sequential pipeline execution performance"""
        pipeline = ValidationPipeline(execution_mode="fail_fast")

        # Add multiple validators
        validators = [
            StringInputValidator(max_length=1000),
            StringInputValidator(min_length=1),
            StringInputValidator(allowed_pattern=r'^[a-zA-Z0-9\s]+$')
        ]

        for validator in validators:
            pipeline.add_validator(validator)

        test_input = "Valid test input 123"
        operation = lambda: pipeline.validate(test_input, {})
        self.time_operation(operation, iterations=1000, name="sequential_pipeline")

        self.assert_performance_threshold("sequential_pipeline", max_mean_time=0.002)

    def test_parallel_pipeline_performance(self):
        """Test parallel pipeline execution performance"""
        pipeline = ValidationPipeline(
            execution_mode="collect_all",
            parallel_execution=True
        )

        # Add validators that can run in parallel
        validators = [
            StringInputValidator(max_length=1000),
            StringInputValidator(min_length=1),
            StringInputValidator(allowed_pattern=r'^[a-zA-Z0-9\s]+$'),
            StringInputValidator(max_length=500)  # Additional validator
        ]

        for validator in validators:
            pipeline.add_validator(validator)

        test_input = "Valid test input for parallel processing"
        operation = lambda: pipeline.validate(test_input, {})
        self.time_operation(operation, iterations=100, name="parallel_pipeline")

        # Parallel should be competitive with sequential for this case
        # (overhead might make it slower for simple validators)
        self.assert_performance_threshold("parallel_pipeline", max_mean_time=0.01)

    def test_specialized_pipeline_performance(self):
        """Test performance of specialized pipelines"""
        # Test signal validation pipeline
        signal_pipeline = create_signal_validation_pipeline("audio")

        signal_data = {
            'frequency': 440.0,
            'amplitude': 1.0,
            'sample_rate': 44100,
            'data': [0.1, 0.2, -0.1, -0.2] * 25  # 100 samples
        }

        operation = lambda: signal_pipeline.validate(signal_data, {'signal_type': 'audio'})
        self.time_operation(operation, iterations=100, name="signal_pipeline")

        # Test API validation pipeline
        api_pipeline = create_api_validation_pipeline("public")

        api_data = {
            'method': 'GET',
            'endpoint': '/api/test',
            'headers': {'User-Agent': 'TestClient'},
            'client_ip': '192.168.1.1'
        }

        operation = lambda: api_pipeline.validate(api_data, {'client_ip': '192.168.1.1'})
        self.time_operation(operation, iterations=100, name="api_pipeline")

        # Specialized pipelines should complete within reasonable time
        self.assert_performance_threshold("signal_pipeline", max_mean_time=0.01)
        self.assert_performance_threshold("api_pipeline", max_mean_time=0.01)


class TestConcurrencyPerformance(PerformanceTestCase):
    """Test performance under concurrent load"""

    def test_thread_safety_performance(self):
        """Test performance under multi-threaded access"""
        validator = StringInputValidator(max_length=1000)
        test_input = "Thread safety test input"

        def validation_worker():
            for _ in range(100):
                result = validator.validate(test_input)
                self.assertTrue(result.is_valid)

        # Test with multiple threads
        thread_counts = [1, 2, 4, 8]

        for thread_count in thread_counts:
            start_time = time.perf_counter()

            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(validation_worker) for _ in range(thread_count)]
                for future in futures:
                    future.result()

            end_time = time.perf_counter()

            total_validations = thread_count * 100
            total_time = end_time - start_time

            self.performance_data[f"concurrent_{thread_count}_threads"] = {
                'total_time': total_time,
                'total_validations': total_validations,
                'validations_per_second': total_validations / total_time,
                'thread_count': thread_count
            }

        # Should handle concurrent access without significant degradation
        single_thread_rate = self.performance_data['concurrent_1_threads']['validations_per_second']
        multi_thread_rate = self.performance_data['concurrent_4_threads']['validations_per_second']

        # Multi-threaded should be at least 50% of single-threaded rate per thread
        # (accounting for overhead and contention)
        min_expected_rate = single_thread_rate * 0.5
        self.assertGreater(multi_thread_rate, min_expected_rate,
                          "Multi-threaded performance degradation is too high")

    def test_memory_usage_under_load(self):
        """Test memory usage characteristics under load"""
        validator = StringInputValidator(max_length=10000)

        # Large input that might cause memory issues
        large_input = "A" * 9000

        # Record initial memory
        initial_memory = memory_profiler.memory_usage()[0]

        # Perform many validations
        for _ in range(1000):
            result = validator.validate(large_input)
            self.assertTrue(result.is_valid)

        # Record final memory
        final_memory = memory_profiler.memory_usage()[0]
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB for this test)
        self.assertLess(memory_increase, 50.0,
                       f"Memory usage increased by {memory_increase:.1f}MB, which may indicate a memory leak")

    def test_pipeline_scalability(self):
        """Test how pipelines scale with number of validators"""
        validator_counts = [1, 5, 10, 20]
        test_input = "Scalability test input"

        for count in validator_counts:
            pipeline = ValidationPipeline(execution_mode="collect_all")

            # Add specified number of validators
            for i in range(count):
                validator = StringInputValidator(max_length=1000 + i)  # Slight variation
                pipeline.add_validator(validator)

            operation = lambda: pipeline.validate(test_input, {})
            self.time_operation(operation, iterations=100, name=f"pipeline_scale_{count}")

        # Scaling should be roughly linear
        single_validator_time = self.performance_data['pipeline_scale_1']['mean']
        twenty_validator_time = self.performance_data['pipeline_scale_20']['mean']

        scaling_factor = twenty_validator_time / single_validator_time

        # Should scale no worse than linearly (with some overhead tolerance)
        self.assertLess(scaling_factor, 25,  # 20 validators + 25% overhead tolerance
                       f"Pipeline scaling factor {scaling_factor:.1f} indicates poor scalability")


class TestRealWorldScenarios(PerformanceTestCase):
    """Test performance in realistic usage scenarios"""

    def test_web_form_validation_scenario(self):
        """Test performance for typical web form validation"""
        # Simulate typical web form data
        form_data = {
            'identificador': 1234,
            'descripcion': 'Signal from sensor array #42 located in building A',
            'fecha': '2024-01-15',
            'frecuencia': 1000.0,
            'amplitud': 5.0,
            'email': 'user@example.com',
            'telefono': '+1-555-123-4567'
        }

        validators = {
            'identificador': StringInputValidator(max_length=10, allowed_pattern=r'^\d+$'),
            'descripcion': StringInputValidator(max_length=200),
            'fecha': StringInputValidator(max_length=20, allowed_pattern=r'^\d{4}-\d{2}-\d{2}$'),
            'frecuencia': SignalParameterValidator('frequency'),
            'amplitud': SignalParameterValidator('amplitude'),
            'email': StringInputValidator(max_length=100, allowed_pattern=r'^[^@]+@[^@]+\.[^@]+$'),
            'telefono': StringInputValidator(max_length=20, allowed_pattern=r'^[+\-\d\s()]+$')
        }

        def validate_form():
            for field, value in form_data.items():
                if field in validators:
                    result = validators[field].validate(value)
                    if not result.is_valid:
                        return False
            return True

        self.time_operation(validate_form, iterations=1000, name="web_form_validation")

        # Web form validation should be very fast for good user experience
        self.assert_performance_threshold("web_form_validation", max_mean_time=0.005)

    def test_file_upload_scenario(self):
        """Test performance for file upload validation"""
        # Create test files of various sizes
        file_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB

        file_pipeline = create_file_validation_pipeline("signal", max_size=1024*1024)

        for size in file_sizes:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                # Write numeric data simulating signal file
                for i in range(size // 10):  # Approximate size
                    f.write(f"{i * 0.1}\n")
                test_file = f.name

            try:
                operation = lambda: file_pipeline.validate(test_file, {'file_type': 'signal'})
                self.time_operation(operation, iterations=10, name=f"file_upload_{size}")

            finally:
                os.unlink(test_file)

        # File upload validation should complete within reasonable time
        self.assert_performance_threshold("file_upload_1024", max_mean_time=0.01)
        self.assert_performance_threshold("file_upload_102400", max_mean_time=0.1)

    def test_api_request_scenario(self):
        """Test performance for API request validation"""
        api_pipeline = create_api_validation_pipeline("public", rate_limit=1000)

        # Typical API request
        api_request = {
            'method': 'POST',
            'endpoint': '/api/signals',
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': 'Mobile App v1.2.3',
                'Authorization': 'Bearer jwt_token_here'
            },
            'body': {
                'identificador': 5678,
                'descripcion': 'Mobile sensor data',
                'frecuencia': 2400.0,
                'amplitud': 3.2,
                'timestamp': '2024-01-15T10:30:00Z'
            },
            'client_ip': '192.168.1.100'
        }

        operation = lambda: api_pipeline.validate(api_request, {'client_ip': '192.168.1.100'})
        self.time_operation(operation, iterations=1000, name="api_request_validation")

        # API validation should be fast to minimize latency
        self.assert_performance_threshold("api_request_validation", max_mean_time=0.002)
        self.assert_performance_threshold("api_request_validation", min_ops_per_second=500)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()

    # Add performance test cases
    performance_test_classes = [
        TestValidatorPerformance,
        TestSanitizationPerformance,
        TestPipelinePerformance,
        TestConcurrencyPerformance,
        TestRealWorldScenarios
    ]

    for test_class in performance_test_classes:
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
    print("SSA-24 Input Validation Framework - Performance Tests")
    print("=" * 70)
    print("Testing performance characteristics and scalability")
    print()

    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # Print performance summary
    print()
    print("=" * 70)
    print("Performance Test Summary")
    print("=" * 70)
    print(f"Performance tests run: {result.testsRun}")
    print(f"Total execution time: {end_time - start_time:.2f}s")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Performance success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    # Performance categories
    performance_categories = [
        "Individual Validator Performance",
        "Sanitization Performance",
        "Pipeline Performance",
        "Concurrency Performance",
        "Real-world Scenarios"
    ]

    print(f"\nPerformance categories tested: {len(performance_categories)}")
    for category in performance_categories:
        print(f"  ⚡ {category}")

    if result.failures:
        print(f"\nPerformance failures: {len(result.failures)}")
        for test, traceback in result.failures:
            print(f"  ⚠️  {test}")

    if result.errors:
        print(f"\nPerformance errors: {len(result.errors)}")
        for test, traceback in result.errors:
            print(f"  ❌ {test}")

    # Performance assessment
    if result.wasSuccessful():
        print("\n⚡ Performance validation: PASSED")
        print("   All performance thresholds met")
    else:
        print("\n⚠️  Performance validation: ISSUES DETECTED")
        print("   Some performance thresholds may need optimization")

    print("\nNote: Performance results may vary based on system hardware and load")

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)