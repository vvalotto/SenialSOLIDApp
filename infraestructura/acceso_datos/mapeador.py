"""Object mapping module for persistence transformations.

This module provides object-to-storage mapping capabilities for converting
Python objects to different persistence formats. Implements the Mapper pattern
to handle serialization and deserialization between domain objects and
storage representations.

Classes:
    Mapeador: Abstract base class defining mapping interface
    MapeadorArchivo: File-based mapping implementation for text storage

The module supports:
    - Recursive object mapping for complex object graphs
    - Type preservation and reconstruction
    - Collection (list) handling
    - Primitive type mapping with validation

This is part of the infrastructure layer supporting the Repository pattern
for domain object persistence in various storage formats.
"""
from abc import ABCMeta, abstractmethod
from typing import Any, Union


class Mapeador(metaclass=ABCMeta):
    """Abstract base class for object-to-storage mapping.

    Defines the interface for converting Python objects to and from
    storage representations. Provides common utilities for type
    handling and recursive mapping operations.

    This class follows the Template Method pattern, providing
    concrete utilities while requiring subclasses to implement
    specific mapping strategies for different storage formats.

    Class Attributes:
        lista_tipos_base: List of primitive types that don't require
                         recursive mapping (terminal types)

    Abstract Methods:
        ir_a_persistidor: Convert object to storage format
        venir_desde_persistidor: Convert storage format back to object

    Example:
        Cannot be instantiated directly, use concrete implementations:

        >>> mapper = MapeadorArchivo()
        >>> storage_format = mapper.ir_a_persistidor(domain_object)
        >>> reconstructed = mapper.venir_desde_persistidor(template, storage_format)
    """
    # Lista los tipo de dato base (fin del proceso recursivo)
    lista_tipos_base = ['int', 'str', 'float', 'None', 'bool', 'date']

    def __init__(self) -> None:
        """Initialize the base mapper.

        Note:
            Base class initialization for concrete mapper implementations.
            Concrete classes should call super().__init__() in their constructors.
        """
        pass

    @staticmethod
    def tipo_dato(tipo: str, dato: str) -> Union[int, str, float, bool, None]:
        """Convert string data to appropriate Python type.

        Utility method that converts string representations back to their
        original Python types based on type name. Used during deserialization
        to restore proper type information.

        Args:
            tipo: String name of the target type ('int', 'str', 'float', 'bool')
            dato: String representation of the data to convert

        Returns:
            Union[int, str, float, bool, None]: Converted value in proper type,
                                               None for unsupported types

        Example:
            >>> Mapeador.tipo_dato('int', '42')
            42
            >>> Mapeador.tipo_dato('float', '3.14')
            3.14
            >>> Mapeador.tipo_dato('bool', 'True')
            True
            >>> Mapeador.tipo_dato('invalid', 'data')
            None

        Note:
            Supports only basic Python types. Complex objects require
            recursive mapping through ir_a_persistidor/venir_desde_persistidor.
        """
        if tipo == 'int':
            return int(dato)
        elif tipo == 'str':
            return str(dato)
        elif tipo == 'float':
            return float(dato)
        elif tipo == 'bool':
            return bool(dato)
        else:
            return None

    @abstractmethod
    def ir_a_persistidor(self, entidad: Any) -> str:
        """Convert object to storage representation.

        Abstract method that must be implemented by concrete mapper classes.
        Each implementation defines specific serialization strategy for
        converting Python objects to storage format.

        Args:
            entidad: Python object to be converted to storage format

        Returns:
            str: String representation suitable for storage backend

        Raises:
            NotImplementedError: If not implemented by concrete class

        Note:
            Implementations should handle complex object graphs recursively
            and preserve type information for accurate reconstruction.
        """
        pass

    @abstractmethod
    def venir_desde_persistidor(self, entidad: Any, entidad_mapeada: str) -> Any:
        """Convert storage representation back to object.

        Abstract method that must be implemented by concrete mapper classes.
        Each implementation defines specific deserialization strategy for
        reconstructing Python objects from storage format.

        Args:
            entidad: Template object indicating the expected type and structure
            entidad_mapeada: String representation from storage backend

        Returns:
            Any: Reconstructed Python object with restored state and type

        Raises:
            NotImplementedError: If not implemented by concrete class

        Note:
            Implementations should use the template object to understand
            the expected structure and restore all object attributes.
        """
        pass


class MapeadorArchivo(Mapeador):
    """File-based mapping implementation for text storage.

    Concrete implementation of Mapeador that converts Python objects
    to and from text-based representations suitable for file storage.
    Handles complex object graphs, collections, and primitive types
    with a custom serialization format.

    Storage Format:
        - Key-value pairs separated by colons (:)
        - Fields separated by commas (,)
        - Collections use array notation with indices (field>index:value)
        - Newlines separate object levels and collection elements
        - Recursive mapping for nested objects

    This implementation is ideal for:
        - Human-readable storage formats
        - Debugging and manual inspection
        - Simple text-based persistence
        - Cross-platform compatibility

    Example:
        Using file-based object mapping:

        >>> mapper = MapeadorArchivo()
        >>> signal = Senial()
        >>> signal.id = 'SIG_001'
        >>> signal._comentario = 'Test signal'
        >>> signal.poner_valor(25.5)
        >>> text_format = mapper.ir_a_persistidor(signal)
        >>> print(text_format)
        _id:SIG_001,_comentario:Test signal,_cantidad:1,_tamanio:10,
        _valores>0:25.5

        >>> template = Senial()
        >>> restored = mapper.venir_desde_persistidor(template, text_format)
        >>> print(restored.id)
        SIG_001

    Note:
        This format is custom and specific to this implementation.
        Not compatible with standard serialization formats.
    """
    def __init__(self) -> None:
        """Initialize the file-based mapper.

        Sets up the mapper with internal state for tracking mapped objects
        during recursive serialization operations.

        Attributes:
            _objeto_mapeado: Internal state for tracking mapping progress
                           (used during recursive operations)
        """
        super().__init__()
        self._objeto_mapeado = None

    def ir_a_persistidor(self, entidad: Any) -> str:
        """Convert Python object to text-based storage format.

        Recursively maps a Python object to a custom text format suitable
        for file storage. Handles primitive types, complex objects, and
        collections with proper type preservation.

        The mapping process:
            1. For primitive types: direct string conversion
            2. For complex objects: recursive field-by-field mapping
            3. For collections: indexed element mapping with special notation
            4. Preserves object structure for accurate reconstruction

        Args:
            entidad: Python object to be converted to storage format

        Returns:
            str: Text representation with custom format for file storage

        Example:
            >>> mapper = MapeadorArchivo()
            >>> signal = Senial()
            >>> signal._id = 'TEST'
            >>> signal._valores = [1.0, 2.0]
            >>> text = mapper.ir_a_persistidor(signal)
            >>> print(text)
            _id:TEST,_valores>0:1.0,_valores>1:2.0,

        Note:
            Uses recursive mapping for nested objects and special notation
            (field>index:value) for collection elements.
        """
        atr_lista = []
        # Inicializa la variable de mapeo serializada
        entidad_mapaeada = ''

        # Si es un tipo base mapea solo el valor interno del objeto
        if entidad.__class__.__name__ in Mapeador.lista_tipos_base:
            entidad_mapaeada += str(entidad) + ','
        else:
            # Recorre los miembros que son campos de la clase para el caso de una clase compleja
            # O sea una clase que contiene variables de intancia (campos)
            # Por lo tanto recorre los campos
            for atributo in entidad.__dict__.keys():
                # Si el campo es de tipo de clase base, lo mapea (lo serializa)
                if entidad.__dict__[atributo].__class__.__name__ in Mapeador.lista_tipos_base:
                    entidad_mapaeada += atributo + ':' + str(entidad.__dict__[atributo]) + ','
                else:
                    # Si el clase contiene una coleccion (lista) lo agrega para procesarlo
                    # despues
                    if type(entidad.__dict__[atributo]) is list:
                        atr_lista.append(atributo)
                    else:
                        # Si es un campo que corresponde a una clase compuesta
                        entidad_mapaeada += atributo + ':' + self.ir_a_persistidor(atributo)
            entidad_mapaeada += '\n'

            # Mapeo de los elementos de la coleccion (lista)
            for atributo in atr_lista:
                if type(entidad.__dict__[atributo]) is list:
                    i = 0
                    for elemento in entidad.__dict__[atributo]:
                        entidad_mapaeada += atributo + '>' + str(i) + ':' + self.ir_a_persistidor(elemento)
                        i += 1
                        entidad_mapaeada += '\n'
        return entidad_mapaeada

    def venir_desde_persistidor(self, entidad: Any, entidad_mapeada: str) -> Any:
        """Convert text storage format back to Python object.

        Reconstructs a Python object from the custom text format created by
        ir_a_persistidor. Uses the template entity to understand the expected
        structure and properly restore all object attributes and collections.

        The reconstruction process:
            1. Parse text format into records and fields
            2. Match fields with template object attributes
            3. Apply appropriate type conversion using tipo_dato
            4. Handle collections by appending to object attributes
            5. Return fully reconstructed object

        Args:
            entidad: Template object indicating expected type and structure
            entidad_mapeada: Text representation from storage (custom format)

        Returns:
            Any: Reconstructed Python object with restored state

        Example:
            >>> template = Senial()
            >>> text = "_id:TEST,_cantidad:2,_valores>0:1.0,_valores>1:2.0"
            >>> restored = mapper.venir_desde_persistidor(template, text)
            >>> print(restored.id)
            TEST
            >>> print(len(restored._valores))
            2

        Note:
            Relies on template object structure to guide reconstruction.
            Collection elements are appended in order using the indexed notation.
        """
        # separa la lineas del archivo
        sep_registros = entidad_mapeada.split('\n')
        for registro in sep_registros:
            if registro != '':
                # separa cada linea en campos(atributos)
                sep_campos = registro.split(',')
                for campo in sep_campos:
                    # separa cada campo en clave y valor
                    sep_valor = campo.split(':')
                    for atributo in entidad.__dict__.keys():
                        if atributo in sep_valor[0]:
                            if entidad.__dict__[atributo].__class__.__name__ in Mapeador.lista_tipos_base:
                                entidad.__dict__[atributo] = super().tipo_dato(
                                    entidad.__dict__[atributo].__class__.__name__,
                                    sep_valor[1]
                                )
                            elif type(entidad.__dict__[atributo]) is list:
                                entidad.__dict__[atributo].append(float(sep_valor[1]))
        return entidad
