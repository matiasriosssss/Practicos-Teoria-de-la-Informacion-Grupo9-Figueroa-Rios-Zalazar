"""
Ejercicio 8 - Cálculo de Capacidad de Canal por Búsqueda Exhaustiva
             (Binario a Cuaternario)

Teoría de la Información - Práctico en máquina 1

Figueroa - Rios - Zalazar

Este programa calcula la Capacidad de Canal (C) de un sistema discreto
sin memoria con entrada binaria y salida cuaternaria.

El usuario ingresa los 8 valores de la matriz de transición P(Y|X),
correspondiente a una matriz de 2x4. Se valida que todas las
probabilidades estén entre 0 y 1 y que la suma de cada fila sea
exactamente 1.

Luego se realiza una búsqueda exhaustiva de P(X=0), utilizando un
incremento de 0.01. Para cada valor se obtiene:

    P(X=1) = 1 - P(X=0)

Se calculan las probabilidades de salida P(Y), la entropía H(Y),
la entropía condicional H(Y|X) y la información mutua:

    I(X;Y) = H(Y) - H(Y|X)

Finalmente se selecciona el mayor valor de I(X;Y), que corresponde
a la capacidad del canal encontrada.
"""

import math


def entropia(probabilidades):
    """Calcula la entropía en bits."""
    h = 0.0

    for p in probabilidades:
        if p > 0:
            h -= p * math.log2(p)

    return h


def ingresar_matriz():
    """Solicita y valida la matriz P(Y|X) de 2x4."""
    print("\nIngrese la matriz del canal P(Y|X).")
    print("Debe ingresar 4 probabilidades para X=0 y 4 para X=1.")
    print("Cada fila debe sumar exactamente 1.\n")

    while True:
        matriz = []

        for x in range(2):
            while True:
                fila = []

                print(f"Probabilidades para X={x}:")

                for y in range(4):
                    while True:
                        try:
                            p = float(input(f"  P(Y={y}|X={x}): "))

                            if 0 <= p <= 1:
                                fila.append(p)
                                break
                            else:
                                print("  Error: la probabilidad debe estar entre 0 y 1.")

                        except ValueError:
                            print("  Error: ingrese un número válido.")

                suma = sum(fila)

                # Tolerancia para evitar problemas propios de los floats.
                if math.isclose(suma, 1.0, rel_tol=0.0, abs_tol=1e-9):
                    # Ajuste mínimo para dejar la suma exactamente en 1
                    # cuando existe una diferencia de redondeo.
                    fila[-1] += 1.0 - suma
                    matriz.append(fila)
                    print(f"  Suma de la fila = {sum(fila):.10f}\n")
                    break
                else:
                    print(
                        f"  Error: la suma de la fila es {suma:.10f} "
                        "y debe ser exactamente 1."
                    )
                    print("  Vuelva a ingresar las 4 probabilidades.\n")

        return matriz


def calcular_probabilidades_salida(matriz, px0, px1):
    """
    Calcula P(Y) usando el Teorema de la Probabilidad Total:

    P(Y=y) = P(X=0)P(Y=y|X=0) + P(X=1)P(Y=y|X=1)
    """
    py = []

    for y in range(4):
        probabilidad = (
            px0 * matriz[0][y]
            + px1 * matriz[1][y]
        )
        py.append(probabilidad)

    return py


def calcular_entropia_condicional(matriz, px0, px1):
    """
    Calcula H(Y|X):

    H(Y|X) = P(X=0)H(Y|X=0) + P(X=1)H(Y|X=1)
    """
    h_x0 = entropia(matriz[0])
    h_x1 = entropia(matriz[1])

    return px0 * h_x0 + px1 * h_x1


def buscar_capacidad(matriz):
    """Realiza la búsqueda exhaustiva con salto de 0.01."""

    maximo = -1.0
    mejor_px0 = 0.0
    mejor_px1 = 1.0
    mejor_py = []
    mejor_hy = 0.0
    mejor_hy_x = 0.0

    # Se utiliza un entero de 0 a 100 para evitar errores de
    # representación de números decimales como 0.01.
    for i in range(101):

        px0 = i / 100.0
        px1 = 1.0 - px0

        # P(Y)
        py = calcular_probabilidades_salida(matriz, px0, px1)

        # H(Y)
        hy = entropia(py)

        # H(Y|X)
        hy_x = calcular_entropia_condicional(matriz, px0, px1)

        # Información Mutua
        informacion_mutua = hy - hy_x

        # Maximización
        if informacion_mutua > maximo:
            maximo = informacion_mutua
            mejor_px0 = px0
            mejor_px1 = px1
            mejor_py = py
            mejor_hy = hy
            mejor_hy_x = hy_x

    return (
        maximo,
        mejor_px0,
        mejor_px1,
        mejor_py,
        mejor_hy,
        mejor_hy_x
    )


def mostrar_matriz(matriz):
    """Muestra la matriz del canal."""
    print("\nMatriz del canal P(Y|X):")
    print("             Y=0       Y=1       Y=2       Y=3")
    print(
        f"X=0     {matriz[0][0]:.4f}    {matriz[0][1]:.4f}    "
        f"{matriz[0][2]:.4f}    {matriz[0][3]:.4f}"
    )
    print(
        f"X=1     {matriz[1][0]:.4f}    {matriz[1][1]:.4f}    "
        f"{matriz[1][2]:.4f}    {matriz[1][3]:.4f}"
    )


def main():
    print("=" * 65)
    print("  EJERCICIO 8 - CAPACIDAD DE CANAL")
    print("  Búsqueda Exhaustiva - Binario a Cuaternario")
    print("=" * 65)

    # a) Ingreso y validación de la matriz
    matriz = ingresar_matriz()

    mostrar_matriz(matriz)

    # b), c) y d) Búsqueda exhaustiva, cálculo de I(X;Y) y maximización
    (
        capacidad,
        px0,
        px1,
        py,
        hy,
        hy_x
    ) = buscar_capacidad(matriz)

    # e) Mostrar resultados
    print("\n" + "=" * 65)
    print("  RESULTADO DE LA BÚSQUEDA EXHAUSTIVA")
    print("=" * 65)

    print(f"\nCapacidad del Canal (C) : {capacidad:.6f} bits/símbolo")

    print("\nDistribución de entrada que maximiza el canal:")
    print(f"  P(X=0) = {px0:.2f}")
    print(f"  P(X=1) = {px1:.2f}")

    print("\nProbabilidades de salida P(Y):")
    for y in range(4):
        print(f"  P(Y={y}) = {py[y]:.6f}")

    print(f"\nEntropía de salida H(Y)       = {hy:.6f} bits")
    print(f"Entropía condicional H(Y|X)  = {hy_x:.6f} bits")
    print(f"Información Mutua I(X;Y)     = {capacidad:.6f} bits")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
