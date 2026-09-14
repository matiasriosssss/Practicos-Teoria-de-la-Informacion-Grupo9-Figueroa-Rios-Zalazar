"""
Ejercicio 4 - Índice de Coincidencia en Archivos
Teoría de la Información - Practico en maquina 1
Figueroa - Rios - Zalazar

Este programa lee un archivo arbitrario byte por byte en O(N), calcula
la frecuencia de cada elemento y su Índice de Coincidencia (IC) mediante la fórmula:
    IC = Σ [f_i * (f_i - 1)] / [N * (N - 1)]

donde:
    f_i: frecuencia absoluta de cada elemento de la fuente.
    N  : cantidad total de elementos analizados en la secuencia.
"""
import sys
import math
import os

ALFABETO_ES = "abcdefghijklmnñopqrstuvwxyz"
MAPA_ACENTOS = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'ü': 'u', 'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'
}

def calcular_ic(ruta_archivo: str) -> None:
    if not os.path.isfile(ruta_archivo):
        print(f"Error: no se encontró el archivo '{ruta_archivo}'.")
        sys.exit(1)

    tamanio = os.path.getsize(ruta_archivo)
    if tamanio < 2:
        print("Error: el archivo debe tener al menos 2 elementos para calcular el IC.")
        sys.exit(1)

    # --- Paso 1: contar ocurrencias de cada byte (O(N)) ---
    frecuencias = [0] * 256
    with open(ruta_archivo, "rb") as f:
        while True:
            bloque = f.read(4096)
            if not bloque:
                break
            for byte in bloque:
                frecuencias[byte] += 1

    N = tamanio

    # --- Paso 2: cálculo del Índice de Coincidencia a nivel de fuente (bytes) ---
    numerador_ic = sum(f * (f - 1) for f in frecuencias)
    denominador_ic = N * (N - 1)
    ic = numerador_ic / denominador_ic

    # --- Paso 3: mostrar tabla de frecuencias y términos f*(f-1) ---
    simbolos_presentes = 0
    print("=" * 60)
    print(f"Archivo: {ruta_archivo}")
    print(f"Tamaño : {N} bytes")
    print("=" * 60)
    print(f"\n{'Byte':>6}  {'Carácter':>10}  {'Frecuencia':>12}  {'Prob (pi)':>12}  {'fi*(fi-1)':>14}")
    print("-" * 60)

    for i in range(256):
        if frecuencias[i] > 0:
            simbolos_presentes += 1
            pi = frecuencias[i] / N
            par = frecuencias[i] * (frecuencias[i] - 1)
            caracter = chr(i) if 32 <= i <= 126 else "."
            print(f"  {i:>4}  {caracter:>10}  {frecuencias[i]:>12}  {pi:>12.6f}  {par:>14}")

    # --- Paso 4: análisis complementario sobre letras (si es texto) ---
    ic_letras = None
    n_letras = 0
    try:
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f_txt:
            texto = f_txt.read().lower()

        for k, v in MAPA_ACENTOS.items():
            texto = texto.replace(k, v)

        conteo_letras = {c: 0 for c in ALFABETO_ES}
        for c in texto:
            if c in conteo_letras:
                conteo_letras[c] += 1
                n_letras += 1

        if n_letras >= 2:
            num_letras = sum(f * (f - 1) for f in conteo_letras.values())
            den_letras = n_letras * (n_letras - 1)
            ic_letras = num_letras / den_letras
    except Exception:
        ic_letras = None

    # --- Paso 5: Mostrar resultados finales ---
    print("-" * 60)
    print(f"\nSimbolos distintos encontrados: {simbolos_presentes} / 256")
    print(f"Total de elementos (N):         {N}")
    print(f"Suma de pares SUM fi*(fi-1):    {numerador_ic}")
    print(f"Denominador N*(N-1):            {denominador_ic}")
    print(f"Indice de Coincidencia (IC):    {ic:.6f}")
    print(f"  -> Valor esperado uniforme (256 bytes): {1/256:.6f} (~0.0039)")

    if ic_letras is not None and simbolos_presentes < 180:
        print(f"\n--- Analisis especifico sobre Letras del Espanol (27 simbolos) ---")
        print(f"Total de letras analizadas (N_letras):  {n_letras}")
        print(f"Indice de Coincidencia (Letras):        {ic_letras:.5f}")
        print(f"  -> Valor esperado en espanol:         ~0.0740")
        print(f"  -> Valor esperado aleatorio (27 letras): ~0.0380 (1/27 = {1/27:.4f})")

        if ic_letras >= 0.060:
            print("Interpretacion: Distribucion tipica de lenguaje natural en espanol (IC cercano a 0.074).")
        elif ic_letras <= 0.045:
            print("Interpretacion: Distribucion aplanada/aleatoria (IC cercano a 0.038, tipico de cifrado Vigenere o texto aleatorio).")
        else:
            print("Interpretacion: Distribucion intermedia.")
    else:
        if ic < 0.005:
            print("\nInterpretacion: Archivo fuertemente comprimido o aleatorio. Las frecuencias de bytes estan")
            print("uniformemente distribuidas, por lo que el IC se acerca al minimo teorico (1/256 ~ 0.0039).")

    print("FIN")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ejercicio4.py <ruta_archivo>")
        print("Ejemplo: python ejercicio4.py archivo.txt")
        print("Ejemplo: python ejercicio4.py archivo.zip")
        sys.exit(1)

    print("=" * 60)
    print("Ejercicio 4 - Practico en Maquina - Indice de Coincidencia")
    print("Figueroa - Rios - Zalazar")
    calcular_ic(sys.argv[1])