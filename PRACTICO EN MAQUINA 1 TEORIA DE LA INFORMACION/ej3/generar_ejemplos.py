"""
Script auxiliar para generar archivos de prueba de tamaño similar (~10 KB).
  - ejemplo.txt: texto plano con contenido variado (~10 KB)
  - ejemplo.zip: archivo comprimido de tamaño similar (~10 KB)

Para que la demostración sea efectiva, el .zip se genera comprimiendo un
archivo binario grande de datos aleatorios. Dado que los datos aleatorios
son incompresibles, el .zip resultante tiene un tamaño apenas mayor que
los datos originales, pero su contenido a nivel de bytes se distribuye
de forma casi uniforme (entropía cercana a 8 bits/símbolo).
"""

import os
import zipfile
import random

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))

# ===========================================================
# 1. Generar ejemplo.txt de ~10 KB con texto variado
# ===========================================================
parrafos = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida.",
    "Donec lacinia congue felis in faucibus. Pellentesque venenatis dolor sit amet velit laoreet consequat. Praesent blandit dolor sed nunc faucibus hendrerit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.",
    "Suspendisse vel eros sagittis, hendrerit nulla at, facilisis felis. Vivamus fermentum sapien at neque eleifend, id facilisis nisi efficitur. Maecenas sodales imperdiet tortor vel aliquam. Proin euismod lacinia erat quis vehicula.",
    "Aliquam erat volutpat. Nunc fermentum tortor ac porta dapibus. In rutrum ac purus sit amet tempus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Cras id dolor eu sapien dignissim pretium.",
    "Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui.",
    "Aenean lacinia bibendum nulla sed consectetur. Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ut facilisis in, egestas eget quam. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.",
    "Sed posuere consectetur est at lobortis. Maecenas faucibus mollis interdum. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor.",
    "Praesent commodo cursus magna, vel scelerisque nisl consectetur et. Donec id elit non mi porta gravida at eget metus. Nulla vitae elit libero, a pharetra augue. Etiam vel tortor sodales tellus ultricies commodo.",
    "Nullam quis risus eget urna mollis ornare vel eu leo. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer posuere erat a ante venenatis dapibus posuere velit aliquet.",
    "Vestibulum id ligula porta felis euismod semper. Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.",
]

ruta_txt = os.path.join(DIRECTORIO, "ejemplo.txt")
with open(ruta_txt, "w", encoding="utf-8") as f:
    i = 0
    while f.tell() < 10_000:
        f.write(parrafos[i % len(parrafos)] + "\n\n")
        i += 1

tamanio_txt = os.path.getsize(ruta_txt)
print(f"Creado: ejemplo.txt ({tamanio_txt} bytes)")

# ===========================================================
# 2. Generar ejemplo.zip de tamaño similar
# ===========================================================
# Estrategia: generamos un archivo de bytes pseudoaleatorios y lo
# metemos en un ZIP. Como los datos aleatorios son prácticamente
# incompresibles, el .zip tiene un tamaño levemente mayor que los
# datos originales (por los headers del formato ZIP).
# Ajustamos el tamaño de los datos para que el .zip resultante
# sea lo más parecido posible al .txt.

ruta_zip = os.path.join(DIRECTORIO, "ejemplo.zip")
ruta_temp = os.path.join(DIRECTORIO, "_temp_random.bin")

# Los headers de ZIP agregan ~150-200 bytes, así que generamos datos
# un poco más chicos que el tamaño objetivo.
random.seed(42)  # semilla fija para reproducibilidad
tamanio_datos = tamanio_txt - 200  # estimación inicial

for intento in range(20):
    datos = bytes(random.randint(0, 255) for _ in range(tamanio_datos))
    with open(ruta_temp, "wb") as f:
        f.write(datos)

    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(ruta_temp, arcname="datos.bin")

    tamanio_zip = os.path.getsize(ruta_zip)
    diferencia = tamanio_zip - tamanio_txt

    # Si estamos dentro del 5%, aceptamos
    if abs(diferencia) < tamanio_txt * 0.05:
        break

    # Ajustar: si el zip salió muy grande, reducimos datos; si muy chico, aumentamos
    tamanio_datos -= diferencia

os.remove(ruta_temp)

print(f"Creado: ejemplo.zip ({tamanio_zip} bytes)")
print(f"\nTamaño .txt: {tamanio_txt} bytes")
print(f"Tamaño .zip: {tamanio_zip} bytes")
print(f"Diferencia:  {abs(tamanio_txt - tamanio_zip)} bytes ({abs(tamanio_txt - tamanio_zip)/tamanio_txt*100:.1f}%)")
