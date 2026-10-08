"""
Módulo de cálculo de métricas de compresión según especificaciones de la cátedra.
Todas las métricas se computan a partir del tamaño real del archivo .tdi completo (Sc).
"""

from dataclasses import dataclass


@dataclass
class CompressionMetrics:
    original_size: int         # So (bytes)
    compressed_size: int       # Sc (bytes totales del .tdi)
    header_size: int           # H (bytes de cabecera fija + diccionario)
    compressed_data_size: int  # Sc - H (bytes de datos comprimidos)
    compression_time: float    # tc (segundos)
    total_pairs: int           # Pares totales procesados
    unique_pairs: int          # Pares diferentes en el diccionario
    valid_bits: int            # Bits válidos en el bitstream

    @property
    def ratio(self) -> float:
        """Ratio de compresión R = So / Sc."""
        if self.compressed_size == 0:
            return 0.0
        return self.original_size / self.compressed_size

    @property
    def savings(self) -> float:
        """Ahorro de espacio A = (1 - Sc / So) * 100."""
        if self.original_size == 0:
            return 0.0
        return (1.0 - (self.compressed_size / self.original_size)) * 100.0

    @property
    def relative_size(self) -> float:
        """Tamaño relativo P = (Sc / So) * 100."""
        if self.original_size == 0:
            return 0.0
        return (self.compressed_size / self.original_size) * 100.0

    @property
    def header_overhead(self) -> float:
        """Overhead de cabecera O = (H / Sc) * 100."""
        if self.compressed_size == 0:
            return 0.0
        return (self.header_size / self.compressed_size) * 100.0

    @property
    def throughput(self) -> float:
        """Throughput Vc = tamaño original (MB) / tiempo compresión (s)."""
        if self.compression_time <= 0:
            return 0.0
        original_mb = self.original_size / 1_000_000.0
        return original_mb / self.compression_time


@dataclass
class DecompressionMetrics:
    compressed_size: int       # Sc (bytes)
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
