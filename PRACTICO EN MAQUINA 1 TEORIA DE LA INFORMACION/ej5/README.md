# Ejercicio 5: Gestión de Personas con Optimización Bitwise
Esta aplicación de Python genera y gestiona datos de personas simuladas, demostrando las diferencias clave entre almacenar información en formatos de texto de longitud variable y formatos binarios de longitud fija empleando técnicas de **empaquetado a nivel de bits (Bitwise)**.

## Requisitos Previos
No se requiere ninguna biblioteca externa. El proyecto utiliza exclusivamente módulos incluidos en la librería estándar de Python (`json`, `struct`, `os`, `random`).
- Se requiere Python 3.6 o superior.

## Archivos Generados
Al ejecutar la aplicación, se generarán dos archivos locales para realizar una comparativa:
1. `personas.json`: Archivo de texto estructurado de longitud variable (donde los booleanos son Strings `"True"` o `"False"`).
2. `personas.bin`: Archivo binario de longitud fija, donde cada registro tiene el mismo tamaño en bytes exactos y los 8 booleanos están compactados en **1 byte**.

## Instrucciones de Ejecución
1. Abre tu terminal o símbolo del sistema.
2. Navega al directorio donde se encuentra el archivo `main.py`.
3. Ejecuta el script de Python con el siguiente comando:
python main.py

4. La consola mostrará:
   - El proceso de generación.
   - Una **tabla de comparación de tamaños** en disco.
   - Una **conclusión teórica detallada** sobre el impacto de estas optimizaciones en sistemas de alta escala.
5. Luego de leer la conclusión, presiona `Enter` y el programa procederá a leer ambos archivos del disco, procesar el desempaquetado de bits y mostrar los datos en pantalla para comprobar que toda la información se ha guardado y recuperado exitosamente.

## Conceptos Aplicados
- **Bitwise OR (`|`) y Left Shift (`<<`)**: Utilizados para encender bits específicos y empaquetar 8 condiciones booleanas dentro de los 8 bits de un único byte.
- **Bitwise AND (`&`) y Left Shift (`<<`)**: Utilizados junto a máscaras binarias para comprobar el estado de un bit y desempaquetar los booleanos al leer el archivo.
- **Módulo `struct`**: Empleado para la codificación y decodificación en C-structs para manejo binario determinista y de longitud fija.