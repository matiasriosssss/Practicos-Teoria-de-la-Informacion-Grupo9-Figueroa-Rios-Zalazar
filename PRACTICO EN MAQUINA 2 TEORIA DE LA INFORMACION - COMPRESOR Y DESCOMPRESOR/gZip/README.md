# Compresor y Descompresor Gzip (-n -6)
## Teoría de la Información — Proyecto Independiente Gzip

Este módulo implementa un compresor y descompresor autónomo de archivos utilizando el estándar **Gzip** con nivel de compresión **6** y sin almacenamiento de metadatos (nombre de archivo ni timestamp original), equivalente a la ejecución por línea de comandos de `gzip -n -6`.

---

## 1. Métricas de Rendimiento Calculadas

El sistema calcula e informa exactamente las mismas métricas exigidas por la cátedra para el análisis de compresión:

* **$S_o$ (Tamaño original)**: Tamaño en bytes del archivo original sin comprimir.
* **$S_c$ (Tamaño comprimido)**: Tamaño real y completo en bytes del archivo `.gz` generado en disco.
* **$R$ (Ratio de compresión)**:
  $$R = \frac{S_o}{S_c}$$
* **$A$ (Ahorro de espacio porcentual)**:
  $$A = \left(1 - \frac{S_c}{S_o}\right) \times 100$$
* **$P$ (Tamaño relativo porcentual)**:
  $$P = \left(\frac{S_c}{S_o}\right) \times 100$$
* **$t_c$ (Tiempo de compresión)**: Tiempo medido con temporizadores de alta resolución (`time.perf_counter`) en segundos.
* **$t_d$ (Tiempo de descompresión)**: Tiempo medido en segundos durante la descompresión.
* **$V_c$ (Throughput de compresión)**:
  $$V_c = \frac{S_o \text{ (MB)}}{t_c \text{ (s)}}$$
* **$V_d$ (Throughput de descompresión)**:
  $$V_d = \frac{S_o \text{ (MB)}}{t_d \text{ (s)}}$$
* **Validación de Integridad**: Hash criptográfico **SHA-256** del archivo reconstruido comparado contra el original (`SHA256(original) == SHA256(reconstruido)`).

---

## 2. Estructura de la Carpeta `gZip`

```text
gZip/
├── compressorgzip.py     # Script CLI y funciones de compresión Gzip (-n -6)
├── decompressorgzip.py   # Script CLI y funciones de descompresión Gzip
├── metrics.py            # Dataclasses y cálculo de métricas (So, Sc, R, A, P, tc, td, Vc, Vd)
├── utils.py              # Hash SHA-256, buscador de gzip binario y formateo de reportes
├── test_gzip.py          # Suite de pruebas unitarias automatizadas
└── README.md             # Esta documentación
```

---

## 3. Uso por Línea de Comandos

### Compresión
```bash
# Sintaxis básica:
python gZip/compressorgzip.py <archivo_origen> [<archivo_destino.gz>]

# Ejemplo:
python gZip/compressorgzip.py documento.txt documento.txt.gz
```
*(Si no se especifica el archivo de salida, se genera automáticamente `<archivo_origen>.gz`)*.

Opcionalmente se puede forzar el uso del binario ejecutable `gzip` del sistema si está instalado:
```bash
python gZip/compressorgzip.py documento.txt documento.txt.gz --use-cli
```

### Descompresión
```bash
# Sintaxis básica:
python gZip/decompressorgzip.py <archivo.gz> [<archivo_reconstruido>] [--original <archivo_original>]

# Ejemplo con validación directa SHA-256:
python gZip/decompressorgzip.py documento.txt.gz documento_restaurado.txt --original documento.txt
```

---

## 4. Pruebas Automatizadas

Para ejecutar la suite de pruebas unitarias que valida archivos vacíos, de 1 byte, impares, repetitivos y secuencias binarias:

```bash
python gZip/test_gzip.py
```
