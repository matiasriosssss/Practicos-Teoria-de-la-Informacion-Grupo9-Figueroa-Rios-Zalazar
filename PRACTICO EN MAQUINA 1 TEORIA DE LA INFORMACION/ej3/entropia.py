"""
Ejercicio 3 - Entropía Empírica en Archivos (Texto vs. Comprimidos)
Teoría de la Información - Practico en maquina 1
Figueroa - Rios - Zalazar
Este programa lee un archivo byte por byte en O(N), calcula la frecuencia
relativa de cada byte (0..255), la entropía empírica (H) y la redundancia (R).
"""
import sys
import math
import os

def calcular_entropia(ruta_archivo: str) -> None:
    """
    Lee el archivo indicado byte por byte, calcula la frecuencia relativa
    de cada byte, la entropía empírica y la redundancia.

    Parámetros:
        ruta_archivo: ruta al archivo a analizar.
    """

    # Verificar que el archivo existe
    if not os.path.isfile(ruta_archivo):
        print(f"Error: no se encontró el archivo '{ruta_archivo}'.")
        sys.exit(1)

    # --- Paso 1: contar ocurrencias de cada byte (O(N)) ---
    # Usamos una lista de 256 posiciones (una por cada valor posible de byte).
    frecuencias = [0] * 256

    tamanio = os.path.getsize(ruta_archivo)
    if tamanio == 0:    #Si el archivo está vacío, no tiene sentido calcular entropía
        print("Error: el archivo está vacío.")
        sys.exit(1)

    # Leemos el archivo en bloques para mayor eficiencia, pero conceptualmente es equivalente a leer byte por byte.
    with open(ruta_archivo, "rb") as f:
        while True:
            bloque = f.read(4096)
            if not bloque:
                break
            for byte in bloque:
                frecuencias[byte] += 1

    N = tamanio  # cantidad total de bytes leídos

    # --- Paso 2: calcular frecuencia relativa y entropía ---
    # Entropía máxima para un alfabeto de 256 símbolos: H_max = log2(256) = 8 bits/símbolo
    H_max = 8.0

    entropia = 0.0
    simbolos_presentes = 0

    print("=" * 60)
    print(f"Archivo: {ruta_archivo}")
    print(f"Tamaño: {N} bytes")
    print("=" * 60)
    print(f"\n{'Byte':>6}  {'Carácter':>10}  {'Frecuencia':>12}  {'Prob (pi)':>12}")
    print("-" * 50)

    for i in range(256):
        if frecuencias[i] > 0:
            simbolos_presentes += 1
            pi = frecuencias[i] / N  # frecuencia relativa (probabilidad)

            # H = - Σ pi * log2(pi)
            entropia -= pi * math.log2(pi)

            # Mostrar solo los bytes que aparecen al menos una vez
            # Representamos el carácter si es imprimible, sino mostramos '.'
            caracter = chr(i) if 32 <= i <= 126 else "."
            print(f"  {i:>4}  {caracter:>10}  {frecuencias[i]:>12}  {pi:>12.6f}")

    # --- Paso 3: calcular redundancia ---
    # Redundancia: R = H_max - H  (en bits/símbolo)
    # Redundancia relativa: R_rel = 1 - H / H_max
    redundancia = H_max - entropia
    redundancia_relativa = 1 - (entropia / H_max)

    # --- Mostrar resultados ---
    print("-" * 50)
    print(f"\nSímbolos distintos encontrados: {simbolos_presentes} / 256")
    print(f"Entropía máxima (H_max):        {H_max:.4f} bits/símbolo")
    print(f"Entropía empírica (H):          {entropia:.4f} bits/símbolo")
    print(f"Redundancia absoluta (R):       {redundancia:.4f} bits/símbolo")
    print(f"Redundancia relativa:           {redundancia_relativa:.4f} ({redundancia_relativa*100:.2f}%)")
    print("FIN")
    print("=" * 60)


# --- Punto de entrada ---
if __name__ == "__main__":
    if len(sys.argv) != 2: #Si no se pasa un argumento, mostrar mensaje de uso
        print("Uso: python entropia.py <ruta_archivo>")
        print("Ejemplo: python entropia.py archivo.txt")
        sys.exit(1)
    print("=" * 60)
    print("Ejercicio 3 - Practico en Maquina - Entropía Empírica en Archivos (Texto vs. Comprimidos)")
    print("Figueroa - Rios - Zalazar")
    calcular_entropia(sys.argv[1])
