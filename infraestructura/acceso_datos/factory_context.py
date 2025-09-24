"""Factory for creating persistence context instances.

This module implements the Factory pattern for creating appropriate
persistence context instances based on configuration parameters.
Supports multiple storage backend strategies while providing a
unified interface for context creation.

Factory Pattern Implementation:
    - Centralized context creation logic
    - Strategy selection based on type parameter
    - Consistent initialization across different backends
    - Simplified context management for clients
"""

from typing import Optional, Union
from acceso_datos.contexto import *


class FactoryContexto:
    """Factory for creating data persistence context instances.

    Implements the Factory pattern to create appropriate persistence context
    instances based on the specified storage strategy. Centralizes context
    creation logic and provides a consistent interface for obtaining
    different types of persistence contexts.

    Supported Context Types:
        - 'archivo': File-based persistence with custom mapping
        - 'pickle': Binary serialization using Python pickle

    Example:
        Creating different context types:

        >>> # Create pickle-based context
        >>> pickle_context = FactoryContexto.obtener_contexto('pickle', '/data/signals')
        >>> isinstance(pickle_context, ContextoPickle)
        True

        >>> # Create file-based context
        >>> file_context = FactoryContexto.obtener_contexto('archivo', '/data/files')
        >>> isinstance(file_context, ContextoArchivo)
        True

    Note:
        This factory provides a single point of configuration for context
        creation and makes it easy to add new persistence strategies.
    """
    def __init__(self) -> None:
        """Initialize the context factory.

        Note:
            Factory methods are static, so instantiation is not required.
            This constructor is provided for completeness but factory
            methods should be called on the class directly.
        """
        pass

    @staticmethod
    def obtener_contexto(tipo_contexto: str, param: str) -> Optional[Union[ContextoArchivo, ContextoPickle]]:
        """Create and return appropriate persistence context instance.

        Factory method that creates the appropriate persistence context
        based on the specified type and configuration parameter.

        Args:
            tipo_contexto: Type of context to create ('archivo' or 'pickle')
            param: Configuration parameter (usually directory path)

        Returns:
            Optional[Union[ContextoArchivo, ContextoPickle]]:
                Created context instance or None if type not supported

        Example:
            >>> context = FactoryContexto.obtener_contexto('pickle', '/data/signals')
            >>> if context:
            ...     context.persistir(signal, 'SIG_001')

            >>> file_context = FactoryContexto.obtener_contexto('archivo', '/data/files')
            >>> signals = file_context.listar() if file_context else []

        Note:
            Returns None for unsupported context types. Clients should
            check for None return value before using the context.
        """
        contexto = None
        if tipo_contexto == 'archivo':
            contexto = ContextoArchivo(param)
        elif tipo_contexto == 'pickle':
            contexto = ContextoPickle(param)

        return contexto