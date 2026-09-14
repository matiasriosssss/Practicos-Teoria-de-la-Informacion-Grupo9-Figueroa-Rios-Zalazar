# Ejercicio 6: Comparación de Textos y Similitud Algorítmica
Este proyecto es una herramienta escrita en Python que permite comparar dos cadenas de texto y evaluar su grado de similitud algorítmica a través de distintas metodologías, específicamente la **Distancia de Hamming** y la **Distancia de Levenshtein (Distancia de Edición)**.

## Requisitos
- Python 3.6 o superior.
- No requiere la instalación de bibliotecas externas (utiliza únicamente módulos estándar como `unicodedata`).

## Instrucciones para la Ejecución
1. Abre tu terminal o consola de comandos (Command Prompt, PowerShell, Bash, etc.).
2. Navega hasta el directorio donde se encuentra el archivo `similitud.py`:
cd "ruta/al/directorio/Ejercicio 6"
3. Ejecuta el script invocando el intérprete de Python:
python similitud.py

## Salida Esperada
Al ejecutar el script, el programa ejecutará pruebas automáticas respondiendo a cada inciso del requerimiento:

1. Demostrará cómo la Distancia de Hamming procesa "Juan Perez" vs "Jaun Perez", así como la excepción controlada al comparar palabras de distinta longitud ("Juan" vs "Juana").
2. Calculará la Distancia de Levenshtein probando con los nombres "Horacio López" y "Oracio López", retornando la cantidad de errores de tipeo o ediciones detectadas (que es 1).
3. Mostrará un flujo propuesto (Heurística) que primero normaliza textos "ruidosos" (con espacios extra o diferencias de acentuación/capitalización) y luego arroja un porcentaje exacto de similitud.