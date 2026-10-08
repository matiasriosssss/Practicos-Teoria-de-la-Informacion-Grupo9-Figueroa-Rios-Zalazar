"""
Suite completa de pruebas de compresión y descompresión.
Verifica obligatoriamente los 15 casos mínimos requeridos por la cátedra (Página 12)
y valida byte a byte: SHA256(original) == SHA256(reconstruido).
"""

import os
import unittest
from compressor import compress_bytes
from decompressor import decompress_bytes
from format import TDIFormatError
from utils import compute_sha256


class TestTDICompressionSuite(unittest.TestCase):

    def _assert_roundtrip(self, original_data: bytes) -> None:
        """Comprime, descomprime y valida que SHA-256 coincida exactamente."""
        tdi_bytes, metrics = compress_bytes(original_data)
        reconstructed_data, orig_size, comp_size = decompress_bytes(tdi_bytes)

        self.assertEqual(orig_size, len(original_data))
        self.assertEqual(comp_size, len(tdi_bytes))
        self.assertEqual(len(reconstructed_data), len(original_data))

        sha_orig = compute_sha256(original_data)
        sha_recon = compute_sha256(reconstructed_data)
        self.assertEqual(sha_orig, sha_recon, "¡Fallo de integridad SHA-256 byte a byte!")

    # 1. Archivo vacío
    def test_01_empty_file(self):
        self._assert_roundtrip(b"")

    # 2. Archivo de 1 byte
    def test_02_one_byte_file(self):
        self._assert_roundtrip(b"X")

    # 3. Archivo de 2 bytes
    def test_03_two_bytes_file(self):
        self._assert_roundtrip(b"OK")

    # 4. Archivo con cantidad impar de bytes
    def test_04_odd_length_file(self):
        self._assert_roundtrip(b"ABCDE")
        self._assert_roundtrip(b"Teoria de la Informacion 2026!")

    # 5. Archivo con cantidad par de bytes
    def test_05_even_length_file(self):
        self._assert_roundtrip(b"ABCD")
        self._assert_roundtrip(b"Algoritmo Fano Orden 2 OK!!")

    # 6. Archivo pequeño
    def test_06_small_file(self):
        data = b"Hola mundo!"
        self._assert_roundtrip(data)

    # 7. Archivo de texto normal
    def test_07_normal_text_file(self):
        text = (
            "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, "
            "no ha mucho tiempo que vivia un hidalgo de los de lanza en astillero, "
            "adarga antigua, rocin flaco y galgo corredor. Una olla de algo mas "
            "vaca que carnero, salpicon las mas noches, duelos y quebrantos los sabados..."
        ).encode("utf-8")
        self._assert_roundtrip(text)

    # 8. Archivo con muchos símbolos repetidos
    def test_08_repeated_symbols_file(self):
        data = b"A" * 5000 + b"B" * 2000 + b"C" * 100
        self._assert_roundtrip(data)

    # 9. Archivo con distribución variada
    def test_09_varied_distribution_file(self):
        # Generar patrón con distintas frecuencias y bytes arbitrarios
        data = bytes([(i * 7 + 13) % 256 for i in range(4000)])
        self._assert_roundtrip(data)

    # 10. Archivo relativamente grande (> 100 KB)
    def test_10_relatively_large_file(self):
        # 128 KB de datos estructurados repetitivos y variados
        pattern = b"TeoriaDeLaInformacionTP1FanoOrden2" * 100
        data = pattern * 40  # ~136 KB
        self._assert_roundtrip(data)

    # 11. .tdi corrupto (modificación en el payload)
    def test_11_corrupt_tdi(self):
        data = b"Mensaje para corromper en el payload"
        tdi_bytes, _ = compress_bytes(data)
        
        # Corromper los últimos bytes invirtiendo bits
        corrupted = bytearray(tdi_bytes)
        corrupted[-1] ^= 0xFF
        corrupted[-2] ^= 0xAA

        # Al descomprimir un archivo corrupto, debe lanzar error o fallar integridad
        try:
            reconstructed, _, _ = decompress_bytes(bytes(corrupted))
            # Si no lanzó excepción en el árbol, debe haber fallado la integridad
            self.assertNotEqual(compute_sha256(data), compute_sha256(reconstructed))
        except TDIFormatError:
            pass  # Excepción esperada por símbolo inexistente o datos corruptos

    # 12. .tdi truncado
    def test_12_truncated_tdi(self):
        data = b"Mensaje para truncar durante la prueba"
        tdi_bytes, _ = compress_bytes(data)
        
        # Truncar a la mitad
        truncated = tdi_bytes[: len(tdi_bytes) // 2]
        with self.assertRaises(TDIFormatError):
            decompress_bytes(truncated)

    # 13. Cabecera inválida (magic bytes incorrectos)
    def test_13_invalid_magic_bytes(self):
        data = b"Prueba de magic bytes invalidos"
        tdi_bytes, _ = compress_bytes(data)

        # Modificar los primeros 4 bytes
        bad_magic = b"XYZ9" + tdi_bytes[4:]
        with self.assertRaises(TDIFormatError) as ctx:
            decompress_bytes(bad_magic)
        self.assertIn("Magic bytes", str(ctx.exception))

    # 14. Versión incorrecta
    def test_14_invalid_version(self):
        data = b"Prueba de version incorrecta"
        tdi_bytes, _ = compress_bytes(data)

        # Byte en posición 4 es la versión
        bad_version = bytearray(tdi_bytes)
        bad_version[4] = 99  # Versión 99 inexistente
        with self.assertRaises(TDIFormatError) as ctx:
            decompress_bytes(bytes(bad_version))
        self.assertIn("Versión", str(ctx.exception))

    # 15. Algoritmo / Orden de extensión incorrecto
    def test_15_invalid_extension_order(self):
        data = b"Prueba de orden incorrecto"
        tdi_bytes, _ = compress_bytes(data)

        # Byte en posición 5 es el orden de extensión
        bad_order = bytearray(tdi_bytes)
        bad_order[5] = 3  # Orden 3 no soportado
        with self.assertRaises(TDIFormatError) as ctx:
            decompress_bytes(bytes(bad_order))
        self.assertIn("Orden de extensión", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
