"""
Módulo de Benchmark y Pruebas de Rendimiento Comparativas.
Automatiza mediciones sobre un corpus de archivos de prueba (texto, binarios, repetitivos, vacíos)
y genera reportes tabulares y en formato CSV/JSON en la carpeta results/.
"""

import csv
import gzip
import json
import time
from pathlib import Path
from typing import Any, Dict, List

from compressor import compress_bytes
from decompressor import decompress_bytes
from utils import compute_sha256


def run_benchmark_on_dataset(test_files: Dict[str, bytes], output_dir: Path) -> List[Dict[str, Any]]:
    """
    Ejecuta el benchmark sobre un conjunto de archivos de prueba en memoria o disco,
    comparando Fano Orden 2 contra compresión estándar GZIP (como referencia externa).
    """
    results: List[Dict[str, Any]] = []

    print(f"{'Archivo':<25} | {'Orig (B)':<10} | {'Fano (B)':<10} | {'Ratio':<8} | {'Ahorro %':<9} | {'T_comp(s)':<10} | {'SHA256'}")
    print("-" * 90)

    for name, data in test_files.items():
        orig_size = len(data)
        sha_orig = compute_sha256(data)

        # 1. Medir Fano Orden 2
        t0 = time.perf_counter()
        tdi_bytes, comp_metrics = compress_bytes(data)
        t_comp = time.perf_counter() - t0

        t0 = time.perf_counter()
        reconstructed, recon_size, comp_size = decompress_bytes(tdi_bytes)
        t_decomp = time.perf_counter() - t0

        sha_recon = compute_sha256(reconstructed)
        integrity_ok = (sha_orig == sha_recon)

        # 2. Medir GZIP de referencia (cátedra)
        t0 = time.perf_counter()
        gzip_bytes = gzip.compress(data)
        t_gzip_comp = time.perf_counter() - t0
        gzip_size = len(gzip_bytes)

        record = {
            "archivo": name,
            "tamaño_original_bytes": orig_size,
            "fano_tamaño_tdi_bytes": comp_size,
            "fano_tamaño_cabecera_bytes": comp_metrics.header_size,
            "fano_overhead_cabecera_pct": round(comp_metrics.header_overhead, 2),
            "fano_ratio": round(comp_metrics.ratio, 4),
            "fano_ahorro_pct": round(comp_metrics.savings, 2),
            "fano_tamaño_relativo_pct": round(comp_metrics.relative_size, 2),
            "fano_tiempo_compresion_s": round(t_comp, 6),
            "fano_tiempo_descompresion_s": round(t_decomp, 6),
            "fano_throughput_compresion_mbs": round(comp_metrics.throughput, 4),
            "fano_integridad_sha256": "OK" if integrity_ok else "FALLO",
            "gzip_tamaño_bytes": gzip_size,
            "gzip_ratio": round(orig_size / gzip_size, 4) if gzip_size > 0 else 0,
            "gzip_tiempo_compresion_s": round(t_gzip_comp, 6)
        }
        results.append(record)

        print(
            f"{name:<25} | {orig_size:<10} | {comp_size:<10} | "
            f"{comp_metrics.ratio:<8.4f} | {comp_metrics.savings:<9.2f} | "
            f"{t_comp:<10.5f} | {'OK' if integrity_ok else 'FALLO'}"
        )

    # Guardar en CSV y JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "benchmark_results.csv"
    json_path = output_dir / "benchmark_results.json"

    if results:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\nResultados exportados con éxito a:")
    print(f" - CSV:  {csv_path}")
    print(f" - JSON: {json_path}")

    return results


def main():
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"

    # Corpus sintético representativo de pruebas para el benchmark
    dataset = {
        "vacio.bin": b"",
        "un_byte.bin": b"Z",
        "impar_cinco_bytes.txt": b"12345",
        "texto_corto.txt": b"Teoria de la Informacion - Trabajo Practico Nro 1 Fano 2026",
        "texto_literario.txt": (
            "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, "
            "no ha mucho tiempo que vivia un hidalgo de los de lanza en astillero, "
            "adarga antigua, rocin flaco y galgo corredor. "
        ).encode("utf-8") * 20,
        "altamente_repetitivo.bin": b"AABBCCDDEEFF" * 500,
        "datos_aleatorios_10kb.bin": bytes([(i * 37 + 101) % 256 for i in range(10240)]),
        "grande_estructurado_100kb.bin": (b"ENCABEZADO_REPETIDO_LINEA_DE_DATOS_1234567890\n" * 2500),
    }

    print("==========================================================================================")
    print(" EJECUTANDO BENCHMARK: FANO ORDEN 2 vs REFERENCIA GZIP")
    print("==========================================================================================")
    run_benchmark_on_dataset(dataset, results_dir)


if __name__ == "__main__":
    main()
