"""
File Validation for SSA-24 Input Validation Framework

Specialized validators for file uploads, types, and content security
"""

import os
import mimetypes
import hashlib
import re
from typing import Any, Dict, List, Optional, Union, BinaryIO
import logging
from pathlib import Path
import tempfile

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from ..framework.validator_base import AbstractValidator, ValidationResult
from ..exceptions.validation_exceptions import FileValidationError, SecurityValidationError


class FileTypeValidator(AbstractValidator):
    """
    Validator for file types and MIME types
    """

    # Allowed file types for signal processing
    SIGNAL_FILE_TYPES = {
        'wav': 'audio/wav',
        'csv': 'text/csv',
        'json': 'application/json',
        'txt': 'text/plain',
        'dat': 'application/octet-stream',
        'mat': 'application/octet-stream',  # MATLAB files
        'h5': 'application/x-hdf',          # HDF5 files
        'hdf5': 'application/x-hdf'
    }

    # Dangerous file types that should always be rejected
    DANGEROUS_TYPES = {
        'exe', 'bat', 'cmd', 'com', 'scr', 'pif', 'vbs', 'js', 'jar',
        'app', 'deb', 'pkg', 'dmg', 'iso', 'msi', 'dll', 'so'
    }

    def __init__(
        self,
        allowed_extensions: List[str] = None,
        allowed_mime_types: List[str] = None,
        strict_mime_check: bool = True
    ):
        super().__init__("file_type_validator")
        self.allowed_extensions = allowed_extensions or list(self.SIGNAL_FILE_TYPES.keys())
        self.allowed_mime_types = allowed_mime_types or list(self.SIGNAL_FILE_TYPES.values())
        self.strict_mime_check = strict_mime_check

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate file type based on extension and MIME type"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Handle different input types
        if isinstance(value, str):
            # String path or filename
            filename = value
            file_content = None
        elif hasattr(value, 'filename') and hasattr(value, 'read'):
            # File upload object (Flask/Werkzeug FileStorage)
            filename = value.filename
            file_content = value
        elif isinstance(value, dict) and 'filename' in value:
            # Dictionary with file info
            filename = value['filename']
            file_content = value.get('content')
        else:
            error = FileValidationError(
                message="Invalid file input type",
                filename="unknown",
                context=context
            )
            result.add_error(error)
            return result

        if not filename:
            error = FileValidationError(
                message="Filename is required",
                filename="",
                context=context
            )
            result.add_error(error)
            return result

        # Extract file extension
        file_extension = Path(filename).suffix.lower().lstrip('.')

        # Check for dangerous file types
        if file_extension in self.DANGEROUS_TYPES:
            error = SecurityValidationError(
                message=f"Dangerous file type detected: {file_extension}",
                threat_type="malicious_file_type",
                context={**context, 'filename': filename, 'extension': file_extension}
            )
            result.add_error(error)
            return result

        # Validate extension
        if file_extension not in self.allowed_extensions:
            error = FileValidationError(
                message=f"File extension '{file_extension}' not allowed",
                filename=filename,
                file_type=file_extension,
                context={**context, 'allowed_extensions': self.allowed_extensions}
            )
            result.add_error(error)

        # MIME type validation if content is available
        if file_content and self.strict_mime_check:
            self._validate_mime_type(file_content, filename, file_extension, result, context)

        # Store validated file info
        result.metadata.update({
            'filename': filename,
            'extension': file_extension,
            'expected_mime': self.SIGNAL_FILE_TYPES.get(file_extension, 'unknown')
        })

        return result

    def _validate_mime_type(
        self,
        file_content: Any,
        filename: str,
        extension: str,
        result: ValidationResult,
        context: Dict[str, Any]
    ):
        """Validate MIME type of file content"""
        try:
            # Get MIME type from file content
            if hasattr(file_content, 'read'):
                # File-like object
                current_pos = file_content.tell() if hasattr(file_content, 'tell') else 0
                content_sample = file_content.read(1024)
                if hasattr(file_content, 'seek'):
                    file_content.seek(current_pos)

                detected_mime = magic.from_buffer(content_sample, mime=True)
            else:
                # Raw bytes
                detected_mime = magic.from_buffer(file_content[:1024], mime=True)

            expected_mime = self.SIGNAL_FILE_TYPES.get(extension)

            if expected_mime and detected_mime not in self.allowed_mime_types:
                error = FileValidationError(
                    message=f"MIME type mismatch: detected '{detected_mime}', expected '{expected_mime}'",
                    filename=filename,
                    file_type=detected_mime,
                    context={**context, 'detected_mime': detected_mime, 'expected_mime': expected_mime}
                )
                result.add_error(error)

            result.metadata['detected_mime'] = detected_mime

        except Exception as e:
            result.add_warning(f"MIME type detection failed: {str(e)}")


class FileSizeValidator(AbstractValidator):
    """
    Validator for file size limits
    """

    def __init__(
        self,
        max_size: int = 100 * 1024 * 1024,  # 100MB default
        min_size: int = 1  # 1 byte minimum
    ):
        super().__init__("file_size_validator")
        self.max_size = max_size
        self.min_size = min_size

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate file size"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        file_size = self._get_file_size(value)

        if file_size is None:
            error = FileValidationError(
                message="Cannot determine file size",
                context=context
            )
            result.add_error(error)
            return result

        # Size validation
        if file_size < self.min_size:
            error = FileValidationError(
                message=f"File too small: {file_size} bytes (minimum: {self.min_size} bytes)",
                file_size=file_size,
                context=context
            )
            result.add_error(error)

        if file_size > self.max_size:
            error = FileValidationError(
                message=f"File too large: {self._format_size(file_size)} (maximum: {self._format_size(self.max_size)})",
                file_size=file_size,
                context=context
            )
            result.add_error(error)

        result.metadata['file_size'] = file_size
        result.metadata['file_size_formatted'] = self._format_size(file_size)

        return result

    def _get_file_size(self, value: Any) -> Optional[int]:
        """Extract file size from various input types"""
        if isinstance(value, str) and os.path.exists(value):
            # File path
            return os.path.getsize(value)
        elif hasattr(value, 'content_length') and value.content_length:
            # Flask FileStorage with content_length
            return value.content_length
        elif hasattr(value, 'seek') and hasattr(value, 'tell'):
            # File-like object
            current_pos = value.tell()
            value.seek(0, 2)  # Seek to end
            size = value.tell()
            value.seek(current_pos)  # Return to original position
            return size
        elif isinstance(value, (bytes, bytearray)):
            # Raw bytes
            return len(value)
        elif isinstance(value, dict) and 'size' in value:
            # Dictionary with size info
            return value['size']
        else:
            return None

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class FileContentValidator(AbstractValidator):
    """
    Validator for file content security and structure
    """

    # Malicious content patterns
    MALICIOUS_PATTERNS = [
        rb'<script.*?>',  # JavaScript
        rb'javascript:',  # JavaScript URLs
        rb'vbscript:',   # VBScript URLs
        rb'onload=',     # Event handlers
        rb'onerror=',
        rb'onclick=',
        rb'eval\(',      # eval() calls
        rb'exec\(',      # exec() calls
        rb'system\(',    # system() calls
        rb'\x00',        # Null bytes
        rb'MZ\x90\x00\x03',  # PE executable header
        rb'\x7fELF',     # ELF executable header
        rb'\xca\xfe\xba\xbe',  # Java class file header
    ]

    def __init__(
        self,
        scan_content: bool = True,
        max_scan_size: int = 10 * 1024 * 1024,  # 10MB scan limit
        virus_scan: bool = False
    ):
        super().__init__("file_content_validator")
        self.scan_content = scan_content
        self.max_scan_size = max_scan_size
        self.virus_scan = virus_scan

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate file content for security threats"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not self.scan_content:
            return result

        content = self._get_file_content(value)
        if content is None:
            result.add_warning("Could not access file content for security scanning")
            return result

        # Limit scan size for performance
        scan_content = content[:self.max_scan_size]

        # Scan for malicious patterns
        threats_found = []
        for pattern in self.MALICIOUS_PATTERNS:
            if pattern in scan_content:
                threat_name = self._get_threat_name(pattern)
                threats_found.append(threat_name)

        if threats_found:
            error = SecurityValidationError(
                message=f"Malicious content detected: {', '.join(threats_found)}",
                threat_type="malicious_file_content",
                context={**context, 'threats': threats_found}
            )
            result.add_error(error)

        # Check for suspicious file structure
        self._check_file_structure(scan_content, result, context)

        # Calculate content hash for integrity
        content_hash = hashlib.sha256(scan_content).hexdigest()
        result.metadata['content_hash'] = content_hash
        result.metadata['scanned_size'] = len(scan_content)

        return result

    def _get_file_content(self, value: Any) -> Optional[bytes]:
        """Extract file content from various input types"""
        if isinstance(value, str) and os.path.exists(value):
            # File path
            try:
                with open(value, 'rb') as f:
                    return f.read()
            except Exception:
                return None
        elif hasattr(value, 'read'):
            # File-like object
            try:
                current_pos = value.tell() if hasattr(value, 'tell') else 0
                value.seek(0)
                content = value.read()
                if hasattr(value, 'seek'):
                    value.seek(current_pos)
                return content if isinstance(content, bytes) else content.encode('utf-8')
            except Exception:
                return None
        elif isinstance(value, (bytes, bytearray)):
            # Raw bytes
            return bytes(value)
        elif isinstance(value, dict) and 'content' in value:
            # Dictionary with content
            content = value['content']
            return content if isinstance(content, bytes) else content.encode('utf-8')
        else:
            return None

    def _get_threat_name(self, pattern: bytes) -> str:
        """Get human-readable threat name from pattern"""
        threat_map = {
            rb'<script.*?>': 'HTML_Script',
            rb'javascript:': 'JavaScript_URL',
            rb'vbscript:': 'VBScript_URL',
            rb'onload=': 'Event_Handler',
            rb'onerror=': 'Event_Handler',
            rb'onclick=': 'Event_Handler',
            rb'eval\(': 'Code_Injection',
            rb'exec\(': 'Code_Injection',
            rb'system\(': 'System_Call',
            rb'\x00': 'Null_Byte',
            rb'MZ\x90\x00\x03': 'PE_Executable',
            rb'\x7fELF': 'ELF_Executable',
            rb'\xca\xfe\xba\xbe': 'Java_Class'
        }
        return threat_map.get(pattern, 'Unknown_Threat')

    def _check_file_structure(self, content: bytes, result: ValidationResult, context: Dict[str, Any]):
        """Check file structure for suspicious characteristics"""
        # Check for embedded executables
        if b'This program cannot be run in DOS mode' in content:
            error = SecurityValidationError(
                message="Embedded executable detected",
                threat_type="embedded_executable",
                context=context
            )
            result.add_error(error)

        # Check for excessive null bytes (potential binary hiding)
        null_count = content.count(b'\x00')
        if null_count > len(content) * 0.1:  # More than 10% null bytes
            result.add_warning(f"High null byte content: {null_count} null bytes")

        # Check for very long lines (potential attack vector)
        if b'\n' in content:
            lines = content.split(b'\n')
            max_line_length = max(len(line) for line in lines)
            if max_line_length > 10000:  # 10KB line
                result.add_warning(f"Very long line detected: {max_line_length} characters")


class FilePathValidator(AbstractValidator):
    """
    Validator for file paths with security checks against path traversal attacks
    """

    # Dangerous path patterns
    DANGEROUS_PATH_PATTERNS = [
        r'\.\.[\\/]',           # Path traversal
        r'[\\/]\.\.[\\/]',      # Path traversal in middle
        r'^\.\.[\\/]',          # Path traversal at start
        r'[\\/]\.\.[\/\\]*$',   # Path traversal at end
        r'[<>:"|?*]',          # Windows invalid chars
        r'[\x00-\x1f]',        # Control characters
        r'[\x7f-\x9f]',        # Extended control characters
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)',  # Windows reserved names
        r'^\.{1,2}$',          # Current/parent directory
        r'^\.',                # Hidden files (optional check)
    ]

    # Maximum path component lengths
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 4096
    MAX_PATH_DEPTH = 20

    def __init__(
        self,
        allowed_extensions: List[str] = None,
        base_directory: str = None,
        strict_mode: bool = True,
        allow_hidden_files: bool = False
    ):
        super().__init__("file_path_validator")
        self.allowed_extensions = allowed_extensions or []
        self.base_directory = Path(base_directory) if base_directory else None
        self.strict_mode = strict_mode
        self.allow_hidden_files = allow_hidden_files

        # Compile patterns for performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATH_PATTERNS
        ]

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate file path for security issues"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        if not value:
            return result

        path_str = str(value).strip()
        original_path = path_str

        # Normalize path separators
        path_str = path_str.replace('\\', '/')

        # Basic length checks
        if len(path_str) > self.MAX_PATH_LENGTH:
            error = SecurityValidationError(
                message=f"Path too long: {len(path_str)} chars (max: {self.MAX_PATH_LENGTH})",
                threat_type="path_length_attack",
                context={**context, 'path_length': len(path_str)}
            )
            result.add_error(error)
            return result

        # Check path depth
        path_parts = [part for part in path_str.split('/') if part and part != '.']
        if len(path_parts) > self.MAX_PATH_DEPTH:
            error = SecurityValidationError(
                message=f"Path depth too deep: {len(path_parts)} levels (max: {self.MAX_PATH_DEPTH})",
                threat_type="path_depth_attack",
                context={**context, 'path_depth': len(path_parts)}
            )
            result.add_error(error)

        # Check for dangerous patterns
        detected_threats = []
        for pattern in self.compiled_patterns:
            if pattern.search(path_str):
                threat_name = self._get_path_threat_name(pattern.pattern)
                detected_threats.append(threat_name)

        # Check each path component
        for part in path_parts:
            if len(part) > self.MAX_FILENAME_LENGTH:
                error = SecurityValidationError(
                    message=f"Filename too long: {part[:50]}... ({len(part)} chars, max: {self.MAX_FILENAME_LENGTH})",
                    threat_type="filename_length_attack",
                    context={**context, 'long_component': part[:100]}
                )
                result.add_error(error)

        # Hidden file check
        if not self.allow_hidden_files and any(part.startswith('.') for part in path_parts):
            detected_threats.append('Hidden_File')

        # Extension validation
        if self.allowed_extensions:
            file_ext = Path(path_str).suffix.lower().lstrip('.')
            if file_ext and file_ext not in self.allowed_extensions:
                error = FileValidationError(
                    message=f"File extension not allowed: {file_ext}",
                    context={**context, 'extension': file_ext, 'allowed': self.allowed_extensions}
                )
                result.add_error(error)

        # Base directory validation
        if self.base_directory:
            try:
                full_path = (self.base_directory / path_str).resolve()
                if not str(full_path).startswith(str(self.base_directory.resolve())):
                    error = SecurityValidationError(
                        message="Path escapes base directory",
                        threat_type="path_traversal",
                        context={**context, 'base_dir': str(self.base_directory)}
                    )
                    result.add_error(error)
            except (OSError, ValueError) as e:
                error = FileValidationError(
                    message=f"Invalid path: {str(e)}",
                    context=context
                )
                result.add_error(error)

        # Apply sanitization
        sanitized_path = self._sanitize_path(path_str)

        # Report security issues
        if detected_threats:
            if self.strict_mode:
                error = SecurityValidationError(
                    message=f"Dangerous path patterns detected: {', '.join(detected_threats)}",
                    threat_type="path_traversal",
                    context={
                        **context,
                        'detected_threats': detected_threats,
                        'original_path': original_path
                    }
                )
                result.add_error(error)
            else:
                result.add_warning(f"Suspicious path patterns detected: {', '.join(detected_threats)}")

        result.sanitized_value = sanitized_path
        result.was_sanitized = (original_path != sanitized_path)

        return result

    def _sanitize_path(self, path_str: str) -> str:
        """Sanitize file path to remove dangerous elements"""
        sanitized = path_str

        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)

        # Remove path traversal patterns
        sanitized = re.sub(r'\.\.[\\/]', '', sanitized)
        sanitized = re.sub(r'[\\/]\.\.', '', sanitized)

        # Remove dangerous characters for Windows
        sanitized = re.sub(r'[<>:"|?*]', '_', sanitized)

        # Normalize multiple slashes
        sanitized = re.sub(r'/+', '/', sanitized)

        # Remove leading/trailing slashes and dots
        sanitized = sanitized.strip('/.\\')

        # Ensure we don't create empty components
        parts = [part for part in sanitized.split('/') if part and part != '.' and part != '..']
        sanitized = '/'.join(parts)

        return sanitized

    def _get_path_threat_name(self, pattern: str) -> str:
        """Get human-readable threat name from path pattern"""
        threat_map = {
            r'\.\.[\\/]': 'Path_Traversal',
            r'[\\/]\.\.[\\/]': 'Path_Traversal_Middle',
            r'^\.\.[\\/]': 'Path_Traversal_Start',
            r'[\\/]\.\.[\/\\]*$': 'Path_Traversal_End',
            r'[<>:"|?*]': 'Invalid_Characters',
            r'[\x00-\x1f]': 'Control_Characters',
            r'[\x7f-\x9f]': 'Extended_Control',
            r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)': 'Reserved_Name',
            r'^\.{1,2}$': 'Directory_Reference',
            r'^\.': 'Hidden_File'
        }

        for key, name in threat_map.items():
            if key in pattern:
                return name
        return 'Unknown_Path_Threat'

    def validate_directory_path(self, directory_path: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate directory path specifically"""
        result = self.validate(directory_path, context)

        # Additional directory-specific checks
        if result.is_valid and self.base_directory:
            try:
                full_path = (self.base_directory / directory_path).resolve()

                # Check if it's actually a directory (if it exists)
                if full_path.exists() and not full_path.is_dir():
                    error = FileValidationError(
                        message="Path exists but is not a directory",
                        context=context or {}
                    )
                    result.add_error(error)

            except (OSError, ValueError):
                pass  # Error already handled in main validation

        return result


class SignalFileValidator(AbstractValidator):
    """
    Specialized validator for signal data files
    """

    def __init__(self):
        super().__init__("signal_file_validator")

    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate signal-specific file requirements"""
        result = ValidationResult(is_valid=True, sanitized_value=value)
        context = context or {}

        # Get file extension for format-specific validation
        filename = self._get_filename(value)
        if not filename:
            error = FileValidationError(
                message="Cannot determine filename for signal validation",
                context=context
            )
            result.add_error(error)
            return result

        extension = Path(filename).suffix.lower().lstrip('.')

        # Format-specific validation
        if extension == 'csv':
            self._validate_csv_signal(value, result, context)
        elif extension == 'json':
            self._validate_json_signal(value, result, context)
        elif extension == 'wav':
            self._validate_wav_signal(value, result, context)

        return result

    def _get_filename(self, value: Any) -> Optional[str]:
        """Extract filename from various input types"""
        if isinstance(value, str):
            return value
        elif hasattr(value, 'filename'):
            return value.filename
        elif isinstance(value, dict) and 'filename' in value:
            return value['filename']
        else:
            return None

    def _validate_csv_signal(self, value: Any, result: ValidationResult, context: Dict[str, Any]):
        """Validate CSV signal file format"""
        try:
            content = self._get_content_sample(value)
            if content:
                # Check for CSV header
                lines = content.decode('utf-8', errors='ignore').split('\n')[:5]
                if len(lines) < 2:
                    result.add_warning("CSV file appears to have insufficient data")

                # Check for numeric data
                for line in lines[1:3]:  # Check first 2 data lines
                    if line.strip():
                        try:
                            # Try to parse as numeric values
                            values = [float(x.strip()) for x in line.split(',')]
                            if len(values) < 1:
                                result.add_warning("CSV lines contain no numeric data")
                        except ValueError:
                            result.add_warning("CSV contains non-numeric data")
                            break

        except Exception as e:
            result.add_warning(f"CSV validation failed: {str(e)}")

    def _validate_json_signal(self, value: Any, result: ValidationResult, context: Dict[str, Any]):
        """Validate JSON signal file format"""
        try:
            import json
            content = self._get_content_sample(value, size=1024)
            if content:
                # Try to parse JSON
                json_data = json.loads(content.decode('utf-8'))

                # Check for expected signal fields
                expected_fields = ['data', 'sample_rate', 'duration']
                missing_fields = [field for field in expected_fields if field not in json_data]

                if missing_fields:
                    result.add_warning(f"JSON missing recommended fields: {missing_fields}")

        except json.JSONDecodeError as e:
            error = FileValidationError(
                message=f"Invalid JSON format: {str(e)}",
                context=context
            )
            result.add_error(error)
        except Exception as e:
            result.add_warning(f"JSON validation failed: {str(e)}")

    def _validate_wav_signal(self, value: Any, result: ValidationResult, context: Dict[str, Any]):
        """Validate WAV audio file format"""
        try:
            content = self._get_content_sample(value, size=44)  # WAV header is 44 bytes
            if content and len(content) >= 12:
                # Check WAV header
                if content[:4] != b'RIFF' or content[8:12] != b'WAVE':
                    error = FileValidationError(
                        message="Invalid WAV file header",
                        context=context
                    )
                    result.add_error(error)

        except Exception as e:
            result.add_warning(f"WAV validation failed: {str(e)}")

    def _get_content_sample(self, value: Any, size: int = 1024) -> Optional[bytes]:
        """Get a sample of file content for validation"""
        if isinstance(value, str) and os.path.exists(value):
            try:
                with open(value, 'rb') as f:
                    return f.read(size)
            except Exception:
                return None
        elif hasattr(value, 'read'):
            try:
                current_pos = value.tell() if hasattr(value, 'tell') else 0
                content = value.read(size)
                if hasattr(value, 'seek'):
                    value.seek(current_pos)
                return content if isinstance(content, bytes) else content.encode('utf-8')
            except Exception:
                return None
        else:
            return None


# Factory function for creating file validation pipeline
def create_file_validation_pipeline(
    file_type: str = "signal",
    max_size: int = 100 * 1024 * 1024,
    strict_security: bool = True
) -> 'ValidationPipeline':
    """
    Create a pre-configured validation pipeline for file uploads

    Args:
        file_type: Type of files to validate (signal, general)
        max_size: Maximum file size in bytes
        strict_security: Enable strict security scanning

    Returns:
        Configured ValidationPipeline
    """
    from ..framework.validation_pipeline import ValidationPipeline, PipelineStage

    pipeline = ValidationPipeline(f"file_validation_{file_type}")

    # Basic file validation
    pipeline.add_validator(
        FileTypeValidator(),
        PipelineStage.TYPE_VALIDATION
    )
    pipeline.add_validator(
        FileSizeValidator(max_size=max_size),
        PipelineStage.TYPE_VALIDATION
    )

    # Security validation
    if strict_security:
        pipeline.add_validator(
            FileContentValidator(scan_content=True),
            PipelineStage.SECURITY_VALIDATION
        )

    # Signal-specific validation
    if file_type == "signal":
        pipeline.add_validator(
            SignalFileValidator(),
            PipelineStage.BUSINESS_VALIDATION
        )

    return pipeline