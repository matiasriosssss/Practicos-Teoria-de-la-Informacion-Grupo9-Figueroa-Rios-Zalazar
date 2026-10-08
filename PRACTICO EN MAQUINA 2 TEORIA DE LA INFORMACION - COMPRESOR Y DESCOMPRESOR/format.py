"""
Módulo de serialización y deserialización del formato binario .tdi.
Diseñado con cabecera mínima, estructurada y validación exhaustiva de integridad.
"""

import struct
from typing import Dict, Tuple

MAGIC_BYTES = b"TDI2"
FORMAT_VERSION = 1
EXTENSION_ORDER = 2

# Encabezado fijo:
# Magic bytes (4B) + Version (1B) + Extension order (1B) + Original size (8B) + Valid bits last byte (1B) + Symbols count (4B)
HEADER_FIXED_FORMAT = ">4sBBQBI"
HEADER_FIXED_SIZE = struct.calcsize(HEADER_FIXED_FORMAT)


class TDIFormatError(Exception):
    """Excepción base para errores en el formato de archivo .tdi."""
    pass


def serialize_tdi(
    original_size: int,
    codes: Dict[bytes, str],
    compressed_bytes: bytes,
    valid_bits_last_byte: int
) -> bytes:
    """
    Serializa la cabecera, diccionario y payload comprimido en el formato final .tdi.
    
    Estructura:
      [CABECERA FIJA - 19 bytes]:
        - 4 bytes: Magic bytes (b'TDI2')
        - 1 byte:  Versión (1)
        - 1 byte:  Orden de extensión (2)
        - 8 bytes: Tamaño original en bytes (uint64)
        - 1 byte:  Bits válidos en el último byte del payload (0 a 8)
        - 4 bytes: Cantidad de símbolos en el diccionario (uint32)
      [DICCIONARIO DE CÓDIGOS]:
        Para cada par:
          - 2 bytes: Par de bytes (b1, b2)
          - 1 byte:  Longitud del código en bits (L)
          - ceil(L / 8) bytes: Bits del código empaquetados (alineados a MSB)
      [DATOS COMPRIMIDOS (PAYLOAD)]:
        - Bytes del bitstream codificado con Fano.
    """
    num_symbols = len(codes)

    # 1. Empaquetar cabecera fija
    header_fixed = struct.pack(
        HEADER_FIXED_FORMAT,
        MAGIC_BYTES,
        FORMAT_VERSION,
        EXTENSION_ORDER,
        original_size,
        valid_bits_last_byte,
        num_symbols
    )

    # 2. Empaquetar diccionario de códigos Fano
    dict_buffer = bytearray()
    for symbol, code_str in codes.items():
        if len(symbol) != 2:
            raise ValueError(f"El símbolo debe ser de exactamente 2 bytes, recibido: {len(symbol)}")
        
        code_len = len(code_str)
        if code_len > 255:
            raise ValueError(f"Longitud de código Fano excede 255 bits: {code_len}")

        # Empaquetar bits del código en bytes (MSB primero)
        code_bytes = bytearray()
        cur_byte = 0
        bit_count = 0
        for b in code_str:
            cur_byte = (cur_byte << 1) | (1 if b == '1' else 0)
            bit_count += 1
            if bit_count == 8:
                code_bytes.append(cur_byte)
                cur_byte = 0
                bit_count = 0
        if bit_count > 0:
            code_bytes.append(cur_byte << (8 - bit_count))

        dict_buffer.extend(symbol)                      # 2 bytes
        dict_buffer.append(code_len)                     # 1 byte
        dict_buffer.extend(code_bytes)                   # ceil(L / 8) bytes

    return bytes(header_fixed) + bytes(dict_buffer) + compressed_bytes


def deserialize_tdi(tdi_data: bytes) -> Tuple[int, Dict[bytes, str], bytes, int, int]:
    """
    Deserializa y valida un archivo .tdi completo.
    
    Retorna:
      (original_size, codes, compressed_payload, total_bits_payload, header_total_size)
      
    Lanza TDIFormatError ante cualquier inconsistencia o corrupción.
    """
    if len(tdi_data) < HEADER_FIXED_SIZE:
        raise TDIFormatError("Archivo .tdi truncado: tamaño insuficiente para leer la cabecera básica.")

    magic, version, order, original_size, valid_bits_last, num_symbols = struct.unpack(
        HEADER_FIXED_FORMAT, tdi_data[:HEADER_FIXED_SIZE]
    )

    # Validaciones obligatorias de cabecera
    if magic != MAGIC_BYTES:
        raise TDIFormatError(f"Magic bytes inválidos. Esperado {MAGIC_BYTES!r}, obtenido {magic!r}. Archivo incompatible.")
    
    if version != FORMAT_VERSION:
        raise TDIFormatError(f"Versión de formato no soportada ({version}). Se espera versión {FORMAT_VERSION}.")

    if order != EXTENSION_ORDER:
        raise TDIFormatError(f"Orden de extensión incorrecto ({order}). El algoritmo requiere orden {EXTENSION_ORDER}.")

    if valid_bits_last > 8:
        raise TDIFormatError(f"Bits válidos en último byte fuera de rango (0-8): {valid_bits_last}.")

    offset = HEADER_FIXED_SIZE
    codes: Dict[bytes, str] = {}

    # Deserializar diccionario
    for i in range(num_symbols):
        if offset + 3 > len(tdi_data):
            raise TDIFormatError(f"Cabecera corrupta o archivo truncado: datos insuficientes para leer símbolo {i+1} de {num_symbols}.")

        symbol = tdi_data[offset:offset + 2]
        code_len = tdi_data[offset + 2]
        offset += 3

        packed_bytes_count = (code_len + 7) // 8
        if offset + packed_bytes_count > len(tdi_data):
            raise TDIFormatError(f"Diccionario incompleto: archivo truncado al leer el código del símbolo {symbol!r}.")

        code_bytes = tdi_data[offset:offset + packed_bytes_count]
        offset += packed_bytes_count

        # Reconstruir string de bits del código
        bits = []
        bits_extracted = 0
        for byte_val in code_bytes:
            for b_idx in range(7, -1, -1):
                if bits_extracted < code_len:
                    bit = (byte_val >> b_idx) & 1
                    bits.append(str(bit))
                    bits_extracted += 1
                else:
                    break
        codes[symbol] = "".join(bits)

    header_total_size = offset
    compressed_payload = tdi_data[offset:]

    # Calcular cantidad total de bits válidos en el payload
    payload_len = len(compressed_payload)
    if payload_len == 0:
        total_bits = 0
    else:
        total_bits = (payload_len - 1) * 8 + (valid_bits_last if valid_bits_last > 0 else 8)

    return original_size, codes, compressed_payload, total_bits, header_total_size
