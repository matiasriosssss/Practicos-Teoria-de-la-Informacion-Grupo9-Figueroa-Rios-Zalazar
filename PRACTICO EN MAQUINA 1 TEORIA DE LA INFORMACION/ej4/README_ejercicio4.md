# Ejercicio 4 - Índice de Coincidencia en Archivos

## Descripción

Este programa calcula el Índice de Coincidencia (IC) de un archivo.

El archivo se analiza byte por byte y se obtiene la frecuencia de aparición de cada uno de los 256 posibles valores de byte. A partir de estas frecuencias se calcula el Índice de Coincidencia mediante:

IC = Σ [fi * (fi - 1)] / [N * (N - 1)]

Donde:

- `fi` es la frecuencia absoluta de cada elemento.
- `N` es la cantidad total de elementos analizados.

El programa también realiza un análisis adicional sobre las letras del español cuando el archivo corresponde a un texto.

## Funcionamiento

1. Verifica que el archivo indicado exista.
2. Obtiene su tamaño en bytes.
3. Lee el archivo en modo binario y cuenta la frecuencia de cada byte.
4. Calcula el Índice de Coincidencia general.
5. Muestra una tabla con:
   - Byte.
   - Carácter.
   - Frecuencia.
   - Probabilidad.
   - Término `fi*(fi-1)`.
6. Si corresponde, analiza las letras del español, normalizando mayúsculas y acentos.
7. Muestra una interpretación del resultado obtenido.

## Uso

Ejecutar desde una terminal:

```bash
python ejercicio4.py <ruta_archivo>
```

Ejemplos:

```bash
python ejercicio4.py archivo.txt
python ejercicio4.py archivo.zip
```

## Resultados

El programa muestra el número de símbolos distintos, el total de elementos, la suma de los términos `fi*(fi-1)`, el denominador y el Índice de Coincidencia.

Para el análisis de bytes se utiliza como referencia el valor esperado para una distribución uniforme de 256 símbolos:

`1/256 ≈ 0.0039`

En archivos de texto también se compara el IC de las letras con valores de referencia del español.

## Complejidad

El conteo de bytes se realiza en tiempo `O(N)`, donde `N` es la cantidad de bytes del archivo.

## Asignatura

Teoría de la Información - Práctico en máquina 1.

## Integrantes

Figueroa - Rios - Zalazar
