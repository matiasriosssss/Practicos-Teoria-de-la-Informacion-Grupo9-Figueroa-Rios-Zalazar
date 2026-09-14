# Ejercicio 2 - Análisis de Entropía, Histogramas y Estructura de Archivos (BMP vs. JPG)


Aplicación que analiza la distribución estadística y estructura interna de archivos BMP y JPG, calculando entropía de Shannon y generando histogramas comparativos.

### Funcionalidades

- **a)** Validación de extensión y formato interno (firma BMP `BM` / firma JPEG `FF D8`).
- **b)** Lectura e impresión de la cabecera BMP (54 bytes): firma, tamaño, dimensiones, profundidad de color, compresión, etc.
- **c)** Lectura byte a byte y cálculo de frecuencia relativa P(x) para cada símbolo (0-255).
- **d)** Generación de histogramas comparativos (frecuencia absoluta y distribución de probabilidad).
- **e)** Cálculo de entropía empírica de Shannon: `H(X) = -Σ P(x) · log₂(P(x))`.
- **f)** Comparación de entropías y análisis teórico de las diferencias.

## Requisitos

- **Python 3.8+**
- Bibliotecas:
  - `matplotlib` (gráficos)
  - `numpy` (cálculos numéricos)

### Instalación de dependencias

```bash
pip install matplotlib numpy
```

## Ejecución

```bash
python main.py
```

El programa solicitará por consola:
1. La ruta al archivo `.bmp`
2. La ruta al archivo `.jpg`

> **Nota:** Ambos archivos deben contener la misma fotografía para que la comparación sea significativa.

### Ejemplo de uso

```
Ingrese las rutas de los archivos de imagen:
  Ruta del archivo BMP: C:\imagenes\foto.bmp
  Ruta del archivo JPG: C:\imagenes\foto.jpg
  En ese orden
```

## Salida

- Datos de la cabecera BMP impresos en consola
- Valores de entropía de Shannon para ambos archivos
- Análisis teórico comparativo
- Archivo `histogramas_comparativos.png` con los 4 gráficos generados

## Anotacion

-Las imagenes guardadas sobreescriben a las guardadas anteriormente
-Es necesario cerrar la grafica para que cargue el resto de la ejecucion del programa

