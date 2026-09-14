import json
import struct
import os
import random

# Definicion de los 8 campos booleanos
# 1. Estudios Primarios
# 2. Estudios Secundarios
# 3. Estudios Universitarios
# 4. Vivienda Propia
# 5. Obra Social
# 6. Trabaja
# 7. Tiene Hijos
# 8. Casado/a

def generar_personas_aleatorias(n=20):
    """Genera datos aleatorios para n personas."""
    nombres = ["Juan Perez", "Maria Lopez", "Carlos Gomez", "Ana Silva", "Luis Fernandez", 
               "Laura Martinez", "Pedro Sanchez", "Lucia Diaz", "Diego Romero", "Sofia Sosa"]
    direcciones = ["Calle 123", "Av Siempre Viva 742", "Ruta 9 km 45", "Bulevar Oronio 120", 
                   "San Martin 456", "Belgrano 789", "Corrientes 1011", "Cordoba 2022", "Mitre 3033", "Sarmiento 4044"]
    people = []
    for i in range(n):
        person = {
            "nombre": f"{random.choice(nombres)} {i}", # Aniadimos un numero para asegurar cierta unicidad
            "direccion": random.choice(direcciones),
            "dni": str(random.randint(10000000, 99999999)),
            "estudios_primarios": random.choice([True, False]),
            "estudios_secundarios": random.choice([True, False]),
            "estudios_universitarios": random.choice([True, False]),
            "vivienda_propia": random.choice([True, False]),
            "obra_social": random.choice([True, False]),
            "trabaja": random.choice([True, False]),
            "tiene_hijos": random.choice([True, False]),
            "casado": random.choice([True, False])
        }
        people.append(person)
    return people

def guardar_json(data, filename="personas.json"):
    """
    Almacena los datos en un archivo JSON (formato de longitud variable).
    Convierte los valores booleanos a cadenas de texto ("True" o "False").
    """
    almacena_datos = []
    for p in data:
        p_copy = p.copy()
        for k, v in p_copy.items():
            if isinstance(v, bool):
                p_copy[k] = str(v)
        almacena_datos.append(p_copy)
        
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(almacena_datos, f, indent=4)

def guardar_binario(data, filename="personas.bin"):
    """
    Almacena los datos en un archivo binario (formato de longitud fija).
    Empaqueta los 8 campos booleanos en 1 solo byte utilizando operadores Bitwise.
    """
    # Formato fijo (struct format):
    # - 30s: string de 30 bytes para Nombre
    # - 30s: string de 30 bytes para Direccion
    # - 10s: string de 10 bytes para DNI
    # - B:   unsigned char de 1 byte para los 8 booleanos
    # Tamanio total por registro: 71 bytes
    with open(filename, 'wb') as f:
        for p in data:
            # 1. Preparar las cadenas (ljust para rellenar con espacios y asegurar longitud fija)
            nombre_bytes = p["nombre"].ljust(30).encode('utf-8')[:30]
            direccion_bytes = p["direccion"].ljust(30).encode('utf-8')[:30]
            dni_bytes = p["dni"].ljust(10).encode('utf-8')[:10]
            
            # 2. Empaquetado Bitwise de los 8 booleanos en 1 solo byte
            # Inicializamos el byte en 0 (00000000 en binario)
            booleanos_empaquetados = 0
            
            # Usamos el operador OR bit a bit (|) y corrimiento a la izquierda (<<) 
            # para encender el bit correspondiente si la condicion es True.
            if p["estudios_primarios"]:      booleanos_empaquetados |= (1 << 7) # Bit mas significativo
            if p["estudios_secundarios"]:    booleanos_empaquetados |= (1 << 6)
            if p["estudios_universitarios"]: booleanos_empaquetados |= (1 << 5)
            if p["vivienda_propia"]:         booleanos_empaquetados |= (1 << 4)
            if p["obra_social"]:             booleanos_empaquetados |= (1 << 3)
            if p["trabaja"]:                 booleanos_empaquetados |= (1 << 2)
            if p["tiene_hijos"]:             booleanos_empaquetados |= (1 << 1)
            if p["casado"]:                  booleanos_empaquetados |= (1 << 0) # Bit menos significativo
            
            # 3. Escribir el registro binario empaquetado
            registro = struct.pack('30s 30s 10s B', nombre_bytes, direccion_bytes, dni_bytes, booleanos_empaquetados)
            f.write(registro)

def leer_json(filename="personas.json"):
    """Lee y muestra los datos del archivo JSON."""
    print(f"\n--- LEYENDO ARCHIVO JSON (LONGITUD VARIABLE): {filename} ---")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i, p in enumerate(data):
            # Imprimimos todos los campos para verificar
            print(f"[{i+1}] {p['nombre']} | {p['direccion']} | DNI: {p['dni']}")
            print(f"    Booleanos (Texto): Primarios={p['estudios_primarios']}, Trabaja={p['trabaja']}, Casado/a={p['casado']}")
            print("-" * 60)

def leer_binario(filename="personas.bin"):
    """Lee, desempaqueta con Bitwise y muestra los datos del archivo binario."""
    print(f"\n--- LEYENDO ARCHIVO BINARIO (LONGITUD FIJA): {filename} ---")
    tamanio_registro = struct.calcsize('30s 30s 10s B')
    
    with open(filename, 'rb') as f:
        i = 1
        while True:
            # Leer exactamente los bytes que corresponden a un registro
            record = f.read(tamanio_registro)
            if not record:
                break # Fin del archivo
                
            # Desempaquetar la estructura binaria
            nombre_bytes, direccion_bytes, dni_bytes, booleanos_epaquetados = struct.unpack('30s 30s 10s B', record)
            
            # Decodificar bytes a string y eliminar espacios de relleno (.strip())
            nombre = nombre_bytes.decode('utf-8').strip()
            direccion = direccion_bytes.decode('utf-8').strip()
            dni = dni_bytes.decode('utf-8').strip()
            
            # Desempaquetado Bitwise de los booleanos
            # Usamos el operador AND bit a bit (&) con una mascara para extraer el valor de un bit especifico
            estudios_primarios = bool(booleanos_epaquetados & (1 << 7))
            estudios_secundarios = bool(booleanos_epaquetados & (1 << 6))
            estudios_universitarios = bool(booleanos_epaquetados & (1 << 5))
            vivienda_propia = bool(booleanos_epaquetados & (1 << 4))
            obra_social = bool(booleanos_epaquetados & (1 << 3))
            trabaja = bool(booleanos_epaquetados & (1 << 2))
            tiene_hijos = bool(booleanos_epaquetados & (1 << 1))
            casado = bool(booleanos_epaquetados & (1 << 0))
            
            print(f"[{i}] {nombre} | {direccion} | DNI: {dni}")
            print(f"    Booleanos (Desempaquetados): Primarios={estudios_primarios}, Trabaja={trabaja}, Casado/a={casado}")
            print("-" * 60)
            i += 1

def mostrar_conclusion_teorica(json_file, bin_file):
    """Muestra la comparacion de tamanios y redacta una conclusion teorica."""
    tamanio_json = os.path.getsize(json_file)
    tamanio_binario = os.path.getsize(bin_file)
    
    print("\n" + "="*80)
    print(f"{'COMPARACION DE TAMANIOS EN DISCO':^80}")
    print("="*80)
    print(f"Tamanio archivo JSON (Longitud variable) : {tamanio_json} bytes")
    print(f"Tamanio archivo Binario (Longitud fija)  : {tamanio_binario} bytes")
    print(f"-> El archivo binario es aprox. {tamanio_json / tamanio_binario:.2f} veces mas pequenio.")
    print("="*80)
    
    print("\n" + "="*80)
    print(f"{'CONCLUSIoN TEORICA SOBRE ALTA ESCALA':^80}")
    print("="*80)
    print("1. EFICIENCIA DE ALMACENAMIENTO (STORAGE):")
    print("   En formatos de texto como JSON o CSV, almacenar booleanos como cadenas ('True'")
    print("   o 'False') desperdicia entre 4 y 5 bytes por cada valor, ademas de las")
    print("   comillas y llaves o comas necesarias. Con operadores Bitwise, comprimimos")
    print("   esos 8 campos enteros (que normalmente tomarian minimo 8 bytes en memoria")
    print("   o hasta 40 bytes en texto) en exactamente 1 unico byte de memoria.")
    print("\n2. IMPACTO EN COSTOS Y TRANSFERENCIA (I/O & NETWORK):")
    print("   En sistemas de alta escala (ej: bases de datos con cientos de millones de")
    print("   registros), esta diferencia se magnifica enormemente. Pasar de 800 bytes por")
    print("   registro (JSON con claves repetidas) a ~71 bytes por registro (Binario)")
    print("   reduce de manera drastica el costo de almacenamiento en disco, el uso de")
    print("   memoria RAM y, crucialmente, el ancho de banda necesario al transferir")
    print("   y leer datos, reduciendo cuellos de botella de I/O.")
    print("\n3. TIEMPOS DE ACCESO (O(1) vs O(N)):")
    print("   Los archivos de longitud fija permiten acceso aleatorio (Random Access) ")
    print("   extremadamente rapido. Para buscar a la persona N, solo debemos mover ")
    print("   el puntero a 'N * tamanio_registro'. En JSON/CSV de longitud variable, se ")
    print("   debe escanear el archivo secuencialmente para encontrar un registro, lo")
    print("   cual es inviable en Big Data sin usar indices adicionales.")
    print("="*80 + "\n")

def main():
    print("1. Generando datos en memoria para 20 personas...")
    datos_personas = generar_personas_aleatorias(20)
    
    archivo_json = "personas.json"
    archivo_binario = "personas.bin"
    
    print(f"2. Guardando en {archivo_json} (con booleanos en texto)...")
    guardar_json(datos_personas, archivo_json)
    
    print(f"3. Guardando en {archivo_binario} (aplicando Bitwise para empaquetar booleanos en 1 byte)...")
    guardar_binario(datos_personas, archivo_binario)
    
    # c) Conclusion teorica sobre tamanios
    mostrar_conclusion_teorica(archivo_json, archivo_binario)
    
    # d) Leer los archivos y desempaquetar
    print("\nLeyendo los archivos generados...")
    leer_json(archivo_json)
    leer_binario(archivo_binario)

if __name__ == "__main__":
    main()