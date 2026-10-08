"""
Módulo de cálculo de métricas de compresión para Gzip según especificaciones de la cátedra.
Todas las métricas se computan a partir del tamaño real del archivo .gz completo (Sc)
y el archivo original (So).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GzipCompressionMetrics:
    original_size: int         # So (bytes del archivo original)
    compressed_size: int       # Sc (bytes totales del archivo .gz generado)
    compression_time: float    # tc (segundos)
    header_overhead_bytes: int = 18  # Header (10B) + Trailer (8B) en gzip -n

    @property
    def ratio(self) -> float:
        """Ratio de compresión R = So / Sc."""
        if self.compressed_size <= 0:
            return 0.0
        return self.original_size / self.compressed_size

    @property
    def savings(self) -> float:
        """Ahorro de espacio A = (1 - Sc / So) * 100."""
        if self.original_size <= 0:
            return 0.0
        return (1.0 - (self.compressed_size / self.original_size)) * 100.0

    @property
    def relative_size(self) -> float:
        """Tamaño relativo P = (Sc / So) * 100."""
        if self.original_size <= 0:
            return 0.0
        return (self.compressed_size / self.original_size) * 100.0

    @property
    def throughput(self) -> float:
        """Throughput Vc = tamaño original (MB) / tiempo compresión (s)."""
        if self.compression_time <= 0:
            return 0.0
        original_mb = self.original_size / 1_000_000.0
        return original_mb / self.compression_time

    @property
    def throughput_bps(self) -> float:
        """Throughput Vc en bytes/segundo = So / tiempo compresión (s)."""
        if self.compression_time <= 0:
            return 0.0
        return self.original_size / self.compression_time


@dataclass
class GzipDecompressionMetrics:
    compressed_size: int       # Sc (bytes del archivo .gz)
    original_size: int         # So (bytes reconstruidos)
    decompression_time: float  # td (segundos)
    sha256_original: str
    sha256_reconstructed: str
    is_valid: bool

    @property
    def throughput(self) -> float:
        """Throughput Vd = tamaño original (MB) / tiempo descompresión (s)."""
        if self.decompression_time <= 0:
            return 0.0
        original_mb = self.original_size / 1_000_000.0
        return original_mb / self.decompression_time

    @property
    def throughput_bps(self) -> float:
        """Throughput Vd en bytes/segundo = So / tiempo descompresión (s)."""
        if self.decompression_time <= 0:
            return 0.0
        return self.original_size / self.decompression_time
