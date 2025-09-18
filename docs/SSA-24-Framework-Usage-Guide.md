# SSA-24 Input Validation Framework - Usage Guide

## 📋 **OVERVIEW**

The SSA-24 Input Validation Framework provides comprehensive, security-focused validation and sanitization capabilities for the SenialSOLID application. This framework implements multiple layers of protection against common security vulnerabilities including XSS, SQL injection, and file-based attacks.

## 🚀 **QUICK START**

### Basic Import
```python
from aplicacion.validation import (
    # Core framework
    ValidationResult,
    ValidationPipeline,
    SanitizationEngine,

    # Validators
    StringInputValidator,
    EmailValidator,
    FileTypeValidator,
    SQLInjectionValidator,

    # Decorators
    validate_input,
    auto_sanitize
)
```

### Simple Validation Example
```python
# String validation with XSS protection
validator = StringInputValidator(max_length=100)
result = validator.validate("<script>alert('xss')</script>")

if result.is_valid:
    print(f"Safe input: {result.sanitized_value}")
else:
    print(f"Validation failed: {result.errors}")
```

## 🔧 **CORE COMPONENTS**

### 1. ValidationResult
Central result object for all validation operations.

```python
result = ValidationResult(is_valid=True, sanitized_value="clean_data")

# Check status
if result.is_valid:
    process_data(result.sanitized_value)

# Handle errors
for error in result.errors:
    logger.error(f"Validation error: {error.message}")

# Handle warnings
for warning in result.warnings:
    logger.warning(f"Validation warning: {warning}")
```

### 2. SanitizationEngine
Advanced sanitization with configurable security levels.

```python
from aplicacion.validation.framework import SanitizationLevel

# Basic sanitization
engine = SanitizationEngine(SanitizationLevel.MODERATE)
result = engine.sanitize(user_input)

# Strict security mode
strict_engine = SanitizationEngine(SanitizationLevel.STRICT)
result = strict_engine.sanitize(user_input)

# Context-aware HTML sanitization
clean_html = engine.sanitize_html_output(html_content, context="comment")
```

### 3. ValidationPipeline
Orchestrate multiple validators in sequence.

```python
from aplicacion.validation.framework import PipelineMode

# Create pipeline
pipeline = ValidationPipeline("user_input_pipeline", mode=PipelineMode.FAIL_FAST)

# Add validators
pipeline.add_validator(StringInputValidator(max_length=50))
pipeline.add_validator(SQLInjectionValidator(strict_mode=True))

# Validate input
result = pipeline.validate(user_input)
```

## 🛡️ **SECURITY VALIDATORS**

### SQL Injection Prevention
```python
sql_validator = SQLInjectionValidator(strict_mode=True, escape_quotes=True)

# Validate user input
result = sql_validator.validate("'; DROP TABLE users; --")

# Validate prepared statements
query = "SELECT * FROM users WHERE id = ?"
params = [user_id]
result = sql_validator.validate_prepared_statement(query, params)
```

### XSS Protection
```python
# Automatic XSS sanitization
engine = SanitizationEngine(SanitizationLevel.STRICT)

# Various XSS vectors
xss_inputs = [
    "<script>alert('xss')</script>",
    "javascript:alert('xss')",
    "<img src=x onerror=alert('xss')>"
]

for xss_input in xss_inputs:
    result = engine.sanitize(xss_input)
    print(f"Sanitized: {result.sanitized_value}")
```

### File Path Security
```python
from aplicacion.validation.rules import FilePathValidator

path_validator = FilePathValidator(
    base_directory="/safe/upload/path",
    allowed_extensions=['txt', 'csv', 'json'],
    strict_mode=True
)

# Prevent path traversal
result = path_validator.validate("../../etc/passwd")  # Will fail
result = path_validator.validate("data/signals.csv")  # Will pass
```

## 📁 **FILE VALIDATION**

### File Type and Content Validation
```python
from aplicacion.validation.rules import (
    FileTypeValidator,
    FileSizeValidator,
    FileContentValidator
)

# File type validation
type_validator = FileTypeValidator(
    allowed_extensions=['wav', 'csv', 'json'],
    strict_mime_check=True
)

# File size limits
size_validator = FileSizeValidator(
    max_size=10*1024*1024,  # 10MB
    min_size=1024           # 1KB
)

# Content security scanning
content_validator = FileContentValidator(scan_content=True)

# Validate file upload
def validate_file_upload(file_upload):
    validators = [type_validator, size_validator, content_validator]

    for validator in validators:
        result = validator.validate(file_upload)
        if not result.is_valid:
            return result

    return ValidationResult(is_valid=True)
```

## 🎯 **SIGNAL-SPECIFIC VALIDATION**

### Signal Parameter Validation
```python
from aplicacion.validation.rules import SignalParameterValidator

# Frequency validation
freq_validator = SignalParameterValidator('frequency')
result = freq_validator.validate(1000.0)  # Valid: 1kHz

# Amplitude validation
amp_validator = SignalParameterValidator('amplitude')
result = amp_validator.validate(5.0)  # Valid: 5V
```

### Signal Data Validation
```python
from aplicacion.validation.rules import SignalDataValidator

data_validator = SignalDataValidator(
    max_length=100000,
    check_anomalies=True,
    anomaly_threshold=3.0
)

# Validate signal array
signal_data = [1.0, 2.0, 3.0, 2.0, 1.0]
result = data_validator.validate(signal_data)

if result.is_valid:
    print(f"Signal stats: {result.metadata}")
```

## 🎨 **DECORATORS**

### Input Validation Decorator
```python
from aplicacion.validation.decorators import validate_parameters

@validate_parameters(
    username=StringInputValidator(max_length=30),
    email=EmailValidator(),
    age=NumericInputValidator(min_value=18, max_value=120)
)
def create_user(username, email, age):
    # Function will only execute if all parameters are valid
    return f"User {username} created with email {email}"

# Usage
try:
    result = create_user("john_doe", "john@example.com", 25)
except ValidationError as e:
    print(f"Invalid input: {e.message}")
```

### Auto-Sanitization Decorator
```python
from aplicacion.validation.decorators import auto_sanitize

@auto_sanitize(level=SanitizationLevel.STRICT)
def process_user_comment(comment):
    # Comment is automatically sanitized before processing
    return f"Comment: {comment}"

# XSS attempt is automatically cleaned
result = process_user_comment("<script>alert('xss')</script>Hello")
# Output: "Comment: Hello"
```

## 🔧 **ADVANCED USAGE**

### Custom Validators
```python
from aplicacion.validation.framework import AbstractValidator

class PhoneNumberValidator(AbstractValidator):
    def __init__(self, country_code=None):
        super().__init__("phone_number_validator")
        self.country_code = country_code

    def validate(self, value, context=None):
        result = ValidationResult(is_valid=True, sanitized_value=value)

        # Remove non-digits
        digits_only = ''.join(filter(str.isdigit, str(value)))

        # Validate length
        if len(digits_only) < 10:
            error = ValidationError("Phone number too short")
            result.add_error(error)

        result.sanitized_value = digits_only
        return result

# Usage
phone_validator = PhoneNumberValidator()
result = phone_validator.validate("+1 (555) 123-4567")
```

### Pipeline with Stages
```python
pipeline = ValidationPipeline("advanced_pipeline")

# Pre-validation stage
pipeline.add_validator(
    StringInputValidator(max_length=1000),
    stage="pre_validation"
)

# Security validation stage
pipeline.add_validator(
    SQLInjectionValidator(strict_mode=True),
    stage="security_validation"
)
pipeline.add_validator(
    FilePathValidator(strict_mode=True),
    stage="security_validation"
)

# Business validation stage
pipeline.add_validator(
    EmailValidator(),
    stage="business_validation"
)

result = pipeline.validate(user_input)
```

### Context-Aware Validation
```python
def validate_api_input(data, endpoint_context):
    context = {
        'endpoint': endpoint_context['name'],
        'user_role': endpoint_context['user_role'],
        'request_ip': endpoint_context['ip_address']
    }

    # Different validation rules based on endpoint
    if endpoint_context['name'] == 'admin_panel':
        validator = StringInputValidator(max_length=50, strict_mode=True)
    else:
        validator = StringInputValidator(max_length=200)

    return validator.validate(data, context)
```

## 📊 **ERROR HANDLING**

### Exception Types
```python
from aplicacion.validation.exceptions import (
    ValidationError,
    SecurityValidationError,
    FileValidationError,
    SanitizationError
)

try:
    result = validator.validate(suspicious_input)
except SecurityValidationError as e:
    # Handle security threats
    logger.critical(f"Security threat detected: {e.threat_type}")
    alert_security_team(e.context)

except ValidationError as e:
    # Handle general validation errors
    logger.warning(f"Validation failed: {e.message}")

except SanitizationError as e:
    # Handle sanitization failures
    logger.error(f"Sanitization failed: {e.message}")
```

### Error Recovery
```python
def safe_validate_with_fallback(input_data, validator):
    try:
        result = validator.validate(input_data)
        if result.is_valid:
            return result.sanitized_value
    except ValidationError:
        pass

    # Fallback: aggressive sanitization
    engine = SanitizationEngine(SanitizationLevel.PARANOID)
    fallback_result = engine.sanitize(input_data)
    return fallback_result.sanitized_value
```

## ⚡ **PERFORMANCE OPTIMIZATION**

### Caching Validators
```python
# Cache frequently used validators
class ValidatorCache:
    def __init__(self):
        self._cache = {}

    def get_string_validator(self, max_length):
        key = f"string_{max_length}"
        if key not in self._cache:
            self._cache[key] = StringInputValidator(max_length=max_length)
        return self._cache[key]

# Global cache instance
validator_cache = ValidatorCache()

# Usage
validator = validator_cache.get_string_validator(100)
```

### Async Validation
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_validate_large_dataset(data_list, validator):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)

    tasks = []
    for data in data_list:
        task = loop.run_in_executor(executor, validator.validate, data)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

## 🔍 **MONITORING AND LOGGING**

### Security Event Logging
```python
import structlog

logger = structlog.get_logger("ssa24.security")

# The framework automatically logs security events
def setup_security_monitoring():
    # Security events are logged with structured data
    # Check logs for patterns like:
    # - "SQL injection attempt detected"
    # - "XSS pattern found in input"
    # - "Path traversal blocked"
    pass

# Custom security event handler
def on_security_event(event_type, context):
    logger.critical(
        "Security event detected",
        event_type=event_type,
        threat_details=context,
        timestamp=datetime.now().isoformat()
    )
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_validation_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        validation_time = end_time - start_time
        if validation_time > 0.1:  # Log slow validations
            logger.warning(
                "Slow validation detected",
                function=func.__name__,
                duration=validation_time,
                input_size=len(str(args[1]) if len(args) > 1 else "")
            )

        return result
    return wrapper

# Apply to custom validators
@monitor_validation_performance
def custom_validate(validator, data):
    return validator.validate(data)
```

## 🧪 **TESTING YOUR VALIDATIONS**

### Unit Testing Validators
```python
import unittest

class TestCustomValidator(unittest.TestCase):
    def setUp(self):
        self.validator = CustomValidator()

    def test_valid_input(self):
        result = self.validator.validate("valid_input")
        self.assertTrue(result.is_valid)

    def test_invalid_input(self):
        result = self.validator.validate("invalid_input")
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

    def test_security_threat(self):
        result = self.validator.validate("<script>alert('xss')</script>")
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.errors[0], SecurityValidationError)
```

### Integration Testing
```python
def test_full_validation_pipeline():
    # Test complete validation flow
    pipeline = create_user_input_pipeline()

    test_cases = [
        {
            'input': 'normal_input',
            'expected': True
        },
        {
            'input': '<script>alert("xss")</script>',
            'expected': False
        },
        {
            'input': "'; DROP TABLE users; --",
            'expected': False
        }
    ]

    for case in test_cases:
        result = pipeline.validate(case['input'])
        assert result.is_valid == case['expected']
```

## 📚 **BEST PRACTICES**

### 1. Layer Your Validations
```python
# Bad: Single validation
result = basic_validator.validate(user_input)

# Good: Layered validation
pipeline = ValidationPipeline("secure_input")
pipeline.add_validator(StringInputValidator(max_length=1000))
pipeline.add_validator(SQLInjectionValidator(strict_mode=True))
pipeline.add_validator(BusinessLogicValidator())
result = pipeline.validate(user_input)
```

### 2. Always Sanitize Output
```python
# Bad: Direct output
return f"Hello {user_name}"

# Good: Sanitized output
engine = SanitizationEngine(SanitizationLevel.MODERATE)
safe_name = engine.sanitize_html_output(user_name, context="general")
return f"Hello {safe_name}"
```

### 3. Use Context Information
```python
# Provide rich context for better error handling
context = {
    'field_name': 'email',
    'user_id': current_user.id,
    'request_ip': request.remote_addr,
    'endpoint': request.endpoint
}

result = validator.validate(email, context)
```

### 4. Handle Errors Gracefully
```python
def safe_process_input(user_input):
    try:
        result = validator.validate(user_input)
        if result.is_valid:
            return result.sanitized_value
        else:
            # Log errors but don't expose details to user
            logger.warning(f"Validation failed: {result.errors}")
            return None
    except SecurityValidationError:
        # Security threat - log and alert
        alert_security_team()
        return None
    except Exception as e:
        # Unexpected error - fail safely
        logger.error(f"Validation error: {e}")
        return None
```

## 🔧 **CONFIGURATION**

### Framework Configuration
```python
# Create custom configuration
VALIDATION_CONFIG = {
    'default_sanitization_level': SanitizationLevel.STRICT,
    'enable_performance_monitoring': True,
    'log_security_events': True,
    'max_input_length': 10000,
    'file_size_limits': {
        'max_size': 100 * 1024 * 1024,  # 100MB
        'min_size': 1024  # 1KB
    }
}

# Apply configuration
def configure_validation_framework(config):
    # Set global defaults based on configuration
    pass
```

This comprehensive guide covers all major aspects of the SSA-24 Input Validation Framework. For additional examples and advanced use cases, refer to the implementation examples and security guide documents.