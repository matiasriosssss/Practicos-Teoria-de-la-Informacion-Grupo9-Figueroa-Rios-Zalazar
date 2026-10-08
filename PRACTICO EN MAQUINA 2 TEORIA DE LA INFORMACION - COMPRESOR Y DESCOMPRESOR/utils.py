"""
Módulo de utilidades: cálculo de hash SHA-256 y formateo de reportes de salida
según el formato exacto requerido por la cátedra.
"""

import hashlib
from pathlib import Path
from typing import Union
from metrics import CompressionMetrics, DecompressionMetrics


def compute_sha256(source: Union[bytes, str, Path]) -> str:
    """Calcula el hash SHA-256 de una secuencia de bytes o de un archivo en disco."""
    hasher = hashlib.sha256()
    if isinstance(source, bytes):
        hasher.update(source)
    else:
        path = Path(source)
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
    return hasher.hexdigest()


def print_compression_report(input_name: str, output_name: str, m: CompressionMetrics) -> None:
    """Muestra por consola el reporte de compresión exigido en la especificación."""
    print("========================================")
    print(" COMPRESIÓN FANO - ORDEN 2")
    print("========================================")
    print(f"Entrada: {input_name}")
    print(f"Salida: {output_name}")
    print()
    print("Algoritmo: Fano")
    print("Extensión: Orden 2")
    print()
    print(f"Tamaño original: {m.original_size} bytes")
    print(f"Tamaño comprimido: {m.compressed_size} bytes")
    print(f"Tamaño cabecera: {m.header_size} bytes")
    print(f"Datos comprimidos: {m.compressed_data_size} bytes")
    print()
    print(f"Ratio: {m.ratio:.4f}")
    print(f"Ahorro: {m.savings:.2f} %")
    print(f"Tamaño relativo: {m.relative_size:.2f} %")
    print(f"Overhead cabecera: {m.header_overhead:.2f} %")
    print()
    print(f"Tiempo compresión: {m.compression_time:.4f} s")
    print(f"Throughput: {m.throughput:.4f} MB/s")
    print()
    print(f"Pares totales: {m.total_pairs}")
    print(f"Pares diferentes: {m.unique_pairs}")
    print(f"Bits válidos: {m.valid_bits}")
    print("========================================")


def print_decompression_report(input_name: str, output_name: str, m: DecompressionMetrics) -> None:
    """Muestra por consola el reporte de descompresión exigido en la especificación."""
    print("========================================")
    print(" DESCOMPRESIÓN FANO - ORDEN 2")
    print("========================================")
    print(f"Entrada: {input_name}")
    print(f"Salida: {output_name}")
    print()
    print(f"Tamaño comprimido: {m.compressed_size} bytes")
    print(f"Tamaño original: {m.original_size} bytes")
    print()
    print(f"Tiempo descompresión: {m.decompression_time:.4f} s")
    print(f"Throughput: {m.throughput:.4f} MB/s")
    print()
    print(f"SHA-256 original: {m.sha256_original if m.sha256_original else '(No provisto)'}")
    print(f"SHA-256 reconstruido: {m.sha256_reconstructed}")
    print()
    status = "OK" if m.is_valid else "ERROR: INTEGRIDAD NO COINCIDE"
    print(f"Integridad: {status}")
    print("========================================")
