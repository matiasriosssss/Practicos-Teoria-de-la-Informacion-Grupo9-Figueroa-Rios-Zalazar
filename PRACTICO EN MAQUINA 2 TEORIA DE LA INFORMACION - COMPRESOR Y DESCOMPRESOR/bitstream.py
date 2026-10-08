"""
Módulo de manipulación de flujos de bits (BitStream).
Permite escribir y leer bits individuales empaquetándolos eficientemente en bytes.
No asume que la longitud de bits sea múltiplo de 8.
"""

from typing import List, Tuple, Union


class BitWriter:
    """
    Acumula bits individuales y los empaqueta en bytes (MSB a LSB).
    Controla el padding del último byte.
    """

    def __init__(self):
        self._buffer: bytearray = bytearray()
        self._current_byte: int = 0
        self._bit_count: int = 0  # Bits acumulados en el byte actual (0 a 7)
        self._total_bits: int = 0

    def write_bit(self, bit: Union[int, str]) -> None:
        """Escribe un único bit (0 o 1)."""
        b = int(bit) & 1
        self._current_byte = (self._current_byte << 1) | b
        self._bit_count += 1
        self._total_bits += 1

        if self._bit_count == 8:
            self._buffer.append(self._current_byte)
            self._current_byte = 0
            self._bit_count = 0

    def write_bits(self, bit_string: str) -> None:
        """Escribe una cadena de caracteres '0' y '1'."""
        for char in bit_string:
            self.write_bit(char)

    def flush(self) -> Tuple[bytes, int]:
        """
        Finaliza la escritura. Si el último byte no se completó (quedan 1..7 bits),
        se rellena hacia la izquierda con ceros a la derecha (padding) y se agrega al buffer.
        
        Retorna:
            (datos_bytes, bits_validos_ultimo_byte)
            donde bits_validos_ultimo_byte es 1..8 (o 0 si no se escribió ningún bit).
        """
        if self._total_bits == 0:
            return bytes(), 0

        valid_bits_last = self._bit_count
        if self._bit_count > 0:
            # Desplazar a la izquierda para alinear con MSB
            padded_byte = self._current_byte << (8 - self._bit_count)
            self._buffer.append(padded_byte)
            self._current_byte = 0
            self._bit_count = 0
        else:
            valid_bits_last = 8

        return bytes(self._buffer), valid_bits_last

    @property
    def total_bits(self) -> int:
        return self._total_bits


class BitReader:
    """
    Lee bits individuales (MSB a LSB) desde un buffer de bytes.
    Respeta la cantidad total de bits válidos para no leer padding.
    """

    def __init__(self, data: bytes, total_bits: int):
        self._data: bytes = data
        self._total_bits: int = total_bits
        self._bits_read: int = 0
        self._byte_index: int = 0
        self._bit_offset: int = 0  # 0 a 7 (0 es MSB)

    def has_more_bits(self) -> bool:
        """Indica si quedan bits válidos por leer."""
        return self._bits_read < self._total_bits

    def read_bit(self) -> int:
        """
        Lee el siguiente bit (0 o 1).
        Lanza IndexError si no quedan más bits válidos.
        """
        if not self.has_more_bits():
            raise IndexError("Intento de leer más allá de los bits válidos disponibles.")

        current_byte = self._data[self._byte_index]
        # Extraer bit en posición (7 - bit_offset) -> MSB primero
        bit = (current_byte >> (7 - self._bit_offset)) & 1

        self._bits_read += 1
        self._bit_offset += 1
        if self._bit_offset == 8:
            self._bit_offset = 0
            self._byte_index += 1

        return bit

    def read_bits(self, count: int) -> str:
        """Lee 'count' bits y los devuelve como cadena '0101...'."""
        chars: List[str] = []
        for _ in range(count):
            chars.append(str(self.read_bit()))
        return "".join(chars)

    @property
    def remaining_bits(self) -> int:
        return max(0, self._total_bits - self._bits_read)
