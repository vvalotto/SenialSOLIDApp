SenialSOLIDApp Documentation
============================

**Domain-Driven Design Signal Processing Application**

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   architecture
   api/modules
   quality/standards
   development/contributing

Bienvenido a SenialSOLIDApp
===========================

SenialSOLIDApp es una aplicación Python para adquisición, procesamiento y visualización de señales que implementa:

* **Principios SOLID** en Python
* **Domain-Driven Design (DDD)**
* **Clean Architecture** con separación clara de responsabilidades
* **Prácticas modernas** de desarrollo Python

Índices y Tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Arquitectura DDD
================

La aplicación sigue una arquitectura DDD con las siguientes capas:

:domain:`Capa de Dominio`
    Contiene las entidades, value objects y lógica de negocio central

:application:`Capa de Aplicación`
    Orquesta los casos de uso y coordina las operaciones del dominio

:infrastructure:`Capa de Infraestructura`
    Implementa los detalles técnicos de persistencia y servicios externos

:presentation:`Capa de Presentación`
    Maneja la interfaz de usuario y las APIs externas

Quick Start
===========

.. code-block:: bash

   # Clonar repositorio
   git clone https://github.com/vvalotto/SenialSOLIDApp.git
   cd SenialSOLIDApp

   # Setup automático
   python scripts/setup.py --dev

   # Ejecutar aplicación
   python presentacion/webapp/views.py

Documentación por Capa
======================

.. toctree::
   :maxdepth: 1
   :caption: Capas DDD

   api/dominio
   api/aplicacion
   api/infraestructura
   api/presentacion
   api/config

Estándares de Calidad
====================

.. toctree::
   :maxdepth: 1
   :caption: SSA-25 & SSA-27

   quality/metrics
   quality/documentation_standards
   quality/quality_gates

Guías de Desarrollo
==================

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/setup
   development/contributing
   development/testing
   development/deployment