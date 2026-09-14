# Ejercicio 1: Análisis de Audio y Teoría de la Información
Esta aplicación en Python realiza un análisis estadístico y estructural de archivos de audio, permitiendo comparar la diferencia entre un archivo de audio sin compresión (`.wav`) y uno comprimido (`.mp3`), bajo la óptica de la **Teoría de la Información**.

## Funcionalidades principales
- **Validación**: Verifica que las extensiones y formatos correspondan a WAV y MP3 reales.
- **Análisis de Cabecera (WAV)**: Lee la estructura `RIFF/WAVE` y muestra sus propiedades principales (frecuencia de muestreo, formato, tamaño, resolución, etc.).
- **Distribución de Probabilidad**: Calcula la frecuencia relativa de cada byte (0-255) a lo largo del archivo.
- **Histogramas**: Genera gráficos visuales con matplotlib de la distribución de símbolos.
- **Cálculo de Entropía**: Obtiene la Entropía Empírica usando la fórmula de Shannon.
- **Comparación Teórica**: Explica los resultados basándose en la compresión de información y redundancia.

## Requisitos previos
Para poder ejecutar el código, se necesita tener **Python 3.x** instalado. 
Además, es necesario instalar la biblioteca `matplotlib` para la generación de los gráficos (histogramas).

### Instalación de dependencias
Abre una terminal o consola y ejecuta el siguiente comando:
pip install matplotlib

## Instrucciones de ejecución
1. Asegúrate de contar con dos archivos de audio, de preferencia con la misma pista, uno en formato `.wav` y otro en formato `.mp3`.
2. Ejecuta el script desde la terminal o consola ubicándote en la carpeta del proyecto:
python analizador_audio.py

3. El programa te solicitará las rutas de ambos archivos. Puedes escribir la ruta completa manualmente o arrastrar los archivos hacia la consola.
   - **Ejemplo WAV**: `C:\MisAudios\pista1.wav`
   - **Ejemplo MP3**: `C:\MisAudios\pista1.mp3`

4. El programa ejecutará las validaciones, análisis y cálculos, imprimiendo en pantalla los datos de la cabecera del WAV, y al final los resultados y conclusiones de la entropía.
5. Se abrirá una ventana con los gráficos (histogramas). Cierra la ventana del gráfico para que el programa finalice su ejecución.