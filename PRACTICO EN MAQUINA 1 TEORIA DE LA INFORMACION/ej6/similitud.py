""" Ejercicio 6 - Teoría de la Información
Medición de Distancia entre Cadenas:
Figueroa - Rios - Zalazar
Esta aplicación de Python permite comparar dos cadenas de texto y evaluar su grado de similitud algorítmica
a través de distintas metodologías, específicamente la **Distancia de Hamming** y la **Distancia de 
Levenshtein (Distancia de Edición)**."""
import unicodedata

def distancia_hamming(str1, str2):
    """
    Calcula la distancia de Hamming entre dos cadenas de texto.
    Ambas cadenas deben tener la misma longitud, ya que el algoritmo
    compara los caracteres posicion por posicion.
    """
    if len(str1) != len(str2):
        raise ValueError("Error: Las cadenas deben tener la misma longitud para calcular la distancia de Hamming.")
    
    # Compara caracter a caracter y suma 1 por cada diferencia encontrada
    return sum(ch1 != ch2 for ch1, ch2 in zip(str1, str2))

def distancia_levenshtein(str1, str2):
    """
    Calcula la distancia de Levenshtein (Distancia de Edicion) entre dos cadenas.
    Utiliza un enfoque de programacion dinamica para contar la cantidad minima de
    operaciones (insercion, eliminacion o sustitucion) necesarias para transformar
    una cadena en la otra.
    """
    m, n = len(str1), len(str2)
    # Crea una matriz de distancias (m+1) x (n+1)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                # Si la primera cadena esta vacia, se deben insertar todos los caracteres de la segunda
                dp[i][j] = j
            elif j == 0:
                # Si la segunda cadena esta vacia, se deben eliminar todos los caracteres de la primera
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]:
                # Si los caracteres coinciden, no hay costo de operacion adicional
                dp[i][j] = dp[i-1][j-1]
            else:
                # Si son diferentes, se toma el minimo entre insercion, eliminacion o sustitucion, mas 1
                dp[i][j] = 1 + min(dp[i][j-1],      # Insercion
                                   dp[i-1][j],      # Eliminacion
                                   dp[i-1][j-1])    # Sustitucion
    return dp[m][n]

def normaliza_texto(text):
    """
    Normaliza el texto para facilitar la comparacion:
    1. Convierte a minusculas.
    2. Elimina tildes y diacriticos.
    3. Elimina espacios en blanco redundantes en los extremos.
    """
    text = text.lower().strip()
    # Descompone los caracteres (ej. a -> a + ´) y elimina las marcas diacriticas
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text

def compara_huristica_texto(str1, str2):
    """
    Heuristica propuesta para la comparacion de textos (como nombres de personas).
    Proceso:
    1. Normalizacion de las cadenas (minusculas, sin acentos ni espacios extra).
    2. Calculo de la Distancia de Levenshtein entre las cadenas normalizadas.
    3. Calculo del porcentaje de similitud algoritmica.
    """
    norm_str1 = normaliza_texto(str1)
    norm_str2 = normaliza_texto(str2)
    
    distancia = distancia_levenshtein(norm_str1, norm_str2)
    maximo = max(len(norm_str1), len(norm_str2))
    
    if maximo == 0:
        return distancia, 100.0  # Si ambas estan vacias, son 100% identicas
        
    # El porcentaje de similitud es relativo a la longitud de la cadena mas larga
    similarity = (1 - (distancia / maximo)) * 100
    return norm_str1, norm_str2, distancia, similarity

def main():
    print("=====================================================")
    print("A) DISTANCIA DE HAMMING Y PROBLEMA DEL DESFASE")
    print("=====================================================")
    s1, s2 = "Juan Perez", "Jaun Perez"
    print(f"Cadenas a comparar: '{s1}' vs '{s2}'")
    
    try:
        dist_hamming = distancia_hamming(s1, s2)
        print(f"-> Distancia de Hamming calculada: {dist_hamming}")
        print("\n[Explicacion]")
        print("La Distancia de Hamming encuentra 2 diferencias ('u' vs 'a' y 'a' vs 'u').")
        print("El algoritmo NO detecta que las letras estan desfasadas o intercambiadas,")
        print("solo compara rigidamente posicion a posicion.")
        
        print("\nQue pasa si tienen distinta longitud (ej. 'Juan' vs 'Juana')?")
        s3, s4 = "Juan", "Juana"
        print(f"Comparando '{s3}' vs '{s4}'...")
        distancia_hamming(s3, s4) # Esto lanzara el ValueError
    except ValueError as e:
        print(f"-> EXCEPCIoN: {e}")
        print("Esto demuestra que Hamming no es aplicable para cadenas de longitudes distintas.")

    print("\n=====================================================")
    print("B & C) DISTANCIA DE LEVENSHTEIN (ERRORES DE TIPEO)")
    print("=====================================================")
    nombre1 = "Horacio Lopez"
    nombre2 = "Oracio Lopez"
    dist_lev = distancia_levenshtein(nombre1, nombre2)
    print(f"Cadenas a comparar: '{nombre1}' vs '{nombre2}'")
    print(f"-> Distancia de Levenshtein (cantidad minima de errores/ediciones): {dist_lev}")
    print("En este caso, la distancia es 2 porque requiere 2 operaciones matematicas:")
    print(" 1. Eliminar la 'H'.")
    print(" 2. Sustituir la 'o' minuscula por una 'O' mayuscula (ya que sin normalizar, son distintas).")

    print("\n=====================================================")
    print("D) HEURiSTICA Y PROCESO DE COMPARACION PROPUESTO")
    print("=====================================================")
    print("Proceso propuesto para comparar nombres de usuarios:")
    print("  1. Normalizar: convertir a minusculas, quitar acentos y espacios extremos.")
    print("  2. Aplicar el algoritmo de Levenshtein.")
    print("  3. Transformar la distancia en un porcentaje de similitud confiable.")
    
    n1, n2 = "Horacio Lopez", " oracio lopez"
    print(f"\nTexto 1 (original): '{n1}'")
    print(f"Texto 2 (original): '{n2}'")
    
    norm1, norm2, dist_heur, sim = compara_huristica_texto(n1, n2)
    print(f"\nTexto 1 (normalizado): '{norm1}'")
    print(f"Texto 2 (normalizado): '{norm2}'")
    print(f"-> Distancia Levenshtein final: {dist_heur}")
    print(f"-> Similitud Algoritmica: {sim:.2f}%")

if __name__ == '__main__':
    main()
