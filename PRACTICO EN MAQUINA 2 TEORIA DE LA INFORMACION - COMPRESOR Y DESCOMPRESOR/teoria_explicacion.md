# Marco Teórico y Justificación Académica: Compresión Fano con Fuente Extendida de Orden 2

Este documento contiene la explicación conceptual, teórica y matemática completa del proyecto, diseñada específicamente para preparar la defensa oral y responder a todas las inquietudes requeridas por la cátedra de **Teoría de la Información**.

---

## 1. Fundamentos de la Fuente de Información

### ¿Qué es una fuente extendida?
En Teoría de la Información, una fuente de memoria nula emite símbolos individuales pertenecientes a un alfabeto base $S = \{s_1, s_2, \dots, s_q\}$.
La **fuente extendida de orden $n$** (denotada $S^n$) es aquella cuyos símbolos son secuencias (tuplas) de $n$ símbolos consecutivos de la fuente original. Su alfabeto está compuesto por todas las combinaciones posibles de longitud $n$:
$$S^n = \{ \sigma = (s_{i_1}, s_{i_2}, \dots, s_{i_n}) \mid s_{i_k} \in S \}$$
El cardinal del alfabeto extendido pasa a ser $|S^n| = |S|^n$.

### ¿Qué significa extensión de orden 2?
En nuestro caso particular, el alfabeto base $S$ está constituido por los $256$ valores posibles de un byte ($0 \text{ a } 255$, es decir, $|S| = 256$).
La **extensión de orden 2** toma los bytes de entrada agrupados estrictamente de a dos en dos:
$$S^2 = \{ (b_1, b_2) \mid b_1, b_2 \in [0, 255] \}$$
El alfabeto resultante tiene un tamaño máximo teórico de:
$$|S^2| = 256^2 = 65.536 \text{ símbolos posibles}.$$
Cada par de bytes $(b_1, b_2)$ es tratado como una **unidad atómica indivisible** durante todo el proceso de codificación.

### ¿Por qué se utilizan pares en lugar de bytes individuales?
1. **Captura de dependencias estadísticas y correlación**: En la mayoría de los archivos reales (textos en lenguaje natural, ejecutables, imágenes sin comprimir), los bytes adyacentes no son estadísticamente independientes. Ciertas secuencias de letras (ejemplo en español: `"qu"`, `"de"`, `"os"`, `"en"`, `\r\n`) aparecen con una frecuencia desproporcionadamente alta en comparación con el producto de sus probabilidades marginales.
2. **Reducción de la entropía por byte**: Según los teoremas fundamentales de Shannon para fuentes con memoria:
   $$\frac{H(S^n)}{n} \le \frac{H(S^{n-1})}{n-1} \le \dots \le H(S)$$
   Al codificar bloques de mayor longitud, la longitud media de palabra codificada por byte puede aproximarse mucho más a la entropía de la fuente real, permitiendo mayores factores de compresión que si codificáramos cada byte de forma aislada.

---

## 2. Modelado de la Fuente y Estadísticas

### ¿Cómo se calculan las frecuencias?
1. Se lee el archivo como un flujo continuo de bytes: $B = [b_0, b_1, b_2, \dots, b_{N-1}]$.
2. Se recorre de a saltos de 2 posiciones: $(b_0, b_1), (b_2, b_3), \dots$
3. Un mapa de frecuencias (o tabla hash) registra la cantidad de apariciones exactas de cada par único:
   $$\text{freq}(p) = \sum_{k=0}^{\lfloor N/2 \rfloor - 1} \mathbb{I}( (b_{2k}, b_{2k+1}) = p )$$

### ¿Cómo se obtienen las probabilidades?
Siendo $M$ la cantidad total de pares en el archivo ($M = \lceil N/2 \rceil$):
$$P(p_i) = \frac{\text{freq}(p_i)}{M}, \quad \text{con } \sum_{i=1}^{K} P(p_i) = 1$$
donde $K$ es la cantidad de pares diferentes encontrados en el archivo ($K \le M$).

### Ordenamiento determinista
Antes de particionar, los $K$ pares únicos se ordenan de forma **descendente** según su frecuencia:
$$P(p_1) \ge P(p_2) \ge \dots \ge P(p_K)$$
Para garantizar determinismo absoluto ante empates (frecuencias iguales), el algoritmo utiliza como criterio secundario de desempate el orden numérico de los dos bytes del par.

---

## 3. El Algoritmo de Codificación de Fano

### Principio de funcionamiento
El algoritmo de Fano (propuesto por Robert Fano en 1949) es un método determinista **Top-Down** (de arriba hacia abajo) para construir códigos de prefijo de longitud variable:

1. **Ordenamiento**: Se listan los símbolos de mayor a menor probabilidad.
2. **Partición Óptima**: Se busca el punto de corte $k$ que divide el conjunto en dos subgrupos, $G_0$ y $G_1$, tales que la diferencia entre la suma de probabilidades de ambos sea mínima:
   $$\min_k \left| \sum_{j=1}^{k} P(p_j) - \sum_{j=k+1}^{n} P(p_j) \right|$$
3. **Asignación de bits**: Se antepone el bit `'0'` a todos los códigos de los símbolos de $G_0$, y el bit `'1'` a los de $G_1$.
4. **Recursión**: Se repite el procedimiento sobre $G_0$ y $G_1$ de forma independiente hasta que cada subgrupo contenga un único símbolo.

### Propiedad de código de prefijo (Instantaneidad)
Ningún código asignado a un símbolo es prefijo del código de otro símbolo. Esto garantiza que el flujo de bits recibido se puede decodificar de izquierda a derecha de forma unívoca y en tiempo lineal sin necesidad de delimitadores intermedios.

### Manejo de casos especiales
* **Archivo de 0 bytes**: El alfabeto está vacío ($K = 0$). Se emite una cabecera indicando tamaño 0 y 0 símbolos; no hay datos comprimidos.
* **Archivo con 1 único símbolo repetido**: La división en dos grupos no es posible porque $|G| = 1$. Se le asigna por convención un código fijo de 1 solo bit: `'0'`.

---

## 4. Estructura del Archivo Binario `.tdi`

El archivo comprimido debe ser completamente autónomo. Su estructura consta de:

```text
+--------------------------------------------------------------------------+
| CABECERA FIJA (19 bytes)                                                 |
|  - Magic Bytes: b'TDI2' (4 bytes)                                        |
|  - Versión: 0x01 (1 byte)                                                |
|  - Orden Extensión: 0x02 (1 byte)                                        |
|  - Tamaño Original: uint64 (8 bytes)                                     |
|  - Bits Válidos Último Byte: uint8 (1 byte, 0..8)                        |
|  - Cantidad de Símbolos K: uint32 (4 bytes)                              |
+--------------------------------------------------------------------------+
| DICCIONARIO DE CÓDIGOS (Longitud variable)                               |
|  Por cada uno de los K símbolos:                                         |
|    - Par de bytes: (b1, b2) (2 bytes)                                    |
|    - Longitud de código L: uint8 (1 byte)                                |
|    - Código empaquetado: ceil(L / 8) bytes                               |
+--------------------------------------------------------------------------+
| PAYLOAD / DATOS COMPRIMIDOS (Longitud variable)                          |
|  - Flujo empaquetado de bits generados por la codificación de los pares. |
+--------------------------------------------------------------------------+
```

### Justificación de cada campo:
* **Magic Bytes (`b'TDI2'`)**: Identifica que el archivo pertenece a nuestro formato específico y fue originado por un compresor de orden 2. Previene procesar archivos corruptos o de formato ajeno.
* **Versión (`0x01`)**: Permite evolucionar el software en el futuro sin romper compatibilidad hacia atrás.
* **Orden de Extensión (`0x02`)**: Asegura que el descompresor verifique que el modelo utilizado corresponde a pares de bytes.
* **Tamaño Original ($S_o$)**: Crucial para resolver la cantidad impar de bytes y controlar exactamente el fin de los datos decodificados.
* **Bits Válidos en Último Byte**: Los códigos binarios rara vez totalizan un múltiplo exacto de 8 bits. Este campo indica cuántos bits del byte final del archivo corresponden a datos reales y cuántos son bits de relleno (padding).
* **Cantidad de Símbolos ($K$)**: Delimita con exactitud cuántas entradas deben leerse para reconstruir el diccionario antes de comenzar con el payload.

---

## 5. Manejo de Casos Límite: Padding e Impares

### Manejo de archivos con cantidad impar de bytes
Si un archivo tiene longitud $N$ impar:
1. Se procesan los primeros $N-1$ bytes normalmente en pares: $(b_0, b_1), \dots, (b_{N-3}, b_{N-2})$.
2. El último byte $b_{N-1}$ se completa con un byte neutro `0x00` para formar el par $(b_{N-1}, \text{0x00})$.
3. Este par entra en el diccionario y en el flujo Fano de forma completamente normal.
4. Al descomprimir, se decodifican todos los pares concatenando sus bytes, y la salida se trunca a los **$S_o$ bytes originales exactos**. De este modo, el byte de relleno se descarta sin ambigüedad y sin agregar marcas complejas al bitstream.

### Manejo del padding de bits
En la computadora, los archivos se escriben a nivel de bytes (múltiplos de 8 bits). Si el compresor genera, por ejemplo, 73 bits de datos:
* Se escriben 9 bytes completos ($9 \times 8 = 72$ bits).
* El bit restante (el número 73) se ubica en el bit más significativo (MSB) del 10º byte, rellenando los 7 bits restantes con `0`.
* En la cabecera se almacena `Bits Válidos = 1`.
* El `BitReader` del descompresor se configura para leer exactamente 73 bits; al completarlos, ignora el resto del byte, evitando decodificar símbolos falsos.

---

## 6. Proceso de Descompresión

1. **Lectura de Cabecera**: Se validan los magic bytes, versión y orden. Se extraen $S_o$, bits válidos y $K$.
2. **Reconstrucción del Diccionario**: Se lee cada una de las $K$ entradas (par, longitud, bits de código) y se almacenan en un mapa `{código_bits: par}`.
3. **Construcción del Árbol de Prefijo (Trie)**:
   * Para optimizar la búsqueda y asegurar un proceso en tiempo lineal, los códigos se insertan en un árbol binario donde cada nodo tiene ramas `0` (izquierda) y `1` (derecha), y las hojas almacenan el par $(b_1, b_2)$.
4. **Decodificación**:
   * Se lee bit a bit desde el `BitReader`.
   * Se desciende por el árbol desde la raíz. Al alcanzar una hoja, se emite el par correspondiente y se regresa a la raíz.
5. **Reconstrucción byte a byte**:
   * Se ensamblan los pares y se trunca la secuencia resultante a $S_o$ bytes.
6. **Validación de Integridad**:
   * Se verifica que la cantidad de bytes sea idéntica a $S_o$.
   * Se computa el hash SHA-256 sobre el archivo generado y se compara contra el original.

---

## 7. Métricas de Rendimiento y Overhead

### Definiciones matemáticas:
* **Ratio de compresión**:
  $$R = \frac{S_o}{S_c}$$
  * $R > 1$: Existe reducción efectiva de tamaño.
  * $R < 1$: Expansión (el archivo comprimido es más grande que el original).
* **Ahorro de espacio**:
  $$A = \left(1 - \frac{S_c}{S_o}\right) \times 100\%$$
* **Tamaño relativo**:
  $$P = \left(\frac{S_c}{S_o}\right) \times 100\%$$
* **Overhead de cabecera**:
  $$O = \left(\frac{H}{S_c}\right) \times 100\%$$
  donde $H$ es el tamaño en bytes de la cabecera fija sumado al tamaño del diccionario serializado.
* **Throughputs de compresión y descompresión**:
  $$V_c = \frac{S_o \text{ (en MB)}}{t_c \text{ (en segundos)}}, \quad V_d = \frac{S_o \text{ (en MB)}}{t_d \text{ (en segundos)}}$$

### ¿Por qué un archivo comprimido puede resultar más grande ($S_c > S_o$)?
En archivos de tamaño pequeño (por ejemplo, menos de 500 bytes) o en archivos con alta entropía (datos aleatorios, archivos ya comprimidos como JPEG o ZIP):
1. **El costo del diccionario**: Cada par nuevo requiere almacenar en la cabecera sus 2 bytes de valor más la representación de su código.
2. **Entropía máxima**: Si todos los pares aparecen con frecuencias similares, los códigos Fano tienen longitudes cercanas a $\approx 16$ bits por par (es decir, 8 bits por byte original), lo que no produce ahorro de datos pero sí paga el costo fijo de la cabecera ($H$).
Por tanto, en archivos pequeños es un fenómeno natural y matemáticamente esperado que $R < 1$, $A < 0\%$ y $P > 100\%$.

---

## 8. Análisis de Complejidad Algorítmica y Espacial

| Etapa | Complejidad Temporal | Complejidad Espacial | Justificación |
|---|---|---|---|
| **Lectura de bytes** | $O(N)$ | $O(N)$ | Lectura secuencial de los $N$ bytes del archivo. |
| **Construcción de pares** | $O(N)$ | $O(N)$ | Recorrido lineal agrupando pares adyacentes. |
| **Conteo de frecuencias** | $O(M) = O(N)$ | $O(K)$ | Inserción en tabla hash de los $M = N/2$ pares. $K \le 65536$. |
| **Ordenamiento** | $O(K \log K)$ | $O(K)$ | Timsort sobre los $K$ pares únicos ($K \le 65536$, prácticamente constante en tiempo de ejecución). |
| **Construcción de Fano** | $O(K \log K)$ a $O(K^2)$ | $O(K)$ | Búsqueda del corte óptimo recursivo sobre el árbol de símbolos. |
| **Codificación (emisión)** | $O(M \cdot L_{prom}) = O(N)$ | $O(S_c)$ | Consulta en diccionario $O(1)$ por par y escritura en el `BitWriter`. |
| **Decodificación (lectura)** | $O(\text{bits}) = O(N)$ | $O(N)$ | Recorrido del árbol Trie bit a bit: cada paso toma $O(1)$. |

La implementación fue optimizada para no cargar estructuras innecesarias en memoria, manteniendo el código limpio, intuitivo y pedagógico para su exposición.
