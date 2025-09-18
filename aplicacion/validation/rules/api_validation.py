"""
API Validation for SSA-24 Input Validation Framework

Specialized validators for API requests, parameters, and data structures
"""

import json
import re
from typing import Any, Dict, List, Optional, Union, Type
import logging
from datetime import datetime
from urllib.parse import parse_qs, urlparse
import ipaddress

from ..framework.validator_base import AbstractValidator, ValidationResult
from ..exceptions.validation_exceptions import APIValidationError, SecurityValidationError


class APIParameterValidator(AbstractValidator):
    """
    Validator for API request parameters with type checking and constraints
    """

    def __init__(
        self,
        parameter_name: str,
        parameter_type: Type,
        required: bool = True,
        default_value: Any = None,
        allowed_values: List[Any] = None,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        min_length: int = None,
        max_length: int = None,
        pattern: str = None
    ):
        super().__init__(f"api_param_{parameter_name}")
        self.parameter_name = parameter_name
        self.parameter_type = parameter_type
        self.required = required
        self.default_value = default_value
        self.allowed_values = allowed_values
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate API parameter"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}
        context['parameter_name'] = self.parameter_name

        # Handle missing values
        if value is None or value == '':
            if self.required:
                error = APIValidationError(
                    message=f"Required parameter '{self.parameter_name}' is missing",
                    endpoint=context.get('endpoint', 'unknown'),
                    invalid_parameters=[self.parameter_name],
                    context=context
                )
                result.add_error(error)
                return result
            elif self.default_value is not None:
                value = self.default_value
                result.sanitized_value = value

        if value is None:
            return result

        # Type conversion and validation
        try:
            converted_value = self._convert_type(value)
        except (ValueError, TypeError) as e:
            error = APIValidationError(
                message=f"Parameter '{self.parameter_name}' type error: {str(e)}",
                endpoint=context.get('endpoint', 'unknown'),
                invalid_parameters=[self.parameter_name],
                context={**context, 'expected_type': self.parameter_type.__name__}
            )
            result.add_error(error)
            return result

        # Value constraints validation
        self._validate_constraints(converted_value, result, context)

        result.sanitized_value = converted_value
        return result

    def _convert_type(self, value: Any) -> Any:
        """Convert value to expected type"""
        if isinstance(value, self.parameter_type):
            return value

        if self.parameter_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif self.parameter_type == int:
            return int(float(value))  # Handle strings like "10.0"
        elif self.parameter_type == float:
            return float(value)
        elif self.parameter_type == str:
            return str(value)
        elif self.parameter_type == list:
            if isinstance(value, str):
                # Try to parse as JSON array or comma-separated
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return [x.strip() for x in value.split(',')]
            return list(value)
        elif self.parameter_type == dict:
            if isinstance(value, str):
                return json.loads(value)
            return dict(value)
        else:
            return self.parameter_type(value)

    def _validate_constraints(self, value: Any, result: ValidationResult, context: Dict[str, Any]):
        """Validate value constraints"""
        # Allowed values check
        if self.allowed_values and value not in self.allowed_values:
            error = APIValidationError(
                message=f"Parameter '{self.parameter_name}' value '{value}' not in allowed values: {self.allowed_values}",
                endpoint=context.get('endpoint', 'unknown'),
                invalid_parameters=[self.parameter_name],
                context={**context, 'allowed_values': self.allowed_values}
            )
            result.add_error(error)

        # Numeric range checks
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                error = APIValidationError(
                    message=f"Parameter '{self.parameter_name}' value {value} below minimum {self.min_value}",
                    endpoint=context.get('endpoint', 'unknown'),
                    invalid_parameters=[self.parameter_name],
                    context=context
                )
                result.add_error(error)

            if self.max_value is not None and value > self.max_value:
                error = APIValidationError(
                    message=f"Parameter '{self.parameter_name}' value {value} exceeds maximum {self.max_value}",
                    endpoint=context.get('endpoint', 'unknown'),
                    invalid_parameters=[self.parameter_name],
                    context=context
                )
                result.add_error(error)

        # Length checks for sequences
        if hasattr(value, '__len__'):
            length = len(value)
            if self.min_length is not None and length < self.min_length:
                error = APIValidationError(
                    message=f"Parameter '{self.parameter_name}' length {length} below minimum {self.min_length}",
                    endpoint=context.get('endpoint', 'unknown'),
                    invalid_parameters=[self.parameter_name],
                    context=context
                )
                result.add_error(error)

            if self.max_length is not None and length > self.max_length:
                error = APIValidationError(
                    message=f"Parameter '{self.parameter_name}' length {length} exceeds maximum {self.max_length}",
                    endpoint=context.get('endpoint', 'unknown'),
                    invalid_parameters=[self.parameter_name],
                    context=context
                )
                result.add_error(error)

        # Pattern validation for strings
        if self.pattern and isinstance(value, str):
            if not self.pattern.match(value):
                error = APIValidationError(
                    message=f"Parameter '{self.parameter_name}' does not match required pattern",
                    endpoint=context.get('endpoint', 'unknown'),
                    invalid_parameters=[self.parameter_name],
                    context=context
                )
                result.add_error(error)


class JSONSchemaValidator(AbstractValidator):
    """
    Validator for JSON request bodies with schema validation
    """

    def __init__(self, schema: Dict[str, Any], strict: bool = True):
        super().__init__("json_schema_validator")
        self.schema = schema
        self.strict = strict

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate JSON against schema"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Parse JSON if string
        if isinstance(value, str):
            try:
                json_data = json.loads(value)
            except json.JSONDecodeError as e:
                error = APIValidationError(
                    message=f"Invalid JSON format: {str(e)}",
                    endpoint=context.get('endpoint', 'unknown'),
                    context=context
                )
                result.add_error(error)
                return result
        elif isinstance(value, dict):
            json_data = value
        else:
            error = APIValidationError(
                message="Request body must be valid JSON",
                endpoint=context.get('endpoint', 'unknown'),
                context=context
            )
            result.add_error(error)
            return result

        # Validate against schema
        self._validate_schema(json_data, self.schema, result, context, path="")

        result.sanitized_value = json_data
        return result

    def _validate_schema(
        self,
        data: Any,
        schema: Dict[str, Any],
        result: ValidationResult,
        context: Dict[str, Any],
        path: str
    ):
        """Recursively validate data against schema"""
        schema_type = schema.get('type')
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})

        # Type validation
        if schema_type == 'object' and not isinstance(data, dict):
            error = APIValidationError(
                message=f"Expected object at {path or 'root'}, got {type(data).__name__}",
                endpoint=context.get('endpoint', 'unknown'),
                context={**context, 'path': path}
            )
            result.add_error(error)
            return

        if schema_type == 'array' and not isinstance(data, list):
            error = APIValidationError(
                message=f"Expected array at {path or 'root'}, got {type(data).__name__}",
                endpoint=context.get('endpoint', 'unknown'),
                context={**context, 'path': path}
            )
            result.add_error(error)
            return

        # Object validation
        if isinstance(data, dict):
            # Check required fields
            for field in required_fields:
                if field not in data:
                    error = APIValidationError(
                        message=f"Required field '{field}' missing at {path or 'root'}",
                        endpoint=context.get('endpoint', 'unknown'),
                        invalid_parameters=[field],
                        context={**context, 'path': path}
                    )
                    result.add_error(error)

            # Validate properties
            for field, value in data.items():
                field_path = f"{path}.{field}" if path else field
                if field in properties:
                    self._validate_schema(value, properties[field], result, context, field_path)
                elif self.strict:
                    result.add_warning(f"Unknown field '{field}' at {path or 'root'}")

        # Array validation
        elif isinstance(data, list):
            items_schema = schema.get('items')
            if items_schema:
                for i, item in enumerate(data):
                    item_path = f"{path}[{i}]"
                    self._validate_schema(item, items_schema, result, context, item_path)


class RateLimitValidator(AbstractValidator):
    """
    Validator for API rate limiting checks
    """

    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 3600,  # seconds (1 hour)
        per_client: bool = True
    ):
        super().__init__("rate_limit_validator")
        self.max_requests = max_requests
        self.time_window = time_window
        self.per_client = per_client
        self.request_history: Dict[str, List[datetime]] = {}

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate rate limit for client"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Get client identifier
        client_id = self._get_client_id(value, context)
        if not client_id:
            result.add_warning("Cannot identify client for rate limiting")
            return result

        # Get current time
        now = datetime.utcnow()

        # Initialize or clean history for client
        if client_id not in self.request_history:
            self.request_history[client_id] = []

        client_history = self.request_history[client_id]

        # Remove old requests outside time window
        cutoff_time = now.timestamp() - self.time_window
        client_history[:] = [
            req_time for req_time in client_history
            if req_time.timestamp() > cutoff_time
        ]

        # Check rate limit
        if len(client_history) >= self.max_requests:
            error = APIValidationError(
                message=f"Rate limit exceeded: {len(client_history)} requests in {self.time_window} seconds (limit: {self.max_requests})",
                endpoint=context.get('endpoint', 'unknown'),
                context={
                    **context,
                    'client_id': client_id,
                    'requests_count': len(client_history),
                    'rate_limit': self.max_requests,
                    'time_window': self.time_window
                }
            )
            result.add_error(error)
            return result

        # Add current request to history
        client_history.append(now)

        # Add rate limit info to metadata
        result.metadata.update({
            'requests_in_window': len(client_history),
            'rate_limit': self.max_requests,
            'time_window': self.time_window,
            'requests_remaining': self.max_requests - len(client_history)
        })

        return result

    def _get_client_id(self, value: Any, context: Dict[str, Any]) -> Optional[str]:
        """Extract client identifier from request"""
        # Try different sources for client ID
        if isinstance(value, dict):
            # From request data
            return value.get('client_id') or value.get('api_key') or value.get('user_id')

        # From context (IP address, user ID, etc.)
        if 'client_ip' in context:
            return context['client_ip']
        if 'user_id' in context:
            return str(context['user_id'])
        if 'api_key' in context:
            return context['api_key']

        return None


class IPWhitelistValidator(AbstractValidator):
    """
    Validator for IP address whitelisting
    """

    def __init__(self, allowed_ips: List[str], allow_private: bool = True):
        super().__init__("ip_whitelist_validator")
        self.allowed_networks = []
        self.allow_private = allow_private

        # Parse allowed IPs/networks
        for ip_str in allowed_ips:
            try:
                network = ipaddress.ip_network(ip_str, strict=False)
                self.allowed_networks.append(network)
            except ValueError:
                logging.warning(f"Invalid IP/network in whitelist: {ip_str}")

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate client IP against whitelist"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Get client IP
        client_ip = self._get_client_ip(value, context)
        if not client_ip:
            result.add_warning("Cannot determine client IP for whitelist validation")
            return result

        try:
            ip_addr = ipaddress.ip_address(client_ip)
        except ValueError:
            error = SecurityValidationError(
                message=f"Invalid client IP address: {client_ip}",
                threat_type="invalid_ip",
                context={**context, 'client_ip': client_ip}
            )
            result.add_error(error)
            return result

        # Check if IP is allowed
        is_allowed = False

        # Check against whitelist
        for network in self.allowed_networks:
            if ip_addr in network:
                is_allowed = True
                break

        # Check private networks if allowed
        if not is_allowed and self.allow_private and ip_addr.is_private:
            is_allowed = True

        # Check loopback for development
        if not is_allowed and ip_addr.is_loopback:
            is_allowed = True

        if not is_allowed:
            error = SecurityValidationError(
                message=f"Client IP {client_ip} not in whitelist",
                threat_type="ip_not_whitelisted",
                context={**context, 'client_ip': client_ip}
            )
            result.add_error(error)

        result.metadata['client_ip'] = client_ip
        result.metadata['is_private'] = ip_addr.is_private
        result.metadata['is_loopback'] = ip_addr.is_loopback

        return result

    def _get_client_ip(self, value: Any, context: Dict[str, Any]) -> Optional[str]:
        """Extract client IP from request"""
        # Try different sources
        if isinstance(value, dict) and 'client_ip' in value:
            return value['client_ip']

        if 'client_ip' in context:
            return context['client_ip']

        if 'request' in context:
            request = context['request']
            # Flask/Werkzeug request object
            if hasattr(request, 'remote_addr'):
                return request.remote_addr
            # Check headers for forwarded IP
            if hasattr(request, 'headers'):
                forwarded_for = request.headers.get('X-Forwarded-For')
                if forwarded_for:
                    return forwarded_for.split(',')[0].strip()

        return None


class APISecurityValidator(AbstractValidator):
    """
    Validator for general API security checks
    """

    def __init__(self):
        super().__init__("api_security_validator")

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Perform security validation on API request"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Check for suspicious patterns in request
        if isinstance(value, dict):
            self._check_injection_patterns(value, result, context)
            self._check_request_size(value, result, context)

        # Check request headers for security issues
        if 'headers' in context:
            self._validate_headers(context['headers'], result, context)

        return result

    def _check_injection_patterns(self, data: dict, result: ValidationResult, context: Dict[str, Any]):
        """Check for injection attack patterns"""
        injection_patterns = [
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)',  # SQL
            r'(<script|javascript:|vbscript:|onload=|onerror=)',  # XSS
            r'(\.\./|\.\.\\)',  # Path traversal
            r'(\beval\b|\bexec\b|\bsystem\b)',  # Code injection
        ]

        for key, value in data.items():
            if isinstance(value, str):
                for pattern in injection_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        error = SecurityValidationError(
                            message=f"Potential injection attack detected in parameter '{key}'",
                            threat_type="injection_attack",
                            context={**context, 'parameter': key, 'pattern': pattern}
                        )
                        result.add_error(error)

    def _check_request_size(self, data: dict, result: ValidationResult, context: Dict[str, Any]):
        """Check for unusually large requests"""
        try:
            request_size = len(json.dumps(data))
            max_size = 10 * 1024 * 1024  # 10MB

            if request_size > max_size:
                error = APIValidationError(
                    message=f"Request too large: {request_size} bytes (maximum: {max_size})",
                    endpoint=context.get('endpoint', 'unknown'),
                    context={**context, 'request_size': request_size}
                )
                result.add_error(error)

            result.metadata['request_size'] = request_size
        except Exception:
            result.add_warning("Could not calculate request size")

    def _validate_headers(self, headers: dict, result: ValidationResult, context: Dict[str, Any]):
        """Validate HTTP headers for security issues"""
        # Check for suspicious user agents
        user_agent = headers.get('User-Agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'wget', 'curl']

        for agent in suspicious_agents:
            if agent in user_agent:
                result.add_warning(f"Suspicious user agent detected: {agent}")

        # Check for missing security headers
        if 'Authorization' not in headers and context.get('requires_auth', True):
            result.add_warning("Missing Authorization header")


# Factory function for creating API validation pipeline
def create_api_validation_pipeline(
    endpoint_type: str = "general",
    rate_limit: int = 100,
    require_auth: bool = True
) -> 'ValidationPipeline':
    """
    Create a pre-configured validation pipeline for API endpoints

    Args:
        endpoint_type: Type of endpoint (general, public, internal)
        rate_limit: Maximum requests per hour
        require_auth: Whether authentication is required

    Returns:
        Configured ValidationPipeline
    """
    from ..framework.validation_pipeline import ValidationPipeline, PipelineStage

    pipeline = ValidationPipeline(f"api_validation_{endpoint_type}")

    # Security validation for all endpoints
    pipeline.add_validator(
        APISecurityValidator(),
        PipelineStage.SECURITY_VALIDATION
    )

    # Rate limiting
    pipeline.add_validator(
        RateLimitValidator(max_requests=rate_limit),
        PipelineStage.PRE_VALIDATION
    )

    # Endpoint-specific validation
    if endpoint_type == "public":
        # More restrictive for public endpoints
        pipeline.add_validator(
            IPWhitelistValidator(
                allowed_ips=['0.0.0.0/0'],  # Allow all but with monitoring
                allow_private=False
            ),
            PipelineStage.SECURITY_VALIDATION
        )

    elif endpoint_type == "internal":
        # Only allow internal networks
        pipeline.add_validator(
            IPWhitelistValidator(
                allowed_ips=['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'],
                allow_private=True
            ),
            PipelineStage.SECURITY_VALIDATION
        )

    return pipeline