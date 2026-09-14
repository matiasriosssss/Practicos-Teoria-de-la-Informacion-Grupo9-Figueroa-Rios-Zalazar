# Ejercicio 7 - Validador de CUIT/CUIL

## Descripción

Este programa permite validar un número de CUIT/CUIL utilizando el algoritmo de Módulo 11.

El usuario puede ingresar el número con o sin separadores, por ejemplo:

```text
20-38441703-6
20384417036
```

El programa elimina los caracteres no numéricos y verifica que el número resultante tenga exactamente 11 dígitos.

## Funcionamiento

Para realizar la validación:

1. Se eliminan los caracteres que no sean numéricos.
2. Se verifica que existan exactamente 11 dígitos.
3. Se separan los primeros 10 dígitos del dígito verificador ingresado.
4. Se aplican los pesos:

```text
[5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
```

5. Se calcula cada producto entre un dígito y su peso.
6. Se suman los productos obtenidos.
7. Se calcula el resto de la división de la suma por 11.
8. Se obtiene el dígito verificador esperado.
9. Se compara el dígito esperado con el dígito ingresado.
10. Se informa si el CUIT/CUIL es válido o inválido.

## Cálculo del dígito verificador

El resto se obtiene mediante:

```text
resto = suma_ponderada % 11
```

Luego:

```text
DV = 11 - resto
```

Existen dos casos especiales:

- Si `resto = 0`, el dígito verificador es `0`.
- Si `resto = 1`, el programa considera el dígito verificador como indefinido para los prefijos contemplados.

## Uso

Ejecutar:

```bash
python ejercicio7.py
```

El programa solicitará el CUIT/CUIL por teclado.

## Información mostrada

Además del resultado final, el programa muestra el desglose del cálculo:

- Primeros 10 dígitos.
- Pesos utilizados.
- Productos ponderados.
- Suma acumulada.
- Resto modular.
- Dígito verificador esperado.
- Dígito verificador ingresado.

## Resultado

Si ambos dígitos verificadores coinciden, se muestra:

```text
RESULTADO: >> VÁLIDO <<
```

En caso contrario:

```text
RESULTADO: >> INVÁLIDO <<
```

## Asignatura

Teoría de la Información - Práctico en máquina 1.

## Integrantes

Figueroa - Rios - Zalazar
