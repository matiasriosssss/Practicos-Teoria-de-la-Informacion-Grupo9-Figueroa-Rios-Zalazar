"""
Pruebas unitarias para el algoritmo de Fano y el manejo de flujos de bits (bitstream).
"""

import unittest
from bitstream import BitReader, BitWriter
from fano import build_decoding_trie, generate_fano_codes


class TestFanoAndBitstream(unittest.TestCase):

    def test_bitstream_roundtrip(self):
        """Prueba que el BitWriter y BitReader empaquetan y desempaquetan bits exactamente."""
        test_bits = "1011001010111"
        writer = BitWriter()
        writer.write_bits(test_bits)
        data, valid_bits_last = writer.flush()

        self.assertEqual(writer.total_bits, len(test_bits))

        reader = BitReader(data, len(test_bits))
        read_bits = reader.read_bits(len(test_bits))
        self.assertEqual(read_bits, test_bits)
        self.assertFalse(reader.has_more_bits())

    def test_fano_empty(self):
        """Prueba caso borde: 0 símbolos."""
        codes = generate_fano_codes([])
        self.assertEqual(codes, {})

    def test_fano_single_symbol(self):
        """Prueba caso borde: 1 único símbolo."""
        sym = b"AA"
        codes = generate_fano_codes([(sym, 10)])
        self.assertIn(sym, codes)
        self.assertEqual(codes[sym], "0")

    def test_fano_prefix_property(self):
        """Prueba que los códigos generados cumplen estrictamente con la propiedad de prefijo."""
        symbols_with_freq = [
            (b"A1", 45),
            (b"B2", 25),
            (b"C3", 15),
            (b"D4", 10),
            (b"E5", 5),
        ]
        codes = generate_fano_codes(symbols_with_freq)

        code_list = list(codes.values())
        for i in range(len(code_list)):
            for j in range(len(code_list)):
                if i != j:
                    c1, c2 = code_list[i], code_list[j]
                    self.assertFalse(
                        c1.startswith(c2),
                        f"El código {c2} es prefijo de {c1}, violando la propiedad de código prefijo."
                    )

    def test_trie_decoding(self):
        """Prueba que el Trie decodifica correctamente una secuencia de códigos."""
        codes = {
            b"AB": "00",
            b"CD": "01",
            b"EF": "1",
        }
        root = build_decoding_trie(codes)
        
        # Simular lectura de bits: '01' (CD) + '1' (EF) + '00' (AB)
        stream = "01100"
        writer = BitWriter()
        writer.write_bits(stream)
        raw_bytes, _ = writer.flush()

        reader = BitReader(raw_bytes, len(stream))
        decoded = []
        for _ in range(3):
            curr = root
            while not curr.is_leaf:
                bit = reader.read_bit()
                curr = curr.left if bit == 0 else curr.right
            decoded.append(curr.symbol)

        self.assertEqual(decoded, [b"CD", b"EF", b"AB"])


if __name__ == "__main__":
    unittest.main()
