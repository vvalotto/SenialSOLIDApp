"""
Sanitization Engine for SSA-24 Input Validation Framework

Provides centralized data sanitization and security cleaning capabilities
"""

import re
import html
import urllib.parse
import os
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
import logging

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

from ..exceptions.validation_exceptions import SanitizationError, SecurityValidationError


class SanitizationLevel(Enum):
    """Levels of sanitization intensity"""
    BASIC = "basic"
    MODERATE = "moderate"
    STRICT = "strict"
    PARANOID = "paranoid"


class SanitizationStrategy(Enum):
    """Sanitization strategies"""
    REMOVE = "remove"           # Remove invalid content
    ESCAPE = "escape"           # Escape invalid content
    REPLACE = "replace"         # Replace with safe alternatives
    REJECT = "reject"           # Reject input with invalid content


class SanitizationRule:
    """
    Represents a sanitization rule
    """

    def __init__(
        self,
        name: str,
        pattern: Union[str, re.Pattern],
        strategy: SanitizationStrategy,
        replacement: str = "",
        description: str = None,
        enabled: bool = True
    ):
        self.name = name
        self.pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        self.strategy = strategy
        self.replacement = replacement
        self.description = description or f"Sanitization rule: {name}"
        self.enabled = enabled


class SanitizationResult:
    """
    Result of a sanitization operation
    """

    def __init__(
        self,
        original_value: Any,
        sanitized_value: Any,
        was_modified: bool = False,
        applied_rules: List[str] = None,
        warnings: List[str] = None,
        security_issues: List[str] = None
    ):
        self.original_value = original_value
        self.sanitized_value = sanitized_value
        self.was_modified = was_modified
        self.applied_rules = applied_rules or []
        self.warnings = warnings or []
        self.security_issues = security_issues or []

    def add_warning(self, warning: str):
        """Add a sanitization warning"""
        self.warnings.append(warning)

    def add_security_issue(self, issue: str):
        """Add a security issue detected during sanitization"""
        self.security_issues.append(issue)

    def add_applied_rule(self, rule_name: str):
        """Record that a rule was applied"""
        self.applied_rules.append(rule_name)

    def has_security_issues(self) -> bool:
        """Check if security issues were detected"""
        return len(self.security_issues) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'was_modified': self.was_modified,
            'applied_rules': self.applied_rules,
            'warnings': self.warnings,
            'security_issues': self.security_issues,
            'original_length': len(str(self.original_value)),
            'sanitized_length': len(str(self.sanitized_value))
        }


class SanitizationEngine:
    """
    Centralized engine for data sanitization

    Provides security-focused data cleaning with configurable rules and strategies
    """

    def __init__(self, level: SanitizationLevel = SanitizationLevel.MODERATE):
        self.level = level
        self.logger = logging.getLogger(f"{__name__}.SanitizationEngine")

        # Rule sets by category
        self.rules: Dict[str, List[SanitizationRule]] = {
            'html': [],
            'sql': [],
            'xss': [],
            'file_path': [],
            'command': [],
            'general': []
        }

        # Initialize default rules
        self._initialize_default_rules()

        # Custom sanitization functions
        self.custom_sanitizers: Dict[str, Callable] = {}

    def _initialize_default_rules(self):
        """Initialize default sanitization rules based on security best practices"""

        # HTML/XSS Prevention Rules
        self.rules['html'].extend([
            SanitizationRule(
                name="script_tags",
                pattern=r'<script[^>]*>.*?</script>',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove script tags"
            ),
            SanitizationRule(
                name="on_event_handlers",
                pattern=r'\bon\w+\s*=\s*["\'][^"\']*["\']',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove on* event handlers"
            ),
            SanitizationRule(
                name="javascript_urls",
                pattern=r'javascript\s*:',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove javascript: URLs"
            )
        ])

        # SQL Injection Prevention Rules
        self.rules['sql'].extend([
            SanitizationRule(
                name="sql_comments",
                pattern=r'(-{2}|/\*|\*/)',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove SQL comment patterns"
            ),
            SanitizationRule(
                name="sql_union",
                pattern=r'\b(union|select|insert|update|delete|drop|create|alter)\b',
                strategy=SanitizationStrategy.ESCAPE,
                description="Escape SQL keywords"
            )
        ])

        # File Path Security Rules
        self.rules['file_path'].extend([
            SanitizationRule(
                name="path_traversal",
                pattern=r'\.\.[\\/]',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove path traversal patterns"
            ),
            SanitizationRule(
                name="null_bytes",
                pattern=r'\x00',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove null bytes"
            )
        ])

        # Command Injection Prevention Rules
        self.rules['command'].extend([
            SanitizationRule(
                name="command_separators",
                pattern=r'[;&|`$()]',
                strategy=SanitizationStrategy.ESCAPE,
                description="Escape command separators"
            )
        ])

        # General Security Rules
        self.rules['general'].extend([
            SanitizationRule(
                name="control_characters",
                pattern=r'[\x00-\x1f\x7f-\x9f]',
                strategy=SanitizationStrategy.REMOVE,
                description="Remove control characters"
            ),
            SanitizationRule(
                name="excessive_whitespace",
                pattern=r'\s{10,}',
                strategy=SanitizationStrategy.REPLACE,
                replacement=' ',
                description="Normalize excessive whitespace"
            )
        ])

    def add_rule(self, category: str, rule: SanitizationRule):
        """Add a custom sanitization rule"""
        if category not in self.rules:
            self.rules[category] = []
        self.rules[category].append(rule)
        self.logger.info(f"Added sanitization rule {rule.name} to category {category}")

    def remove_rule(self, category: str, rule_name: str) -> bool:
        """Remove a sanitization rule"""
        if category not in self.rules:
            return False

        initial_count = len(self.rules[category])
        self.rules[category] = [rule for rule in self.rules[category] if rule.name != rule_name]
        removed = len(self.rules[category]) < initial_count

        if removed:
            self.logger.info(f"Removed sanitization rule {rule_name} from category {category}")

        return removed

    def add_custom_sanitizer(self, name: str, sanitizer_func: Callable):
        """Add a custom sanitization function"""
        self.custom_sanitizers[name] = sanitizer_func
        self.logger.info(f"Added custom sanitizer: {name}")

    def sanitize(
        self,
        value: Any,
        categories: List[str] = None,
        strict_mode: bool = None
    ) -> SanitizationResult:
        """
        Sanitize input value according to specified rules

        Args:
            value: Value to sanitize
            categories: Rule categories to apply (default: all)
            strict_mode: Override default strictness

        Returns:
            SanitizationResult with sanitized value and metadata
        """
        if value is None:
            return SanitizationResult(None, None)

        original_value = value
        sanitized_value = str(value)
        result = SanitizationResult(original_value, sanitized_value)

        # Determine strictness
        strict_mode = strict_mode if strict_mode is not None else (
            self.level in [SanitizationLevel.STRICT, SanitizationLevel.PARANOID]
        )

        # Determine categories to apply
        if categories is None:
            categories = list(self.rules.keys())

        try:
            # Apply rule-based sanitization
            for category in categories:
                if category in self.rules:
                    sanitized_value = self._apply_category_rules(
                        sanitized_value, category, result, strict_mode
                    )

            # Apply built-in sanitizers
            sanitized_value = self._apply_builtin_sanitizers(sanitized_value, result)

            # Apply custom sanitizers
            for name, sanitizer in self.custom_sanitizers.items():
                try:
                    custom_result = sanitizer(sanitized_value)
                    if custom_result != sanitized_value:
                        sanitized_value = custom_result
                        result.add_applied_rule(f"custom_{name}")
                        result.was_modified = True
                except Exception as e:
                    self.logger.warning(f"Custom sanitizer {name} failed: {str(e)}")

            # Final security check
            if strict_mode:
                self._perform_security_scan(sanitized_value, result)

            result.sanitized_value = sanitized_value
            result.was_modified = (original_value != sanitized_value)

        except Exception as e:
            raise SanitizationError(
                message=f"Sanitization failed: {str(e)}",
                context={'original_value': str(original_value)[:100]},
                cause=e
            )

        return result

    def _apply_category_rules(
        self,
        value: str,
        category: str,
        result: SanitizationResult,
        strict_mode: bool
    ) -> str:
        """Apply sanitization rules from a specific category"""
        sanitized = value

        for rule in self.rules[category]:
            if not rule.enabled:
                continue

            matches = rule.pattern.findall(sanitized)
            if matches:
                if rule.strategy == SanitizationStrategy.REJECT and strict_mode:
                    raise SecurityValidationError(
                        message=f"Input rejected due to rule: {rule.name}",
                        threat_type=category,
                        context={'matches': matches[:5]}  # Limit logged matches
                    )

                # Apply sanitization strategy
                if rule.strategy == SanitizationStrategy.REMOVE:
                    sanitized = rule.pattern.sub('', sanitized)
                elif rule.strategy == SanitizationStrategy.ESCAPE:
                    sanitized = self._escape_matches(sanitized, rule.pattern)
                elif rule.strategy == SanitizationStrategy.REPLACE:
                    sanitized = rule.pattern.sub(rule.replacement, sanitized)

                if sanitized != value:
                    result.add_applied_rule(rule.name)
                    result.was_modified = True

                    if category in ['html', 'sql', 'command']:
                        result.add_security_issue(f"Detected {category} injection attempt")

        return sanitized

    def _apply_builtin_sanitizers(self, value: str, result: SanitizationResult) -> str:
        """Apply built-in sanitization functions"""
        sanitized = value

        # Advanced XSS prevention with bleach (if available)
        if BLEACH_AVAILABLE and self.level in [SanitizationLevel.STRICT, SanitizationLevel.PARANOID]:
            # Define allowed tags and attributes for different contexts
            if self.level == SanitizationLevel.STRICT:
                # Allow basic formatting
                allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'p', 'br']
                allowed_attributes = {}
            else:  # PARANOID
                # Strip all HTML
                allowed_tags = []
                allowed_attributes = {}

            bleach_cleaned = bleach.clean(
                sanitized,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True,
                strip_comments=True
            )

            if bleach_cleaned != sanitized:
                sanitized = bleach_cleaned
                result.add_applied_rule("bleach_html_sanitization")
                result.was_modified = True
        else:
            # Fallback to basic HTML entity encoding for XSS prevention
            if self.level in [SanitizationLevel.MODERATE, SanitizationLevel.STRICT, SanitizationLevel.PARANOID]:
                html_escaped = html.escape(sanitized, quote=True)
                if html_escaped != sanitized:
                    sanitized = html_escaped
                    result.add_applied_rule("html_entity_encoding")
                    result.was_modified = True

        # URL encoding for special characters
        if self.level in [SanitizationLevel.STRICT, SanitizationLevel.PARANOID]:
            # Only encode truly dangerous characters in URLs
            dangerous_chars = ['<', '>', '"', "'", '&']
            for char in dangerous_chars:
                if char in sanitized:
                    sanitized = sanitized.replace(char, urllib.parse.quote(char))
                    result.add_applied_rule("url_encoding")
                    result.was_modified = True

        return sanitized

    def _escape_matches(self, value: str, pattern: re.Pattern) -> str:
        """Escape matches found by pattern"""
        def escape_func(match):
            return html.escape(match.group(0), quote=True)

        return pattern.sub(escape_func, value)

    def _perform_security_scan(self, value: str, result: SanitizationResult):
        """Perform additional security scanning in strict mode"""
        # Check for remaining suspicious patterns
        suspicious_patterns = [
            (r'<[^>]+>', 'html_tags'),
            (r'javascript:', 'javascript_protocol'),
            (r'data:.*base64', 'base64_data_uri'),
            (r'\b(eval|setTimeout|setInterval)\s*\(', 'dangerous_js_functions')
        ]

        for pattern, threat_type in suspicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                result.add_security_issue(f"Suspicious pattern detected: {threat_type}")

    def sanitize_filename(self, filename: str) -> str:
        """Specialized sanitization for filenames"""
        if not filename:
            return filename

        # Remove path traversal
        sanitized = re.sub(r'[\.]{2,}', '.', filename)

        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', sanitized)

        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext

        # Ensure it's not empty or just dots
        if not sanitized or sanitized.strip('.') == '':
            sanitized = 'unnamed_file'

        return sanitized

    def sanitize_sql_identifier(self, identifier: str) -> str:
        """Specialized sanitization for SQL identifiers"""
        if not identifier:
            return identifier

        # Only allow alphanumeric and underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', identifier)

        # Ensure it starts with letter or underscore
        if sanitized and not re.match(r'^[a-zA-Z_]', sanitized):
            sanitized = '_' + sanitized

        return sanitized

    def sanitize_html_output(self, html_content: str, context: str = "general") -> str:
        """
        Specialized HTML output sanitization for XSS prevention
        Context-aware sanitization for different output contexts
        """
        if not html_content:
            return html_content

        if not BLEACH_AVAILABLE:
            # Fallback to basic escaping
            return html.escape(html_content, quote=True)

        # Context-specific sanitization rules
        context_rules = {
            'general': {
                'tags': ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li'],
                'attributes': {
                    '*': ['class'],
                    'a': ['href', 'title'],
                }
            },
            'comment': {
                'tags': ['b', 'i', 'strong', 'em'],
                'attributes': {}
            },
            'strict': {
                'tags': [],
                'attributes': {}
            },
            'email': {
                'tags': ['p', 'br', 'strong', 'em'],
                'attributes': {}
            }
        }

        rules = context_rules.get(context, context_rules['strict'])

        # Use bleach for comprehensive XSS protection
        sanitized = bleach.clean(
            html_content,
            tags=rules['tags'],
            attributes=rules['attributes'],
            strip=True,
            strip_comments=True
        )

        # Additional XSS protection for URLs
        if BLEACH_AVAILABLE:
            sanitized = bleach.linkify(
                sanitized,
                callbacks=[self._validate_url_callback],
                skip_tags=['pre', 'code']
            )

        return sanitized

    def _validate_url_callback(self, attrs, new=False):
        """Callback to validate URLs during linkification"""
        href = attrs.get('href', '')

        # Block dangerous protocols
        dangerous_protocols = ['javascript:', 'vbscript:', 'data:', 'file:']
        for protocol in dangerous_protocols:
            if href.lower().startswith(protocol):
                return None  # Remove the link

        # Only allow http/https
        if not href.startswith(('http://', 'https://', '//', '/')):
            return None

        return attrs

    def sanitize_css(self, css_content: str) -> str:
        """
        Sanitize CSS content to prevent CSS injection attacks
        """
        if not css_content:
            return css_content

        # Remove dangerous CSS properties and values
        dangerous_patterns = [
            r'expression\s*\(',      # CSS expressions
            r'javascript\s*:',       # JavaScript URLs
            r'vbscript\s*:',        # VBScript URLs
            r'@import',             # CSS imports
            r'behavior\s*:',        # IE behaviors
            r'binding\s*:',         # Mozilla bindings
            r'-moz-binding',        # Mozilla bindings
            r'url\s*\(\s*["\']?javascript:', # JavaScript URLs in url()
        ]

        sanitized = css_content
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        return sanitized

    def sanitize_json_output(self, json_data: str) -> str:
        """
        Sanitize JSON output to prevent JSON injection
        """
        if not json_data:
            return json_data

        # Escape potential XSS in JSON strings
        # This is important when JSON is embedded in HTML
        dangerous_chars = {
            '<': '\\u003c',
            '>': '\\u003e',
            '&': '\\u0026',
            "'": '\\u0027',
            '"': '\\"'
        }

        sanitized = json_data
        for char, replacement in dangerous_chars.items():
            if char in sanitized:
                sanitized = sanitized.replace(char, replacement)

        return sanitized

    def get_rule_count(self) -> Dict[str, int]:
        """Get count of rules by category"""
        return {category: len(rules) for category, rules in self.rules.items()}

    def disable_category(self, category: str):
        """Disable all rules in a category"""
        if category in self.rules:
            for rule in self.rules[category]:
                rule.enabled = False
            self.logger.info(f"Disabled all rules in category: {category}")

    def enable_category(self, category: str):
        """Enable all rules in a category"""
        if category in self.rules:
            for rule in self.rules[category]:
                rule.enabled = True
            self.logger.info(f"Enabled all rules in category: {category}")

    def __str__(self) -> str:
        total_rules = sum(len(rules) for rules in self.rules.values())
        return f"SanitizationEngine(level={self.level.value}, rules={total_rules})"

    def __repr__(self) -> str:
        return (
            f"SanitizationEngine("
            f"level={self.level.value}, "
            f"categories={list(self.rules.keys())}, "
            f"custom_sanitizers={len(self.custom_sanitizers)})"
        )