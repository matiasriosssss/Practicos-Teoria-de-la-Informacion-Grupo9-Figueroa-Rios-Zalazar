# Ejercicio 8 - Cálculo de Capacidad de Canal

## Descripción

Este programa calcula la capacidad de un canal de comunicación discreto sin memoria con entrada binaria y salida cuaternaria.

El canal se representa mediante una matriz de transición `P(Y|X)` de tamaño 2x4:

- Dos posibles valores de entrada: `X=0` y `X=1`.
- Cuatro posibles valores de salida: `Y=0`, `Y=1`, `Y=2` y `Y=3`.

## Ingreso de datos

El usuario debe ingresar las 8 probabilidades de la matriz de transición.

Cada probabilidad debe estar entre `0` y `1` y la suma de cada fila debe ser igual a `1`.

La matriz tiene la forma:

```text
             Y=0    Y=1    Y=2    Y=3
X=0           ...
X=1           ...
```

## Funcionamiento

El programa realiza una búsqueda exhaustiva de la distribución de entrada.

Se prueban todos los valores posibles de:

```text
P(X=0) = 0.00, 0.01, 0.02, ..., 1.00
```

Para cada valor se calcula:

```text
P(X=1) = 1 - P(X=0)
```

Luego se obtienen las probabilidades de salida utilizando el Teorema de la Probabilidad Total:

```text
P(Y=y) = P(X=0)P(Y=y|X=0) + P(X=1)P(Y=y|X=1)
```

## Entropía

El programa calcula la entropía de una distribución mediante:

```text
H = -Σ p * log2(p)
```

También calcula la entropía condicional:

```text
H(Y|X) = P(X=0)H(Y|X=0) + P(X=1)H(Y|X=1)
```

## Información mutua

Para cada distribución de entrada se calcula:

```text
I(X;Y) = H(Y) - H(Y|X)
```

La capacidad del canal corresponde al mayor valor de información mutua encontrado durante la búsqueda.

## Uso

Ejecutar:

```bash
python ejercicio8.py
```

El programa solicitará las probabilidades de la matriz del canal.

## Resultados

Al finalizar, se muestra:

- Capacidad del canal en bits/símbolo.
- `P(X=0)` que maximiza la información mutua.
- `P(X=1)` que maximiza la información mutua.
- Probabilidades de salida `P(Y)`.
- Entropía de salida `H(Y)`.
- Entropía condicional `H(Y|X)`.
- Información mutua máxima `I(X;Y)`.

## Método de búsqueda

La búsqueda utiliza un incremento de `0.01`, por lo que se evalúan 101 distribuciones posibles de entrada.

Se utiliza un entero de `0` a `100` internamente para evitar problemas de representación de números decimales.

## Asignatura

Teoría de la Información - Práctico en máquina 1.

## Integrantes

Figueroa - Rios - Zalazar
