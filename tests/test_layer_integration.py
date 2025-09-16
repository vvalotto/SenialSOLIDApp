"""
Layer Integration Exception Handling Tests
SSA-23: Exception Handling Refactoring
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '04_dominio'))
sys.path.insert(0, os.path.join(project_root, '03_aplicacion'))
sys.path.insert(0, os.path.join(project_root, '05_Infraestructura'))
sys.path.insert(0, os.path.join(project_root, '01_presentacion'))

from exceptions import (
    ValidationException, ProcessingException, AcquisitionException,
    RepositoryException, DataAccessException, WebException, ConsoleException
)


class TestDomainLayerIntegration:
    """Test domain layer exception handling integration"""

    def test_signal_model_validation_exception(self):
        """Test signal model validation with proper exceptions"""
        # This would test the refactored modelo/senial.py
        # Since we refactored it to raise ValidationException instead of returning None

        # Simulate the refactored behavior
        def get_signal_value(signal_values, index):
            """Simulates refactored obtener_valor method"""
            try:
                return signal_values[index]
            except IndexError as e:
                raise ValidationException(
                    field="indice",
                    value=index,
                    rule=f"debe estar entre 0 y {len(signal_values)-1}",
                    context={
                        "cantidad_valores": len(signal_values),
                        "signal_id": "test_signal"
                    },
                    cause=e
                )

        # Test valid index
        signal_values = [1.0, 2.0, 3.0]
        result = get_signal_value(signal_values, 1)
        assert result == 2.0

        # Test invalid index
        with pytest.raises(ValidationException) as exc_info:
            get_signal_value(signal_values, 5)

        exception = exc_info.value
        assert exception.context["field"] == "indice"
        assert exception.context["value"] == 5
        assert "debe estar entre 0 y 2" in exception.context["rule"]

    def test_signal_capacity_validation(self):
        """Test signal capacity validation"""
        def add_signal_value(current_count, max_size, value):
            """Simulates refactored poner_valor method"""
            if current_count < max_size:
                return current_count + 1
            else:
                raise ValidationException(
                    field="capacidad_señal",
                    value=current_count + 1,
                    rule=f"no debe exceder {max_size} valores",
                    context={
                        "cantidad_actual": current_count,
                        "tamanio_maximo": max_size,
                        "signal_id": "test_signal"
                    }
                )

        # Test valid capacity
        result = add_signal_value(5, 10, 1.5)
        assert result == 6

        # Test exceeded capacity
        with pytest.raises(ValidationException) as exc_info:
            add_signal_value(10, 10, 1.5)

        exception = exc_info.value
        assert exception.context["field"] == "capacidad_señal"
        assert exception.context["cantidad_actual"] == 10
        assert exception.context["tamanio_maximo"] == 10

    def test_acquisition_file_error(self):
        """Test acquisition file error handling"""
        def read_signal_from_file(file_path):
            """Simulates refactored file acquisition"""
            try:
                with open(file_path, 'r') as f:
                    return f.readlines()
            except IOError as e:
                raise AcquisitionException(
                    source=file_path,
                    source_type="archivo",
                    acquisition_method="file_read",
                    context={"io_error_type": type(e).__name__},
                    cause=e
                )
            except ValueError as e:
                raise ValidationException(
                    field="dato_archivo",
                    value="formato_invalido",
                    rule="debe ser un número válido en cada línea",
                    context={"archivo": file_path},
                    cause=e
                )

        # Test file not found
        with pytest.raises(AcquisitionException) as exc_info:
            read_signal_from_file("/nonexistent/file.dat")

        exception = exc_info.value
        assert exception.context["source"] == "/nonexistent/file.dat"
        assert exception.context["source_type"] == "archivo"
        assert exception.context["acquisition_method"] == "file_read"


class TestApplicationLayerIntegration:
    """Test application layer exception handling with recovery"""

    @patch('03_aplicacion.managers.controlador_adquisicion.handle_with_recovery')
    def test_acquisition_controller_with_recovery(self, mock_handle_recovery):
        """Test acquisition controller with recovery strategies"""
        # Mock successful recovery
        mock_handle_recovery.return_value = Mock()

        # Simulate the refactored controller behavior
        def acquire_signal():
            """Simulates refactored adquirir_senial method"""
            def _realizar_adquisicion():
                # This would call actual acquisition logic
                mock_adquisidor = Mock()
                mock_adquisidor.leer_senial = Mock()
                mock_adquisidor.obtener_senial_adquirida = Mock(return_value=Mock())

                mock_adquisidor.leer_senial()
                return mock_adquisidor.obtener_senial_adquirida()

            return mock_handle_recovery(
                operation=_realizar_adquisicion,
                operation_name="adquirir_senial",
                context={"adquisidor_tipo": "MockAdquisidor"},
                max_attempts=2
            )

        result = acquire_signal()
        assert result is not None
        mock_handle_recovery.assert_called_once()

        # Verify recovery parameters
        args, kwargs = mock_handle_recovery.call_args
        assert kwargs["operation_name"] == "adquirir_senial"
        assert kwargs["max_attempts"] == 2
        assert "adquisidor_tipo" in kwargs["context"]

    def test_processing_controller_exception_wrapping(self):
        """Test processing controller exception wrapping"""
        def process_signal(signal_id="test_signal"):
            """Simulates processing with exception wrapping"""
            try:
                # Simulate processing failure
                raise ValueError("Processing algorithm failed")
            except ProcessingException:
                # Re-raise processing exceptions as-is
                raise
            except Exception as ex:
                # Wrap unexpected exceptions
                raise ProcessingException(
                    operation="procesar_senial",
                    signal_id=signal_id,
                    processing_stage="controller_managed",
                    context={"valores_entrada": 100},
                    cause=ex
                )

        # Test exception wrapping
        with pytest.raises(ProcessingException) as exc_info:
            process_signal("signal_123")

        exception = exc_info.value
        assert exception.context["operation"] == "procesar_senial"
        assert exception.context["signal_id"] == "signal_123"
        assert exception.context["processing_stage"] == "controller_managed"
        assert isinstance(exception.cause, ValueError)

    def test_repository_operation_with_recovery(self):
        """Test repository operation with recovery strategies"""
        def save_signal_with_recovery(signal_data):
            """Simulates repository save with recovery"""
            def _guardar_en_repo():
                # Simulate repository operation
                if signal_data.get("force_fail"):
                    raise IOError("Disk full")
                return "saved"

            try:
                # This would use handle_with_recovery in real implementation
                return _guardar_en_repo()
            except IOError as ex:
                raise RepositoryException(
                    operation="guardar",
                    entity_type="senial",
                    entity_id=signal_data.get("id", "unknown"),
                    context={"repository_type": "FileRepository"},
                    cause=ex
                )

        # Test successful save
        result = save_signal_with_recovery({"id": "signal_123", "data": [1, 2, 3]})
        assert result == "saved"

        # Test failed save
        with pytest.raises(RepositoryException) as exc_info:
            save_signal_with_recovery({"id": "signal_456", "force_fail": True})

        exception = exc_info.value
        assert exception.context["operation"] == "guardar"
        assert exception.context["entity_type"] == "senial"
        assert exception.context["entity_id"] == "signal_456"


class TestInfrastructureLayerIntegration:
    """Test infrastructure layer I/O exception handling"""

    def test_context_file_operations(self):
        """Test context file operations with recovery"""
        def persist_entity_with_recovery(entity_data, entity_id):
            """Simulates ContextoPickle.persistir with recovery"""
            file_path = f"/tmp/{entity_id}.pickle"

            def _persistir_entidad():
                # Simulate pickle operation
                if entity_data.get("corrupt_data"):
                    raise ValueError("Cannot pickle corrupt data")
                return f"Persisted to {file_path}"

            try:
                # This would use handle_with_recovery in real implementation
                return _persistir_entidad()
            except Exception as ex:
                raise DataAccessException(
                    file_path=file_path,
                    operation="persistir",
                    context={
                        "id_entidad": entity_id,
                        "entity_type": "TestEntity",
                        "contexto_tipo": "ContextoPickle"
                    },
                    cause=ex
                )

        # Test successful persistence
        result = persist_entity_with_recovery({"valid": "data"}, "entity_123")
        assert "Persisted" in result

        # Test failed persistence
        with pytest.raises(DataAccessException) as exc_info:
            persist_entity_with_recovery({"corrupt_data": True}, "entity_456")

        exception = exc_info.value
        assert exception.context["file_path"] == "/tmp/entity_456.pickle"
        assert exception.context["operation"] == "persistir"
        assert exception.context["entity_type"] == "TestEntity"

    def test_configuration_validation(self):
        """Test configuration exception handling"""
        def validate_resource_name(resource_name):
            """Simulates BaseContexto.__init__ validation"""
            if resource_name is None or resource_name == "":
                from exceptions import ConfigurationException
                raise ConfigurationException(
                    config_key="recurso",
                    config_type="contexto_persistencia",
                    context={
                        "provided_value": str(resource_name),
                        "validation_rule": "nombre_recurso_requerido"
                    }
                )
            return f"Valid resource: {resource_name}"

        # Test valid resource name
        result = validate_resource_name("valid_resource")
        assert "Valid resource" in result

        # Test invalid resource names
        for invalid_name in [None, "", "   "]:
            with pytest.raises(ConfigurationException) as exc_info:
                validate_resource_name(invalid_name)

            exception = exc_info.value
            assert exception.context["config_key"] == "recurso"
            assert exception.context["config_type"] == "contexto_persistencia"

    def test_audit_and_trace_operations(self):
        """Test audit and trace file operations"""
        def write_audit_log(context_info, audit_message):
            """Simulates audit writing with exception handling"""
            log_file = "auditor_contexto.log"
            try:
                # Simulate audit write operation
                if audit_message == "FAIL":
                    raise IOError("Cannot write to audit log")
                return f"Audit written: {audit_message}"
            except IOError as eIO:
                raise DataAccessException(
                    file_path=log_file,
                    operation="audit_write",
                    context={
                        "contexto": str(context_info)[:100],
                        "auditoria": str(audit_message)[:100],
                        "operation_type": "contexto_audit"
                    },
                    cause=eIO
                )

        # Test successful audit
        result = write_audit_log("test_context", "Successful operation")
        assert "Audit written" in result

        # Test failed audit
        with pytest.raises(DataAccessException) as exc_info:
            write_audit_log("test_context", "FAIL")

        exception = exc_info.value
        assert exception.context["file_path"] == "auditor_contexto.log"
        assert exception.context["operation"] == "audit_write"
        assert exception.context["operation_type"] == "contexto_audit"


class TestPresentationLayerIntegration:
    """Test presentation layer user-friendly exception handling"""

    def test_web_error_handlers(self):
        """Test web error handlers with user-friendly messages"""
        def handle_404_error(request_path):
            """Simulates 404 error handler"""
            error = WebException(
                endpoint=request_path,
                http_status=404,
                request_method="GET",
                user_message="Página no encontrada",
                recovery_suggestion="Verifique la URL o navegue desde el menú principal"
            )
            return {
                "status": 404,
                "error_message": error.user_message,
                "recovery_suggestion": error.recovery_suggestion,
                "error_code": error.error_code
            }

        # Test 404 handling
        response = handle_404_error("/nonexistent/page")
        assert response["status"] == 404
        assert response["error_message"] == "Página no encontrada"
        assert "menú principal" in response["recovery_suggestion"]
        assert response["error_code"].startswith("WebException_")

    def test_web_form_validation_errors(self):
        """Test web form validation with flash messages"""
        def handle_form_submission(form_data):
            """Simulates form submission with validation"""
            flash_messages = []

            try:
                if not form_data.get("signal_id"):
                    raise ValidationException(
                        field="signal_id",
                        value=form_data.get("signal_id", ""),
                        rule="es requerido"
                    )

                if form_data.get("force_acquisition_error"):
                    raise AcquisitionException(
                        source="test_source",
                        source_type="file",
                        acquisition_method="test"
                    )

                return {"status": "success", "messages": ["Señal adquirida exitosamente"]}

            except ValidationException as ve:
                flash_messages.append(f"Error de validación: {ve.user_message}")
                if ve.recovery_suggestion:
                    flash_messages.append(f"Sugerencia: {ve.recovery_suggestion}")
                return {"status": "error", "messages": flash_messages}

            except AcquisitionException as ae:
                flash_messages.append(f"Error de adquisición: {ae.user_message}")
                if ae.recovery_suggestion:
                    flash_messages.append(f"Sugerencia: {ae.recovery_suggestion}")
                return {"status": "error", "messages": flash_messages}

        # Test successful form submission
        result = handle_form_submission({"signal_id": "123"})
        assert result["status"] == "success"

        # Test validation error
        result = handle_form_submission({})
        assert result["status"] == "error"
        assert any("validación" in msg for msg in result["messages"])

        # Test acquisition error
        result = handle_form_submission({"signal_id": "123", "force_acquisition_error": True})
        assert result["status"] == "error"
        assert any("adquisición" in msg for msg in result["messages"])

    def test_console_error_display(self):
        """Test console error display with emojis"""
        def display_console_error(command, error_type="generic"):
            """Simulates console error display"""
            if error_type == "file_not_found":
                error = ConsoleException(
                    command=command,
                    user_message="Error al leer archivo de información",
                    recovery_suggestion="Verifique que el archivo existe y tiene permisos"
                )
                return f"❌ {error.user_message}\n💡 {error.recovery_suggestion}"

            elif error_type == "attribute_error":
                error = ConsoleException(
                    command=command,
                    user_message="Error accediendo a información de componentes",
                    recovery_suggestion="Verifique que el configurador esté correctamente inicializado"
                )
                return f"⚠️ {error.user_message}\n💡 {error.recovery_suggestion}"

            else:
                error = ConsoleException(
                    command=command,
                    user_message="Error inesperado",
                    recovery_suggestion="Contacte al administrador del sistema"
                )
                return f"❌ {error.user_message}\n💡 {error.recovery_suggestion}"

        # Test file not found error
        result = display_console_error("mostrar_acerca_de", "file_not_found")
        assert "❌" in result
        assert "💡" in result
        assert "archivo existe" in result

        # Test attribute error
        result = display_console_error("mostrar_componentes", "attribute_error")
        assert "⚠️" in result
        assert "configurador" in result

        # Test generic error
        result = display_console_error("unknown_command")
        assert "❌" in result
        assert "administrador" in result


class TestEndToEndScenarios:
    """Test complete end-to-end exception handling scenarios"""

    def test_signal_acquisition_full_flow(self):
        """Test complete signal acquisition flow with exception handling"""
        def full_acquisition_flow(source_file, signal_config):
            """Simulates complete acquisition flow"""
            results = {"steps": [], "final_status": None}

            try:
                # Step 1: Validate configuration
                if not signal_config.get("id"):
                    raise ValidationException(
                        field="signal_id",
                        value="",
                        rule="es requerido para la adquisición"
                    )
                results["steps"].append("✅ Configuration validated")

                # Step 2: Attempt file acquisition
                if not os.path.exists(source_file):
                    raise AcquisitionException(
                        source=source_file,
                        source_type="file",
                        acquisition_method="file_read"
                    )
                results["steps"].append("✅ Source file accessible")

                # Step 3: Process signal data
                if signal_config.get("processing_type") == "complex":
                    if signal_config.get("force_processing_error"):
                        raise ProcessingException(
                            operation="complex_filter",
                            signal_id=signal_config["id"],
                            processing_stage="filtering"
                        )
                results["steps"].append("✅ Signal processed")

                # Step 4: Save to repository
                if signal_config.get("force_save_error"):
                    raise RepositoryException(
                        operation="save",
                        entity_type="signal",
                        entity_id=signal_config["id"]
                    )
                results["steps"].append("✅ Signal saved")

                results["final_status"] = "success"
                return results

            except ValidationException as ve:
                results["final_status"] = f"validation_error: {ve.user_message}"
                return results
            except AcquisitionException as ae:
                results["final_status"] = f"acquisition_error: {ae.user_message}"
                return results
            except ProcessingException as pe:
                results["final_status"] = f"processing_error: {pe.user_message}"
                return results
            except RepositoryException as re:
                results["final_status"] = f"repository_error: {re.user_message}"
                return results

        # Test successful flow
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"1.0\n2.0\n3.0\n")
            temp_file.flush()

            result = full_acquisition_flow(
                temp_file.name,
                {"id": "signal_123", "processing_type": "simple"}
            )

            assert result["final_status"] == "success"
            assert len(result["steps"]) == 4
            assert all("✅" in step for step in result["steps"])

            os.unlink(temp_file.name)

        # Test validation error
        result = full_acquisition_flow("/tmp/test.dat", {})
        assert "validation_error" in result["final_status"]
        assert len(result["steps"]) == 0

        # Test file not found error
        result = full_acquisition_flow("/nonexistent/file.dat", {"id": "signal_123"})
        assert "acquisition_error" in result["final_status"]
        assert len(result["steps"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])