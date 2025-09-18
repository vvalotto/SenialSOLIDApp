"""
Se modifica la clase base y se extiende con la clase abstracta trazador
Integrado con SSA-24 Input Validation Framework
"""
from abc import ABCMeta, abstractmethod
from modelo.senial import *
from utilidades.trazador import *
import math
import sys
import os
from config.logging_config import get_logger
from exceptions import AcquisitionException, ValidationException

# Add validation framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from aplicacion.validation import (
    SignalParameterValidator,
    SignalDataValidator,
    FileTypeValidator,
    FileContentValidator,
    StringInputValidator,
    ValidationError,
    FileValidationError,
    SignalValidationError,
    auto_sanitize,
    validate_parameters
)

logger = get_logger(__name__)


class BaseAdquisidor(BaseTrazador, metaclass=ABCMeta):
    """
    Clase Abstracta Adquisidor
    """
    def __init__(self, senial):
        """
        Inicializa el adquisidor con una lista vacia de valores de la senial
        :valor: Tamanio de la coleccion de valores de la senial
        """
        self._senial = senial

    def obtener_senial_adquirida(self):
        """
        Devuelve la lista de valores de la senial adquirida
        :return: senial
        """
        return self._senial

    @abstractmethod
    def leer_senial(self):
        """
        Metodo abstracto. Cada adquisidor tiene su propia implementacion
        de la lectura de la senial
        """
        pass

    @abstractmethod
    def _leer_dato_entrada(self):
        pass

    def trazar(self, entidad, accion, mensaje):
        """
        Registra un evento asociado a la proceso de adquisicion
        entidad: clase que genera el evento
        accion: metodo o funcion en la que se genera el evento
        mensaje: Comentario
        """
        nombre = 'adquisidor_logger.log'
        try:
            with open(nombre, 'a') as logger:
                logger.writelines('------->\n')
                logger.writelines('Accion: ' + str(accion) + '\n')
                logger.writelines(str(entidad) + '\n')
                logger.writelines(str(datetime.datetime.now()) + '\n')
                logger.writelines(str(mensaje) + '\n')
        except IOError as eIO:
            raise eIO


class AdquisidorSimple(BaseAdquisidor):
    """
    Adquisidor de datos desde el teclado
    """
    def _leer_dato_entrada(self):
        """
        Lee un dato por teclaso
        :return: dato leido
        """
        dato = 0
        while True:
            try:
                dato = float(input('Valor:'))
                break
            except ValueError:
                logger.warning("Entrada inválida: se esperaba número")
            finally:
                return dato

    def leer_senial(self):
        """
        llena la coleccion de valores de la senial desde el teclado
        :return:
        """
        logger.info("Iniciando lectura de señal desde teclado", extra={"tamanio": self._senial.tamanio})
        for i in range(0, self._senial.tamanio):
            logger.debug("Leyendo dato", extra={"numero_dato": i})
            self._senial.poner_valor(self._leer_dato_entrada())
        logger.info("Lectura de señal desde teclado completada", extra={"valores_leidos": self._senial.cantidad})
        return


class AdquisidorArchivo(BaseAdquisidor):
    """
    Adquisidor de datos desde Archivo con validación SSA-24
    """
    @property
    def ubicacion(self):
        return self._ubicacion

    @auto_sanitize()
    def __init__(self, senial, ubicacion):
        """
        Inicializa la instancia con la ubicacion del archivo a leer con validación
        :param ubicacion: Ruta del archivo a validar
        """
        BaseAdquisidor.__init__(self, senial)

        # Validate file path using SSA-24 framework
        try:
            # First validate that it's a string and sanitize
            path_validator = StringInputValidator(
                max_length=500,
                allowed_pattern=r'^[a-zA-Z0-9\s\-_.\\/:]+$'  # Allow path characters
            )
            path_result = path_validator.validate(ubicacion)

            if not path_result.is_valid:
                raise ValidationError(
                    message="Invalid file path format",
                    field_name="file_path",
                    invalid_value=ubicacion,
                    context={'validation_errors': [e.message for e in path_result.errors]}
                )

            sanitized_path = path_result.sanitized_value

            # Validate file type
            file_validator = FileTypeValidator(
                allowed_extensions=['txt', 'csv', 'dat', 'json'],
                strict_mime_check=False
            )
            file_result = file_validator.validate(sanitized_path)

            if not file_result.is_valid:
                raise FileValidationError(
                    message="File type not allowed for signal acquisition",
                    filename=sanitized_path,
                    context={'validation_errors': [e.message for e in file_result.errors]}
                )

            # Additional security validation
            content_validator = FileContentValidator(scan_content=True, max_scan_size=1024*1024)  # 1MB scan
            if os.path.exists(sanitized_path):
                content_result = content_validator.validate(sanitized_path)
                if not content_result.is_valid:
                    raise FileValidationError(
                        message="File contains unsafe content",
                        filename=sanitized_path,
                        context={'security_issues': content_result.security_issues}
                    )

            self._ubicacion = sanitized_path

            logger.info("File acquisition initialized with validation", extra={
                'file_path': sanitized_path,
                'file_extension': file_result.metadata.get('extension'),
                'validation_passed': True
            })

        except (ValidationError, FileValidationError) as ve:
            logger.error("File validation failed for acquisition", extra={
                'file_path': str(ubicacion)[:100],
                'error_code': ve.error_code,
                'error_message': ve.message
            })
            super().trazar(AdquisidorArchivo,
                           'Inicializacion',
                           f'File validation failed: {ve.message}')
            raise ve

        except Exception as e:
            logger.error("Unexpected error in file acquisition initialization", exc_info=True)
            super().trazar(AdquisidorArchivo,
                           'Inicializacion',
                           f'Unexpected error: {str(e)}')
            raise AcquisitionException(
                message="Failed to initialize file acquisition",
                acquisition_source="file",
                context={'file_path': str(ubicacion)[:100]},
                cause=e
            )

        return



    def _leer_dato_entrada(self):
        pass

    def leer_senial(self):
        """
        Lee señal desde archivo con validación SSA-24 de los datos
        """
        logger.info("Iniciando lectura de señal desde archivo", extra={"archivo": self._ubicacion})

        # Initialize signal data validator
        data_validator = SignalDataValidator(
            max_length=100000,  # 100K samples max
            min_length=1,
            check_anomalies=True,
            anomaly_threshold=3.0
        )

        signal_data = []

        try:
            # Read data from file
            with open(self._ubicacion, 'r') as a:
                for line_number, linea in enumerate(a, 1):
                    try:
                        dato = float(linea.strip())
                        signal_data.append(dato)
                        logger.debug("Valor leído desde archivo", extra={
                            "valor": dato,
                            "linea": line_number
                        })

                        # Prevent excessive memory usage
                        if len(signal_data) > 100000:
                            raise SignalValidationError(
                                message="Signal data exceeds maximum length",
                                signal_parameter="data_length",
                                actual_value=len(signal_data),
                                context={'max_allowed': 100000, 'file': self._ubicacion}
                            )

                    except ValueError as ve:
                        raise SignalValidationError(
                            message=f"Invalid numeric data at line {line_number}",
                            signal_parameter="data_format",
                            actual_value=linea.strip(),
                            context={'line_number': line_number, 'file': self._ubicacion}
                        )

            # Validate the complete signal data using SSA-24
            validation_context = {
                'source_file': self._ubicacion,
                'acquisition_method': 'file_read',
                'total_samples': len(signal_data)
            }

            validation_result = data_validator.validate(signal_data, validation_context)

            if not validation_result.is_valid:
                # Log validation errors
                for error in validation_result.errors:
                    logger.error("Signal data validation failed", extra={
                        'error_code': error.error_code,
                        'error_message': error.message,
                        'file': self._ubicacion
                    })

                raise SignalValidationError(
                    message="Signal data validation failed",
                    signal_parameter="data_quality",
                    context={
                        'validation_errors': [error.message for error in validation_result.errors],
                        'file': self._ubicacion
                    }
                )

            # Log validation warnings
            for warning in validation_result.warnings:
                logger.warning("Signal data warning", extra={
                    'warning': warning,
                    'file': self._ubicacion
                })

            # Use sanitized data if available
            validated_data = validation_result.sanitized_value if validation_result.sanitized_value else signal_data

            # Store validated data in signal
            for dato in validated_data:
                self._senial.poner_valor(dato)

            logger.info("Señal leída y validada exitosamente", extra={
                'archivo': self._ubicacion,
                'total_samples': len(validated_data),
                'validation_metadata': validation_result.metadata,
                'has_warnings': len(validation_result.warnings) > 0
            })

        except IOError as ex:
            super().trazar(AdquisidorArchivo,
                           'leer_senial',
                           'I/O Error: ' + str(ex))
            raise AcquisitionException(
                message="Cannot read signal file",
                acquisition_source="file",
                context={'file_path': self._ubicacion},
                cause=ex
            )

        except (SignalValidationError, ValidationError) as ve:
            super().trazar(AdquisidorArchivo,
                           'leer_senial',
                           f'Signal validation error: {ve.message}')
            logger.error("Signal validation failed during acquisition", extra={
                'archivo': self._ubicacion,
                'error_code': ve.error_code,
                'error_message': ve.message
            })
            raise ve

        except Exception as ex:
            super().trazar(AdquisidorArchivo,
                           'leer_senial',
                           'Error en la carga de datos: ' + str(ex))
            logger.error("Error en la carga de datos desde archivo", extra={
                "archivo": self._ubicacion
            }, exc_info=True)
            raise AcquisitionException(
                message="Unexpected error during signal acquisition",
                acquisition_source="file",
                context={'file_path': self._ubicacion},
                cause=ex
            )


class AdquisidorSenoidal(BaseAdquisidor):
    """
    Simulador de una entrada de senial senoidal con validación SSA-24
    """
    @validate_parameters(amplitude=SignalParameterValidator('amplitude'))
    def __init__(self, senial, amplitude=10.0, frequency=1.0):
        """
        Inicializa generador senoidal con validación de parámetros
        :param senial: Objeto señal
        :param amplitude: Amplitud de la señal (default 10.0)
        :param frequency: Frecuencia relativa (default 1.0)
        """
        BaseAdquisidor.__init__(self, senial)

        # Validate signal parameters using SSA-24
        try:
            # Validate amplitude
            amp_validator = SignalParameterValidator('amplitude')
            amp_result = amp_validator.validate(amplitude)

            if not amp_result.is_valid:
                raise SignalValidationError(
                    message="Invalid amplitude for sinusoidal signal",
                    signal_parameter="amplitude",
                    actual_value=amplitude,
                    expected_range=(-10.0, 10.0)
                )

            # Validate signal size
            if senial.tamanio > 100000:
                raise SignalValidationError(
                    message="Signal size too large for generation",
                    signal_parameter="signal_size",
                    actual_value=senial.tamanio,
                    expected_range=(1, 100000)
                )

            self._amplitude = amp_result.sanitized_value
            self._frequency = max(0.1, min(10.0, frequency))  # Clamp frequency
            self._valor = 0
            self._i = 0

            logger.info("Sinusoidal signal generator initialized", extra={
                'amplitude': self._amplitude,
                'frequency': self._frequency,
                'signal_size': senial.tamanio
            })

        except SignalValidationError as sve:
            logger.error("Signal parameter validation failed", extra={
                'error_code': sve.error_code,
                'amplitude': amplitude,
                'frequency': frequency
            })
            raise sve

    def _leer_dato_entrada(self):
        """Generate next sinusoidal sample with bounds checking"""
        if self._i >= self._senial.tamanio:
            raise SignalValidationError(
                message="Signal index out of bounds",
                signal_parameter="sample_index",
                actual_value=self._i,
                expected_range=(0, self._senial.tamanio - 1)
            )

        # Generate sinusoidal value
        phase = (float(self._i) / float(self._senial.tamanio)) * 2 * math.pi * self._frequency
        self._valor = math.sin(phase) * self._amplitude
        self._i += 1

        # Validate generated value is within expected amplitude bounds
        if abs(self._valor) > abs(self._amplitude) * 1.1:  # Allow 10% tolerance
            logger.warning("Generated sample outside expected bounds", extra={
                'sample_value': self._valor,
                'expected_amplitude': self._amplitude,
                'sample_index': self._i - 1
            })

        return self._valor

    def leer_senial(self):
        """
        Generate sinusoidal signal with validation
        """
        logger.info("Iniciando generación de señal senoidal", extra={
            "tamanio": self._senial.tamanio,
            "amplitude": self._amplitude,
            "frequency": self._frequency
        })

        generated_samples = []
        i = 0

        try:
            while i < self._senial.tamanio:
                valor = self._leer_dato_entrada()
                generated_samples.append(valor)
                self._senial.poner_valor(valor)
                i += 1

            # Validate generated signal using SSA-24
            data_validator = SignalDataValidator(
                max_length=self._senial.tamanio,
                check_anomalies=False  # Expected sinusoidal pattern
            )

            validation_context = {
                'generation_method': 'sinusoidal',
                'amplitude': self._amplitude,
                'frequency': self._frequency,
                'total_samples': len(generated_samples)
            }

            validation_result = data_validator.validate(generated_samples, validation_context)

            if not validation_result.is_valid:
                logger.error("Generated signal validation failed", extra={
                    'validation_errors': [error.message for error in validation_result.errors],
                    'generation_parameters': validation_context
                })

                raise SignalValidationError(
                    message="Generated sinusoidal signal validation failed",
                    signal_parameter="generated_data",
                    context={
                        'validation_errors': [error.message for error in validation_result.errors],
                        'generation_method': 'sinusoidal'
                    }
                )

            logger.info("Señal senoidal generada y validada exitosamente", extra={
                "valores_generados": i,
                "validation_metadata": validation_result.metadata,
                "amplitude_range": (min(generated_samples), max(generated_samples))
            })

        except SignalValidationError as sve:
            super().trazar(AdquisidorSenoidal,
                           'leer_senial',
                           f'Signal validation error: {sve.message}')
            logger.error("Signal validation failed during generation", extra={
                'error_code': sve.error_code,
                'generated_samples': i
            })
            raise sve

        except Exception as ex:
            super().trazar(AdquisidorSenoidal,
                           'leer_senial',
                           'Error en la generación de datos: ' + str(ex))
            logger.error("Error en la generación de señal senoidal", exc_info=True)
            raise AcquisitionException(
                message="Unexpected error during sinusoidal signal generation",
                acquisition_source="generator",
                context={'generated_samples': i, 'target_samples': self._senial.tamanio},
                cause=ex
            )