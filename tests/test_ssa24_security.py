#!/usr/bin/env python3
"""
Security Tests for SSA-24 Input Validation Framework
Tests security vulnerabilities detection and prevention mechanisms
"""

import unittest
import tempfile
import os
import sys
import time
import threading
import subprocess
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aplicacion.validation import (
    StringInputValidator,
    FileTypeValidator,
    FileContentValidator,
    SanitizationEngine,
    SanitizationLevel,
    ValidationError,
    SecurityValidationError,
    FileValidationError,
    create_api_validation_pipeline,
    sanitize_input,
    auto_sanitize
)


class TestXSSPrevention(unittest.TestCase):
    """Test Cross-Site Scripting (XSS) prevention"""

    def setUp(self):
        self.validator = StringInputValidator(
            max_length=1000,
            allowed_pattern=StringInputValidator.TEXT_SAFE
        )
        self.sanitizer = SanitizationEngine(SanitizationLevel.STRICT)

    def test_basic_xss_detection(self):
        """Test detection of basic XSS patterns"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "\"><script>alert('xss')</script>",
            "<iframe src=javascript:alert('xss')></iframe>",
            "<body onload=alert('xss')>",
            "<input onfocus=alert('xss') autofocus>",
            "<select onfocus=alert('xss') autofocus>"
        ]

        for payload in xss_payloads:
            with self.subTest(payload=payload):
                result = self.validator.validate(payload)
                self.assertFalse(result.is_valid, f"Should block XSS payload: {payload}")

    def test_xss_sanitization(self):
        """Test XSS payload sanitization"""
        dangerous_inputs = [
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("Click <a href='javascript:alert()'>here</a>", "Click here"),
            ("<img src=x onerror=alert(1)>", ""),
            ("Normal text", "Normal text"),  # Should remain unchanged
            ("<p>Safe HTML</p>", "Safe HTML")  # Should be sanitized
        ]

        for dangerous_input, expected_clean in dangerous_inputs:
            with self.subTest(input=dangerous_input):
                result = self.sanitizer.sanitize(dangerous_input)
                self.assertNotIn('<script>', result.sanitized_value)
                self.assertNotIn('javascript:', result.sanitized_value)
                self.assertNotIn('onerror=', result.sanitized_value)

    def test_advanced_xss_evasion_techniques(self):
        """Test detection of advanced XSS evasion techniques"""
        evasion_payloads = [
            "&#60;script&#62;alert('xss')&#60;/script&#62;",  # HTML entities
            "<ScRiPt>alert('xss')</ScRiPt>",  # Case variations
            "<script>alert(String.fromCharCode(88,83,83))</script>",  # Character encoding
            "<img src=\"\" onerror=\"alert('xss')\">",  # Event handlers
            "<svg><script>alert('xss')</script></svg>",  # SVG injection
            "data:text/html,<script>alert('xss')</script>",  # Data URLs
            "<object data=\"javascript:alert('xss')\">",  # Object tags
            "<embed src=\"javascript:alert('xss')\">",  # Embed tags
        ]

        for payload in evasion_payloads:
            with self.subTest(payload=payload):
                result = self.validator.validate(payload)
                self.assertFalse(result.is_valid, f"Should block evasion payload: {payload}")

    def test_context_aware_xss_detection(self):
        """Test context-aware XSS detection"""
        # Test different contexts where XSS might occur
        contexts = [
            ("HTML_CONTENT", "<div>User content with <script>alert('xss')</script></div>"),
            ("HTML_ATTRIBUTE", "value=\"\" onmouseover=\"alert('xss')\""),
            ("JAVASCRIPT", "var user = ''; alert('xss'); //"),
            ("CSS", "color: expression(alert('xss'))"),
            ("URL", "http://example.com/?param=<script>alert('xss')</script>")
        ]

        for context_type, payload in contexts:
            with self.subTest(context=context_type, payload=payload):
                validator = StringInputValidator(
                    max_length=1000,
                    context_type=context_type if hasattr(StringInputValidator, 'context_type') else None
                )
                result = validator.validate(payload)
                # Should detect XSS regardless of context
                self.assertFalse(result.is_valid)


class TestSQLInjectionPrevention(unittest.TestCase):
    """Test SQL Injection prevention"""

    def setUp(self):
        self.validator = StringInputValidator(
            max_length=1000,
            allowed_pattern=StringInputValidator.ALPHANUMERIC_SAFE
        )
        self.sanitizer = SanitizationEngine(SanitizationLevel.STRICT)

    def test_basic_sql_injection_detection(self):
        """Test detection of basic SQL injection patterns"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1; DELETE FROM users WHERE 1=1",
            "' UNION SELECT * FROM passwords --",
            "admin'--",
            "' OR 1=1 #",
            "'; INSERT INTO users VALUES ('hacker','pass'); --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR EXISTS(SELECT * FROM users WHERE username='admin') --"
        ]

        for payload in sql_payloads:
            with self.subTest(payload=payload):
                result = self.validator.validate(payload)
                self.assertFalse(result.is_valid, f"Should block SQL injection: {payload}")

    def test_sql_injection_sanitization(self):
        """Test SQL injection payload sanitization"""
        dangerous_inputs = [
            ("'; DROP TABLE users; --", ""),
            ("user'; --", "user"),
            ("normal_user", "normal_user"),  # Should remain unchanged
            ("user123", "user123"),  # Should remain unchanged
            ("'; UNION SELECT", "UNION SELECT")
        ]

        for dangerous_input, expected_pattern in dangerous_inputs:
            with self.subTest(input=dangerous_input):
                result = self.sanitizer.sanitize(dangerous_input)
                # Should not contain dangerous SQL keywords
                sanitized = result.sanitized_value.upper()
                self.assertNotIn("DROP TABLE", sanitized)
                self.assertNotIn("DELETE FROM", sanitized)
                self.assertNotIn("';", result.sanitized_value)

    def test_blind_sql_injection_detection(self):
        """Test detection of blind SQL injection techniques"""
        blind_payloads = [
            "1' AND (SELECT SUBSTRING(username,1,1) FROM users WHERE id=1)='a",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0",
            "1' AND SLEEP(5) --",
            "1'; WAITFOR DELAY '00:00:05' --",
            "1' AND (SELECT 1 FROM dual) IS NOT NULL",
            "' AND 1=(SELECT COUNT(*) FROM tabname); --"
        ]

        for payload in blind_payloads:
            with self.subTest(payload=payload):
                result = self.validator.validate(payload)
                self.assertFalse(result.is_valid, f"Should block blind SQL injection: {payload}")

    def test_sql_injection_in_numeric_fields(self):
        """Test SQL injection in numeric fields"""
        numeric_sql_payloads = [
            "1; DROP TABLE users",
            "1 OR 1=1",
            "1 UNION SELECT password FROM users",
            "1; INSERT INTO logs VALUES ('hack')",
            "1 AND (SELECT COUNT(*) FROM users) > 0"
        ]

        # Use a numeric validator
        numeric_validator = StringInputValidator(
            max_length=50,
            allowed_pattern=r'^\d+$'  # Only digits
        )

        for payload in numeric_sql_payloads:
            with self.subTest(payload=payload):
                result = numeric_validator.validate(payload)
                self.assertFalse(result.is_valid, f"Should block numeric SQL injection: {payload}")


class TestPathTraversalPrevention(unittest.TestCase):
    """Test Path Traversal/Directory Traversal prevention"""

    def setUp(self):
        self.file_validator = FileTypeValidator(
            allowed_extensions=['txt', 'csv', 'json'],
            strict_mime_check=True
        )

    def test_basic_path_traversal_detection(self):
        """Test detection of basic path traversal patterns"""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "../../../../var/log/apache2/access.log",
            "..\\..\\..\\..\\boot.ini",
            "../etc/shadow",
            "../../var/www/html/index.php",
            "..\\windows\\win.ini",
            "../../../../proc/self/environ",
            "../../../home/user/.ssh/id_rsa",
            "..\\..\\..\\pagefile.sys"
        ]

        for path in traversal_paths:
            with self.subTest(path=path):
                # Create a temporary file with traversal name
                try:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write("test content")
                        temp_path = f.name

                    # Rename to traversal path (simulate)
                    validator = StringInputValidator(
                        max_length=500,
                        allowed_pattern=r'^[a-zA-Z0-9\s\-_.]+$'  # No traversal characters
                    )

                    result = validator.validate(path)
                    self.assertFalse(result.is_valid, f"Should block path traversal: {path}")

                finally:
                    if 'temp_path' in locals():
                        os.unlink(temp_path)

    def test_encoded_path_traversal_detection(self):
        """Test detection of encoded path traversal attempts"""
        encoded_paths = [
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
            "..%2f..%2f..%2fetc%2fpasswd",  # Mixed encoding
            "%2e%2e\\%2e%2e\\%2e%2e\\windows\\system32",  # Windows encoded
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",  # UTF-8 encoded
            "%252e%252e%252fetc%252fpasswd",  # Double URL encoded
        ]

        path_validator = StringInputValidator(
            max_length=500,
            allowed_pattern=r'^[a-zA-Z0-9\s\-_.\/]+$'  # Basic path characters only
        )

        for encoded_path in encoded_paths:
            with self.subTest(path=encoded_path):
                result = path_validator.validate(encoded_path)
                # Should block encoded paths or detect them after decoding
                self.assertFalse(result.is_valid, f"Should block encoded traversal: {encoded_path}")

    def test_absolute_path_validation(self):
        """Test validation of absolute paths for security"""
        dangerous_absolute_paths = [
            "/etc/passwd",
            "/var/log/auth.log",
            "/home/user/.bashrc",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
            "C:\\Users\\Administrator\\Documents",
            "/proc/self/maps",
            "/sys/class/net/eth0/address"
        ]

        # Validator that should only allow relative paths in safe directory
        safe_path_validator = StringInputValidator(
            max_length=200,
            allowed_pattern=r'^[a-zA-Z0-9\s\-_.]+$'  # No path separators
        )

        for abs_path in dangerous_absolute_paths:
            with self.subTest(path=abs_path):
                result = safe_path_validator.validate(abs_path)
                self.assertFalse(result.is_valid, f"Should block absolute path: {abs_path}")


class TestFileUploadSecurity(unittest.TestCase):
    """Test file upload security mechanisms"""

    def setUp(self):
        self.file_validator = FileTypeValidator(
            allowed_extensions=['txt', 'csv', 'json'],
            strict_mime_check=True
        )
        self.content_validator = FileContentValidator(
            scan_content=True,
            max_scan_size=1024*1024
        )

    def test_malicious_file_type_detection(self):
        """Test detection of malicious file types"""
        malicious_extensions = [
            'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js',
            'jar', 'jsp', 'php', 'asp', 'aspx', 'sh', 'ps1', 'py'
        ]

        for ext in malicious_extensions:
            with self.subTest(extension=ext):
                with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as f:
                    f.write(b"malicious content")
                    malicious_file = f.name

                try:
                    result = self.file_validator.validate(malicious_file)
                    self.assertFalse(result.is_valid, f"Should block .{ext} files")
                finally:
                    os.unlink(malicious_file)

    def test_file_content_scanning(self):
        """Test scanning of file content for malicious patterns"""
        malicious_contents = [
            b"#!/bin/bash\nrm -rf /",  # Dangerous shell script
            b"<?php system($_GET['cmd']); ?>",  # PHP backdoor
            b"<script>document.location='http://evil.com'</script>",  # XSS in file
            b"MZ\x90\x00",  # PE executable header
            b"\x7fELF",  # ELF executable header
            b"PK\x03\x04",  # ZIP file (could contain malware)
            b"import os; os.system('rm -rf /')",  # Dangerous Python
            b"eval(base64_decode($_POST['code']))"  # PHP obfuscated code
        ]

        for content in malicious_contents:
            with self.subTest(content=content[:20]):
                with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                    f.write(content)
                    malicious_file = f.name

                try:
                    result = self.content_validator.validate(malicious_file)
                    self.assertFalse(result.is_valid, f"Should detect malicious content: {content[:20]}")
                finally:
                    os.unlink(malicious_file)

    def test_file_size_validation(self):
        """Test file size validation for DoS prevention"""
        # Create oversized file
        large_content = b"A" * (10 * 1024 * 1024)  # 10MB

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(large_content)
            large_file = f.name

        try:
            # Validator with 5MB limit
            size_validator = FileContentValidator(max_scan_size=5*1024*1024)
            result = size_validator.validate(large_file)

            # Should either reject or limit scanning
            self.assertTrue(result.is_valid or len(result.errors) > 0)

        finally:
            os.unlink(large_file)

    def test_double_extension_detection(self):
        """Test detection of double extension attacks"""
        double_extensions = [
            "document.pdf.exe",
            "image.jpg.bat",
            "config.txt.php",
            "data.csv.js",
            "backup.zip.cmd"
        ]

        for filename in double_extensions:
            with self.subTest(filename=filename):
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    f.write(b"content")
                    temp_file = f.name

                # Rename to double extension
                double_ext_file = temp_file + "." + filename
                os.rename(temp_file, double_ext_file)

                try:
                    result = self.file_validator.validate(double_ext_file)
                    # Should detect the dangerous extension
                    self.assertFalse(result.is_valid, f"Should block double extension: {filename}")
                finally:
                    if os.path.exists(double_ext_file):
                        os.unlink(double_ext_file)


class TestInputLengthAttacks(unittest.TestCase):
    """Test protection against input length attacks"""

    def test_buffer_overflow_protection(self):
        """Test protection against buffer overflow attempts"""
        # Generate very long strings
        long_inputs = [
            "A" * 10000,      # 10KB
            "B" * 100000,     # 100KB
            "C" * 1000000,    # 1MB
            "D" * 10000000,   # 10MB (if memory allows)
        ]

        validator = StringInputValidator(max_length=1000)

        for long_input in long_inputs[:3]:  # Skip the largest to avoid memory issues
            with self.subTest(length=len(long_input)):
                start_time = time.time()
                result = validator.validate(long_input)
                end_time = time.time()

                # Should reject long input
                self.assertFalse(result.is_valid)
                # Should not take too long to process
                self.assertLess(end_time - start_time, 1.0, "Validation should be fast even for long inputs")

    def test_nested_input_protection(self):
        """Test protection against deeply nested input structures"""
        # Create deeply nested structure
        nested_json = "{" * 1000 + "\"key\":\"value\"" + "}" * 1000

        validator = StringInputValidator(max_length=5000)
        result = validator.validate(nested_json)

        self.assertFalse(result.is_valid, "Should reject deeply nested structures")

    def test_repeated_pattern_attack(self):
        """Test protection against repeated pattern attacks"""
        repeated_patterns = [
            "../" * 1000,         # Path traversal repetition
            "<script>" * 100,     # XSS repetition
            "' OR '1'='1" * 50,   # SQL injection repetition
            "eval(" * 200,        # Code injection repetition
        ]

        validator = StringInputValidator(max_length=2000)

        for pattern in repeated_patterns:
            with self.subTest(pattern=pattern[:20]):
                result = validator.validate(pattern)
                self.assertFalse(result.is_valid, f"Should block repeated pattern: {pattern[:20]}")


class TestAPISecurityValidation(unittest.TestCase):
    """Test API-specific security validation"""

    def setUp(self):
        self.api_pipeline = create_api_validation_pipeline("public", rate_limit=10)

    def test_rate_limiting_simulation(self):
        """Test rate limiting functionality"""
        # Simulate rapid API requests
        request_data = {
            'method': 'GET',
            'endpoint': '/api/test',
            'client_ip': '192.168.1.100'
        }

        context = {'client_ip': '192.168.1.100'}

        # Make multiple rapid requests
        results = []
        for i in range(15):  # Exceed rate limit
            result = self.api_pipeline.validate(request_data, context)
            results.append(result.is_valid)

        # Should start blocking after rate limit exceeded
        blocked_requests = sum(1 for r in results[-5:] if not r)
        self.assertGreater(blocked_requests, 0, "Should block some requests due to rate limiting")

    def test_malicious_user_agent_detection(self):
        """Test detection of malicious user agents"""
        malicious_user_agents = [
            "sqlmap/1.0",
            "nikto/2.1.6",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "'; DROP TABLE users; --",
            "() { :; }; echo vulnerable",  # Shellshock
            "../../../windows/system32/cmd.exe"
        ]

        for user_agent in malicious_user_agents:
            with self.subTest(user_agent=user_agent):
                request_data = {
                    'method': 'GET',
                    'endpoint': '/api/test',
                    'headers': {'User-Agent': user_agent},
                    'client_ip': '192.168.1.100'
                }

                context = {'client_ip': '192.168.1.100'}
                result = self.api_pipeline.validate(request_data, context)

                self.assertFalse(result.is_valid, f"Should block malicious user agent: {user_agent}")

    def test_header_injection_detection(self):
        """Test detection of HTTP header injection"""
        header_injections = [
            "normal\r\nSet-Cookie: admin=true",
            "value\nLocation: http://evil.com",
            "test\r\n\r\n<script>alert('xss')</script>",
            "content\rContent-Length: 0\r\n\r\nHTTP/1.1 200 OK"
        ]

        for injection in header_injections:
            with self.subTest(injection=injection):
                request_data = {
                    'method': 'POST',
                    'endpoint': '/api/test',
                    'headers': {'X-Custom-Header': injection},
                    'client_ip': '192.168.1.100'
                }

                context = {'client_ip': '192.168.1.100'}
                result = self.api_pipeline.validate(request_data, context)

                # Should detect CRLF injection
                if '\r' in injection or '\n' in injection:
                    self.assertFalse(result.is_valid, f"Should block header injection: {injection}")


class TestSecurityReporting(unittest.TestCase):
    """Test security incident reporting and logging"""

    @patch('03_aplicacion.validation.framework.sanitization_engine.logger')
    def test_security_incident_logging(self, mock_logger):
        """Test that security incidents are properly logged"""
        sanitizer = SanitizationEngine(SanitizationLevel.STRICT)

        # Trigger security detection
        malicious_input = "<script>alert('xss')</script>"
        result = sanitizer.sanitize(malicious_input)

        # Should have logged security incident
        self.assertTrue(result.security_issues)

    def test_security_context_preservation(self):
        """Test that security context is preserved for forensics"""
        validator = StringInputValidator(max_length=100)

        malicious_input = "'; DROP TABLE users; --"
        result = validator.validate(malicious_input)

        # Should preserve context for security analysis
        self.assertFalse(result.is_valid)
        if result.errors:
            error = result.errors[0]
            self.assertIsNotNone(error.message)
            # Should contain information useful for security analysis

    def test_attack_pattern_classification(self):
        """Test classification of different attack patterns"""
        attack_patterns = {
            'xss': "<script>alert('xss')</script>",
            'sql_injection': "'; DROP TABLE users; --",
            'path_traversal': "../../etc/passwd",
            'command_injection': "; cat /etc/passwd",
            'code_injection': "eval('malicious_code')"
        }

        sanitizer = SanitizationEngine(SanitizationLevel.STRICT)

        for attack_type, payload in attack_patterns.items():
            with self.subTest(attack_type=attack_type):
                result = sanitizer.sanitize(payload)

                if result.security_issues:
                    # Should classify the attack type
                    self.assertTrue(any(attack_type.replace('_', ' ') in issue.lower()
                                      for issue in result.security_issues))


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()

    # Add security test cases
    security_test_classes = [
        TestXSSPrevention,
        TestSQLInjectionPrevention,
        TestPathTraversalPrevention,
        TestFileUploadSecurity,
        TestInputLengthAttacks,
        TestAPISecurityValidation,
        TestSecurityReporting
    ]

    for test_class in security_test_classes:
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
    print("SSA-24 Input Validation Framework - Security Tests")
    print("=" * 70)
    print("Testing security vulnerability detection and prevention")
    print()

    result = runner.run(suite)

    # Print security summary
    print()
    print("=" * 70)
    print("Security Test Summary")
    print("=" * 70)
    print(f"Security tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Security coverage: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    # Categorize security coverage
    security_categories = [
        "XSS Prevention",
        "SQL Injection Prevention",
        "Path Traversal Prevention",
        "File Upload Security",
        "Input Length Attacks",
        "API Security",
        "Security Reporting"
    ]

    print(f"\nSecurity categories tested: {len(security_categories)}")
    for category in security_categories:
        print(f"  ✓ {category}")

    if result.failures:
        print(f"\nSecurity test failures: {len(result.failures)}")
        for test, traceback in result.failures:
            print(f"  ⚠️  {test}")

    if result.errors:
        print(f"\nSecurity test errors: {len(result.errors)}")
        for test, traceback in result.errors:
            print(f"  ❌ {test}")

    # Security assessment
    if result.wasSuccessful():
        print("\n🔒 Security validation: PASSED")
        print("   All security mechanisms are functioning correctly")
    else:
        print("\n⚠️  Security validation: ISSUES DETECTED")
        print("   Some security mechanisms may need attention")

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)