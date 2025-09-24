API Reference
=============

**SenialSOLIDApp - Complete API Documentation**

This section contains the complete API documentation generated from the Google Style docstrings following SSA-27 standards.

.. toctree::
   :maxdepth: 2
   :caption: API Modules:

   dominio
   aplicacion
   infraestructura
   presentacion
   config

Module Organization
==================

The API is organized following **Domain-Driven Design** principles:

* :doc:`dominio` - Core business logic and entities
* :doc:`aplicacion` - Use cases and application services
* :doc:`infraestructura` - Technical implementation details
* :doc:`presentacion` - User interfaces and external APIs
* :doc:`config` - Configuration and dependency injection

Documentation Standards
========================

All API documentation follows **SSA-27 Google Style** standards:

* Complete docstrings for all public APIs
* Type hints for better IDE support
* Business context for domain code
* Usage examples for complex operations
* Exception handling documentation

Quality Assurance
==================

This documentation is automatically validated for:

* **Docstring Coverage**: >= 90%
* **Type Annotation Coverage**: >= 85%
* **Documentation Build**: Must succeed without errors
* **Link Validation**: All references must be valid

For development guidelines, see :doc:`../development/contributing`.