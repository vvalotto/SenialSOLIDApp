Aplicación (Application Layer)
===============================

**Use Cases and Application Services**

The application layer orchestrates domain operations and coordinates between the domain and infrastructure layers. It contains the use cases and application services that implement business workflows.

.. currentmodule:: aplicacion

Application Services
====================

Core application services that orchestrate domain operations.

Controllers
-----------

Main application controllers for signal operations.

.. automodule:: aplicacion.managers.controlador_adquisicion
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aplicacion.managers.controlador_procesamiento
   :members:
   :undoc-members:
   :show-inheritance:

Validation Framework
====================

Input validation and sanitization following SSA-26 patterns.

Validation Rules
----------------

.. automodule:: aplicacion.validation.rules.file_validation
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aplicacion.validation.rules.user_input_validation
   :members:
   :undoc-members:
   :show-inheritance:

Validation Framework
--------------------

.. automodule:: aplicacion.validation.framework.validation_engine
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aplicacion.validation.framework.sanitization_engine
   :members:
   :undoc-members:
   :show-inheritance:

Exception Handling
==================

Application-level exception patterns following SSA-26.

.. automodule:: aplicacion.patterns.exception_handling
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: aplicacion.patterns.recovery_strategies
   :members:
   :undoc-members:
   :show-inheritance:

Dependency Injection
====================

Configuration and dependency management.

.. automodule:: aplicacion.contenedor.configurador
   :members:
   :undoc-members:
   :show-inheritance:

Use Cases
=========

.. use-case:: Signal Acquisition

   **Primary Flow:**
   1. Configure acquisition source
   2. Execute signal reading
   3. Validate acquired data
   4. Store signal with metadata
   5. Notify completion

   **Business Rules:**
   - Signal must meet capacity constraints
   - Acquisition source must be available
   - Data must pass validation rules

.. use-case:: Signal Processing

   **Primary Flow:**
   1. Retrieve signal from repository
   2. Apply processing operations
   3. Validate processed results
   4. Store processed signal
   5. Generate processing report

   **Business Rules:**
   - Processing must preserve signal integrity
   - Operations must be mathematically valid
   - Results must meet quality thresholds

Application Patterns
====================

The application layer implements several architectural patterns:

* **Application Service Pattern**: Controllers coordinate domain operations
* **Command/Query Separation**: Clear separation of read/write operations
* **Transaction Script Pattern**: For complex business workflows
* **Dependency Injection**: Loose coupling through configuration container

Error Handling Strategy
=======================

Following SSA-26 patterns:

* **Exception Wrapping**: Infrastructure exceptions wrapped with business context
* **Recovery Strategies**: Automatic retry and fallback mechanisms
* **Logging Integration**: Structured logging for monitoring and debugging
* **User-Friendly Messages**: Technical errors translated to business language

For development guidelines, see :doc:`../development/contributing`.