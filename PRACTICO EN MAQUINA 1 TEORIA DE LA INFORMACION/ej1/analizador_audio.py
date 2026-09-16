""" Ejercicio 1 - Teoría de la Información
Análisis de Información en Señales de Audio (Formato WAV)
Figueroa - Rios - Zalazar
Este programa analiza la distribución estadística de la
información y la estructura interna de archivos de audio crudos y comprimidos """
import os
import struct
import math
from collections import Counter
import matplotlib.pyplot as plt

def validar_archivos(ruta_wav, ruta_mp3):
    """
    Valida las extensiones y que los archivos existan.
    Se hace una lectura basica para comprobar formatos.
    """
    if not os.path.isfile(ruta_wav) or not ruta_wav.lower().endswith('.wav'):
        raise ValueError(f"Archivo WAV invalido o no encontrado: {ruta_wav}")
    if not os.path.isfile(ruta_mp3) or not ruta_mp3.lower().endswith('.mp3'):
        raise ValueError(f"Archivo MP3 invalido o no encontrado: {ruta_mp3}")
    
    # Comprobacion basica de formato WAV
    with open(ruta_wav, 'rb') as f:
        riff = f.read(4)
        f.read(4) # Tamanio del archivo
        wave = f.read(4)
        if riff != b'RIFF' or wave != b'WAVE':
            raise ValueError(f"El archivo {ruta_wav} no tiene la cabecera estandar RIFF/WAVE.")

    # Comprobacion basica de formato MP3
    with open(ruta_mp3, 'rb') as f:
        header = f.read(3)
        if header != b'ID3' and not header.startswith(b'\xff'):
            print("Advertencia: El archivo MP3 no empieza con 'ID3' ni con un frame sync estandar, pero se continuara con el analisis.")
            
    print("Validacion completada: Archivos WAV y MP3 correctos.\n")

def analizar_cabecera_wav(ruta_wav):
    """
    Lee y aisla la cabecera estandar (RIFF/WAVE) del archivo WAV e imprime sus datos.
    """
    print("--- Analisis de Cabecera WAV ---")
    with open(ruta_wav, 'rb') as f:
        cabecera = f.read(44) # Leemos los 44 bytes de la cabecera estandar
        
        # Uso de struct.unpack para decodificar los bytes
        # Los formatos se especifican con > o < dependiendo del endianness.
        # En los archivos WAV, RIFF/WAVE/fmt/data son strings (big-endian basicamente en lectura directa).
        # Los enteros suelen ser little-endian (<).
        chunk_id = cabecera[0:4].decode('ascii')
        chunk_tamanio = struct.unpack('<I', cabecera[4:8])[0]
        formato_wave = cabecera[8:12].decode('ascii')
        subchunk1_id = cabecera[12:16].decode('ascii')
        subchunk1_tamanio = struct.unpack('<I', cabecera[16:20])[0]
        formato_audio = struct.unpack('<H', cabecera[20:22])[0]
        numero_canales = struct.unpack('<H', cabecera[22:24])[0]
        frecuencia_muestreo = struct.unpack('<I', cabecera[24:28])[0]
        tasa_byte = struct.unpack('<I', cabecera[28:32])[0]
        alineacion_bloque = struct.unpack('<H', cabecera[32:34])[0]
        bits_muestra = struct.unpack('<H', cabecera[34:36])[0]
        
        print(f"Identificador de archivo: {chunk_id}")
        print(f"Tamanio total (Chunk Size): {chunk_tamanio} bytes (Archivo: {chunk_tamanio + 8} bytes)")
        print(f"Formato: {formato_wave}")
        print(f"Identificador de sub-bloque (Format): '{subchunk1_id}'")
        print(f"Formato de Audio (1 = PCM): {formato_audio}")
        print(f"Numero de Canales: {numero_canales}")
        print(f"Frecuencia de Muestreo (Sample Rate): {frecuencia_muestreo} Hz")
        print(f"Tasa de Bytes (Byte Rate): {tasa_byte} bytes/s")
        print(f"Resolucion (Bits por Muestra): {bits_muestra} bits")
        print("--------------------------------\n")

def calcular_distribucion_y_entropia(ruta_archivo):
    """
    Lee el archivo byte a byte, calcula la probabilidad de aparicion de cada byte
    y retorna las probabilidades y la entropia de Shannon.
    """
    with open(ruta_archivo, 'rb') as f:
        datos = f.read()
        
    total_bytes = len(datos)
    
    # Contar la frecuencia de cada byte (valores de 0 a 255)
    frecuencias = Counter(datos)
    
    # Calcular la distribucion de probabilidad (frecuencia relativa)
    probabilidades = {i: frecuencias.get(i, 0) / total_bytes for i in range(256)}
    
    # Calcular la Entropia de Shannon (en bits/simbolo)
    # H = - Σ p(x) * log2(p(x))
    entropia = 0
    for p in probabilidades.values():
        if p > 0:
            entropia -= p * math.log2(p)
            
    return probabilidades, entropia

def generar_histogramas(probs_wav, probs_mp3):
    """
    Genera y muestra los histogramas de frecuencia de ambos archivos para comparacion visual.
    """
    valores_x = list(range(256))
    
    # Extraemos las probabilidades en el orden del 0 al 255
    y_wav = [probs_wav[i] for i in valores_x]
    y_mp3 = [probs_mp3[i] for i in valores_x]
    
    plt.figure(figsize=(12, 6))
    
    # Subplot para WAV
    plt.subplot(1, 2, 1)
    plt.bar(valores_x, y_wav, width=1.0, color='blue', alpha=0.7)
    plt.title('Distribucion de Probabilidades - WAV')
    plt.xlabel('Valor del Byte (0 - 255)')
    plt.ylabel('Probabilidad')
    plt.grid(axis='y', alpha=0.5)
    
    # Subplot para MP3
    plt.subplot(1, 2, 2)
    plt.bar(valores_x, y_mp3, width=1.0, color='red', alpha=0.7)
    plt.title('Distribucion de Probabilidades - MP3')
    plt.xlabel('Valor del Byte (0 - 255)')
    plt.ylabel('Probabilidad')
    plt.grid(axis='y', alpha=0.5)
    
    plt.tight_layout()
    plt.show()

def mostrar_conclusiones(entropia_wav, entropia_mp3):
    """
    Imprime las conclusiones teoricas en base a los resultados obtenidos.
    """
    print("--- Resultados de Entropia ---")
    print(f"Entropia del archivo WAV: {entropia_wav:.4f} bits/simbolo")
    print(f"Entropia del archivo MP3: {entropia_mp3:.4f} bits/simbolo")
    print("------------------------------\n")
    
    print("--- Conclusion desde la Teoria de la Informacion ---")
    print("Diferencia radical en los histogramas y la entropia:")
    print("1. WAV (Sin compresion): La distribucion de bytes refleja las amplitudes de la senial analogica original.")
    print("   Habra valores mucho mas frecuentes que otros (ej. silencios o amplitudes bajas), lo que genera una")
    print("   baja entropia empirica, evidenciando alta redundancia de informacion.")
    print("2. MP3 (Compresion con perdida + Codificacion entropica): El proceso de compresion elimina informacion")
    print("   no perceptible y luego aplica una codificacion entropica (como algoritmos de Huffman).")
    print("   Esto comprime los datos de forma que todos los simbolos (bytes) tiendan a tener una probabilidad de")
    print("   aparicion uniforme equiprobable. Al estar mas uniformemente distribuidos (histograma plano),")
    print("   la entropia sube y se acerca al maximo teorico de 8 bits por simbolo. Esto indica que se elimino")
    print("   la redundancia, maximizando la informacion aportada por cada byte.\n")

def main():
    print("=== Analisis de Audio: Teoria de la Informacion ===\n")
    
    ruta_wav = input("Ingrese la ruta completa del archivo WAV: ").strip()
    # Eliminar posibles comillas aniadidas al arrastrar y soltar el archivo en la consola
    ruta_wav = ruta_wav.strip('\"\'')
    
    ruta_mp3 = input("Ingrese la ruta completa del archivo MP3: ").strip()
    ruta_mp3 = ruta_mp3.strip('\"\'')
    
    print("\nIniciando procesamiento...\n")
    try:
        # a) Carga y Validacion
        validar_archivos(ruta_wav, ruta_mp3)
        
        # b) Analisis de cabecera WAV
        analizar_cabecera_wav(ruta_wav)
        
        # c y e) Distribucion y Entropia
        print("Calculando distribucion de probabilidades y entropia. Esto puede tomar unos segundos...")
        probs_wav, entropia_wav = calcular_distribucion_y_entropia(ruta_wav)
        probs_mp3, entropia_mp3 = calcular_distribucion_y_entropia(ruta_mp3)
        
        # f) Comparacion teorica
        mostrar_conclusiones(entropia_wav, entropia_mp3)
        
        # d) Histogramas
        print("Generando graficos de histogramas... Cierre la ventana del grafico para finalizar.")
        generar_histogramas(probs_wav, probs_mp3)
        
    except Exception as e:
        print(f"\nOcurrio un error: {e}")

if __name__ == "__main__":
    main()
