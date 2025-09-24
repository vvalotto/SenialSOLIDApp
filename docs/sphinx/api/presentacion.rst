Presentación (Presentation Layer)
==================================

**User Interfaces and External APIs**

The presentation layer handles all user interaction and external API endpoints. It provides multiple interfaces for accessing the application functionality while maintaining separation from business logic.

.. currentmodule:: presentacion

Web Application
===============

Flask-based web interface for signal management.

Views and Controllers
--------------------

Main web application views and HTTP endpoints.

.. automodule:: presentacion.webapp.views
   :members:
   :undoc-members:
   :show-inheritance:

Forms and Templates
-------------------

Web forms and template rendering components.

.. automodule:: presentacion.webapp.forms
   :members:
   :undoc-members:
   :show-inheritance:

Static Resources
----------------

CSS, JavaScript, and other static assets for the web interface.

Console Application
===================

Command-line interface for signal operations.

Console Interface
-----------------

Terminal-based user interface components.

.. automodule:: presentacion.consola.interfaz_usuario
   :members:
   :undoc-members:
   :show-inheritance:

Command Launcher
----------------

Application entry point and command processing.

.. automodule:: presentacion.consola.lanzador
   :members:
   :undoc-members:
   :show-inheritance:

API Endpoints
=============

REST API endpoints for external integrations.

Signal Operations
-----------------

HTTP endpoints for signal management operations.

.. automodule:: presentacion.api.signal_endpoints
   :members:
   :undoc-members:
   :show-inheritance:

Health Checks
-------------

System health and monitoring endpoints.

.. automodule:: presentacion.api.health_endpoints
   :members:
   :undoc-members:
   :show-inheritance:

User Interface Patterns
========================

The presentation layer follows established UI patterns:

* **MVC Pattern**: Model-View-Controller separation
* **Template Pattern**: Consistent UI rendering
* **Command Pattern**: User action processing
* **Observer Pattern**: Real-time UI updates
* **Facade Pattern**: Simplified API interfaces

Web Interface Features
======================

The Flask web application provides:

**Signal Management**
   * Create, read, update, delete operations
   * Visual signal plotting and analysis
   * Batch processing capabilities
   * Export functionality

**User Experience**
   * Responsive design for mobile/desktop
   * Real-time status updates
   * Form validation with user feedback
   * Accessibility compliance

**Security Features**
   * CSRF protection
   * Input sanitization
   * Session management
   * Rate limiting

Console Interface Features
==========================

The command-line interface offers:

**Interactive Mode**
   * Menu-driven navigation
   * Real-time feedback
   * Progress indicators
   * Error handling with recovery

**Batch Mode**
   * Script automation support
   * Configuration file processing
   * Bulk operations
   * Output formatting options

API Design
==========

REST API follows modern design principles:

**Resource-Oriented**
   * Clear URL structure
   * HTTP method semantics
   * Status code compliance
   * Content negotiation

**Documentation**
   * OpenAPI/Swagger specification
   * Interactive API explorer
   * Code examples
   * Integration guides

**Versioning**
   * URL-based versioning
   * Backward compatibility
   * Deprecation notices
   * Migration guides

Error Handling
==============

User-friendly error presentation:

* **Web Interface**: Error pages with helpful messages
* **Console Interface**: Colored output with suggestions
* **API**: Structured error responses with error codes
* **Logging**: Detailed technical information for debugging

For development guidelines, see :doc:`../development/contributing`.