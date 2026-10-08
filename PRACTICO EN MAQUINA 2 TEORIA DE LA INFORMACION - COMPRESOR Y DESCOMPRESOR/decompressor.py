"""
Descompresor de archivos .tdi codificados con Fuente Extendida de Orden 2 + Fano.
Uso por línea de comandos:
    python decompressor.py <archivo.tdi> <archivo_reconstruido> [--original <archivo_original>]
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

from bitstream import BitReader
from fano import build_decoding_trie
from format import TDIFormatError, deserialize_tdi
from metrics import DecompressionMetrics
from source import reconstruct_bytes_from_pairs
from utils import compute_sha256, print_decompression_report


def decompress_bytes(tdi_data: bytes) -> Tuple[bytes, int, int]:
    """
    Descomprime una secuencia de bytes en formato .tdi.
    
    Retorna:
      (datos_reconstruidos, tamaño_original, tamaño_comprimido)
      
    Lanza TDIFormatError si los datos están truncados, corruptos o son incompatibles.
    """
    compressed_size = len(tdi_data)
    original_size, codes, payload, total_bits, _ = deserialize_tdi(tdi_data)

    if original_size == 0:
        return bytes(), 0, compressed_size

    # Si hay tamaño pero no hay códigos en el diccionario
    if not codes:
        raise TDIFormatError("Cabecera corrupta: el archivo indica tamaño mayor a 0 pero no contiene diccionario.")

    # Construir árbol de búsqueda de prefijo para decodificación rápida y segura
    trie_root = build_decoding_trie(codes)
    reader = BitReader(payload, total_bits)

    expected_pairs = (original_size + 1) // 2
    decoded_pairs = []

    for _ in range(expected_pairs):
        curr = trie_root
        while not curr.is_leaf:
            if not reader.has_more_bits():
                raise TDIFormatError("Datos insuficientes: el flujo de bits terminó antes de completar el código Fano.")
            bit = reader.read_bit()
            if bit == 0:
                if curr.left is None:
                    raise TDIFormatError("Código inexistente durante la decodificación (secuencia inválida en Fano).")
                curr = curr.left
            else:
                if curr.right is None:
                    raise TDIFormatError("Código inexistente durante la decodificación (secuencia inválida en Fano).")
                curr = curr.right

        decoded_pairs.append(curr.symbol)

    if len(decoded_pairs) != expected_pairs:
        raise TDIFormatError(
            f"Cantidad incorrecta de pares decodificados: obtenidos {len(decoded_pairs)}, esperados {expected_pairs}."
        )

    # Reconstruir bytes y truncar al tamaño exacto original (eliminando posible relleno impar)
    reconstructed = reconstruct_bytes_from_pairs(decoded_pairs, original_size)

    if len(reconstructed) != original_size:
        raise TDIFormatError(
            f"Cantidad incorrecta de bytes reconstruidos: obtenidos {len(reconstructed)}, esperados {original_size}."
        )

    return reconstructed, original_size, compressed_size


def decompress_file(
    input_tdi_path: str,
    output_path: str,
    original_reference_path: Optional[str] = None
) -> DecompressionMetrics:
    """
    Lee el archivo .tdi, ejecuta la descompresión, escribe el archivo reconstruido
    y valida la integridad SHA-256.
    """
    in_file = Path(input_tdi_path)
    if not in_file.exists():
        raise FileNotFoundError(f"El archivo .tdi no existe: '{input_tdi_path}'")
    if not in_file.is_file():
        raise ValueError(f"La ruta no es un archivo regular: '{input_tdi_path}'")

    tdi_data = in_file.read_bytes()

    t_start = time.perf_counter()
    reconstructed_bytes, original_size, compressed_size = decompress_bytes(tdi_data)
    t_end = time.perf_counter()
    decompression_time = t_end - t_start

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(reconstructed_bytes)

    # Hash SHA-256 del archivo reconstruido
    sha_reconstructed = compute_sha256(reconstructed_bytes)

    # Si se especificó el original de referencia, comparamos con él
    sha_original = ""
    is_valid = True
    if original_reference_path:
        ref_path = Path(original_reference_path)
        if ref_path.exists():
            sha_original = compute_sha256(ref_path)
            is_valid = (sha_original == sha_reconstructed)
        else:
            is_valid = False

    return DecompressionMetrics(
        compressed_size=compressed_size,
        original_size=original_size,
        decompression_time=decompression_time,
        sha256_original=sha_original,
        sha256_reconstructed=sha_reconstructed,
        is_valid=is_valid,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Descompresor de archivos .tdi codificados con Fuente Extendida de Orden 2 y Fano."
    )
    parser.add_argument("entrada", help="Ruta al archivo comprimido (.tdi).")
    parser.add_argument("salida", help="Ruta de destino para el archivo reconstruido.")
    parser.add_argument(
        "--original",
        dest="original",
        default=None,
        help="(Opcional) Ruta al archivo original para validación directa de SHA-256.",
    )

    args = parser.parse_args()

    try:
        metrics = decompress_file(args.entrada, args.salida, args.original)
        print_decompression_report(args.entrada, args.salida, metrics)
    except FileNotFoundError as e:
        print(f"Error de archivo: {e}", file=sys.stderr)
        sys.exit(1)
    except TDIFormatError as e:
        print(f"Error de formato .tdi: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la descompresión: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
