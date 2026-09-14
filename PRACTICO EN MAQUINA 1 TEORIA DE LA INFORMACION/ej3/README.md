# Ejercicio 3 – Entropía Empírica en Archivos (Texto vs. Comprimidos)

## Descripción

Programa en Python que lee un archivo arbitrario byte por byte (en tiempo O(N)) y calcula:

- **Frecuencia relativa** de cada byte (valores 0 a 255).
- **Entropía empírica** H = − Σ pᵢ · log₂(pᵢ) [bits/símbolo].
- **Redundancia absoluta** R = H_max − H [bits/símbolo].
- **Redundancia relativa** R_rel = 1 − H / H_max.

donde H_max = log₂(256) = 8 bits/símbolo es la entropía máxima teórica para un alfabeto de 256 símbolos.

## Requisitos

- Python 3.6 o superior (no se requieren dependencias externas).

## Ejecución

```bash
python entropia.py <ruta_del_archivo>
```

### Ejemplos

```bash
# Analizar un archivo de texto plano
python entropia.py ejemplo.txt

# Analizar un archivo comprimido
python entropia.py ejemplo.zip
```

## Salida esperada

El programa imprime por consola:

1. La tabla de bytes presentes con su frecuencia absoluta y probabilidad.
2. La cantidad de símbolos distintos encontrados.
3. La entropía máxima (8 bits/símbolo).
4. La entropía empírica calculada.
5. La redundancia absoluta y relativa.

## Análisis conceptual (punto c)

**¿Por qué la entropía de un archivo .zip se acerca al máximo teórico de 8 bits/símbolo?**

Un algoritmo de compresión (como el usado en ZIP) elimina la redundancia de los datos originales. Su objetivo es representar la información con la menor cantidad de bits posible, acercándose al límite inferior que impone la entropía de la fuente.

Al comprimir un archivo, se eliminan patrones repetitivos y correlaciones estadísticas entre los bytes. El resultado es una secuencia de bytes que se comporta de forma cuasi-aleatoria: cada valor de byte (0–255) tiende a aparecer con una frecuencia similar, y no quedan patrones explotables.

En consecuencia:

- La distribución de bytes se aproxima a una **distribución uniforme**.
- La entropía empírica se acerca a **H_max = 8 bits/símbolo**.
- La **redundancia es cercana a cero**, lo que indica que prácticamente no queda información redundante por eliminar.

Esto es coherente con el **Teorema de codificación de fuente de Shannon**: un código óptimo produce una longitud promedio de código cercana a la entropía de la fuente. Un archivo ya comprimido no puede comprimirse significativamente más, precisamente porque su entropía ya es casi máxima.
