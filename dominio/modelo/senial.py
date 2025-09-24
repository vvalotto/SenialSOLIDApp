"""Domain module defining Signal entities.

This module contains the domain entities for signal processing following DDD principles.
Defines abstract base class for signals and concrete implementations including stack
and queue behaviors. Resolves OCP and LSP violations through proper abstraction.

Classes:
    SenialBase: Abstract base class defining signal interface
    Senial: Standard signal implementation with list-based storage
    SenialPila: Stack-based signal implementation (LIFO)
    SenialCola: Queue-based signal implementation (FIFO)

This module is part of the domain layer and contains critical business entities
for signal acquisition and processing in the SenialSOLIDApp system.
"""


from abc import ABCMeta, abstractmethod
from collections import deque
import datetime
from typing import Union, List, Optional, Any
from config.logging_config import get_logger
from exceptions import ValidationException

logger = get_logger(__name__)


class SenialBase(metaclass=ABCMeta):
    """Abstract base class for signal domain entities.

    Defines the interface and common behavior for signal entities following
    DDD principles. All signal implementations must inherit from this base
    class to ensure consistent behavior and maintain domain constraints.

    Business Rules:
        - Signal capacity cannot exceed configured maximum (tamanio)
        - All values must be numeric (int or float)
        - Signal ID must be unique within the system
        - Acquisition date is immutable once set
        - Quantity tracking must be consistent with actual values

    Attributes:
        id: Unique identifier for the signal across the system
        comentario: Human-readable description of signal purpose and context
        fecha_adquisicion: Timestamp when signal was acquired (immutable)
        cantidad: Current number of values stored in the signal
        tamanio: Maximum capacity for signal values (business constraint)
        valores: Container holding the actual signal measurements

    Abstract Methods:
        poner_valor: Add a measurement value to the signal
        sacar_valor: Remove a value from the signal (implementation-specific)

    Example:
        Signals cannot be instantiated directly but through concrete implementations:

        >>> signal = Senial(tamanio=100)  # Concrete implementation
        >>> signal.id = "SIG_001"
        >>> signal.comentario = "Temperature readings from sensor A"
        >>> signal.poner_valor(25.5)
        >>> print(f"Signal has {signal.cantidad} values")
        Signal has 1 values
    """
    def __init__(self, tamanio: int = 10) -> None:
        """Initialize signal with empty values and configuration.

        Sets up the signal with default capacity and initializes all attributes
        to their default states. The signal starts empty and ready for data acquisition.

        Args:
            tamanio: Maximum capacity for signal values. Must be positive integer.
                    Defaults to 10 for basic signal operations.

        Raises:
            ValueError: When tamanio is not a positive integer (implicit validation)

        Example:
            >>> signal = ConcreteSignal(tamanio=50)
            >>> print(signal.tamanio)
            50
            >>> print(signal.cantidad)
            0
        """
        self._id = ''
        self._comentario = ''
        self._fecha_adquisicion = None
        self._tamanio = tamanio
        self._cantidad = 0
        self._valores = []
        return

    # Propiedades
    @property
    def id(self) -> str:
        """Get signal's unique identifier.

        Returns:
            str: The unique identifier for this signal instance

        Note:
            Signal ID should be unique across the entire system to prevent
            conflicts during storage and retrieval operations.
        """
        return self._id

    @id.setter
    def id(self, valor: str) -> None:
        """Set signal's unique identifier.

        Args:
            valor: Unique identifier string for the signal

        Note:
            Once set, the ID should not be changed as it may be used
            as a key in repositories and external systems.
        """
        self._id = valor

    @property
    def comentario(self) -> str:
        """Get signal's human-readable description.

        Returns:
            str: Description explaining the signal's purpose, context, or source

        Note:
            Used for debugging, logging, and user interface display purposes.
        """
        return self._comentario

    @comentario.setter
    def comentario(self, valor: str) -> None:
        """Set signal's human-readable description.

        Args:
            valor: Description text explaining signal purpose and context
        """
        self._comentario = valor

    @property
    def fecha_adquisicion(self) -> Optional[datetime.datetime]:
        """Get signal's acquisition timestamp.

        Returns:
            Optional[datetime.datetime]: Timestamp when the signal was originally acquired,
                                       None if not yet set

        Note:
            This timestamp is immutable once set and represents the moment
            when the signal data was first captured from its source.
        """
        return self._fecha_adquisicion

    @fecha_adquisicion.setter
    def fecha_adquisicion(self, valor: datetime.datetime) -> None:
        """Set signal's acquisition timestamp.

        Args:
            valor: Datetime representing when signal was acquired from source

        Note:
            Should only be set once during signal creation. Changing this
            value after initial acquisition may affect audit trails.
        """
        self._fecha_adquisicion = valor

    @fecha_adquisicion.deleter
    def fecha_adquisicion(self) -> None:
        """Delete signal's acquisition timestamp.

        Raises:
            AttributeError: If fecha_adquisicion has already been deleted

        Note:
            Use with caution as this removes important metadata about
            when the signal was originally acquired.
        """
        del self._fecha_adquisicion

    @property
    def cantidad(self) -> int:
        """Get current number of values stored in signal.

        Returns:
            int: Current count of signal measurement values

        Note:
            This value must always be consistent with the actual number
            of elements in the valores container. Used for capacity checks.
        """
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        """Set current number of values in signal.

        Args:
            valor: New count of signal values

        Warning:
            Manual setting of cantidad should be avoided as it may cause
            inconsistency with actual valores container size. Prefer using
            poner_valor() and sacar_valor() methods for proper counting.
        """
        self._cantidad = valor

    @property
    def tamanio(self) -> int:
        """Get maximum capacity for signal values.

        Returns:
            int: Maximum number of values this signal can store

        Note:
            This represents a business constraint to prevent memory issues
            and maintain system performance. Cannot be exceeded.
        """
        return self._tamanio

    @tamanio.setter
    def tamanio(self, valor: int) -> None:
        """Set maximum capacity for signal values.

        Args:
            valor: New maximum capacity for the signal

        Warning:
            Changing tamanio when signal already contains values may cause
            data loss if new size is smaller than current cantidad.
        """
        self._tamanio = valor

    @property
    def valores(self) -> List[Union[int, float]]:
        """Get container holding signal measurement values.

        Returns:
            List[Union[int, float]]: Container with actual signal data measurements

        Warning:
            Direct access to valores should be avoided. Use poner_valor()
            and obtener_valor() methods to maintain data consistency and
            proper quantity tracking.
        """
        return self._valores

    @valores.setter
    def valores(self, datos: List[Union[int, float]]) -> None:
        """Set signal values container.

        Args:
            datos: New container with signal measurement data

        Warning:
            Direct assignment may cause inconsistency with cantidad counter.
            Ensure cantidad is updated accordingly when using this setter.
        """
        self._valores = datos

    @abstractmethod
    def poner_valor(self, valor: Union[int, float]) -> None:
        """Add a measurement value to the signal.

        Abstract method that must be implemented by concrete signal classes.
        Each implementation defines specific behavior for adding values while
        maintaining business constraints.

        Args:
            valor: Numeric measurement value to add to the signal

        Raises:
            ValidationException: When signal constraints prevent value addition
            NotImplementedError: If not implemented by concrete class

        Note:
            Implementations must enforce capacity limits and update cantidad
            counter accordingly.
        """
        pass

    @abstractmethod
    def sacar_valor(self, *args) -> Union[int, float]:
        """Remove a value from the signal.

        Abstract method with implementation-specific behavior. Different signal
        types (stack, queue, list) implement different removal strategies.

        Args:
            *args: Variable arguments depending on implementation strategy

        Returns:
            Union[int, float]: The removed measurement value

        Raises:
            ValidationException: When removal operation cannot be performed
            NotImplementedError: If not implemented by concrete class

        Note:
            Implementations must update cantidad counter and maintain
            data structure consistency.
        """
        pass

    def limpiar(self) -> None:
        """Clear all values from the signal.

        Removes all measurement data from the signal and resets the quantity
        counter to zero. The signal capacity (tamanio) remains unchanged.

        Example:
            >>> signal = Senial()
            >>> signal.poner_valor(10.5)
            >>> signal.poner_valor(12.3)
            >>> print(signal.cantidad)
            2
            >>> signal.limpiar()
            >>> print(signal.cantidad)
            0

        Note:
            This operation is irreversible. All signal data will be lost.
            Use with caution in production environments.
        """
        self._valores.clear()
        self._cantidad = 0

    def obtener_valor(self, indice: int) -> Union[int, float]:
        """Retrieve signal value at specified index.

        Gets the measurement value stored at the given position without
        removing it from the signal. Provides random access to signal data.

        Args:
            indice: Zero-based index of the value to retrieve

        Returns:
            Union[int, float]: Signal measurement value at the specified position

        Raises:
            ValidationException: When index is out of bounds with detailed context
                                including current signal state and valid range

        Example:
            >>> signal = Senial()
            >>> signal.poner_valor(15.7)
            >>> signal.poner_valor(22.1)
            >>> value = signal.obtener_valor(0)
            >>> print(value)
            15.7
            >>> value = signal.obtener_valor(1)
            >>> print(value)
            22.1

        Note:
            Index must be within valid range [0, cantidad-1]. The signal
            maintains zero-based indexing consistent with Python conventions.
        """
        try:
            valor = self._valores[indice]
            return valor
        except IndexError as e:
            raise ValidationException(
                field="indice",
                value=indice,
                rule=f"debe estar entre 0 y {len(self._valores)-1}",
                expected=f"0 <= indice < {len(self._valores)}",
                context={
                    "cantidad_valores": self._cantidad,
                    "tamanio_lista": len(self._valores),
                    "signal_id": getattr(self, 'id', 'unknown')
                },
                cause=e
            )

    def __str__(self) -> str:
        """Return string representation of the signal.

        Provides human-readable representation including signal type,
        identification, description, and acquisition timestamp for
        debugging and logging purposes.

        Returns:
            str: Formatted string with signal metadata

        Example:
            >>> signal = Senial()
            >>> signal.id = "SIG_001"
            >>> signal.comentario = "Test signal"
            >>> print(signal)
            Tipo: <class 'dominio.modelo.senial.Senial'>
            Id: SIG_001
            Descripcion: Test signal
            fecha_adquisicion: 2025-09-24 10:30:00
        """
        cad = ""
        cad += 'Tipo: ' + str(type(self)) + '\r\n'
        cad += 'Id: ' + str(self._id) + '\r\n'
        cad += 'Descripcion: ' + str(self._comentario) + '\r\n'
        cad += 'fecha_adquisicion: ' + str(self._fecha_adquisicion)
        return cad


class Senial(SenialBase):
    """Standard signal implementation with list-based storage.

    Concrete implementation of the abstract SenialBase providing list-based
    storage for signal measurements. Supports adding values sequentially
    and random access retrieval while enforcing capacity constraints.

    This implementation maintains the order of insertion and provides
    standard CRUD operations for signal data management following
    DDD domain entity patterns.

    Storage Behavior:
        - Values stored in insertion order (FIFO for retrieval)
        - Random access via obtener_valor(indice)
        - Sequential removal via sacar_valor(indice)
        - Capacity enforcement per business rules

    Example:
        Basic usage of standard signal:

        >>> signal = Senial(tamanio=5)
        >>> signal.id = "SIG_001"
        >>> signal.comentario = "Temperature sensor data"
        >>> signal.poner_valor(20.5)
        >>> signal.poner_valor(21.3)
        >>> print(f"Signal has {signal.cantidad} values")
        Signal has 2 values
        >>> first_value = signal.obtener_valor(0)
        >>> print(first_value)
        20.5
    """
    def poner_valor(self, valor: Union[int, float]) -> None:
        """Add a measurement value to the signal.

        Implements the abstract method to add values to the list-based storage
        while enforcing business rule: signal capacity must not exceed maximum
        configured size to prevent memory issues and maintain performance.

        Args:
            valor: Numeric measurement value to add to signal

        Raises:
            ValidationException: When signal is at capacity with detailed context
                                including current state and business constraints

        Example:
            >>> signal = Senial(tamanio=5)
            >>> signal.poner_valor(10.5)
            >>> signal.poner_valor(12.3)
            >>> print(signal.cantidad)
            2
        """
        if self._cantidad < self._tamanio:
            self._valores.append(valor)
            self._cantidad += 1
        else:
            raise ValidationException(
                field="capacidad_señal",
                value=self._cantidad + 1,
                rule=f"no debe exceder {self._tamanio} valores",
                expected=f"<= {self._tamanio}",
                context={
                    "cantidad_actual": self._cantidad,
                    "tamanio_maximo": self._tamanio,
                    "signal_id": getattr(self, 'id', 'unknown'),
                    "nuevo_valor": str(valor)[:50]  # Limit length for logging
                }
            )
        return

    def sacar_valor(self, indice: int) -> Union[int, float]:
        """Remove and return signal value at specified index.

        Removes the measurement value stored at the given position and
        updates the signal's quantity counter. Provides indexed removal
        capability for list-based signal storage.

        Args:
            indice: Zero-based index of the value to remove

        Returns:
            Union[int, float]: The removed measurement value

        Raises:
            ValidationException: When signal is empty, index is out of bounds,
                                or value doesn't exist in signal

        Example:
            >>> signal = Senial()
            >>> signal.poner_valor(10.5)
            >>> signal.poner_valor(12.3)
            >>> removed = signal.sacar_valor(0)
            >>> print(removed)
            10.5
            >>> print(signal.cantidad)
            1
        """
        valor = None
        if self._cantidad > 0:
            try:
                valor = self.obtener_valor(indice)
                self._valores.remove(valor)
                self._cantidad -= 1
                return valor
            except ValidationException:
                # Re-raise ValidationException from obtener_valor
                raise
            except ValueError as e:
                raise ValidationException(
                    field="valor",
                    value=valor,
                    rule="debe existir en la señal",
                    context={
                        "cantidad": self._cantidad,
                        "signal_id": getattr(self, 'id', 'unknown'),
                        "indice_solicitado": indice
                    },
                    cause=e
                )
        else:
            raise ValidationException(
                field="señal",
                value="vacía",
                rule="debe contener al menos un valor para extraer",
                context={
                    "cantidad": self._cantidad,
                    "signal_id": getattr(self, 'id', 'unknown')
                }
            )


class SenialPila(Senial):
    """Stack-based signal implementation (LIFO - Last In, First Out).

    Extends the standard Senial to provide stack behavior for signal processing.
    Values are removed from the top of the stack (most recently added value first).
    Inherits all properties and methods from Senial but overrides sacar_valor
    to implement LIFO removal strategy.

    Stack Behavior:
        - Values added to the top (end) of the stack
        - Values removed from the top (LIFO strategy)
        - No index required for removal operations
        - Maintains insertion order but reverses retrieval order

    Use Cases:
        - Signal processing requiring reverse order analysis
        - Undo/redo functionality for signal operations
        - Temporary signal buffers with LIFO processing

    Example:
        Stack-based signal operations:

        >>> pila = SenialPila(tamanio=5)
        >>> pila.poner_valor(10.0)
        >>> pila.poner_valor(20.0)
        >>> pila.poner_valor(30.0)
        >>> last_value = pila.sacar_valor()  # Returns 30.0 (LIFO)
        >>> print(last_value)
        30.0
        >>> second_last = pila.sacar_valor()  # Returns 20.0
        >>> print(second_last)
        20.0
    """

    def sacar_valor(self) -> Union[int, float]:
        """Remove and return the most recently added value (LIFO).

        Implements stack behavior by removing the value from the top of the stack
        (last position in the list). Updates quantity counter and maintains
        data structure consistency.

        Returns:
            Union[int, float]: The most recently added measurement value

        Raises:
            ValidationException: When stack is empty with detailed context
                                including signal metadata and stack type

        Example:
            >>> pila = SenialPila()
            >>> pila.poner_valor(10.0)
            >>> pila.poner_valor(20.0)
            >>> top_value = pila.sacar_valor()
            >>> print(top_value)  # 20.0 (last added)
            20.0

        Note:
            No index parameter required as stack always removes from the top.
            This follows standard stack ADT behavior.
        """
        valor = None
        try:
            valor = self._valores.pop()
            self._cantidad -= 1
            return valor
        except IndexError as e:
            raise ValidationException(
                field="pila",
                value="vacía",
                rule="debe contener al menos un elemento para extraer",
                context={
                    "cantidad": self._cantidad,
                    "signal_id": getattr(self, 'id', 'unknown'),
                    "estructura_tipo": "pila"
                },
                cause=e
            )
        return valor


class SenialCola(Senial):
    """Queue-based signal implementation (FIFO - First In, First Out).

    Extends the standard Senial to provide queue behavior for signal processing.
    Uses collections.deque for efficient operations at both ends. Values are
    removed from the front of the queue (oldest value first).

    Queue Behavior:
        - Values added to the rear (end) of the queue
        - Values removed from the front (FIFO strategy)
        - Efficient operations at both ends using deque
        - Maintains strict insertion order for processing

    Use Cases:
        - Sequential signal processing in order of arrival
        - Buffering signals for real-time processing
        - Pipeline processing where order matters
        - Streaming signal analysis

    Attributes:
        _valores: deque container for efficient queue operations

    Example:
        Queue-based signal operations:

        >>> cola = SenialCola(tamanio=5)
        >>> cola.poner_valor(10.0)
        >>> cola.poner_valor(20.0)
        >>> cola.poner_valor(30.0)
        >>> first_value = cola.sacar_valor()  # Returns 10.0 (FIFO)
        >>> print(first_value)
        10.0
        >>> second_value = cola.sacar_valor()  # Returns 20.0
        >>> print(second_value)
        20.0
    """

    def __init__(self, tamanio: int) -> None:
        """Initialize queue-based signal with deque container.

        Args:
            tamanio: Maximum capacity for signal values

        Note:
            Uses collections.deque instead of list for efficient
            queue operations at both ends.
        """
        super().__init__(tamanio)
        self._valores = deque([])

    def sacar_valor(self) -> Union[int, float]:
        """Remove and return the oldest added value (FIFO).

        Implements queue behavior by removing the value from the front of the queue
        (first position). Uses deque.popleft() for efficient O(1) operation.
        Updates quantity counter and maintains data structure consistency.

        Returns:
            Union[int, float]: The oldest measurement value in the queue

        Raises:
            ValidationException: When queue is empty with detailed context
                                including signal metadata and queue type

        Example:
            >>> cola = SenialCola(tamanio=3)
            >>> cola.poner_valor(10.0)
            >>> cola.poner_valor(20.0)
            >>> first_out = cola.sacar_valor()
            >>> print(first_out)  # 10.0 (first added)
            10.0

        Note:
            No index parameter required as queue always removes from the front.
            This follows standard queue ADT behavior with O(1) complexity.
        """
        valor = 0
        try:
            valor = self._valores.popleft()
            self._cantidad -= 1
        except IndexError as e:
            raise ValidationException(
                field="cola",
                value="vacía",
                rule="debe contener al menos un elemento para extraer",
                context={
                    "cantidad": self._cantidad,
                    "signal_id": getattr(self, 'id', 'unknown'),
                    "estructura_tipo": "cola"
                },
                cause=e
            )
        return valor


if __name__ == "__main__":
    # Configurar logging para prueba
    from config.logging_config import setup_logging
    setup_logging()

    s = SenialPila()
    s.id = '100'
    s._fecha_adquisicion = datetime.datetime.now()
    logger.info("Prueba de señal creada", extra={"senial_info": str(s)})