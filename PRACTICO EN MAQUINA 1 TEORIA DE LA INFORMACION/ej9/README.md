# Simulación y Análisis Teórico de un Canal Binario Simétrico (BSC) mediante Sockets TCP

**Teoría de la Información - PRACTICO EN MAQUINA N° 1 - Ejercicio 9**
**GRUPO: Figueroa - Rios - Zalazar**

Este proyecto implementa la simulación y análisis teórico-experimental de un **Canal Binario Simétrico (BSC - *Binary Symmetric Channel*)** sin memoria utilizando una arquitectura Cliente-Servidor sobre **Sockets TCP** en Python.

---

## 1. Descripción del Proyecto

Un Canal Binario Simétrico transmite símbolos binarios ($X \in \{0, 1\}$) hacia una salida ($Y \in \{0, 1\}$). En cada transmisión individual:
- Un bit tiene probabilidad $p$ de invertirse (error de transmisión): $P(Y=1|X=0) = P(Y=0|X=1) = p$.
- Un bit tiene probabilidad $1-p$ de recibirse correctamente: $P(Y=0|X=0) = P(Y=1|X=1) = 1-p$.

El **servidor** actúa como una "caja negra": contiene la probabilidad de error $P_{\text{error}}$ oculta mediante una semilla pseudoaleatoria.  
El **cliente** se conecta al servidor para:
1. **Fase 1**: Descubrir empíricamente el valor de $p$ a través del cálculo de la tasa de error de bits (**BER** - *Bit Error Rate*) enviando tramas sintéticas de diferentes magnitudes ($N = 100$, $10.000$ y $1.000.000$ de bits) y analizando la convergencia estadística (Ley de los Grandes Números). Además, transmite un mensaje de texto para observar visualmente el impacto del ruido.
2. **Fase 2**: Modelar matemáticamente el canal calculando la **Matriz de Transición**, las **Probabilidades de la Fuente**, la **Información Mutua** $I(X;Y)$, la **Capacidad del Canal** $C$, y evaluar si la transmisión maximizó la capacidad del canal.

---

## 2. Arquitectura y Protocolo de Comunicación

La comunicación entre el cliente y el servidor se realiza a través de un socket TCP (`AF_INET`, `SOCK_STREAM`) en el puerto `5555`.

### Protocolo de Enmarcado de Longitud
Para evitar problemas derivados de la fragmentación de paquetes TCP (*streaming byte-oriented*), se utiliza un protocolo de enmarcado con longitud fija:
- **Encabezado (4 bytes)**: Un entero de 32 bits sin signo en formato Big-Endian (`struct.pack("!I", longitud)`), que indica la cantidad exacta de bytes del mensaje.
- **Cuerpo (N bytes)**: Cadena en formato ASCII con la secuencia de bits (`'0'` y `'1'`) o el comando de control (`"SALIR"`).

Tanto el cliente como el servidor implementan la función `recibir_exactamente(sock, cantidad)` para garantizar la recepción íntegra del bloque antes de procesarlo.

---

## 3. Requisitos y Ejecución

### Requisitos
- **Python 3.8** o superior (probado en Python 3.14).
- Bibliotecas estándar únicamente (`socket`, `struct`, `random`, `math`, `sys`, `time`, `threading`). No requiere dependencias externas.

### Paso a paso para la ejecución

1. **Iniciar el Servidor BSC:**
   Abrir una terminal en el directorio del proyecto y ejecutar:
   ```bash
   python servidor_bsc.py
   ```
   *El servidor quedará escuchando conexiones entrantes en el puerto 5555.*

2. **Ejecutar el Cliente BSC:**
   En otra terminal (o pestaña), ejecutar:
   ```bash
   python cliente_bsc.py
   ```
   *Opcionalmente, se pueden pasar como argumentos el host y puerto:*
   ```bash
   python cliente_bsc.py 127.0.0.1 5555
   ```

---

## 4. Resultados Experimentales Obtenidos

### Fase 1: Pruebas Empíricas y BER

| Longitud de Trama ($N$) | Errores Detectados | BER Empírico | Tiempo de Transmisión |
| :---: | :---: | :---: | :---: |
| **100 bits** | 6 | `0.060000` | < 0.001 s |
| **10.000 bits** | 604 | `0.060400` | 0.001 s |
| **1.000.000 bits** | 60.868 | `0.060868` | 0.145 s |

#### Análisis de la Ley de los Grandes Números
- Para $N = 100$, el tamaño de la muestra es reducido; un solo bit erróneo adicional alteraría el BER en un 1%, mostrando alta varianza muestral.
- Al incrementar $N$ a $10.000$ y $1.000.000$ de bits, la varianza del estimador tiende a cero ($\sigma^2 / N \to 0$).
- Conforme a la **Ley Débil de los Grandes Números (Khinchin / Bernoulli)**:
  $$\lim_{N \to \infty} P(|\text{BER}_N - p| > \varepsilon) = 0$$
  La media muestral converge en probabilidad al valor teórico de la probabilidad de error oculta en el servidor:
  $$p \approx 0.060868 \quad (\approx 6.09\%)$$
  *(El valor configurado internamente mediante la semilla 2026 en el servidor es $P_{\text{ERROR}} = 0.060968...$, verificando una coincidencia de 4 decimales exactos).*

#### Efecto Visual del Ruido sobre Texto
- **Texto original (66 caracteres / 528 bits):**
  > `"Teoria de la Informacion - Simulacion de Canal BSC con Sockets TCP"`
- **Texto recibido con ruido ($BER \approx 0.0644$, 34 bits alterados):**
  > `"teOrka de\x00lk Infosmaco.(-\x1b}ueg\x0don$le Can!l QC coN Socke|s VG"`
- Se evidencia cómo un canal con $p \approx 6.1\%$ distorsiona severamente caracteres ASCII al alterar bits de peso bajo o alto, llegando a generar caracteres de control no imprimibles (como `\x00` o `\x1b`).

---

### Fase 2: Modelado Matemático y Capacidad

Tomando la probabilidad descubierta $p \approx 0.060868$:

#### 1. Matriz de Transición del Canal
$$P(Y|X) = \begin{pmatrix} P(Y=0|X=0) & P(Y=1|X=0) \\ P(Y=0|X=1) & P(Y=1|X=1) \end{pmatrix} = \begin{pmatrix} 1 - p & p \\ p & 1 - p \end{pmatrix} = \begin{pmatrix} 0.939132 & 0.060868 \\ 0.060868 & 0.939132 \end{pmatrix}$$

#### 2. Probabilidades de Entrada $P(X)$
- **Trama Sintética ($N = 1.000.000$):**  
  $$P(X=0) = 0.500272, \quad P(X=1) = 0.499728 \quad (\approx 0.5)$$
- **Trama de Texto ($N = 528$):**  
  $$P(X=0) = 0.554924, \quad P(X=1) = 0.445076$$

#### 3. Información Mutua $I(X; Y)$
- Entropía del ruido condicional:
  $$H(Y|X) = H(p) = -p \log_2(p) - (1-p) \log_2(1-p) \approx 0.330881 \text{ bits/símbolo}$$
- **Caso A (Trama Sintética):**  
  $$P(Y=0) \approx 0.500239, \quad H(Y) \approx 1.000000 \text{ bits/símbolo}$$  
  $$I(X;Y) = H(Y) - H(Y|X) = 1.000000 - 0.330881 = 0.669119 \text{ bits/símbolo}$$
- **Caso B (Mensaje de Texto):**  
  $$P(Y=0) \approx 0.548238, \quad H(Y) \approx 0.993276 \text{ bits/símbolo}$$  
  $$I(X;Y) = 0.993276 - 0.330881 = 0.662395 \text{ bits/símbolo}$$

#### 4. Capacidad del Canal ($C$)
$$C = \max_{P(X)} I(X;Y) = 1 - H(p) = 1 - 0.330881 = 0.669119 \text{ bits/canal}$$

---

## 5. Respuestas a las Preguntas Teóricas

### ¿Logró su mensaje maximizar la capacidad del canal?
- **Para la trama sintética aleatoria: SÍ.**  
  $I(X;Y) = 0.669119$ y $C = 0.669119$ (diferencia relativa $< 0.001\%$, holgadamente dentro del margen de tolerancia del 5-10%).
- **Para el mensaje de texto: NO.**  
  Si bien está cerca numéricamente ($1.005\%$ de diferencia), $I(X;Y) = 0.662395 < C$. Esto se debe a que el texto natural no es puramente aleatorio: posee redundancia sintáctica y los códigos ASCII de caracteres alfanuméricos presentan una mayor proporción de bits ceros ($P(X=0) \approx 0.555$).

### Si la respuesta es no, ¿qué característica debería tener la trama de bits enviada para que $I(X; Y)$ sea igual a $C$?
En un Canal Binario Simétrico, la información mutua se expresa como:
$$I(X; Y) = H(Y) - H(Y|X) = H(Y) - H(p)$$
Dado que la probabilidad de error $p$ es una propiedad intrínseca y fija del canal, $H(p)$ es constante. En consecuencia, maximizar $I(X;Y)$ equivale estrictamente a **maximizar la entropía de salida $H(Y)$**.

Como $Y$ es un alfabeto binario ($\{0, 1\}$), el valor máximo absoluto de su entropía es:
$$H(Y)_{\max} = \log_2(2) = 1 \text{ bit/símbolo}$$
el cual se alcanza única y exclusivamente cuando la salida es equiprobable:
$$P(Y=0) = P(Y=1) = 0.5$$

Dado que $P(Y=0) = P(X=0)(1-p) + P(X=1)p$, para que $P(Y=0) = 0.5$ se requiere obligatoriamente que la fuente de entrada sea **EQUIPROBABLE**:
$$P(X=0) = P(X=1) = 0.5$$

**Conclusión:** Para que $I(X; Y) = C$, la trama transmitida debe tener una distribución uniforme de ceros y unos ($50\%$ de ceros y $50\%$ de unos) y una fuente sin memoria (símbolos independientes entre sí, sin redundancia). En telecomunicaciones, esto se logra aplicando técnicas de **compresión previa** (como codificación de Huffman o Lempel-Ziv) o algoritmos de **aleatorización (*scrambling*)** antes de ingresar al canal.
