"""
Módulo del Algoritmo de Codificación de Fano.
Implementación pura desde cero, sin librerías externas de compresión.
Soporta construcción recursiva del código de prefijo y árbol Trie para decodificación.
"""

from typing import Dict, List, Optional, Tuple


class FanoNode:
    """Nodo para el árbol de decodificación de prefijo (Trie)."""
    def __init__(self):
        self.symbol: Optional[bytes] = None
        self.left: Optional['FanoNode'] = None   # Rama '0'
        self.right: Optional['FanoNode'] = None  # Rama '1'

    @property
    def is_leaf(self) -> bool:
        return self.symbol is not None


def _find_best_split(symbols_with_freq: List[Tuple[bytes, int]]) -> int:
    """
    Encuentra el índice de partición 'split' (1 <= split < len) que minimiza
    la diferencia absoluta entre la suma de frecuencias del grupo izquierdo y derecho.
    
    |sum(izq) - sum(der)| -> mínimo.
    Ante diferencias iguales, elige el primer punto de partición para consistencia determinista.
    """
    total_sum = sum(freq for _, freq in symbols_with_freq)
    left_sum = 0
    best_split = 1
    min_diff = float('inf')

    # Evaluar posibles particiones: grupo 1: [0 : i], grupo 2: [i : N]
    for i in range(1, len(symbols_with_freq)):
        left_sum += symbols_with_freq[i - 1][1]
        right_sum = total_sum - left_sum
        diff = abs(left_sum - right_sum)

        if diff < min_diff:
            min_diff = diff
            best_split = i

    return best_split


def _fano_recursive(symbols_with_freq: List[Tuple[bytes, int]], prefix: str, codes: Dict[bytes, str]) -> None:
    """
    Función recursiva núcleo del algoritmo de Fano.
    Divide el conjunto ordenado en dos subconjuntos con sumas lo más parejas posible,
    antepone '0' al primer grupo y '1' al segundo grupo, y continúa recursivamente.
    """
    # Caso base: un solo símbolo en la partición
    if len(symbols_with_freq) == 1:
        symbol = symbols_with_freq[0][0]
        codes[symbol] = prefix if prefix else "0"
        return

    # Si hay 2 o más símbolos, encontrar el mejor punto de corte
    split_index = _find_best_split(symbols_with_freq)

    left_group = symbols_with_freq[:split_index]
    right_group = symbols_with_freq[split_index:]

    # Asignar '0' a la rama izquierda y '1' a la rama derecha
    _fano_recursive(left_group, prefix + "0", codes)
    _fano_recursive(right_group, prefix + "1", codes)


def generate_fano_codes(sorted_symbols_with_freq: List[Tuple[bytes, int]]) -> Dict[bytes, str]:
    """
    Genera el diccionario de códigos Fano a partir de una lista ordenada de (símbolo, frecuencia).
    
    Casos especiales:
      - 0 símbolos (archivo vacío): retorna diccionario vacío {}.
      - 1 símbolo único: se le asigna el código '0'.
    """
    if not sorted_symbols_with_freq:
        return {}

    codes: Dict[bytes, str] = {}

    if len(sorted_symbols_with_freq) == 1:
        # Caso especial de único símbolo
        symbol = sorted_symbols_with_freq[0][0]
        codes[symbol] = "0"
        return codes

    _fano_recursive(sorted_symbols_with_freq, "", codes)
    return codes


def build_decoding_trie(codes: Dict[bytes, str]) -> FanoNode:
    """
    Construye un árbol binario de búsqueda (Trie) a partir del diccionario {símbolo: código_bits}.
    Permite decodificar flujos de bits en tiempo O(longitud_código) por símbolo.
    """
    root = FanoNode()
    for symbol, code_str in codes.items():
        curr = root
        for bit in code_str:
            if bit == '0':
                if curr.left is None:
                    curr.left = FanoNode()
                curr = curr.left
            elif bit == '1':
                if curr.right is None:
                    curr.right = FanoNode()
                curr = curr.right
            else:
                raise ValueError(f"Bit inválido en código Fano: {bit}")
        curr.symbol = symbol
    return root
