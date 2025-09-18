# SSA-24 Implementation Examples

## 🎯 **PRACTICAL IMPLEMENTATION EXAMPLES**

This document provides real-world implementation examples for the SSA-24 Input Validation Framework in various scenarios within the SenialSOLID application.

## 🌐 **WEB FORM VALIDATION**

### User Registration Form
```python
# presentacion/webapp/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length
from aplicacion.validation import (
    StringInputValidator,
    EmailValidator,
    PasswordValidator,
    validate_parameters
)

class UserRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

# presentacion/webapp/views.py
from flask import render_template, request, flash, redirect, url_for
from aplicacion.validation import ValidationPipeline, PipelineMode
from aplicacion.validation.rules import StringInputValidator, EmailValidator, PasswordValidator

def create_user_validation_pipeline():
    """Create validation pipeline for user registration"""
    pipeline = ValidationPipeline("user_registration", mode=PipelineMode.COLLECT_ALL)

    # Username validation
    pipeline.add_validator(
        StringInputValidator(
            min_length=3,
            max_length=30,
            allowed_pattern=StringInputValidator.ALPHANUMERIC_EXTENDED
        ),
        stage="basic_validation"
    )

    # Email validation
    pipeline.add_validator(
        EmailValidator(required=True, max_length=254),
        stage="format_validation"
    )

    # Password validation
    pipeline.add_validator(
        PasswordValidator(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        ),
        stage="security_validation"
    )

    return pipeline

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()

    if form.validate_on_submit():
        # Additional validation with SSA-24 framework
        pipeline = create_user_validation_pipeline()

        # Validate each field
        username_result = pipeline.get_stage_validators("basic_validation")[0].validate(
            form.username.data,
            context={'field_name': 'username', 'user_ip': request.remote_addr}
        )

        email_result = pipeline.get_stage_validators("format_validation")[0].validate(
            form.email.data,
            context={'field_name': 'email'}
        )

        password_result = pipeline.get_stage_validators("security_validation")[0].validate(
            form.password.data,
            context={'field_name': 'password'}
        )

        # Check all validation results
        all_results = [username_result, email_result, password_result]

        if all(result.is_valid for result in all_results):
            # All validations passed - proceed with registration
            try:
                create_user(
                    username=username_result.sanitized_value,
                    email=email_result.sanitized_value,
                    password=password_result.sanitized_value
                )
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                flash('Registration failed. Please try again.', 'error')
                logger.error(f"Registration error: {e}")
        else:
            # Validation failed - show errors
            for result in all_results:
                for error in result.errors:
                    flash(f'Validation error: {error.message}', 'error')

    return render_template('register.html', form=form)
```

### Signal Data Upload Form
```python
# presentacion/webapp/signal_forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SignalUploadForm(FlaskForm):
    signal_file = FileField('Signal File', validators=[FileRequired()])
    sample_rate = FloatField('Sample Rate (Hz)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=100000.0)
    ])
    frequency = FloatField('Signal Frequency (Hz)', validators=[
        DataRequired(),
        NumberRange(min=0.1, max=50000.0)
    ])
    amplitude = FloatField('Amplitude (V)', validators=[
        DataRequired(),
        NumberRange(min=-10.0, max=10.0)
    ])
    signal_type = SelectField('Signal Type', choices=[
        ('sine', 'Sine Wave'),
        ('square', 'Square Wave'),
        ('triangle', 'Triangle Wave'),
        ('sawtooth', 'Sawtooth Wave')
    ])
    submit = SubmitField('Upload Signal')

# Signal upload processing
@app.route('/signals/upload', methods=['GET', 'POST'])
def upload_signal():
    form = SignalUploadForm()

    if form.validate_on_submit():
        # Create comprehensive validation pipeline
        pipeline = create_signal_validation_pipeline()

        # Validate file upload
        file_result = validate_signal_file(form.signal_file.data)

        # Validate signal parameters
        param_context = {
            'user_id': current_user.id,
            'upload_timestamp': datetime.now().isoformat(),
            'file_name': form.signal_file.data.filename
        }

        sample_rate_result = pipeline.validate({
            'parameter_type': 'sample_rate',
            'value': form.sample_rate.data
        }, context=param_context)

        frequency_result = pipeline.validate({
            'parameter_type': 'frequency',
            'value': form.frequency.data
        }, context=param_context)

        amplitude_result = pipeline.validate({
            'parameter_type': 'amplitude',
            'value': form.amplitude.data
        }, context=param_context)

        # Process if all validations pass
        if all(r.is_valid for r in [file_result, sample_rate_result, frequency_result, amplitude_result]):
            try:
                # Save signal with validated parameters
                signal_id = save_signal_data(
                    file_data=file_result.sanitized_value,
                    sample_rate=sample_rate_result.sanitized_value,
                    frequency=frequency_result.sanitized_value,
                    amplitude=amplitude_result.sanitized_value,
                    signal_type=form.signal_type.data
                )

                flash(f'Signal uploaded successfully! ID: {signal_id}', 'success')
                return redirect(url_for('view_signal', signal_id=signal_id))

            except Exception as e:
                flash('Upload failed. Please check your file and try again.', 'error')
                logger.error(f"Signal upload error: {e}")
        else:
            # Show validation errors
            for result in [file_result, sample_rate_result, frequency_result, amplitude_result]:
                for error in result.errors:
                    flash(f'Validation error: {error.message}', 'error')

    return render_template('upload_signal.html', form=form)

def create_signal_validation_pipeline():
    """Create validation pipeline for signal parameters"""
    from aplicacion.validation.rules import SignalParameterValidator

    pipeline = ValidationPipeline("signal_parameters")

    # Add signal-specific validators
    pipeline.add_validator(SignalParameterValidator('sample_rate'))
    pipeline.add_validator(SignalParameterValidator('frequency'))
    pipeline.add_validator(SignalParameterValidator('amplitude'))

    return pipeline

def validate_signal_file(file_upload):
    """Comprehensive file validation for signal uploads"""
    from aplicacion.validation.rules import (
        FileTypeValidator,
        FileSizeValidator,
        FileContentValidator,
        SignalFileValidator
    )

    # File type validation
    type_validator = FileTypeValidator(
        allowed_extensions=['wav', 'csv', 'json', 'txt'],
        strict_mime_check=True
    )

    # File size validation (max 50MB for signal files)
    size_validator = FileSizeValidator(
        max_size=50 * 1024 * 1024,
        min_size=1024
    )

    # Content security validation
    content_validator = FileContentValidator(scan_content=True)

    # Signal-specific validation
    signal_validator = SignalFileValidator()

    # Run all validations
    validators = [type_validator, size_validator, content_validator, signal_validator]

    for validator in validators:
        result = validator.validate(file_upload)
        if not result.is_valid:
            return result

    return ValidationResult(is_valid=True, sanitized_value=file_upload)
```

## 🔗 **API ENDPOINT VALIDATION**

### REST API with Comprehensive Validation
```python
# presentacion/webapp/api_views.py
from flask import Blueprint, request, jsonify
from functools import wraps
from aplicacion.validation import ValidationPipeline, SanitizationEngine, SanitizationLevel
from aplicacion.validation.rules import (
    StringInputValidator,
    NumericInputValidator,
    EmailValidator,
    SQLInjectionValidator,
    FilePathValidator
)
from aplicacion.validation.decorators import validate_parameters, auto_sanitize

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def api_validation_required(pipeline_name):
    """Decorator for API endpoint validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get validation pipeline for this endpoint
            pipeline = get_api_validation_pipeline(pipeline_name)

            # Validate request data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            # Add request context
            context = {
                'endpoint': f.__name__,
                'method': request.method,
                'user_agent': request.headers.get('User-Agent'),
                'remote_addr': request.remote_addr,
                'timestamp': datetime.now().isoformat()
            }

            # Validate each field
            validation_errors = []
            sanitized_data = {}

            for field_name, field_value in data.items():
                result = pipeline.validate(field_value, context={
                    **context,
                    'field_name': field_name
                })

                if result.is_valid:
                    sanitized_data[field_name] = result.sanitized_value
                else:
                    validation_errors.extend([
                        {
                            'field': field_name,
                            'message': error.message,
                            'type': error.__class__.__name__
                        }
                        for error in result.errors
                    ])

            if validation_errors:
                return jsonify({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': validation_errors
                }), 400

            # Replace request data with sanitized data
            request.validated_data = sanitized_data

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api_bp.route('/users', methods=['POST'])
@api_validation_required('user_creation')
def create_user_api():
    """Create user via API with full validation"""
    data = request.validated_data

    try:
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', '')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'user_id': user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"User creation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'User creation failed'
        }), 500

@api_bp.route('/signals/<int:signal_id>/data', methods=['GET'])
@auto_sanitize(level=SanitizationLevel.MODERATE)
def get_signal_data_api(signal_id):
    """Get signal data with parameter validation"""
    # Validate query parameters
    param_validator = NumericInputValidator(min_value=1, max_value=1000000)

    # Validate signal_id
    id_result = param_validator.validate(signal_id, context={
        'field_name': 'signal_id',
        'endpoint': 'get_signal_data'
    })

    if not id_result.is_valid:
        return jsonify({
            'status': 'error',
            'message': 'Invalid signal ID'
        }), 400

    # Validate optional query parameters
    start_sample = request.args.get('start', 0, type=int)
    end_sample = request.args.get('end', -1, type=int)
    format_type = request.args.get('format', 'json')

    # Validate format parameter
    format_validator = StringInputValidator(
        allowed_pattern=r'^(json|csv|binary)$',
        max_length=10
    )

    format_result = format_validator.validate(format_type)
    if not format_result.is_valid:
        return jsonify({
            'status': 'error',
            'message': 'Invalid format parameter'
        }), 400

    try:
        # Get signal data with validated parameters
        signal = Signal.query.get_or_404(id_result.sanitized_value)
        data = signal.get_data_range(start_sample, end_sample)

        if format_result.sanitized_value == 'json':
            return jsonify({
                'status': 'success',
                'signal_id': signal.id,
                'data': data.tolist(),
                'metadata': {
                    'sample_rate': signal.sample_rate,
                    'length': len(data),
                    'start_sample': start_sample,
                    'end_sample': end_sample if end_sample != -1 else len(data)
                }
            })
        elif format_result.sanitized_value == 'csv':
            # Return CSV format
            csv_data = '\n'.join(map(str, data))
            return Response(csv_data, mimetype='text/csv')

    except Exception as e:
        logger.error(f"Signal data retrieval failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve signal data'
        }), 500

def get_api_validation_pipeline(pipeline_name):
    """Get validation pipeline for specific API endpoint"""
    pipelines = {
        'user_creation': create_user_api_pipeline(),
        'signal_upload': create_signal_api_pipeline(),
        'search': create_search_api_pipeline()
    }

    return pipelines.get(pipeline_name, create_default_api_pipeline())

def create_user_api_pipeline():
    """Validation pipeline for user creation API"""
    pipeline = ValidationPipeline("user_api_creation")

    # Basic input validation
    pipeline.add_validator(
        StringInputValidator(max_length=1000),
        stage="basic_validation"
    )

    # Security validation
    pipeline.add_validator(
        SQLInjectionValidator(strict_mode=True),
        stage="security_validation"
    )

    # Field-specific validation would be handled by field-specific validators
    return pipeline

def create_search_api_pipeline():
    """Validation pipeline for search API endpoints"""
    pipeline = ValidationPipeline("search_api")

    # Input length limits
    pipeline.add_validator(
        StringInputValidator(max_length=200),
        stage="basic_validation"
    )

    # Security checks
    pipeline.add_validator(
        SQLInjectionValidator(strict_mode=True),
        stage="security_validation"
    )

    # Path traversal protection
    pipeline.add_validator(
        FilePathValidator(strict_mode=True),
        stage="security_validation"
    )

    return pipeline
```

## 🎛️ **DOMAIN LAYER INTEGRATION**

### Signal Processing with Validation
```python
# dominio/adquisicion/adquisidor.py
from aplicacion.validation import ValidationPipeline
from aplicacion.validation.rules import (
    SignalParameterValidator,
    SignalDataValidator,
    NumericInputValidator
)

class SignalAcquisitionService:
    """Signal acquisition with integrated validation"""

    def __init__(self):
        self.validation_pipeline = self._create_validation_pipeline()
        self.data_validator = SignalDataValidator(
            max_length=1000000,  # 1M samples max
            check_anomalies=True,
            anomaly_threshold=3.0
        )

    def _create_validation_pipeline(self):
        """Create validation pipeline for signal acquisition"""
        pipeline = ValidationPipeline("signal_acquisition")

        # Parameter validation
        pipeline.add_validator(
            SignalParameterValidator('sample_rate'),
            stage="parameter_validation"
        )
        pipeline.add_validator(
            SignalParameterValidator('frequency'),
            stage="parameter_validation"
        )
        pipeline.add_validator(
            SignalParameterValidator('amplitude'),
            stage="parameter_validation"
        )

        # Range validation
        pipeline.add_validator(
            NumericInputValidator(min_value=0.1, max_value=100000.0),
            stage="range_validation"
        )

        return pipeline

    def acquire_signal(self, acquisition_config):
        """Acquire signal with comprehensive validation"""
        # Validate acquisition configuration
        config_result = self._validate_acquisition_config(acquisition_config)

        if not config_result.is_valid:
            raise SignalValidationError(
                message="Invalid acquisition configuration",
                context={'errors': [e.message for e in config_result.errors]}
            )

        # Use validated configuration
        validated_config = config_result.sanitized_value

        try:
            # Perform signal acquisition
            raw_signal = self._acquire_raw_signal(validated_config)

            # Validate acquired signal data
            data_result = self.data_validator.validate(raw_signal, context={
                'acquisition_config': validated_config,
                'timestamp': datetime.now().isoformat()
            })

            if not data_result.is_valid:
                raise SignalValidationError(
                    message="Acquired signal data failed validation",
                    context={'data_errors': [e.message for e in data_result.errors]}
                )

            # Return validated signal
            return Signal(
                data=data_result.sanitized_value,
                sample_rate=validated_config['sample_rate'],
                frequency=validated_config['frequency'],
                amplitude=validated_config['amplitude'],
                metadata=data_result.metadata
            )

        except Exception as e:
            logger.error(f"Signal acquisition failed: {e}")
            raise SignalAcquisitionError(f"Acquisition failed: {str(e)}")

    def _validate_acquisition_config(self, config):
        """Validate signal acquisition configuration"""
        validation_context = {
            'operation': 'signal_acquisition',
            'timestamp': datetime.now().isoformat()
        }

        # Validate each parameter
        param_results = {}

        for param_name, param_value in config.items():
            if param_name in ['sample_rate', 'frequency', 'amplitude']:
                result = self.validation_pipeline.validate({
                    'parameter_type': param_name,
                    'value': param_value
                }, context={**validation_context, 'parameter': param_name})

                param_results[param_name] = result

        # Check if all validations passed
        all_valid = all(result.is_valid for result in param_results.values())

        if all_valid:
            sanitized_config = {
                param: result.sanitized_value
                for param, result in param_results.items()
            }
            return ValidationResult(is_valid=True, sanitized_value=sanitized_config)
        else:
            # Collect all errors
            all_errors = []
            for param, result in param_results.items():
                all_errors.extend(result.errors)

            result = ValidationResult(is_valid=False)
            for error in all_errors:
                result.add_error(error)

            return result

    def _acquire_raw_signal(self, config):
        """Simulate signal acquisition (replace with actual implementation)"""
        import numpy as np

        duration = 1.0  # 1 second
        sample_rate = config['sample_rate']
        frequency = config['frequency']
        amplitude = config['amplitude']

        t = np.linspace(0, duration, int(sample_rate * duration))
        signal = amplitude * np.sin(2 * np.pi * frequency * t)

        return signal.tolist()

# Usage in domain services
class SignalProcessingService:
    """Signal processing service with validation"""

    def __init__(self):
        self.acquisition_service = SignalAcquisitionService()
        self.filter_validator = self._create_filter_validator()

    def _create_filter_validator(self):
        """Create validator for filter parameters"""
        return ValidationPipeline("filter_parameters").add_validator(
            NumericInputValidator(min_value=0.1, max_value=50000.0)
        )

    def process_signal(self, signal_id, processing_params):
        """Process signal with parameter validation"""
        # Validate processing parameters
        param_result = self._validate_processing_params(processing_params)

        if not param_result.is_valid:
            raise ValidationError("Invalid processing parameters")

        # Get signal
        signal = self._get_signal(signal_id)

        # Apply validated processing
        processed_signal = self._apply_processing(signal, param_result.sanitized_value)

        return processed_signal

    def _validate_processing_params(self, params):
        """Validate signal processing parameters"""
        # Implementation depends on specific processing operations
        validators = {
            'low_pass_freq': NumericInputValidator(min_value=0.1, max_value=25000.0),
            'high_pass_freq': NumericInputValidator(min_value=0.1, max_value=25000.0),
            'gain': NumericInputValidator(min_value=0.1, max_value=100.0)
        }

        validated_params = {}
        all_errors = []

        for param_name, param_value in params.items():
            if param_name in validators:
                result = validators[param_name].validate(param_value)
                if result.is_valid:
                    validated_params[param_name] = result.sanitized_value
                else:
                    all_errors.extend(result.errors)

        if all_errors:
            result = ValidationResult(is_valid=False)
            for error in all_errors:
                result.add_error(error)
            return result

        return ValidationResult(is_valid=True, sanitized_value=validated_params)
```

## 🔐 **SECURITY INTEGRATION**

### Authentication and Authorization with Validation
```python
# aplicacion/security/auth_service.py
from aplicacion.validation import SanitizationEngine, SanitizationLevel
from aplicacion.validation.rules import (
    StringInputValidator,
    PasswordValidator,
    EmailValidator,
    SQLInjectionValidator
)

class AuthenticationService:
    """Authentication service with comprehensive input validation"""

    def __init__(self):
        self.sanitizer = SanitizationEngine(SanitizationLevel.STRICT)
        self.login_validator = self._create_login_validator()
        self.session_validator = self._create_session_validator()

    def _create_login_validator(self):
        """Create validator for login credentials"""
        pipeline = ValidationPipeline("login_validation")

        # Basic input validation
        pipeline.add_validator(
            StringInputValidator(max_length=254),  # Email max length
            stage="basic_validation"
        )

        # Security validation
        pipeline.add_validator(
            SQLInjectionValidator(strict_mode=True),
            stage="security_validation"
        )

        return pipeline

    def _create_session_validator(self):
        """Create validator for session tokens"""
        return StringInputValidator(
            allowed_pattern=r'^[a-zA-Z0-9_-]+$',
            min_length=32,
            max_length=128
        )

    def authenticate_user(self, email, password, request_context):
        """Authenticate user with comprehensive validation"""
        # Sanitize inputs
        email_result = self.sanitizer.sanitize(email)
        password_result = self.sanitizer.sanitize(password)

        # Log security events if sanitization modified inputs
        if email_result.was_modified:
            logger.warning(
                "Suspicious email input detected",
                extra={
                    'original_length': len(email),
                    'sanitized_length': len(email_result.sanitized_value),
                    'remote_addr': request_context.get('remote_addr'),
                    'user_agent': request_context.get('user_agent')
                }
            )

        if password_result.was_modified:
            logger.critical(
                "Suspicious password input detected",
                extra={
                    'security_issues': password_result.security_issues,
                    'remote_addr': request_context.get('remote_addr')
                }
            )
            # Reject authentication attempt with suspicious password
            raise SecurityValidationError(
                message="Authentication rejected due to security concerns",
                threat_type="suspicious_credential"
            )

        # Validate email format
        email_validator = EmailValidator()
        email_validation = email_validator.validate(email_result.sanitized_value)

        if not email_validation.is_valid:
            raise ValidationError("Invalid email format")

        # Validate login attempt
        login_validation = self.login_validator.validate(email_result.sanitized_value, context={
            'operation': 'login',
            'remote_addr': request_context.get('remote_addr'),
            'user_agent': request_context.get('user_agent')
        })

        if not login_validation.is_valid:
            logger.warning(
                "Login validation failed",
                extra={
                    'email': email_validation.sanitized_value,
                    'errors': [e.message for e in login_validation.errors],
                    'remote_addr': request_context.get('remote_addr')
                }
            )
            raise ValidationError("Login validation failed")

        try:
            # Perform authentication with validated inputs
            user = User.authenticate(
                email=email_validation.sanitized_value,
                password=password  # Use original password for authentication
            )

            if user:
                # Create secure session
                session_token = self._create_session_token(user, request_context)

                logger.info(
                    "User authenticated successfully",
                    extra={
                        'user_id': user.id,
                        'email': user.email,
                        'remote_addr': request_context.get('remote_addr')
                    }
                )

                return {
                    'user': user,
                    'session_token': session_token,
                    'success': True
                }
            else:
                logger.warning(
                    "Authentication failed - invalid credentials",
                    extra={
                        'email': email_validation.sanitized_value,
                        'remote_addr': request_context.get('remote_addr')
                    }
                )
                return {
                    'success': False,
                    'message': 'Invalid credentials'
                }

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Authentication failed")

    def validate_session_token(self, token, request_context):
        """Validate session token with security checks"""
        # Validate token format
        token_result = self.session_validator.validate(token, context={
            'operation': 'session_validation',
            'remote_addr': request_context.get('remote_addr')
        })

        if not token_result.is_valid:
            logger.warning(
                "Invalid session token format",
                extra={
                    'token_preview': token[:8] + '...' if len(token) > 8 else token,
                    'remote_addr': request_context.get('remote_addr')
                }
            )
            return None

        try:
            # Validate session in database
            session = UserSession.query.filter_by(
                token=token_result.sanitized_value,
                is_active=True
            ).first()

            if session and not session.is_expired():
                return session.user
            else:
                logger.info(
                    "Session validation failed - expired or invalid",
                    extra={
                        'token_preview': token[:8] + '...',
                        'remote_addr': request_context.get('remote_addr')
                    }
                )
                return None

        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None

    def _create_session_token(self, user, request_context):
        """Create secure session token"""
        import secrets
        import hashlib

        # Generate secure random token
        token = secrets.token_urlsafe(32)

        # Create session record
        session = UserSession(
            user_id=user.id,
            token=token,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            remote_addr=request_context.get('remote_addr'),
            user_agent=request_context.get('user_agent')
        )

        db.session.add(session)
        db.session.commit()

        return token

# Rate limiting with validation
class RateLimitingService:
    """Rate limiting service with input validation"""

    def __init__(self):
        self.ip_validator = StringInputValidator(
            allowed_pattern=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',  # IPv4
            max_length=15
        )

    def check_rate_limit(self, identifier, request_context):
        """Check rate limit with validated identifier"""
        # Validate IP address format
        ip_result = self.ip_validator.validate(identifier)

        if not ip_result.is_valid:
            logger.warning(
                "Invalid IP address format for rate limiting",
                extra={
                    'identifier': identifier,
                    'remote_addr': request_context.get('remote_addr')
                }
            )
            # Reject requests with invalid IP format
            return False, "Invalid request format"

        # Check rate limit with validated IP
        return self._check_redis_rate_limit(ip_result.sanitized_value)
```

This comprehensive set of implementation examples demonstrates how to integrate the SSA-24 Input Validation Framework across all layers of the SenialSOLID application, from web forms to domain services and security components.