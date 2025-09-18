
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, FileField, FloatField, validators
from wtforms.validators import ValidationError as WTFormsValidationError
import datetime
import sys
import os

# Add validation framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from aplicacion.validation import (
    StringInputValidator,
    NumericInputValidator,
    DateTimeValidator,
    SignalParameterValidator,
    FileTypeValidator,
    ValidationError,
    SecurityValidationError,
    auto_sanitize,
    sanitize_input
)


class CustomValidator:
    """
    Bridge between SSA-24 validation framework and WTForms
    """

    def __init__(self, validator, field_name=None):
        self.validator = validator
        self.field_name = field_name

    def __call__(self, form, field):
        """WTForms validator interface"""
        try:
            context = {
                'field_name': self.field_name or field.name,
                'form_name': form.__class__.__name__
            }

            result = self.validator.validate(field.data, context)

            if not result.is_valid:
                # Collect all error messages
                error_messages = result.get_user_error_messages()
                raise WTFormsValidationError('; '.join(error_messages))

            # Update field data with sanitized value if available
            if result.sanitized_value is not None:
                field.data = result.sanitized_value

        except (ValidationError, SecurityValidationError) as e:
            raise WTFormsValidationError(e.user_message)
        except Exception as e:
            raise WTFormsValidationError(f"Error de validación: {str(e)}")


class SenialForm(FlaskForm):
    """
    Formulario mejorado para adquisición de señales con validación SSA-24
    """

    identificador = IntegerField(
        'Identificador de Señal',
        [
            validators.DataRequired(message='El identificador es obligatorio'),
            CustomValidator(
                NumericInputValidator(
                    min_value=1,
                    max_value=9999,
                    allow_decimal=False
                ),
                'identificador'
            )
        ],
        description='Identificador único para la señal (1-9999)'
    )

    descripcion = StringField(
        'Descripción',
        [
            validators.DataRequired(message='La descripción es obligatoria'),
            CustomValidator(
                StringInputValidator(
                    min_length=3,
                    max_length=200,
                    allowed_pattern=StringInputValidator.TEXT_SAFE
                ),
                'descripcion'
            )
        ],
        description='Descripción de la señal a adquirir'
    )

    fecha = DateField(
        'Fecha de Adquisición',
        [
            validators.DataRequired(message='La fecha es obligatoria'),
            CustomValidator(
                DateTimeValidator(
                    date_format='%Y-%m-%d',
                    min_date=datetime.datetime(2020, 1, 1),
                    max_date=datetime.datetime(2030, 12, 31)
                ),
                'fecha'
            )
        ],
        format='%Y-%m-%d',
        default=datetime.date.today(),
        description='Fecha en que se realizará la adquisición'
    )

    # Nuevos campos con validación avanzada
    frecuencia = FloatField(
        'Frecuencia (Hz)',
        [
            validators.DataRequired(message='La frecuencia es obligatoria'),
            CustomValidator(
                SignalParameterValidator('frequency'),
                'frecuencia'
            )
        ],
        description='Frecuencia de la señal en Hz (0.1 - 50000)'
    )

    amplitud = FloatField(
        'Amplitud (V)',
        [
            validators.DataRequired(message='La amplitud es obligatoria'),
            CustomValidator(
                SignalParameterValidator('amplitude'),
                'amplitud'
            )
        ],
        description='Amplitud de la señal en Voltios (±10V)'
    )

    archivo_config = FileField(
        'Archivo de Configuración',
        [
            validators.Optional(),
            CustomValidator(
                FileTypeValidator(
                    allowed_extensions=['json', 'yaml', 'yml', 'cfg'],
                    strict_mime_check=False
                ),
                'archivo_config'
            )
        ],
        description='Archivo opcional de configuración (JSON, YAML, CFG)'
    )

    adquirir = SubmitField('Adquirir Señal')

    @auto_sanitize()
    def validate_identificador(self, field):
        """Validación personalizada adicional para identificador"""
        # Verificar que el identificador no esté en uso (simulado)
        existing_ids = [1001, 1002, 1003]  # Simular IDs existentes
        if field.data in existing_ids:
            raise WTFormsValidationError(f'El identificador {field.data} ya está en uso')

    @sanitize_input()
    def validate_descripcion(self, field):
        """Validación personalizada adicional para descripción"""
        # Verificar palabras prohibidas
        prohibited_words = ['test', 'prueba', 'temporal']
        description_lower = field.data.lower()

        for word in prohibited_words:
            if word in description_lower:
                raise WTFormsValidationError(f'La descripción no puede contener la palabra "{word}"')

    def validate(self, extra_validators=None):
        """
        Validación global del formulario con logging estructurado
        """
        try:
            # Ejecutar validación estándar de WTForms
            is_valid = super().validate(extra_validators)

            # Validaciones cruzadas adicionales
            if is_valid:
                self._validate_signal_parameters()
                self._validate_date_constraints()

            return is_valid and len(self.errors) == 0

        except Exception as e:
            # Log estructurado del error
            from config.logging_config import get_logger
            logger = get_logger(__name__)
            logger.error(
                "Error en validación de formulario",
                extra={
                    'form_class': self.__class__.__name__,
                    'form_data': {k: '***' if 'password' in k.lower() else str(v.data)
                                for k, v in self._fields.items()},
                    'error': str(e),
                    'validation_step': 'form_global_validation'
                }
            )
            return False

    def _validate_signal_parameters(self):
        """Validación cruzada de parámetros de señal"""
        if hasattr(self, 'frecuencia') and hasattr(self, 'amplitud'):
            freq = self.frecuencia.data
            amp = self.amplitud.data

            if freq and amp:
                # Verificar compatibilidad entre frecuencia y amplitud
                if freq > 10000 and abs(amp) > 5.0:
                    self.amplitud.errors.append(
                        'Amplitud muy alta para frecuencias superiores a 10kHz'
                    )

                # Verificar límites de potencia
                power_estimate = (amp ** 2) * freq / 1000  # Estimación simplificada
                if power_estimate > 1000:  # 1W límite
                    self.amplitud.errors.append(
                        'Combinación de frecuencia y amplitud excede límites de potencia'
                    )

    def _validate_date_constraints(self):
        """Validación de restricciones de fecha"""
        if hasattr(self, 'fecha') and self.fecha.data:
            fecha = self.fecha.data
            now = datetime.date.today()

            # No permitir fechas muy en el futuro
            if fecha > now + datetime.timedelta(days=365):
                self.fecha.errors.append(
                    'La fecha no puede ser más de un año en el futuro'
                )

            # Advertir sobre fechas en fines de semana
            if fecha.weekday() >= 5:  # Sábado=5, Domingo=6
                # Esto es una advertencia, no un error
                if not hasattr(self, '_warnings'):
                    self._warnings = []
                self._warnings.append(
                    f'La fecha seleccionada ({fecha.strftime("%d/%m/%Y")}) es fin de semana'
                )

    def get_sanitized_data(self):
        """
        Obtener datos sanitizados del formulario
        """
        sanitized_data = {}

        for field_name, field in self._fields.items():
            if hasattr(field, 'data') and field.data is not None:
                sanitized_data[field_name] = field.data

        return sanitized_data

    def get_validation_summary(self):
        """
        Obtener resumen de validación para logging/debugging
        """
        return {
            'form_valid': len(self.errors) == 0,
            'total_errors': sum(len(errors) for errors in self.errors.values()),
            'fields_with_errors': list(self.errors.keys()),
            'warnings': getattr(self, '_warnings', []),
            'sanitized_fields': [
                field_name for field_name, field in self._fields.items()
                if hasattr(field, '_was_sanitized') and field._was_sanitized
            ]
        }
