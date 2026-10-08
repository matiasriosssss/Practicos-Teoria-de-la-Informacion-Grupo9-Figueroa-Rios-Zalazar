# Compresor y Descompresor de Archivos .TDI
## Teoría de la Información — TP1: Fuente Extendida de Orden 2 + Algoritmo de Fano

Este proyecto implementa desde cero en **Python puro** (sin librerías externas de compresión) un compresor y descompresor de archivos binarios utilizando el algoritmo de codificación de **Fano** aplicado sobre una **fuente extendida de orden 2** (pares de bytes).

---

## 1. Características Principales

* **Núcleo de Codificación Propio**: Implementación manual y recursiva de las particiones óptimas de Fano.
* **Extensión de Orden 2**: Los bytes se agrupan en pares $(b_1, b_2)$, modelando el alfabeto extendido de hasta 65.536 símbolos posibles.
* **Formato Propio `.tdi`**: Cabecera compacta, autodocumentada y completamente autónoma (no requiere el archivo original para descomprimir).
* **Manejo Riguroso de Padding e Impares**: Soporta archivos de tamaño impar y bitstreams no alineados a múltiplos de 8 bits mediante control de bits válidos y truncamiento exacto al tamaño original ($S_o$).
* **Integridad Byte a Byte**: Validación exhaustiva con hash criptográfico SHA-256 (`SHA256(original) == SHA256(reconstruido)`).
* **Métricas Académicas Completas**: Ratio de compresión ($R$), ahorro ($A$), tamaño relativo ($P$), overhead de cabecera ($O$) y throughput ($MB/s$).

---

## 2. Estructura del Proyecto

```text
├── bitstream.py       # Lectura y escritura de bits individuales (BitWriter y BitReader)
├── source.py          # Agrupamiento en pares de orden 2, frecuencias y probabilidades
├── fano.py            # Algoritmo recursivo de Fano y árbol de prefijos (Trie)
├── format.py          # Serialización/deserialización binaria del formato .tdi y validaciones
├── metrics.py         # Cálculo estricto de todas las métricas requeridas
├── utils.py           # Cálculo de SHA-256 y formateo de salidas por consola
├── compressor.py      # Interfaz CLI de compresión
├── decompressor.py    # Interfaz CLI de descompresión
├── benchmark.py       # Benchmark automatizado (compara Fano Orden 2 vs GZIP de referencia)
├── tests/
│   ├── test_fano.py         # Pruebas unitarias de Fano y Bitstream
│   └── test_compression.py  # Suite con los 15 casos mínimos obligatorios
├── results/           # Salidas en CSV y JSON generadas por el benchmark
├── teoria_explicacion.md # Justificación teórica y preguntas de examen oral
└── README.md          # Esta documentación
```

---

## 3. Especificación del Formato Binario `.tdi`

El archivo `.tdi` contiene tres secciones contiguas:

### A. Cabecera Fija (19 bytes)
| Campo | Offset | Tamaño | Tipo | Descripción |
|---|---|---|---|---|
| `magic` | 0 | 4 bytes | bytes | Identificador fijo: `b'TDI2'` |
| `version` | 4 | 1 byte | uint8 | Versión del formato (`0x01`) |
| `order` | 5 | 1 byte | uint8 | Orden de extensión de la fuente (`0x02`) |
| `original_size` | 6 | 8 bytes | uint64 (Big-Endian) | Tamaño exacto en bytes del archivo original ($S_o$) |
| `valid_bits_last`| 14 | 1 byte | uint8 | Bits válidos en el último byte del payload ($0$ a $8$) |
| `symbol_count` | 15 | 4 bytes | uint32 (Big-Endian) | Cantidad de pares únicos en el diccionario ($K$) |

### B. Diccionario de Códigos (Longitud variable)
Para cada uno de los $K$ símbolos:
* **2 bytes**: Par de bytes original $(b_1, b_2)$.
* **1 byte**: Longitud del código Fano en bits ($L$).
* **$\lceil L/8 \rceil$ bytes**: Bits del código empaquetados (alineados al MSB).

### C. Payload (Datos Comprimidos)
Flujo continuo de bits generados al reemplazar cada par del archivo original por su código Fano correspondiente, empaquetados en bytes.

---

## 4. Requisitos y Ejecución

### Requisitos
* Python 3.8 o superior.
* No requiere dependencias externas (`pip`). Utiliza únicamente librerías estándar de Python (`struct`, `hashlib`, `time`, `pathlib`, `argparse`, `unittest`).

### Compresión
```bash
python compressor.py <archivo_origen> <archivo_destino.tdi>
```
*Ejemplo:*
```bash
python compressor.py sample.txt compressed.tdi
```

### Descompresión
```bash
python decompressor.py <archivo.tdi> <archivo_reconstruido> [--original <archivo_original>]
```
*Ejemplo:*
```bash
python decompressor.py compressed.tdi reconstructed.txt --original sample.txt
```

### Ejecutar Pruebas Automatizadas (Unit Tests)
```bash
python -m unittest discover tests
```
O de forma individual:
```bash
python tests/test_fano.py
python tests/test_compression.py
```

### Ejecutar Benchmark Comparativo
```bash
python benchmark.py
```
Los resultados se exportarán automáticamente a `results/benchmark_results.csv` y `results/benchmark_results.json`.

---

## 5. Salida de Ejemplo del Compresor y Descompresor

### Salida del Compresor:
```text
========================================
 COMPRESIÓN FANO - ORDEN 2
========================================
Entrada: sample.txt
Salida: compressed.tdi

Algoritmo: Fano
Extensión: Orden 2

Tamaño original: 4500 bytes
Tamaño comprimido: 2150 bytes
Tamaño cabecera: 320 bytes
Datos comprimidos: 1830 bytes

Ratio: 2.0930
Ahorro: 52.22 %
Tamaño relativo: 47.78 %
Overhead cabecera: 14.88 %

Tiempo compresión: 0.0084 s
Throughput: 0.5357 MB/s

Pares totales: 2250
Pares diferentes: 84
Bits válidos: 14640
========================================
```

### Salida del Descompresor:
```text
========================================
 DESCOMPRESIÓN FANO - ORDEN 2
========================================
Entrada: compressed.tdi
Salida: reconstructed.txt

Tamaño comprimido: 2150 bytes
Tamaño original: 4500 bytes

Tiempo descompresión: 0.0062 s
Throughput: 0.7258 MB/s

SHA-256 original: a3b12...
SHA-256 reconstruido: a3b12...

Integridad: OK
========================================
```
