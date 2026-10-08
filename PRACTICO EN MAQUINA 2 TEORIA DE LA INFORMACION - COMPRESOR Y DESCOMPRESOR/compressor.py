"""
Compresor de Fuente Extendida de Orden 2 + Algoritmo de Fano.
Uso por línea de comandos:
    python compressor.py <archivo_origen> <archivo_destino.tdi>
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Tuple

from bitstream import BitWriter
from format import serialize_tdi
from fano import generate_fano_codes
from metrics import CompressionMetrics
from source import (
    calculate_frequencies,
    get_sorted_symbols,
    group_bytes_into_pairs,
)
from utils import print_compression_report


def compress_bytes(data: bytes) -> Tuple[bytes, CompressionMetrics]:
    """
    Comprime un búfer de bytes utilizando Fuente Extendida de Orden 2 y Codificación de Fano.
    Retorna el archivo .tdi completo en bytes y el objeto con las métricas calculadas.
    """
    t_start = time.perf_counter()
    original_size = len(data)

    if original_size == 0:
        # Caso especial: archivo vacío
        codes = {}
        payload = bytes()
        valid_bits_last = 0
        total_pairs = 0
        unique_pairs = 0
        total_bits = 0
    else:
        # 1. Agrupar en pares de orden 2
        pairs, _ = group_bytes_into_pairs(data)
        total_pairs = len(pairs)

        # 2. Frecuencias y ordenamiento
        frequencies = calculate_frequencies(pairs)
        unique_pairs = len(frequencies)
        sorted_symbols = get_sorted_symbols(frequencies)

        # 3. Generación de códigos Fano
        codes = generate_fano_codes(sorted_symbols)

        # 4. Codificación en flujo de bits
        writer = BitWriter()
        for p in pairs:
            writer.write_bits(codes[p])
        payload, valid_bits_last = writer.flush()
        total_bits = writer.total_bits

    # 5. Serialización con cabecera
    tdi_bytes = serialize_tdi(original_size, codes, payload, valid_bits_last)
    t_end = time.perf_counter()

    compression_time = t_end - t_start
    compressed_size = len(tdi_bytes)
    header_size = compressed_size - len(payload)
    compressed_data_size = len(payload)

    metrics = CompressionMetrics(
        original_size=original_size,
        compressed_size=compressed_size,
        header_size=header_size,
        compressed_data_size=compressed_data_size,
        compression_time=compression_time,
        total_pairs=total_pairs,
        unique_pairs=unique_pairs,
        valid_bits=total_bits,
    )

    return tdi_bytes, metrics


def compress_file(input_path: str, output_path: str) -> CompressionMetrics:
    """
    Lee el archivo original en binario, comprime a .tdi y guarda el resultado.
    """
    in_file = Path(input_path)
    if not in_file.exists():
        raise FileNotFoundError(f"El archivo de entrada no existe: '{input_path}'")
    if not in_file.is_file():
        raise ValueError(f"La ruta de entrada no es un archivo regular: '{input_path}'")

    data = in_file.read_bytes()
    tdi_bytes, metrics = compress_bytes(data)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(tdi_bytes)

    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Compresor de archivos .tdi usando Fuente Extendida de Orden 2 y Codificación de Fano."
    )
    parser.add_argument("entrada", help="Ruta al archivo original que se desea comprimir.")
    parser.add_argument("salida", help="Ruta destino para el archivo comprimido (.tdi).")

    args = parser.parse_args()

    try:
        metrics = compress_file(args.entrada, args.salida)
        print_compression_report(args.entrada, args.salida, metrics)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la compresión: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
