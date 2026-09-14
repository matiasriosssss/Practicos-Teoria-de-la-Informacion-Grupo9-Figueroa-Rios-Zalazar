""" Ejercicio 2 - Teoría de la Información
Análisis de Entropía, Histogramas y Estructura de Archivos (BMP vs. JPG)
Figueroa - Rios - Zalazar
Este programa analiza la distribución estadística de la información y la estructura
interna de archivos de imagen BMP y JPG, calculando entropía de Shannon y generando
histogramas comparativos. """
import os
import struct
import math
import matplotlib.pyplot as plt
import numpy as np
# =============================================================================
# a) Validación de archivos
# =============================================================================

def validar_archivo(ruta: str, extension_esperada: str) -> bool:
    """
    Valida que el archivo exista, tenga la extensión correcta y que su contenido
    interno corresponda al formato esperado (BMP o JPG).
    
    Args:
        ruta: Ruta al archivo.
        extension_esperada: '.bmp' o '.jpg' / '.jpeg'.
    
    Returns:
        True si el archivo es válido.
    
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la extensión o el formato interno no coinciden.
    """
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    # Validar extensión
    _, ext = os.path.splitext(ruta)
    ext = ext.lower()

    if extension_esperada == '.bmp':
        if ext != '.bmp':
            raise ValueError(f"Se esperaba un archivo .bmp, se recibió '{ext}'")
        # Validar firma interna BMP: primeros 2 bytes deben ser 'BM'
        with open(ruta, 'rb') as f:
            firma = f.read(2)
        if firma != b'BM':
            raise ValueError(f"El archivo no tiene firma BMP válida ('BM'). Firma: {firma}")

    elif extension_esperada == '.jpg':
        if ext not in ('.jpg', '.jpeg'):
            raise ValueError(f"Se esperaba un archivo .jpg/.jpeg, se recibió '{ext}'")
        # Validar firma interna JPG: primeros 2 bytes deben ser FF D8
        with open(ruta, 'rb') as f:
            firma = f.read(2)
        if firma != b'\xff\xd8':
            raise ValueError(f"El archivo no tiene firma JPEG válida (FF D8). Firma: {firma.hex()}")

    print(f"  ✓ Archivo {extension_esperada.upper()} validado correctamente: {os.path.basename(ruta)}")
    return True
# =============================================================================
# b) Lectura y análisis de cabecera BMP
# =============================================================================

def leer_cabecera_bmp(ruta: str) -> dict:
    """
    Lee los primeros 54 bytes del archivo BMP y extrae los campos de la cabecera
    y las propiedades de la imagen según la especificación del formato BMP.
    Estructura:
        - Cabecera (14 bytes): Signature, FileSize, Reserved, DataOffset
        - Propiedades (40 bytes): Size, Width, Height, Planes, BitCount,
          Compression, ImageSize, XPixelsPerM, YPixelsPerM, ColorsUsed, ColorsImportant
    Args:
        ruta: Ruta al archivo BMP.
    Returns:
        Diccionario que contiene todos los campos de la cabecera.
    """
    with open(ruta, 'rb') as f:
        data = f.read(54)

    if len(data) < 54:
        raise ValueError("Archivo BMP corrupto: menos de 54 bytes")
    cabecera = {}
    # --- Cabecera del archivo (14 bytes) ---
    cabecera['Signature']   = data[0:2].decode('ascii')          # 2 bytes
    cabecera['FileSize']    = struct.unpack('<I', data[2:6])[0]  # 4 bytes, little-endian
    cabecera['Reserved']    = struct.unpack('<I', data[6:10])[0] # 4 bytes
    cabecera['DataOffset']  = struct.unpack('<I', data[10:14])[0]# 4 bytes

    # --- Propiedades de la imagen (40 bytes) ---
    cabecera['InfoSize']        = struct.unpack('<I', data[14:18])[0]
    cabecera['Width']           = struct.unpack('<i', data[18:22])[0]  # signed
    cabecera['Height']          = struct.unpack('<i', data[22:26])[0]  # signed
    cabecera['Planes']          = struct.unpack('<H', data[26:28])[0]
    cabecera['BitCount']        = struct.unpack('<H', data[28:30])[0]
    cabecera['Compression']     = struct.unpack('<I', data[30:34])[0]
    cabecera['ImageSize']       = struct.unpack('<I', data[34:38])[0]
    cabecera['XPixelsPerM']     = struct.unpack('<i', data[38:42])[0]
    cabecera['YPixelsPerM']     = struct.unpack('<i', data[42:46])[0]
    cabecera['ColorsUsed']      = struct.unpack('<I', data[46:50])[0]
    cabecera['ColorsImportant'] = struct.unpack('<I', data[50:54])[0]
    return cabecera

def imprimir_cabecera_bmp(cabecera: dict) -> None:
    """Imprime los campos del diccionario que contiene los datos de la cabecera BMP de forma legible."""
    print("\n" + "=" * 60)
    print("  CABECERA DEL ARCHIVO BMP")
    print("=" * 60)

    print("\n  --- Cabecera del archivo (14 bytes) ---")
    print(f"  Firma (Signature):       {cabecera['Signature']}")
    print(f"  Tamaño del archivo:      {cabecera['FileSize']} bytes ({cabecera['FileSize'] / (1024*1024):.2f} MB)")
    print(f"  Reservado:               {cabecera['Reserved']}")
    print(f"  Offset de datos:         {cabecera['DataOffset']} bytes")

    print("\n  --- Propiedades de la imagen (40 bytes) ---")
    print(f"  Tamaño de info header:   {cabecera['InfoSize']} bytes")
    print(f"  Ancho (Width):           {cabecera['Width']} píxeles")
    print(f"  Alto (Height):           {cabecera['Height']} píxeles")
    print(f"  Planos (Planes):         {cabecera['Planes']}")
    print(f"  Profundidad de color:    {cabecera['BitCount']} bits por píxel")
    print(f"  Compresión:              {cabecera['Compression']} {'(sin compresión)' if cabecera['Compression'] == 0 else ''}")
    print(f"  Tamaño de imagen:        {cabecera['ImageSize']} bytes")
    print(f"  Resolución horizontal:   {cabecera['XPixelsPerM']} píxeles/metro")
    print(f"  Resolución vertical:     {cabecera['YPixelsPerM']} píxeles/metro")
    print(f"  Colores usados:          {cabecera['ColorsUsed']}")
    print(f"  Colores importantes:     {cabecera['ColorsImportant']}")
    print("=" * 60)
# =============================================================================
# c) Cálculo de frecuencias relativas y distribución de probabilidad
# =============================================================================

def calcular_frecuencias(ruta: str) -> tuple:
    """
    Lee el archivo byte por byte y calcula la frecuencia relativa de cada
    símbolo (0-255), obteniendo la distribución de probabilidad P(x).
    
    Args:
        ruta: Ruta al archivo.
    
    Returns:
        Tupla (frecuencias_absolutas, probabilidades) donde ambos son arrays
        de 256 posiciones indexados por valor de byte.
    """
    # Leer todos los bytes del archivo
    with open(ruta, 'rb') as f:
        datos = f.read()

    total_bytes = len(datos)
    # Contar frecuencia absoluta de cada byte (0-255)
    frecuencias = np.zeros(256, dtype=np.int64)
    for byte in datos:
        frecuencias[byte] += 1

    # Calcular frecuencia relativa (probabilidad)
    probabilidades = frecuencias / total_bytes

    print(f"  Total de bytes leídos: {total_bytes} ({total_bytes / (1024*1024):.2f} MB)")
    print(f"  Símbolos distintos presentes: {np.count_nonzero(frecuencias)} de 256")

    return frecuencias, probabilidades
# =============================================================================
# d) Generación de histogramas comparativos
# =============================================================================

def generar_histogramas(freq_bmp: np.ndarray, freq_jpg: np.ndarray,
                        prob_bmp: np.ndarray, prob_jpg: np.ndarray,
                        nombre_bmp: str, nombre_jpg: str) -> None:
    """
    Genera y muestra gráficos de histogramas de frecuencia para ambos archivos,
    permitiendo una comparación visual directa.
    
    Args:
        freq_bmp: Frecuencias absolutas del archivo BMP.
        freq_jpg: Frecuencias absolutas del archivo JPG.
        prob_bmp: Probabilidades del archivo BMP.
        prob_jpg: Probabilidades del archivo JPG.
        nombre_bmp: Nombre del archivo BMP.
        nombre_jpg: Nombre del archivo JPG.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Análisis Comparativo de Distribución de Bytes: BMP vs JPG',
                 fontsize=14, fontweight='bold')
    x = np.arange(256)
    # Histograma de frecuencias absolutas BMP
    axes[0, 0].bar(x, freq_bmp, color='steelblue', width=1.0, edgecolor='none')
    axes[0, 0].set_title(f'Frecuencia Absoluta - BMP ({nombre_bmp})')
    axes[0, 0].set_xlabel('Valor de byte (0-255)')
    axes[0, 0].set_ylabel('Frecuencia')
    axes[0, 0].set_xlim(-1, 256)

    # Histograma de frecuencias absolutas JPG
    axes[0, 1].bar(x, freq_jpg, color='coral', width=1.0, edgecolor='none')
    axes[0, 1].set_title(f'Frecuencia Absoluta - JPG ({nombre_jpg})')
    axes[0, 1].set_xlabel('Valor de byte (0-255)')
    axes[0, 1].set_ylabel('Frecuencia')
    axes[0, 1].set_xlim(-1, 256)

    # Distribución de probabilidad BMP
    axes[1, 0].bar(x, prob_bmp, color='steelblue', width=1.0, edgecolor='none')
    axes[1, 0].set_title(f'Distribución de Probabilidad P(x) - BMP')
    axes[1, 0].set_xlabel('Valor de byte (0-255)')
    axes[1, 0].set_ylabel('P(x)')
    axes[1, 0].set_xlim(-1, 256)

    # Distribución de probabilidad JPG
    axes[1, 1].bar(x, prob_jpg, color='coral', width=1.0, edgecolor='none')
    axes[1, 1].set_title(f'Distribución de Probabilidad P(x) - JPG')
    axes[1, 1].set_xlabel('Valor de byte (0-255)')
    axes[1, 1].set_ylabel('P(x)')
    axes[1, 1].set_xlim(-1, 256)

    plt.tight_layout()
    plt.savefig('histogramas_comparativos.png', dpi=150, bbox_inches='tight')
    print("\n  ✓ Histogramas guardados en 'histogramas_comparativos.png'")
    plt.show()
# =============================================================================
# e) Cálculo de entropía de Shannon
# =============================================================================

def calcular_entropia(probabilidades: np.ndarray) -> float:
    """
    Calcula la entropía empírica de Shannon para una distribución de probabilidad.
    Fórmula: H(X) = -Σ P(x) * log2(P(x))  para todo P(x) > 0
    Args:
        probabilidades: Array de 256 probabilidades (una por cada valor de byte).
    Returns:
        Valor de entropía en bits/símbolo.
    """
    entropia = 0.0
    for p in probabilidades:
        if p > 0:
            entropia -= p * math.log2(p)
    return entropia
# =============================================================================
# f) Comparación y análisis teórico
# =============================================================================

def imprimir_comparacion(entropia_bmp: float, entropia_jpg: float,
                          tam_bmp: int, tam_jpg: int) -> None:
    """
    Compara los valores de entropía y explica las diferencias desde la
    perspectiva de la Teoría de la Información. Incluye información total
    estimada (entropía × cantidad de símbolos) y tamaño real del archivo.

    Args:
        entropia_bmp: Entropía del archivo BMP en bits/símbolo.
        entropia_jpg: Entropía del archivo JPG en bits/símbolo.
        tam_bmp: Tamaño del archivo BMP en bytes.
        tam_jpg: Tamaño del archivo JPG en bytes.
    """
    H_max = math.log2(256)  # Entropía máxima = 8 bits/símbolo

    # Información total estimada = H(X) * N  (en bits)
    info_total_bmp = entropia_bmp * tam_bmp
    info_total_jpg = entropia_jpg * tam_jpg

    print("\n" + "=" * 60)
    print("  COMPARACIÓN DE ENTROPÍAS")
    print("=" * 60)
    print(f"\n  Entropía máxima teórica (log2(256)):  {H_max:.4f} bits/símbolo")
    print(f"  Entropía del archivo BMP:             {entropia_bmp:.4f} bits/símbolo")
    print(f"  Entropía del archivo JPG:             {entropia_jpg:.4f} bits/símbolo")
    print(f"\n  Eficiencia BMP: {(entropia_bmp / H_max) * 100:.2f}%")
    print(f"  Eficiencia JPG: {(entropia_jpg / H_max) * 100:.2f}%")

    print("\n" + "-" * 60)
    print("  INFORMACIÓN TOTAL ESTIMADA")
    print("-" * 60)
    print(f"\n  Archivo BMP:")
    print(f"    Tamaño real del archivo:     {tam_bmp} bytes ({tam_bmp / (1024*1024):.2f} MB)")
    print(f"    Bits totales reales (N×8):   {tam_bmp * 8:,} bits")
    print(f"    Info. total (H×N):           {info_total_bmp:,.2f} bits ({info_total_bmp / 8:,.2f} bytes)")
    print(f"\n  Archivo JPG:")
    print(f"    Tamaño real del archivo:     {tam_jpg} bytes ({tam_jpg / (1024*1024):.2f} MB)")
    print(f"    Bits totales reales (N×8):   {tam_jpg * 8:,} bits")
    print(f"    Info. total (H×N):           {info_total_jpg:,.2f} bits ({info_total_jpg / 8:,.2f} bytes)")
    print(f"\n  Ratio de compresión (tam. real BMP / tam. real JPG): {tam_bmp / tam_jpg:.2f}x")

    print("\n" + "=" * 60)
    print("  EXPLICACIÓN TEÓRICA")
    print("=" * 60)
    print("""
  Archivo BMP (histograma con picos):
    El formato BMP almacena los píxeles sin compresión. En una fotografía
    natural, los píxeles vecinos tienden a tener valores similares (redundancia
    espacial), lo que provoca que ciertos valores de byte aparezcan con mucha
    más frecuencia que otros, generando picos pronunciados en el histograma.
    Esto produce una distribución NO uniforme y, por lo tanto, una entropía
    menor que el máximo teórico. La fuente tiene alta redundancia y es
    predecible: se podría comprimir significativamente.

  Archivo JPG (histograma más uniforme):
    El formato JPEG aplica compresión con pérdida (DCT + cuantización +
    codificación de Huffman/aritmética). El proceso de compresión elimina
    la redundancia espacial y estadística, transformando los datos en una
    secuencia de bytes que se asemeja a una fuente de máxima entropía.
    El histograma resultante es mucho más uniforme y la entropía se acerca
    al límite teórico de 8 bits/símbolo, indicando que hay muy poca
    redundancia remanente: los bytes del archivo comprimido son casi
    impredecibles, comportándose como una fuente casi aleatoria.

  Conclusión:
    La diferencia de entropía demuestra que la compresión JPEG es efectiva
    al eliminar la redundancia inherente en la imagen. Un archivo con
    entropía cercana al máximo no puede comprimirse más sin pérdida
    (según el Teorema de Codificación de Fuente de Shannon).
    """)

# =============================================================================
# Función principal
# =============================================================================

def main():
    """Punto de entrada principal del programa."""
    print("\n" + "=" * 60)
    print("  ANÁLISIS DE ENTROPÍA Y ESTRUCTURA: BMP vs JPG")
    print("  Teoría de la Información - TP1 Ejercicio 2 - Figueroa - Rios - Zalazar")
    print("=" * 60)

    # --- Solicitar rutas ---
    print("\nIngrese las rutas de los archivos de imagen:")
    ruta_bmp = input("  Ruta del archivo BMP: ").strip().strip('"')
    ruta_jpg = input("  Ruta del archivo JPG: ").strip().strip('"')

    # --- a) Validar archivos ---
    print("\n[a] Validando archivos...")
    try:
        validar_archivo(ruta_bmp, '.bmp')
        validar_archivo(ruta_jpg, '.jpg')
    except (FileNotFoundError, ValueError) as e:
        print(f"\n  ✗ Error de validación: {e}")
        return

    # --- b) Leer cabecera BMP ---
    print("\n[b] Leyendo cabecera del archivo BMP...")
    cabecera = leer_cabecera_bmp(ruta_bmp)
    imprimir_cabecera_bmp(cabecera)

    # --- c) Calcular frecuencias y probabilidades ---
    print("\n[c] Calculando distribución de probabilidad...")
    print(f"\n  Procesando BMP ({os.path.basename(ruta_bmp)}):")
    freq_bmp, prob_bmp = calcular_frecuencias(ruta_bmp)

    print(f"\n  Procesando JPG ({os.path.basename(ruta_jpg)}):")
    freq_jpg, prob_jpg = calcular_frecuencias(ruta_jpg)

    # --- d) Generar histogramas ---
    print("\n[d] Generando histogramas comparativos...")
    generar_histogramas(freq_bmp, freq_jpg, prob_bmp, prob_jpg,
                        os.path.basename(ruta_bmp), os.path.basename(ruta_jpg))

    # --- e) Calcular entropía de Shannon ---
    print("\n[e] Calculando entropía de Shannon...")
    entropia_bmp = calcular_entropia(prob_bmp)
    entropia_jpg = calcular_entropia(prob_jpg)
    print(f"  H(BMP) = {entropia_bmp:.4f} bits/símbolo")
    print(f"  H(JPG) = {entropia_jpg:.4f} bits/símbolo")

    # --- f) Comparación y análisis ---
    print("\n[f] Análisis comparativo...")
    tam_bmp = os.path.getsize(ruta_bmp)
    tam_jpg = os.path.getsize(ruta_jpg)
    imprimir_comparacion(entropia_bmp, entropia_jpg, tam_bmp, tam_jpg)
    print("\n  Programa finalizado exitosamente.\n")

if __name__ == '__main__':
    main()
