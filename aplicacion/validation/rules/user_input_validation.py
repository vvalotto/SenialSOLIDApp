"""
User Input Validation for SSA-24 Input Validation Framework

Specialized validators for user interface inputs with XSS and injection prevention
"""

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Pattern, Union
import logging
from datetime import datetime
import unicodedata
import sqlite3

from ..framework.validator_base import AbstractValidator, ValidationResult
from ..exceptions.validation_exceptions import ValidationError, SecurityValidationError


class StringInputValidator(AbstractValidator):
    """
    Validator for general string inputs with security filtering
    """

    # Character whitelists for different input types
    ALPHANUMERIC = r'^[a-zA-Z0-9]+$'
    ALPHANUMERIC_SPACE = r'^[a-zA-Z0-9\s]+$'
    ALPHANUMERIC_EXTENDED = r'^[a-zA-Z0-9\s\-_.@]+$'
    TEXT_SAFE = r'^[a-zA-Z0-9\s\-_.@,;:!?()\[\]{}]+$'

    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript\s*:',             # JavaScript URLs
        r'vbscript\s*:',              # VBScript URLs
        r'on\w+\s*=',                 # Event handlers (onclick, onload, etc.)
        r'expression\s*\(',           # CSS expressions
        r'import\s+',                 # Import statements
        r'@import',                   # CSS imports
        r'document\.',                # DOM access
        r'window\.',                  # Window object access
        r'eval\s*\(',                 # eval() function
        r'setTimeout\s*\(',           # setTimeout function
        r'setInterval\s*\(',          # setInterval function
    ]

    def __init__(
        self,
        min_length: int = 0,
        max_length: int = 1000,
        allowed_pattern: str = None,
        required: bool = True,
        trim_whitespace: bool = True,
        normalize_unicode: bool = True
    ):
        super().__init__("string_input_validator")
        self.min_length = min_length
        self.max_length = max_length
        self.allowed_pattern = re.compile(allowed_pattern) if allowed_pattern else None
        self.required = required
        self.trim_whitespace = trim_whitespace
        self.normalize_unicode = normalize_unicode

        # Compile dangerous patterns
        self.dangerous_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate string input with security checks"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Handle None/empty values
        if value is None or value == '':
            if self.required:
                error = ValidationError(
                    message="Input is required",
                    field_name=context.get('field_name', 'input'),
                    validation_rule="required",
                    context=context
                )
                result.add_error(error)
            return result

        # Convert to string
        if not isinstance(value, str):
            try:
                string_value = str(value)
            except Exception as e:
                error = ValidationError(
                    message=f"Cannot convert input to string: {str(e)}",
                    invalid_value=value,
                    validation_rule="string_conversion",
                    context=context
                )
                result.add_error(error)
                return result
        else:
            string_value = value

        # Unicode normalization
        if self.normalize_unicode:
            string_value = unicodedata.normalize('NFKC', string_value)

        # Trim whitespace
        if self.trim_whitespace:
            string_value = string_value.strip()

        # Length validation
        if len(string_value) < self.min_length:
            error = ValidationError(
                message=f"Input too short: {len(string_value)} characters (minimum: {self.min_length})",
                field_name=context.get('field_name', 'input'),
                invalid_value=string_value,
                validation_rule="min_length",
                context=context
            )
            result.add_error(error)

        if len(string_value) > self.max_length:
            error = ValidationError(
                message=f"Input too long: {len(string_value)} characters (maximum: {self.max_length})",
                field_name=context.get('field_name', 'input'),
                invalid_value=string_value[:100] + "..." if len(string_value) > 100 else string_value,
                validation_rule="max_length",
                context=context
            )
            result.add_error(error)

        # Pattern validation
        if self.allowed_pattern and not self.allowed_pattern.match(string_value):
            error = ValidationError(
                message="Input contains invalid characters",
                field_name=context.get('field_name', 'input'),
                invalid_value=string_value[:100] + "..." if len(string_value) > 100 else string_value,
                validation_rule="character_whitelist",
                context=context
            )
            result.add_error(error)

        # Security validation
        self._check_security_threats(string_value, result, context)

        result.sanitized_value = string_value
        return result

    def _check_security_threats(self, value: str, result: ValidationResult, context: Dict[str, Any]):
        """Check for security threats in input"""
        threats_found = []

        for pattern in self.dangerous_patterns:
            if pattern.search(value):
                threat_name = self._get_threat_name_from_pattern(pattern.pattern)
                threats_found.append(threat_name)

        if threats_found:
            error = SecurityValidationError(
                message=f"Potentially malicious content detected: {', '.join(threats_found)}",
                threat_type="xss_injection",
                context={**context, 'detected_threats': threats_found}
            )
            result.add_error(error)

    def _get_threat_name_from_pattern(self, pattern: str) -> str:
        """Get human-readable threat name from regex pattern"""
        threat_map = {
            r'<script[^>]*>.*?</script>': 'Script_Tag',
            r'javascript\s*:': 'JavaScript_URL',
            r'vbscript\s*:': 'VBScript_URL',
            r'on\w+\s*=': 'Event_Handler',
            r'expression\s*\(': 'CSS_Expression',
            r'import\s+': 'Import_Statement',
            r'@import': 'CSS_Import',
            r'document\.': 'DOM_Access',
            r'window\.': 'Window_Access',
            r'eval\s*\(': 'Code_Eval',
            r'setTimeout\s*\(': 'SetTimeout',
            r'setInterval\s*\(': 'SetInterval'
        }

        for key, name in threat_map.items():
            if key in pattern:
                return name
        return 'Unknown_Threat'


class SQLInjectionValidator(AbstractValidator):
    """
    Advanced SQL Injection prevention validator
    Implements multiple detection and prevention techniques
    """

    # SQL keywords that should be escaped/detected
    SQL_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'UNION', 'JOIN', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'EXEC',
        'EXECUTE', 'DECLARE', 'CAST', 'CONVERT', 'SUBSTRING', 'CHAR',
        'SCRIPT', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW', 'INDEX'
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        # Comment patterns
        r'(-{2}|/\*|\*/|#)',
        # Union-based injection
        r'\b(union\s+select|union\s+all\s+select)\b',
        # Boolean-based injection
        r'\b(or\s+1\s*=\s*1|and\s+1\s*=\s*1|or\s+true|and\s+false)\b',
        # Time-based injection
        r'\b(waitfor\s+delay|sleep\s*\(|benchmark\s*\()\b',
        # Error-based injection
        r'\b(extractvalue\s*\(|updatexml\s*\(|exp\s*\()\b',
        # Stacked queries
        r';\s*(insert|update|delete|drop|create|alter)',
        # Information schema
        r'\b(information_schema|sys\.|pg_|mysql\.)\b',
        # SQL functions
        r'\b(load_file\s*\(|into\s+outfile|into\s+dumpfile)\b',
        # Quote escaping attempts
        r"['\"][^'\"]*['\"]|\\x[0-9a-f]{2}|char\s*\(",
        # Hex encoding
        r'0x[0-9a-f]+',
        # SQL operators
        r'[<>=!]+.*[<>=!]+|[\+\-\*/].*[\+\-\*/]'
    ]

    def __init__(
        self,
        strict_mode: bool = True,
        allow_quotes: bool = False,
        max_length: int = 1000,
        escape_quotes: bool = True
    ):
        super().__init__("sql_injection_validator")
        self.strict_mode = strict_mode
        self.allow_quotes = allow_quotes
        self.max_length = max_length
        self.escape_quotes = escape_quotes

        # Compile patterns for performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.SQL_INJECTION_PATTERNS
        ]

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate input for SQL injection attempts"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if value is None or value == '':
            return result

        input_str = str(value).strip()
        original_str = input_str

        # Length check
        if len(input_str) > self.max_length:
            error = SecurityValidationError(
                message=f"Input too long: {len(input_str)} chars (max: {self.max_length})",
                threat_type="sql_injection",
                context={**context, 'input_length': len(input_str)}
            )
            result.add_error(error)
            return result

        # SQL pattern detection
        detected_threats = []
        for pattern in self.compiled_patterns:
            matches = pattern.findall(input_str)
            if matches:
                threat_name = self._get_sql_threat_name(pattern.pattern)
                detected_threats.append(threat_name)
                self.logger.warning(
                    f"SQL injection pattern detected",
                    extra={
                        'pattern': pattern.pattern,
                        'matches': matches[:3],  # Limit logged matches
                        'input_preview': input_str[:100]
                    }
                )

        # SQL keyword detection
        keywords_found = []
        for keyword in self.SQL_KEYWORDS:
            if re.search(rf'\b{keyword}\b', input_str, re.IGNORECASE):
                keywords_found.append(keyword)

        if keywords_found and self.strict_mode:
            detected_threats.append('SQL_Keywords')
            self.logger.warning(
                f"SQL keywords detected: {keywords_found}",
                extra={'keywords': keywords_found}
            )

        # Quote handling
        if not self.allow_quotes and ("'" in input_str or '"' in input_str):
            detected_threats.append('Quotes')

        # Apply sanitization
        sanitized_str = self._sanitize_sql_input(input_str)

        # Security validation
        if detected_threats:
            if self.strict_mode:
                error = SecurityValidationError(
                    message=f"SQL injection attempt detected: {', '.join(detected_threats)}",
                    threat_type="sql_injection",
                    context={
                        **context,
                        'detected_threats': detected_threats,
                        'original_input': original_str[:100]
                    }
                )
                result.add_error(error)
            else:
                result.add_warning(f"Suspicious SQL patterns detected: {', '.join(detected_threats)}")

        result.sanitized_value = sanitized_str
        result.was_sanitized = (original_str != sanitized_str)

        return result

    def _sanitize_sql_input(self, input_str: str) -> str:
        """Sanitize input to prevent SQL injection"""
        sanitized = input_str

        # Remove SQL comments
        sanitized = re.sub(r'(-{2}.*$|/\*.*?\*/)', '', sanitized, flags=re.MULTILINE | re.DOTALL)

        # Escape quotes if enabled
        if self.escape_quotes:
            sanitized = sanitized.replace("'", "''")  # SQL standard quote escaping
            sanitized = sanitized.replace('"', '""')

        # Remove potentially dangerous characters
        dangerous_chars = [';', '\\', '\x00', '\x1a']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())

        return sanitized

    def _get_sql_threat_name(self, pattern: str) -> str:
        """Get human-readable threat name from SQL pattern"""
        threat_map = {
            r'(-{2}|/\*|\*/|#)': 'SQL_Comments',
            r'\b(union\s+select|union\s+all\s+select)\b': 'Union_Injection',
            r'\b(or\s+1\s*=\s*1|and\s+1\s*=\s*1|or\s+true|and\s+false)\b': 'Boolean_Injection',
            r'\b(waitfor\s+delay|sleep\s*\(|benchmark\s*\()\b': 'Time_Injection',
            r'\b(extractvalue\s*\(|updatexml\s*\(|exp\s*\()\b': 'Error_Injection',
            r';\s*(insert|update|delete|drop|create|alter)': 'Stacked_Queries',
            r'\b(information_schema|sys\.|pg_|mysql\.)\b': 'Schema_Access',
            r'\b(load_file\s*\(|into\s+outfile|into\s+dumpfile)\b': 'File_Operations',
            r"['\"][^'\"]*['\"]|\\x[0-9a-f]{2}|char\s*\(": 'Quote_Manipulation',
            r'0x[0-9a-f]+': 'Hex_Encoding',
            r'[<>=!]+.*[<>=!]+|[\+\-\*/].*[\+\-\*/]': 'Operator_Injection'
        }

        for key, name in threat_map.items():
            if key in pattern:
                return name
        return 'Unknown_SQL_Threat'

    def validate_prepared_statement(self, query: str, parameters: List[Any]) -> ValidationResult:
        """
        Validate a prepared statement and its parameters
        This is the recommended way to prevent SQL injection
        """
        result = ValidationResult(is_valid=True)

        # Validate the query template
        if '?' not in query and '%s' not in query and not re.search(r'\$\d+', query):
            result.add_warning("Query does not appear to use parameterized placeholders")

        # Check for direct concatenation patterns
        dangerous_patterns = [
            r'\+.*[\'"]',  # String concatenation
            r'[\'"].*\+',  # String concatenation
            r'format\s*\(',  # String formatting
            r'%.*%',  # String interpolation
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                error = SecurityValidationError(
                    message="Query contains potential string concatenation",
                    threat_type="sql_injection",
                    context={'query_pattern': pattern}
                )
                result.add_error(error)

        # Validate parameters
        for i, param in enumerate(parameters):
            param_result = self.validate(param, {'parameter_index': i})
            if not param_result.is_valid:
                result.merge_errors(param_result)

        return result


class EmailValidator(AbstractValidator):
    """
    Validator for email addresses
    """

    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    def __init__(self, required: bool = True, max_length: int = 254):
        super().__init__("email_validator")
        self.required = required
        self.max_length = max_length  # RFC 5321 limit

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate email address format"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not value:
            if self.required:
                error = ValidationError(
                    message="Email address is required",
                    field_name="email",
                    validation_rule="required",
                    context=context
                )
                result.add_error(error)
            return result

        if not isinstance(value, str):
            error = ValidationError(
                message="Email must be a string",
                field_name="email",
                invalid_value=value,
                validation_rule="type_check",
                context=context
            )
            result.add_error(error)
            return result

        email = value.strip().lower()

        # Length check
        if len(email) > self.max_length:
            error = ValidationError(
                message=f"Email too long: {len(email)} characters (maximum: {self.max_length})",
                field_name="email",
                invalid_value=email,
                validation_rule="max_length",
                context=context
            )
            result.add_error(error)

        # Format validation
        if not self.EMAIL_PATTERN.match(email):
            error = ValidationError(
                message="Invalid email format",
                field_name="email",
                invalid_value=email,
                validation_rule="email_format",
                context=context
            )
            result.add_error(error)

        # Additional security checks
        self._check_email_security(email, result, context)

        result.sanitized_value = email
        return result

    def _check_email_security(self, email: str, result: ValidationResult, context: Dict[str, Any]):
        """Additional security checks for email addresses"""
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.{2,}',      # Multiple consecutive dots
            r'^\.|\.$',     # Starting or ending with dot
            r'@.*@',        # Multiple @ symbols
            r'[<>"\']',     # HTML/script characters
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email):
                result.add_warning(f"Suspicious email pattern detected: {pattern}")


class NumericInputValidator(AbstractValidator):
    """
    Validator for numeric inputs with range checking
    """

    def __init__(
        self,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        allow_decimal: bool = True,
        decimal_places: int = None,
        required: bool = True
    ):
        super().__init__("numeric_input_validator")
        self.min_value = min_value
        self.max_value = max_value
        self.allow_decimal = allow_decimal
        self.decimal_places = decimal_places
        self.required = required

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate numeric input"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if value is None or value == '':
            if self.required:
                error = ValidationError(
                    message="Numeric value is required",
                    field_name=context.get('field_name', 'number'),
                    validation_rule="required",
                    context=context
                )
                result.add_error(error)
            return result

        # Convert to numeric
        try:
            if isinstance(value, str):
                value = value.strip()
                if '.' in value or 'e' in value.lower():
                    numeric_value = float(value)
                else:
                    numeric_value = int(value)
            else:
                numeric_value = float(value) if self.allow_decimal else int(value)
        except (ValueError, TypeError):
            error = ValidationError(
                message=f"Invalid numeric value: {value}",
                field_name=context.get('field_name', 'number'),
                invalid_value=value,
                validation_rule="numeric_format",
                context=context
            )
            result.add_error(error)
            return result

        # Decimal validation
        if not self.allow_decimal and isinstance(numeric_value, float) and not numeric_value.is_integer():
            error = ValidationError(
                message="Decimal values not allowed",
                field_name=context.get('field_name', 'number'),
                invalid_value=numeric_value,
                validation_rule="integer_only",
                context=context
            )
            result.add_error(error)

        # Decimal places validation
        if self.decimal_places is not None and isinstance(numeric_value, float):
            decimal_str = str(numeric_value).split('.')
            if len(decimal_str) > 1 and len(decimal_str[1]) > self.decimal_places:
                error = ValidationError(
                    message=f"Too many decimal places: {len(decimal_str[1])} (maximum: {self.decimal_places})",
                    field_name=context.get('field_name', 'number'),
                    invalid_value=numeric_value,
                    validation_rule="decimal_places",
                    context=context
                )
                result.add_error(error)

        # Range validation
        if self.min_value is not None and numeric_value < self.min_value:
            error = ValidationError(
                message=f"Value too small: {numeric_value} (minimum: {self.min_value})",
                field_name=context.get('field_name', 'number'),
                invalid_value=numeric_value,
                validation_rule="min_value",
                context=context
            )
            result.add_error(error)

        if self.max_value is not None and numeric_value > self.max_value:
            error = ValidationError(
                message=f"Value too large: {numeric_value} (maximum: {self.max_value})",
                field_name=context.get('field_name', 'number'),
                invalid_value=numeric_value,
                validation_rule="max_value",
                context=context
            )
            result.add_error(error)

        result.sanitized_value = numeric_value
        return result


class DateTimeValidator(AbstractValidator):
    """
    Validator for date and time inputs
    """

    def __init__(
        self,
        date_format: str = '%Y-%m-%d',
        min_date: datetime = None,
        max_date: datetime = None,
        required: bool = True
    ):
        super().__init__("datetime_validator")
        self.date_format = date_format
        self.min_date = min_date
        self.max_date = max_date
        self.required = required

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate date/time input"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not value:
            if self.required:
                error = ValidationError(
                    message="Date is required",
                    field_name=context.get('field_name', 'date'),
                    validation_rule="required",
                    context=context
                )
                result.add_error(error)
            return result

        # Parse date
        if isinstance(value, datetime):
            date_value = value
        elif isinstance(value, str):
            try:
                date_value = datetime.strptime(value, self.date_format)
            except ValueError as e:
                error = ValidationError(
                    message=f"Invalid date format: {value} (expected: {self.date_format})",
                    field_name=context.get('field_name', 'date'),
                    invalid_value=value,
                    validation_rule="date_format",
                    context=context
                )
                result.add_error(error)
                return result
        else:
            error = ValidationError(
                message="Date must be string or datetime object",
                field_name=context.get('field_name', 'date'),
                invalid_value=value,
                validation_rule="type_check",
                context=context
            )
            result.add_error(error)
            return result

        # Range validation
        if self.min_date and date_value < self.min_date:
            error = ValidationError(
                message=f"Date too early: {date_value.strftime(self.date_format)} (minimum: {self.min_date.strftime(self.date_format)})",
                field_name=context.get('field_name', 'date'),
                invalid_value=date_value,
                validation_rule="min_date",
                context=context
            )
            result.add_error(error)

        if self.max_date and date_value > self.max_date:
            error = ValidationError(
                message=f"Date too late: {date_value.strftime(self.date_format)} (maximum: {self.max_date.strftime(self.date_format)})",
                field_name=context.get('field_name', 'date'),
                invalid_value=date_value,
                validation_rule="max_date",
                context=context
            )
            result.add_error(error)

        result.sanitized_value = date_value
        result.metadata['formatted_date'] = date_value.strftime(self.date_format)
        return result


class PasswordValidator(AbstractValidator):
    """
    Validator for password strength and security
    """

    def __init__(
        self,
        min_length: int = 8,
        max_length: int = 128,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    ):
        super().__init__("password_validator")
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.special_chars = special_chars

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate password strength"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not value:
            error = ValidationError(
                message="Password is required",
                field_name="password",
                validation_rule="required",
                context=context
            )
            result.add_error(error)
            return result

        if not isinstance(value, str):
            error = ValidationError(
                message="Password must be a string",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="type_check",
                context=context
            )
            result.add_error(error)
            return result

        password = value

        # Length validation
        if len(password) < self.min_length:
            error = ValidationError(
                message=f"Password too short: {len(password)} characters (minimum: {self.min_length})",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="min_length",
                context=context
            )
            result.add_error(error)

        if len(password) > self.max_length:
            error = ValidationError(
                message=f"Password too long: {len(password)} characters (maximum: {self.max_length})",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="max_length",
                context=context
            )
            result.add_error(error)

        # Character requirement validation
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            error = ValidationError(
                message="Password must contain at least one uppercase letter",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="uppercase_required",
                context=context
            )
            result.add_error(error)

        if self.require_lowercase and not re.search(r'[a-z]', password):
            error = ValidationError(
                message="Password must contain at least one lowercase letter",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="lowercase_required",
                context=context
            )
            result.add_error(error)

        if self.require_digits and not re.search(r'[0-9]', password):
            error = ValidationError(
                message="Password must contain at least one digit",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="digit_required",
                context=context
            )
            result.add_error(error)

        if self.require_special and not any(char in self.special_chars for char in password):
            error = ValidationError(
                message=f"Password must contain at least one special character ({self.special_chars})",
                field_name="password",
                invalid_value="[password hidden]",
                validation_rule="special_required",
                context=context
            )
            result.add_error(error)

        # Security checks
        self._check_password_security(password, result, context)

        # Don't store actual password in sanitized_value for security
        result.sanitized_value = "[password hidden]"
        result.metadata['password_strength_score'] = self._calculate_strength_score(password)

        return result

    def _check_password_security(self, password: str, result: ValidationResult, context: Dict[str, Any]):
        """Additional security checks for passwords"""
        # Check for common weak patterns
        weak_patterns = [
            r'(.)\1{3,}',        # Repeated characters (aaaa)
            r'123456',           # Sequential numbers
            r'abcdef',           # Sequential letters
            r'qwerty',           # Keyboard patterns
            r'password',         # Common word
            r'admin',            # Common word
        ]

        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                result.add_warning(f"Password contains weak pattern: {pattern}")

    def _calculate_strength_score(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0

        # Length scoring
        if len(password) >= 8:
            score += 25
        if len(password) >= 12:
            score += 15

        # Character diversity scoring
        if re.search(r'[a-z]', password):
            score += 15
        if re.search(r'[A-Z]', password):
            score += 15
        if re.search(r'[0-9]', password):
            score += 15
        if any(char in self.special_chars for char in password):
            score += 15

        return min(score, 100)


# Factory function for creating user input validation pipeline
def create_user_input_validation_pipeline(input_type: str = "general") -> 'ValidationPipeline':
    """
    Create a pre-configured validation pipeline for user inputs

    Args:
        input_type: Type of input (general, form, sensitive)

    Returns:
        Configured ValidationPipeline
    """
    from ..framework.validation_pipeline import ValidationPipeline, PipelineStage

    pipeline = ValidationPipeline(f"user_input_validation_{input_type}")

    if input_type == "general":
        # General text inputs
        pipeline.add_validator(
            StringInputValidator(max_length=1000, allowed_pattern=StringInputValidator.TEXT_SAFE),
            PipelineStage.BUSINESS_VALIDATION
        )

    elif input_type == "form":
        # Form inputs with strict validation
        pipeline.add_validator(
            StringInputValidator(max_length=255, allowed_pattern=StringInputValidator.ALPHANUMERIC_EXTENDED),
            PipelineStage.TYPE_VALIDATION
        )

    elif input_type == "sensitive":
        # Sensitive inputs with maximum security
        pipeline.add_validator(
            StringInputValidator(max_length=255, allowed_pattern=StringInputValidator.ALPHANUMERIC_SPACE),
            PipelineStage.SECURITY_VALIDATION
        )

    return pipeline