"""
Módulo de utilidades para Gzip:
- Cálculo de hash SHA-256
- Detección de binario gzip CLI del sistema
- Formateo de reportes de compresión y descompresión idénticos al formato de la cátedra
"""

import hashlib
import shutil
from pathlib import Path
from typing import Optional, Union

from metrics import GzipCompressionMetrics, GzipDecompressionMetrics


def find_gzip_binary() -> Optional[str]:
    """
    Busca el binario gzip en el PATH del sistema o en rutas habituales
    (como Git for Windows).
    """
    gzip_path = shutil.which("gzip")
    if gzip_path:
        return gzip_path

    # Rutas comunes en Windows
    common_win_paths = [
        r"C:\Program Files\Git\usr\bin\gzip.exe",
        r"C:\Program Files (x86)\Git\usr\bin\gzip.exe",
        r"C:\tools\msys64\usr\bin\gzip.exe",
        r"C:\msys64\usr\bin\gzip.exe",
    ]
    for p in common_win_paths:
        if Path(p).is_file():
            return p

    return None


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


def print_compression_report(input_name: str, output_name: str, m: GzipCompressionMetrics) -> None:
    """Muestra por consola el reporte de compresión exigido en la especificación."""
    print("========================================")
    print(" COMPRESIÓN GZIP (-n -6)")
    print("========================================")
    print(f"Entrada: {input_name}")
    print(f"Salida: {output_name}")
    print()
    print("Algoritmo: Gzip (DEFLATE)")
    print("Opciones: -n -6 (Nivel 6, sin nombre ni timestamp)")
    print()
    print(f"Tamaño original (So): {m.original_size} bytes")
    print(f"Tamaño comprimido (Sc): {m.compressed_size} bytes")
    print()
    print(f"Ratio (R = So / Sc): {m.ratio:.4f}")
    print(f"Ahorro (A): {m.savings:.2f} %")
    print(f"Tamaño relativo (P): {m.relative_size:.2f} %")
    print()
    print(f"Tiempo compresión (tc): {m.compression_time:.4f} s")
    print(f"Throughput (Vc): {m.throughput:.4f} MB/s ({m.throughput_bps:.2f} B/s)")
    print("========================================")


def print_decompression_report(input_name: str, output_name: str, m: GzipDecompressionMetrics) -> None:
    """Muestra por consola el reporte de descompresión exigido en la especificación."""
    print("========================================")
    print(" DESCOMPRESIÓN GZIP")
    print("========================================")
    print(f"Entrada: {input_name}")
    print(f"Salida: {output_name}")
    print()
    print("Algoritmo: Gzip")
    print()
    print(f"Tamaño comprimido (Sc): {m.compressed_size} bytes")
    print(f"Tamaño original (So): {m.original_size} bytes")
    print()
    print(f"Tiempo descompresión (td): {m.decompression_time:.4f} s")
    print(f"Throughput (Vd): {m.throughput:.4f} MB/s ({m.throughput_bps:.2f} B/s)")
    print()
    print(f"SHA-256 original: {m.sha256_original if m.sha256_original else '(No provisto)'}")
    print(f"SHA-256 reconstruido: {m.sha256_reconstructed}")
    print()
    status = "OK" if m.is_valid else "ERROR: INTEGRIDAD NO COINCIDE"
    print(f"Integridad: {status}")
    print("========================================")
