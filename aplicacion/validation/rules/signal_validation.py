"""
Signal Data Validation for SSA-24 Input Validation Framework

Specialized validators for signal processing parameters and data
"""

import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple
import json
import logging

from ..framework.validator_base import AbstractValidator, ValidationResult, ValidationRule
from ..exceptions.validation_exceptions import SignalValidationError


class SignalParameterValidator(AbstractValidator):
    """
    Validator for signal processing parameters
    """

    # Signal parameter ranges based on typical signal processing requirements
    FREQUENCY_RANGE = (0.1, 50000.0)  # Hz - from 0.1 Hz to 50 kHz
    AMPLITUDE_RANGE = (-10.0, 10.0)   # Volts - ±10V typical range
    SAMPLE_RATE_RANGE = (1, 1000000)  # Hz - from 1 Hz to 1 MHz
    DURATION_RANGE = (0.001, 3600.0)  # seconds - from 1ms to 1 hour

    def __init__(self, parameter_type: str, custom_range: Tuple[float, float] = None):
        super().__init__(f"signal_{parameter_type}_validator")
        self.parameter_type = parameter_type
        self.custom_range = custom_range

        # Set validation range based on parameter type
        self.valid_range = self._get_parameter_range()

    def _get_parameter_range(self) -> Tuple[float, float]:
        """Get validation range for parameter type"""
        if self.custom_range:
            return self.custom_range

        range_map = {
            'frequency': self.FREQUENCY_RANGE,
            'amplitude': self.AMPLITUDE_RANGE,
            'sample_rate': self.SAMPLE_RATE_RANGE,
            'duration': self.DURATION_RANGE
        }

        return range_map.get(self.parameter_type, (0.0, float('inf')))

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate signal parameter value"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Type validation
        if not isinstance(value, (int, float, np.number)):
            error = SignalValidationError(
                message=f"Signal {self.parameter_type} must be numeric, got {type(value).__name__}",
                signal_parameter=self.parameter_type,
                actual_value=value,
                context=context
            )
            result.add_error(error)
            return result

        # Convert to float for range checking
        numeric_value = float(value)
        min_val, max_val = self.valid_range

        # Range validation
        if numeric_value < min_val or numeric_value > max_val:
            error = SignalValidationError(
                message=f"Signal {self.parameter_type} {numeric_value} outside valid range [{min_val}, {max_val}]",
                signal_parameter=self.parameter_type,
                expected_range=self.valid_range,
                actual_value=numeric_value,
                context=context
            )
            result.add_error(error)

        # Special validations per parameter type
        if self.parameter_type == 'frequency' and numeric_value <= 0:
            error = SignalValidationError(
                message="Frequency must be positive",
                signal_parameter=self.parameter_type,
                actual_value=numeric_value,
                context=context
            )
            result.add_error(error)

        elif self.parameter_type == 'sample_rate':
            # Sample rate should be at least 2x the maximum frequency (Nyquist)
            if 'max_frequency' in context:
                nyquist_limit = 2 * context['max_frequency']
                if numeric_value < nyquist_limit:
                    result.add_warning(
                        f"Sample rate {numeric_value} Hz may be insufficient for max frequency "
                        f"{context['max_frequency']} Hz (Nyquist limit: {nyquist_limit} Hz)"
                    )

        result.sanitized_value = numeric_value
        return result


class SignalDataValidator(AbstractValidator):
    """
    Validator for signal data arrays
    """

    def __init__(
        self,
        max_length: int = 1000000,
        min_length: int = 1,
        check_anomalies: bool = True,
        anomaly_threshold: float = 5.0
    ):
        super().__init__("signal_data_validator")
        self.max_length = max_length
        self.min_length = min_length
        self.check_anomalies = check_anomalies
        self.anomaly_threshold = anomaly_threshold  # Standard deviations

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate signal data array"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Type validation - accept lists, numpy arrays, or array-like objects
        if not hasattr(value, '__len__') or not hasattr(value, '__getitem__'):
            error = SignalValidationError(
                message="Signal data must be array-like (list, numpy array, etc.)",
                signal_parameter="data_array",
                actual_value=type(value).__name__,
                context=context
            )
            result.add_error(error)
            return result

        # Convert to numpy array for analysis
        try:
            data_array = np.array(value, dtype=float)
        except (ValueError, TypeError) as e:
            error = SignalValidationError(
                message=f"Cannot convert signal data to numeric array: {str(e)}",
                signal_parameter="data_array",
                actual_value=str(value)[:100],
                context=context
            )
            result.add_error(error)
            return result

        # Length validation
        if len(data_array) < self.min_length:
            error = SignalValidationError(
                message=f"Signal data too short: {len(data_array)} samples (minimum: {self.min_length})",
                signal_parameter="data_length",
                actual_value=len(data_array),
                context=context
            )
            result.add_error(error)

        if len(data_array) > self.max_length:
            error = SignalValidationError(
                message=f"Signal data too long: {len(data_array)} samples (maximum: {self.max_length})",
                signal_parameter="data_length",
                actual_value=len(data_array),
                context=context
            )
            result.add_error(error)

        # Check for invalid values
        if np.any(np.isnan(data_array)):
            error = SignalValidationError(
                message="Signal data contains NaN values",
                signal_parameter="data_quality",
                actual_value="NaN detected",
                context=context
            )
            result.add_error(error)

        if np.any(np.isinf(data_array)):
            error = SignalValidationError(
                message="Signal data contains infinite values",
                signal_parameter="data_quality",
                actual_value="Infinity detected",
                context=context
            )
            result.add_error(error)

        # Anomaly detection
        if self.check_anomalies and len(data_array) > 2:
            self._check_anomalies(data_array, result, context)

        # Store analysis metadata
        if not result.has_errors():
            result.metadata.update({
                'data_length': len(data_array),
                'mean_value': float(np.mean(data_array)),
                'std_value': float(np.std(data_array)),
                'min_value': float(np.min(data_array)),
                'max_value': float(np.max(data_array)),
                'dynamic_range': float(np.max(data_array) - np.min(data_array))
            })

        result.sanitized_value = data_array.tolist()  # Convert back to list for serialization
        return result

    def _check_anomalies(self, data_array: np.ndarray, result: ValidationResult, context: Dict[str, Any]):
        """Check for statistical anomalies in signal data"""
        try:
            mean_val = np.mean(data_array)
            std_val = np.std(data_array)

            if std_val == 0:
                result.add_warning("Signal data has zero variance (constant value)")
                return

            # Find outliers beyond threshold standard deviations
            z_scores = np.abs((data_array - mean_val) / std_val)
            outliers = np.where(z_scores > self.anomaly_threshold)[0]

            if len(outliers) > 0:
                outlier_percentage = (len(outliers) / len(data_array)) * 100

                if outlier_percentage > 5.0:  # More than 5% outliers
                    error = SignalValidationError(
                        message=f"Signal data contains {len(outliers)} outliers ({outlier_percentage:.1f}%)",
                        signal_parameter="data_anomalies",
                        actual_value=f"{len(outliers)} outliers",
                        context={**context, 'outlier_indices': outliers[:10].tolist()}
                    )
                    result.add_error(error)
                else:
                    result.add_warning(f"Signal data contains {len(outliers)} potential outliers")

        except Exception as e:
            result.add_warning(f"Anomaly detection failed: {str(e)}")


class SignalFormatValidator(AbstractValidator):
    """
    Validator for signal file formats and metadata
    """

    SUPPORTED_FORMATS = ['wav', 'csv', 'json', 'txt', 'dat']

    def __init__(self, allowed_formats: List[str] = None):
        super().__init__("signal_format_validator")
        self.allowed_formats = allowed_formats or self.SUPPORTED_FORMATS

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate signal format specification"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if isinstance(value, str):
            # Validate file extension
            format_name = value.lower().split('.')[-1] if '.' in value else value.lower()

            if format_name not in self.allowed_formats:
                error = SignalValidationError(
                    message=f"Unsupported signal format: {format_name}",
                    signal_parameter="format",
                    actual_value=format_name,
                    context={**context, 'allowed_formats': self.allowed_formats}
                )
                result.add_error(error)

        elif isinstance(value, dict):
            # Validate signal metadata dictionary
            self._validate_signal_metadata(value, result, context)

        else:
            error = SignalValidationError(
                message="Signal format must be string (format name) or dict (metadata)",
                signal_parameter="format",
                actual_value=type(value).__name__,
                context=context
            )
            result.add_error(error)

        return result

    def _validate_signal_metadata(self, metadata: dict, result: ValidationResult, context: Dict[str, Any]):
        """Validate signal metadata dictionary"""
        required_fields = ['sample_rate', 'duration', 'channels']
        optional_fields = ['format', 'bit_depth', 'encoding', 'timestamp']

        # Check required fields
        for field in required_fields:
            if field not in metadata:
                error = SignalValidationError(
                    message=f"Missing required metadata field: {field}",
                    signal_parameter="metadata",
                    actual_value=f"missing_{field}",
                    context=context
                )
                result.add_error(error)

        # Validate field values
        if 'sample_rate' in metadata:
            sr_validator = SignalParameterValidator('sample_rate')
            sr_result = sr_validator.validate(metadata['sample_rate'], context)
            if not sr_result.is_valid:
                result.errors.extend(sr_result.errors)

        if 'duration' in metadata:
            dur_validator = SignalParameterValidator('duration')
            dur_result = dur_validator.validate(metadata['duration'], context)
            if not dur_result.is_valid:
                result.errors.extend(dur_result.errors)

        if 'channels' in metadata:
            channels = metadata['channels']
            if not isinstance(channels, int) or channels < 1 or channels > 32:
                error = SignalValidationError(
                    message=f"Invalid channel count: {channels} (must be 1-32)",
                    signal_parameter="channels",
                    actual_value=channels,
                    context=context
                )
                result.add_error(error)


class SignalQualityValidator(AbstractValidator):
    """
    Validator for signal quality metrics
    """

    def __init__(
        self,
        min_snr: float = 10.0,  # dB
        max_thd: float = 0.1,   # Total Harmonic Distortion (0-1)
        check_clipping: bool = True
    ):
        super().__init__("signal_quality_validator")
        self.min_snr = min_snr
        self.max_thd = max_thd
        self.check_clipping = check_clipping

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate signal quality metrics"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not isinstance(value, dict):
            error = SignalValidationError(
                message="Signal quality metrics must be provided as a dictionary",
                signal_parameter="quality_metrics",
                actual_value=type(value).__name__,
                context=context
            )
            result.add_error(error)
            return result

        metrics = value

        # SNR validation
        if 'snr' in metrics:
            snr = metrics['snr']
            if not isinstance(snr, (int, float)) or snr < self.min_snr:
                error = SignalValidationError(
                    message=f"Signal SNR {snr} dB below minimum {self.min_snr} dB",
                    signal_parameter="snr",
                    actual_value=snr,
                    expected_range=(self.min_snr, float('inf')),
                    context=context
                )
                result.add_error(error)

        # THD validation
        if 'thd' in metrics:
            thd = metrics['thd']
            if not isinstance(thd, (int, float)) or thd > self.max_thd:
                error = SignalValidationError(
                    message=f"Signal THD {thd} exceeds maximum {self.max_thd}",
                    signal_parameter="thd",
                    actual_value=thd,
                    expected_range=(0.0, self.max_thd),
                    context=context
                )
                result.add_error(error)

        # Clipping detection
        if self.check_clipping and 'clipping_detected' in metrics:
            if metrics['clipping_detected']:
                error = SignalValidationError(
                    message="Signal clipping detected - amplitude exceeds dynamic range",
                    signal_parameter="clipping",
                    actual_value="clipping_present",
                    context=context
                )
                result.add_error(error)

        return result


# Factory function for creating signal validators
def create_signal_validation_pipeline(signal_type: str = "general") -> 'ValidationPipeline':
    """
    Create a pre-configured validation pipeline for signal data

    Args:
        signal_type: Type of signal (general, audio, sensor, measurement)

    Returns:
        Configured ValidationPipeline
    """
    from ..framework.validation_pipeline import ValidationPipeline, PipelineStage

    pipeline = ValidationPipeline(f"signal_validation_{signal_type}")

    # Common validators for all signal types
    pipeline.add_validator(
        SignalParameterValidator('frequency'),
        PipelineStage.BUSINESS_VALIDATION
    )
    pipeline.add_validator(
        SignalDataValidator(),
        PipelineStage.BUSINESS_VALIDATION
    )
    pipeline.add_validator(
        SignalFormatValidator(),
        PipelineStage.TYPE_VALIDATION
    )

    # Type-specific validators
    if signal_type == "audio":
        # Audio-specific ranges
        pipeline.add_validator(
            SignalParameterValidator('frequency', custom_range=(20.0, 20000.0)),  # Human hearing range
            PipelineStage.BUSINESS_VALIDATION
        )
        pipeline.add_validator(
            SignalQualityValidator(min_snr=40.0),  # Higher SNR for audio
            PipelineStage.BUSINESS_VALIDATION
        )

    elif signal_type == "sensor":
        # Sensor data typically has lower frequencies
        pipeline.add_validator(
            SignalParameterValidator('frequency', custom_range=(0.001, 1000.0)),
            PipelineStage.BUSINESS_VALIDATION
        )

    return pipeline