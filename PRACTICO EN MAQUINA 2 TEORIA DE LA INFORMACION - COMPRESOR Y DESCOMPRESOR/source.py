"""
Módulo de modelado de fuente de información: Extensión de Orden 2.
Agrupa la secuencia binaria de entrada en pares de bytes (símbolos extendidos),
calcula frecuencias, probabilidades y realiza el ordenamiento determinista.
"""

from collections import Counter
from typing import Dict, List, Tuple


def group_bytes_into_pairs(data: bytes) -> Tuple[List[bytes], bool]:
    """
    Agrupa los bytes en símbolos de orden 2 (pares de 2 bytes).
    
    Si la cantidad de bytes es impar:
      El último byte se empareja con un byte nulo (b'\\x00') para completar el símbolo extendido.
      Al descomprimir, el archivo reconstruido se trunca exactamente al tamaño original
      almacenado en la cabecera, garantizando integridad byte a byte.
      
    Retorna:
      (lista_de_pares, es_impar) donde cada par es un objeto `bytes` de longitud 2.
    """
    n = len(data)
    is_odd = (n % 2 != 0)
    pairs: List[bytes] = []

    for i in range(0, n - 1, 2):
        pairs.append(data[i:i + 2])

    if is_odd:
        # Último byte completado con 0x00
        last_pair = bytes([data[-1], 0x00])
        pairs.append(last_pair)

    return pairs, is_odd


def calculate_frequencies(pairs: List[bytes]) -> Dict[bytes, int]:
    """
    Cuenta la cantidad de apariciones de cada par de bytes en la secuencia.
    """
    return dict(Counter(pairs))


def calculate_probabilities(frequencies: Dict[bytes, int], total_pairs: int) -> Dict[bytes, float]:
    """
    Calcula la probabilidad P(s) = freq(s) / total_pares de cada símbolo.
    """
    if total_pairs == 0:
        return {}
    return {symbol: count / total_pairs for symbol, count in frequencies.items()}


def get_sorted_symbols(frequencies: Dict[bytes, int]) -> List[Tuple[bytes, int]]:
    """
    Ordena los símbolos de forma descendente por frecuencia.
    Para garantizar determinismo estricto ante frecuencias idénticas (empates),
    se utiliza el valor lexicográfico del par de bytes como segundo criterio.
    """
    # Ordenar por: frecuencia descendente (-item[1]), luego por el par en sí (item[0])
    return sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))


def reconstruct_bytes_from_pairs(pairs: List[bytes], original_size: int) -> bytes:
    """
    Desempaqueta la lista de pares de 2 bytes en una secuencia plana de bytes,
    truncando el resultado final al tamaño original exacto (descartando el relleno si era impar).
    """
    reconstructed = bytearray()
    for pair in pairs:
        reconstructed.extend(pair)

    # Truncar al tamaño original exacto registrado en la cabecera
    return bytes(reconstructed[:original_size])
