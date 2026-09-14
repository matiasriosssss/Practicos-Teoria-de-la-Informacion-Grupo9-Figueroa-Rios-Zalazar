# PRACTICO EN MAQUINA 1 - TEORÍA DE LA INFORMACIÓN
# FIGUEROA - RIOS - ZALAZAR
# Ejercicio 9: Simulación y Análisis Teórico de un Canal Binario Simétrico (BSC)
#             mediante Sockets TCP.

# Este script implementa el cliente que interactúa con el servidor BSC ("caja negra"),
# llevando a cabo:
#   - FASE 1: Transmisión y Tasa de Error Empírica (BER) sobre tramas de diferente
#             longitud (100, 10.000, 1.000.000 de bits) y transmisión de texto.
#   - FASE 2: Modelado matemático del canal, cálculo de matriz de transición,
#             probabilidades de la fuente, información mutua I(X;Y), capacidad C,
#             y análisis de maximización de la capacidad del canal.
#
# ==============================================================================

import socket
import struct
import random
import math
import sys
import time

# Configuración de codificación para consolas Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configuración por defecto de conexión
HOST_DEFECTO = "127.0.0.1"
PUERTO_DEFECTO = 5555


# Protocolo de comunicacion con el servidor

def recibir_exactamente(sock: socket.socket, cantidad: int) -> bytes:
    """
    Lee exactamente 'cantidad' de bytes desde el socket TCP.
    Garantiza la recepción completa independientemente de la fragmentación de paquetes.
    """
    datos = bytearray()
    while len(datos) < cantidad:
        bloque = sock.recv(cantidad - len(datos))
        if not bloque:
            raise ConnectionError("La conexión fue cerrada inesperadamente por el servidor.")
        datos.extend(bloque)
    return bytes(datos)


def recibir_mensaje(sock: socket.socket) -> str:
    """
    Recibe un mensaje con prefijo de longitud de 4 bytes (Big-Endian uint32).
    """
    encabezado = recibir_exactamente(sock, 4)
    longitud = struct.unpack("!I", encabezado)[0]
    datos = recibir_exactamente(sock, longitud)
    return datos.decode("ascii")


def enviar_mensaje(sock: socket.socket, mensaje: str) -> None:
    """
    Envía un mensaje precedido por su longitud en 4 bytes (Big-Endian uint32).
    """
    datos = mensaje.encode("ascii")
    encabezado = struct.pack("!I", len(datos))
    sock.sendall(encabezado + datos)

# UTILIDADES DE CONVERSIÓN Y GENERACIÓN DE TRAMAS

def generar_trama_aleatoria(n_bits: int, p0: float = 0.5, seed: int = None) -> str:
    """
    Genera una cadena de bits ('0' y '1') pseudoaleatoria de longitud 'n_bits'.
    p0: Probabilidad de generar un '0'. Por defecto 0.5 (fuente equiprobable).
    """
    rng = random.Random(seed)
    bits = ['0' if rng.random() < p0 else '1' for _ in range(n_bits)]
    return "".join(bits)


def texto_a_binario(texto: str) -> str:
    """
    Convierte una cadena de texto a su representación binaria de 8 bits por carácter (ASCII / UTF-8).
    """
    bytes_texto = texto.encode("utf-8")
    return "".join(f"{byte:08b}" for byte in bytes_texto)


def binario_a_texto(bits: str) -> str:
    """
    Convierte una secuencia binaria en texto (agrupando de a 8 bits).
    En caso de bytes corruptos, utiliza decodificación segura con reemplazo.
    """
    bytes_lista = bytearray()
    for i in range(0, len(bits), 8):
        byte_chunk = bits[i:i + 8]
        if len(byte_chunk) == 8:
            bytes_lista.append(int(byte_chunk, 2))
    return bytes_lista.decode("utf-8", errors="replace")


def formato_legible(texto: str) -> str:
    """
    Reemplaza caracteres no imprimibles o de control para mostrarlos de forma segura en consola.
    """
    return "".join(c if (c.isprintable() and c not in ('\r', '\n', '\t')) else f"\\x{ord(c):02x}" for c in texto)


def calcular_ber(original: str, recibido: str) -> tuple[int, float]:
    """
    Compara la trama original con la recibida bit a bit.
    Retorna:
      - errores: Cantidad total de bits discrepantes.
      - ber: Bit Error Rate (errores / total de bits).
    """
    if len(original) != len(recibido):
        raise ValueError("Las longitudes de la trama original y recibida no coinciden.")
    
    errores = sum(1 for b_orig, b_rec in zip(original, recibido) if b_orig != b_rec)
    ber = errores / len(original)
    return errores, ber



# MODELADO MATEMÁTICO - TEORÍA DE LA INFORMACIÓN

def entropia_binaria(p: float) -> float:
    """
    Calcula la función de entropía binaria H(p) = -p*log2(p) - (1-p)*log2(1-p).
    Si p=0 o p=1, por límite de x*log2(x) cuando x->0, el resultado es 0.
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return - (p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def calcular_probabilidades_fuente(trama: str) -> tuple[float, float]:
    """
    Calcula las probabilidades de entrada de los símbolos P(x0) y P(x1)
    a partir de la frecuencia relativa de '0's y '1's en la trama transmitida.
    """
    total = len(trama)
    if total == 0:
        return 0.0, 0.0
    ceros = trama.count('0')
    unos = total - ceros
    return ceros / total, unos / total


def calcular_informacion_mutua(px0: float, px1: float, p_error: float) -> dict:
    """
    Calcula la Información Mutua I(X;Y) para una transmisión a través de un BSC
    con probabilidad de error 'p_error' y distribución de entrada P(X=0)=px0, P(X=1)=px1.

    En un Canal Binario Simétrico (BSC):
      - P(Y=0 | X=0) = 1 - p,   P(Y=1 | X=0) = p
      - P(Y=0 | X=1) = p,       P(Y=1 | X=1) = 1 - p
    
    Distribución marginal de salida P(Y):
      - P(Y=0) = P(X=0)*P(Y=0|X=0) + P(X=1)*P(Y=0|X=1) = px0*(1-p) + px1*p
      - P(Y=1) = P(X=0)*P(Y=1|X=0) + P(X=1)*P(Y=1|X=1) = px0*p + px1*(1-p)
    
    Entropías:
      - Entropía condicional (ruido del canal): H(Y|X) = H(p)
      - Entropía de salida: H(Y) = - P(Y=0)*log2(P(Y=0)) - P(Y=1)*log2(P(Y=1))
      - Información Mutua: I(X;Y) = H(Y) - H(Y|X)
    """
    py0 = px0 * (1.0 - p_error) + px1 * p_error
    py1 = px0 * p_error + px1 * (1.0 - p_error)

    h_y = entropia_binaria(py0)
    h_ruido = entropia_binaria(p_error)
    i_xy = h_y - h_ruido

    return {
        "py0": py0,
        "py1": py1,
        "h_y": h_y,
        "h_ruido": h_ruido,
        "i_xy": i_xy
    }


def calcular_capacidad_canal(p_error: float) -> float:
    """
    Calcula la Capacidad de canal C de un BSC:
      C = 1 - H(p) = 1 - [-p*log2(p) - (1-p)*log2(1-p)]
    La capacidad es el máximo de I(X;Y) sobre todas las distribuciones de entrada P(X).
    Para el BSC se alcanza cuando P(X=0) = P(X=1) = 0.5.
    """
    return 1.0 - entropia_binaria(p_error)

# EJECUCIÓN DEL CLIENTE

def ejecutar_cliente(host: str = HOST_DEFECTO, puerto: int = PUERTO_DEFECTO):
    print("=" * 70)
    print(" CLIENTE - ANALISIS EXPERIMENTAL Y TEORICO DE UN CANAL BSC")
    print("=" * 70)
    print(f"Conectando al servidor BSC en {host}:{puerto}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, puerto))
        print("Conexion establecida exitosamente con el servidor.\n")
    except Exception as e:
        print(f"Error al conectar con el servidor: {e}")
        print("Verificar haber iniciado primero el script 'servidor_bsc.py'.")
        return

    try:
        # FASE 1: Transmisión y Tasa de Error Empírica (BER)
        print("=" * 70)
        print(" FASE 1: TRANSMISION Y TASA DE ERROR EMPIRICA (BER)")
        print("=" * 70)

        magnitudes = [100, 10000, 1000000]
        resultados_ber = []
        ultima_trama_sintetica = ""

        print("\n--- Bateria de Pruebas Empiricas con Tramas Sinteticas ---")
        print(f"{'N Bits':>12} | {'Errores':>10} | {'BER Empirico':>15} | {'Tiempo (s)':>12}")
        print("-" * 57)

        for n in magnitudes:
            # 1. Generar trama aleatoria equiprobable
            trama_tx = generar_trama_aleatoria(n, p0=0.5, seed=42 + n)
            if n == 1000000:
                ultima_trama_sintetica = trama_tx

            # 2. Enviar y recibir a través del socket
            t_inicio = time.time()
            enviar_mensaje(sock, trama_tx)
            trama_rx = recibir_mensaje(sock)
            duracion = time.time() - t_inicio

            # 3. Contar errores y calcular BER
            errores, ber = calcular_ber(trama_tx, trama_rx)
            resultados_ber.append((n, errores, ber, duracion))

            print(f"{n:>12,d} | {errores:>10,d} | {ber:>15.6f} | {duracion:>12.3f}")

        # Análisis de la Ley de los Grandes Números
        p_estimada = resultados_ber[-1][2]  # La obtenida con 1.000.000 bits
        print("\n[+] Analisis de Convergencia (Ley de los Grandes Numeros):")
        print("    - Para N = 100 bits: La muestra es pequena y la varianza estadistica")
        print(f"      es alta (BER = {resultados_ber[0][2]:.6f}). Unos pocos bits alterados")
        print("      desvian fuertemente el valor estimado.")
        print("    - Para N = 10.000 bits: La estimacion se estabiliza notablemente")
        print(f"      alrededor del valor medio real (BER = {resultados_ber[1][2]:.6f}).")
        print("    - Para N = 1.000.000 bits: Segun el Teorema de la Ley de los Grandes")
        print("      Numeros (Khinchin / Bernoulli), la media muestral converge en probabilidad")
        print(f"      a la esperanza matematica teorica: p ≈ {p_estimada:.6f} (~ {p_estimada*100:.2f}% de error).")

        # Prueba con mensaje de texto
        print("\n--- Transmision de Mensaje de Texto (Efecto Visual del Ruido) ---")
        texto_original = "Teoria de la Informacion - Simulacion de Canal BSC con Sockets TCP"
        bits_texto = texto_a_binario(texto_original)

        enviar_mensaje(sock, bits_texto)
        bits_texto_rx = recibir_mensaje(sock)
        texto_recibido = binario_a_texto(bits_texto_rx)

        errores_txt, ber_txt = calcular_ber(bits_texto, bits_texto_rx)

        print(f"Texto original ({len(texto_original)} caracteres / {len(bits_texto)} bits):")
        print(f"  \"{texto_original}\"")
        print(f"\nTexto recibido con ruido del canal (BER: {ber_txt:.4f}, {errores_txt} bits alterados):")
        print(f"  \"{formato_legible(texto_recibido)}\"")
        print("-" * 70)

        # FASE 2: Modelado Matemático y Capacidad del Canal
        print("\n" + "=" * 70)
        print(" FASE 2: MODELADO MATEMATICO Y CAPACIDAD DEL CANAL")
        print("=" * 70)

        # Utilizamos el valor de p obtenido con mayor precisión estadística (N=1.000.000)
        p = p_estimada
        print(f"\nProbabilidad de error del canal asumida: p = {p:.6f}")

        # 1. Matriz del Canal
        print("\n1. Matriz de Transicion del Canal P(Y_j | X_i):")
        print("           Y=0           Y=1")
        print(f"  X=0  [ {1.0 - p:.6f}    {p:.6f} ]")
        print(f"  X=1  [ {p:.6f}    {1.0 - p:.6f} ]")
        print("   donde P(Y=0|X=0) = 1-p, P(Y=1|X=0) = p, P(Y=0|X=1) = p, P(Y=1|X=1) = 1-p")

        # 2. Probabilidades de la Fuente
        print("\n2. Probabilidades de Entrada de los Simbolos P(X):")
        px0_sint, px1_sint = calcular_probabilidades_fuente(ultima_trama_sintetica)
        px0_txt, px1_txt = calcular_probabilidades_fuente(bits_texto)

        print(f"   [Caso A: Trama Sintetica Aleatoria (N=1.000.000 bits)]")
        print(f"     P(X=0) = {px0_sint:.6f}")
        print(f"     P(X=1) = {px1_sint:.6f}")

        print(f"   [Caso B: Trama del Mensaje de Texto (N={len(bits_texto)} bits)]")
        print(f"     P(X=0) = {px0_txt:.6f}")
        print(f"     P(X=1) = {px1_txt:.6f}")
        print("     (Nota: en ASCII usual, los caracteres tienen predominancia del bit '0')")

        # 3. Información Mutua I(X;Y)
        print("\n3. Informacion Mutua I(X; Y) = H(Y) - H(Y|X):")
        im_sint = calcular_informacion_mutua(px0_sint, px1_sint, p)
        im_txt = calcular_informacion_mutua(px0_txt, px1_txt, p)

        print(f"   - Ruido del canal H(Y|X) = H(p) = {im_sint['h_ruido']:.6f} bits/simbolo")
        print(f"   [Caso A: Trama Sintetica]")
        print(f"     P(Y=0) = {im_sint['py0']:.6f}, P(Y=1) = {im_sint['py1']:.6f}")
        print(f"     H(Y)   = {im_sint['h_y']:.6f} bits/simbolo")
        print(f"     I(X;Y) = {im_sint['i_xy']:.6f} bits/simbolo")

        print(f"   [Caso B: Mensaje de Texto]")
        print(f"     P(Y=0) = {im_txt['py0']:.6f}, P(Y=1) = {im_txt['py1']:.6f}")
        print(f"     H(Y)   = {im_txt['h_y']:.6f} bits/simbolo")
        print(f"     I(X;Y) = {im_txt['i_xy']:.6f} bits/simbolo")

        # 4. Capacidad del Canal
        c = calcular_capacidad_canal(p)
        print("\n4. Capacidad Maxima del Canal BSC:")
        print(f"   C = 1 - H(p) = 1 - {entropia_binaria(p):.6f} = {c:.6f} bits/canal")

        # 5. Análisis de Maximización
        print("\n5. Analisis de Maximizacion:")
        diferencia_sint = abs(c - im_sint['i_xy'])
        pct_error_sint = (diferencia_sint / c) * 100.0 if c > 0 else 0.0

        diferencia_txt = abs(c - im_txt['i_xy'])
        pct_error_txt = (diferencia_txt / c) * 100.0 if c > 0 else 0.0

        print(f"   - Comparacion Caso A (Trama Sintetica):")
        print(f"     I(X;Y) = {im_sint['i_xy']:.6f} vs C = {c:.6f} (Diferencia: {diferencia_sint:.6f} = {pct_error_sint:.3f}%)")
        if pct_error_sint <= 10.0:
            print("     -> SI logro maximizar la capacidad del canal (dentro del margen del 5-10%).")
        else:
            print("     -> NO logro maximizar la capacidad.")

        print(f"   - Comparacion Caso B (Mensaje de Texto):")
        print(f"     I(X;Y) = {im_txt['i_xy']:.6f} vs C = {c:.6f} (Diferencia: {diferencia_txt:.6f} = {pct_error_txt:.3f}%)")
        if pct_error_txt <= 10.0:
            print("     -> SI logro maximizar la capacidad del canal.")
        else:
            print("     -> NO logro maximizar la capacidad (la distribucion del texto no es uniforme).")

        # RESPUESTAS A LAS PREGUNTAS TEÓRICAS (CONSIGNA 5):
        # ¿Logró su mensaje maximizar la capacidad del canal?
        # RESPUESTA:
        # En el caso de la TRAMA SINTÉTICA ALEATORIA (Caso A), SÍ se logra maximizar
        # la capacidad del canal (I(X;Y) ≈ C, con diferencia menor al 0.01%).
        # Esto ocurre porque los bits fueron generados de forma pseudoaleatoria equiprobable,
        # obteniéndose P(X=0) ≈ 0.5 y P(X=1) ≈ 0.5.
        #
        # Por otro lado, en el caso del MENSAJE DE TEXTO (Caso B), NO se logra maximizar
        # la capacidad del canal, ya que I(X;Y) resulta menor a C.
        #
        # ¿Qué característica debería tener la trama de bits enviada para que I(X;Y) sea igual a C?
        #
        # RESPUESTA:
        # La capacidad del canal se define como C = max_{P(X)} I(X;Y).
        # En un Canal Binario Simétrico (BSC), el equívoco / entropía condicional es constante:
        #   H(Y|X) = H(p) = -p*log2(p) - (1-p)*log2(1-p).
        # Por ende, I(X;Y) = H(Y) - H(p).
        # Dado que H(p) es fija (propiedad física del canal), para maximizar I(X;Y)
        # se debe maximizar la entropía de salida H(Y).
        # Siendo Y una variable binaria (0 o 1), el valor máximo de H(Y) es 1 bit,
        # lo cual ocurre si y solo si la salida es equiprobable: P(Y=0) = P(Y=1) = 0.5.
        # Para que P(Y=0) = P(Y=1) = 0.5 en un BSC, la distribución de entrada DEBE SER
        # EQUIPROBABLE:
        #   P(X=0) = P(X=1) = 0.5
        #
        # Por lo tanto, la característica requerida es que la trama de entrada posea
        # símbolos binarios estrictamente equiprobables (50% ceros y 50% unos) e
        # idealmente sin correlación/memoria (fuente sin memoria).

        print("\n" + "=" * 70)
        print(" CONCLUSIONES Y RESPUESTAS A LAS PREGUNTAS TEORICAS:")
        print("=" * 70)
        print("1. ¿Logro su mensaje maximizar la capacidad del canal?")
        print("   - Trama sintetica: SI, porque los bits fueron generados de forma equiprobable")
        print(f"     P(X=0) ≈ {px0_sint:.4f}, P(X=1) ≈ {px1_sint:.4f}, alcanzando I(X;Y) = {im_sint['i_xy']:.6f} ≈ C = {c:.6f}.")
        print("   - Mensaje de texto: NO, debido a que el texto natural codificado en ASCII/UTF-8")
        print(f"     presenta redundancia y desbalance de simbolos (P(X=0)={px0_txt:.4f}, P(X=1)={px1_txt:.4f}),")
        print(f"     por lo que H(Y) < 1 e I(X;Y) = {im_txt['i_xy']:.6f} < C.")
        print("\n2. ¿Que caracteristica deberia tener la trama para que I(X;Y) sea igual a C?")
        print("   - La trama de entrada debe ser EQUIPROBABLE, es decir: P(X=0) = P(X=1) = 0.5.")
        print("   - Esto maximiza la entropia de salida a su cota superior H(Y) = 1 bit,")
        print("     haciendo que I(X;Y) = H(Y) - H(p) = 1 - H(p) = C.")
        print("=" * 70)

        # Enviar mensaje de finalización al servidor
        enviar_mensaje(sock, "SALIR")
        print("\n[+] Sesion finalizada con el servidor correctamente.")

    except (ConnectionError, OSError) as err:
        print(f"\n[ERROR] Error de comunicacion durante la sesion: {err}")
    finally:
        sock.close()
        print("[+] Socket cerrado.")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else HOST_DEFECTO
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else PUERTO_DEFECTO
    ejecutar_cliente(host, puerto)
