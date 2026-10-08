"""
Compresor Gzip (-n -6).
Comprime archivos usando el estándar Gzip con nivel de compresión 6 y sin almacenar
nombre original ni timestamp (-n).

Uso por línea de comandos:
    python compressorgzip.py <archivo_origen> [<archivo_destino.gz>] [--use-cli]
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

from metrics import GzipCompressionMetrics
from utils import find_gzip_binary, print_compression_report


def compress_bytes(data: bytes, use_cli: bool = False) -> Tuple[bytes, GzipCompressionMetrics]:
    """
    Comprime un búfer de bytes utilizando Gzip con nivel 6 y sin metadatos (-n -6).
    
    Args:
        data: Bytes a comprimir.
        use_cli: Si es True, intenta invocar el binario gzip del sistema (gzip -n -6).
                 Si es False (por defecto), utiliza la biblioteca estándar gzip de Python.
                 
    Retorna:
        Tuple de (bytes comprimidos .gz, métricas de compresión).
    """
    original_size = len(data)

    if use_cli:
        gzip_bin = find_gzip_binary()
        if not gzip_bin:
            raise RuntimeError(
                "No se encontró el binario 'gzip' en el PATH ni en rutas comunes. "
                "Ejecute sin '--use-cli' para usar el motor Gzip de Python estándar."
            )
        t_start = time.perf_counter()
        proc = subprocess.run(
            [gzip_bin, "-n", "-6"],
            input=data,
            capture_output=True,
            check=True,
        )
        gz_bytes = proc.stdout
        t_end = time.perf_counter()
    else:
        # Python standard library: compresslevel=6, mtime=0 (equivalente a -n -6)
        t_start = time.perf_counter()
        gz_bytes = gzip.compress(data, compresslevel=6, mtime=0)
        t_end = time.perf_counter()

    compression_time = t_end - t_start
    compressed_size = len(gz_bytes)

    metrics = GzipCompressionMetrics(
        original_size=original_size,
        compressed_size=compressed_size,
        compression_time=compression_time,
    )

    return gz_bytes, metrics


def compress_file(
    input_path: str,
    output_path: Optional[str] = None,
    use_cli: bool = False
) -> Tuple[str, GzipCompressionMetrics]:
    """
    Lee un archivo en disco, lo comprime a formato .gz y guarda el resultado.
    
    Args:
        input_path: Ruta al archivo original.
        output_path: Ruta de destino .gz (opcional; por defecto input_path + '.gz').
        use_cli: Forzar uso del binario gzip del sistema si está disponible.
        
    Retorna:
        Tuple de (ruta_salida, métricas).
    """
    in_file = Path(input_path)
    if not in_file.exists():
        raise FileNotFoundError(f"El archivo de entrada no existe: '{input_path}'")
    if not in_file.is_file():
        raise ValueError(f"La ruta de entrada no es un archivo regular: '{input_path}'")

    if output_path is None:
        out_file = in_file.with_name(in_file.name + ".gz")
    else:
        out_file = Path(output_path)

    data = in_file.read_bytes()
    gz_bytes, metrics = compress_bytes(data, use_cli=use_cli)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(gz_bytes)

    # Medir el tamaño real verificado en disco sobre el archivo completo generado
    real_sc = out_file.stat().st_size
    metrics.compressed_size = real_sc

    return str(out_file), metrics


def main():
    parser = argparse.ArgumentParser(
        description="Compresor de archivos Gzip (-n -6) con reporte detallado de métricas."
    )
    parser.add_argument("entrada", help="Ruta al archivo original que se desea comprimir.")
    parser.add_argument(
        "salida",
        nargs="?",
        default=None,
        help="Ruta destino para el archivo comprimido (.gz). Por defecto: <entrada>.gz"
    )
    parser.add_argument(
        "--use-cli",
        action="store_true",
        help="Invocar binario 'gzip -n -6' del sistema en lugar de la librería estándar de Python.",
    )

    args = parser.parse_args()

    try:
        out_path, metrics = compress_file(args.entrada, args.salida, use_cli=args.use_cli)
        print_compression_report(args.entrada, out_path, metrics)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la compresión Gzip: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
