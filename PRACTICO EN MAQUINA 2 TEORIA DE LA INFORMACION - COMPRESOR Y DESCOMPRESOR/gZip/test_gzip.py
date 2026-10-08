"""
Suite de pruebas automatizadas para el compresor y descompresor Gzip (-n -6).
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from compressorgzip import compress_bytes, compress_file
from decompressorgzip import decompress_bytes, decompress_file
from utils import compute_sha256, find_gzip_binary


class TestGzipSuite(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gzip_test_"))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _test_roundtrip(self, data: bytes, use_cli: bool = False):
        # En memoria
        gz_bytes, comp_metrics = compress_bytes(data, use_cli=use_cli)
        reconstructed, orig_size, comp_size = decompress_bytes(gz_bytes, use_cli=use_cli)

        self.assertEqual(len(data), orig_size)
        self.assertEqual(len(gz_bytes), comp_size)
        self.assertEqual(data, reconstructed)
        self.assertEqual(compute_sha256(data), compute_sha256(reconstructed))

        # En disco
        in_path = self.temp_dir / "sample.bin"
        out_gz = self.temp_dir / "sample.bin.gz"
        out_recon = self.temp_dir / "sample_recon.bin"

        in_path.write_bytes(data)
        _, c_metrics = compress_file(str(in_path), str(out_gz), use_cli=use_cli)
        _, d_metrics = decompress_file(
            str(out_gz),
            str(out_recon),
            original_reference_path=str(in_path),
            use_cli=use_cli,
        )

        self.assertTrue(out_gz.exists())
        self.assertTrue(out_recon.exists())
        self.assertEqual(out_recon.read_bytes(), data)
        self.assertTrue(d_metrics.is_valid)
        self.assertEqual(d_metrics.sha256_original, d_metrics.sha256_reconstructed)
        self.assertEqual(c_metrics.original_size, len(data))
        self.assertEqual(c_metrics.compressed_size, out_gz.stat().st_size)

        # Validar cálculo de métricas
        if len(data) > 0:
            expected_ratio = len(data) / out_gz.stat().st_size
            expected_savings = (1.0 - (out_gz.stat().st_size / len(data))) * 100.0
            expected_relative = (out_gz.stat().st_size / len(data)) * 100.0
            self.assertAlmostEqual(c_metrics.ratio, expected_ratio, places=4)
            self.assertAlmostEqual(c_metrics.savings, expected_savings, places=2)
            self.assertAlmostEqual(c_metrics.relative_size, expected_relative, places=2)

    def test_empty_file(self):
        self._test_roundtrip(b"")

    def test_single_byte(self):
        self._test_roundtrip(b"A")

    def test_odd_size(self):
        self._test_roundtrip(b"Hello World 123")

    def test_repetitive_data(self):
        data = b"ABCDEFGHIJ" * 1000
        self._test_roundtrip(data)

    def test_binary_sequence(self):
        data = bytes(range(256)) * 10
        self._test_roundtrip(data)

    def test_cli_if_available(self):
        gzip_bin = find_gzip_binary()
        if gzip_bin:
            self._test_roundtrip(b"Test CLI integration for gzip -n -6", use_cli=True)
            self._test_roundtrip(b"X" * 500, use_cli=True)
        else:
            self.skipTest("No se encontró el binario gzip en el sistema.")


if __name__ == "__main__":
    unittest.main()
