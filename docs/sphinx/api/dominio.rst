Dominio (Domain Layer)
======================

**Core Business Logic and Domain Entities**

The domain layer contains the heart of the business logic, following Domain-Driven Design principles. This layer is isolated from technical concerns and focuses purely on business rules and concepts.

.. currentmodule:: dominio

Domain Model
============

The central domain entities that represent core business concepts.

.. automodule:: dominio.modelo.senial
   :members:
   :undoc-members:
   :show-inheritance:

Base Classes
============

Abstract base classes that define domain contracts.

.. automodule:: dominio.modelo.senial_base
   :members:
   :undoc-members:
   :show-inheritance:

Repository Interfaces
====================

Domain repository contracts that define persistence abstractions.

.. automodule:: dominio.repositorios
   :members:
   :undoc-members:
   :show-inheritance:

Domain Exceptions
=================

Business-specific exceptions that represent domain violations.

.. automodule:: dominio.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Business Rules
==============

.. business-rule:: Signal Capacity Constraint

   Signals cannot exceed their configured maximum capacity (tamanio).
   This ensures memory management and system performance constraints are respected.

.. business-rule:: Signal Value Validation

   All signal values must be numeric (int or float) to maintain data integrity
   and enable proper mathematical operations on signal data.

.. business-rule:: Signal Identity Uniqueness

   Each signal must have a unique identifier within the system to prevent
   conflicts and ensure proper signal tracking and retrieval.

Domain Events
=============

.. domain-event:: SignalAcquired

   Triggered when a new signal is successfully acquired from an external source.
   Contains signal metadata and acquisition context for downstream processing.

.. domain-event:: SignalValueAdded

   Fired when a new value is added to a signal, enabling reactive processing
   and validation workflows.

Architecture Notes
==================

The domain layer follows these DDD principles:

* **Entity-Centric Design**: `Senial` is the main aggregate root
* **Business Language**: Uses ubiquitous language throughout
* **Invariant Protection**: Business rules are enforced at the entity level
* **Infrastructure Independence**: No dependencies on external frameworks

For implementation guidelines, see :doc:`../development/contributing`.