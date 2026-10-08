"""
Descompresor Gzip.
Descomprime archivos .gz y valida la integridad de los datos reconstruidos mediante SHA-256.

Uso por línea de comandos:
    python decompressorgzip.py <archivo.gz> [<archivo_reconstruido>] [--original <archivo_original>] [--use-cli]
"""

import argparse
import gzip
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

# Asegurar importación de módulos hermanos dentro de la carpeta gZip
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from metrics import GzipDecompressionMetrics
from utils import compute_sha256, find_gzip_binary, print_decompression_report


def decompress_bytes(gz_data: bytes, use_cli: bool = False) -> Tuple[bytes, int, int]:
    """
    Descomprime una secuencia de bytes en formato .gz.
    
    Args:
        gz_data: Bytes del archivo comprimido .gz.
        use_cli: Si es True, intenta invocar el binario 'gzip -d' del sistema.
        
    Retorna:
        Tuple de (bytes_reconstruidos, tamaño_original, tamaño_comprimido).
    """
    compressed_size = len(gz_data)

    if use_cli:
        gzip_bin = find_gzip_binary()
        if not gzip_bin:
            raise RuntimeError(
                "No se encontró el binario 'gzip' en el PATH ni en rutas comunes. "
                "Ejecute sin '--use-cli' para usar el motor Gzip de Python estándar."
            )
        proc = subprocess.run(
            [gzip_bin, "-d", "-c"],
            input=gz_data,
            capture_output=True,
            check=True,
        )
        reconstructed = proc.stdout
    else:
        reconstructed = gzip.decompress(gz_data)

    original_size = len(reconstructed)
    return reconstructed, original_size, compressed_size


def decompress_file(
    input_gz_path: str,
    output_path: Optional[str] = None,
    original_reference_path: Optional[str] = None,
    use_cli: bool = False
) -> Tuple[str, GzipDecompressionMetrics]:
    """
    Lee el archivo .gz en disco, lo descomprime, guarda el resultado
    y computa/valida las métricas e integridad SHA-256.
    
    Retorna:
        Tuple de (ruta_salida, métricas_descompresión).
    """
    in_file = Path(input_gz_path)
    if not in_file.exists():
        raise FileNotFoundError(f"El archivo comprimido .gz no existe: '{input_gz_path}'")
    if not in_file.is_file():
        raise ValueError(f"La ruta no es un archivo regular: '{input_gz_path}'")

    if output_path is None:
        if in_file.name.endswith(".gz") and len(in_file.name) > 3:
            out_file = in_file.with_name(in_file.name[:-3])
        else:
            out_file = in_file.with_name(in_file.name + ".decompressed")
    else:
        out_file = Path(output_path)

    gz_data = in_file.read_bytes()
    real_sc = in_file.stat().st_size

    t_start = time.perf_counter()
    reconstructed_bytes, original_size, _ = decompress_bytes(gz_data, use_cli=use_cli)
    t_end = time.perf_counter()
    decompression_time = t_end - t_start

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(reconstructed_bytes)

    sha_reconstructed = compute_sha256(reconstructed_bytes)

    # Si se especificó el original de referencia, validamos contra él
    sha_original = ""
    is_valid = True
    if original_reference_path:
        ref_path = Path(original_reference_path)
        if ref_path.exists():
            sha_original = compute_sha256(ref_path)
            is_valid = (sha_original == sha_reconstructed)
        else:
            is_valid = False

    metrics = GzipDecompressionMetrics(
        compressed_size=real_sc,
        original_size=original_size,
        decompression_time=decompression_time,
        sha256_original=sha_original,
        sha256_reconstructed=sha_reconstructed,
        is_valid=is_valid,
    )

    return str(out_file), metrics


def main():
    parser = argparse.ArgumentParser(
        description="Descompresor de archivos Gzip (.gz) con reporte de métricas y validación SHA-256."
    )
    parser.add_argument("entrada", help="Ruta al archivo comprimido (.gz).")
    parser.add_argument(
        "salida",
        nargs="?",
        default=None,
        help="Ruta de destino para el archivo reconstruido (opcional)."
    )
    parser.add_argument(
        "--original",
        dest="original",
        default=None,
        help="(Opcional) Ruta al archivo original para validación directa de SHA-256.",
    )
    parser.add_argument(
        "--use-cli",
        action="store_true",
        help="Invocar binario 'gzip -d' del sistema en lugar de la librería estándar de Python.",
    )

    args = parser.parse_args()

    try:
        out_path, metrics = decompress_file(
            args.entrada,
            args.salida,
            original_reference_path=args.original,
            use_cli=args.use_cli
        )
        print_decompression_report(args.entrada, out_path, metrics)
    except FileNotFoundError as e:
        print(f"Error de archivo: {e}", file=sys.stderr)
        sys.exit(1)
    except gzip.BadGzipFile as e:
        print(f"Error de formato Gzip corrupto o inválido: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la descompresión Gzip: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
