"""
Ejercicio 7 - Validador de CUIT/CUIL

Teoría de la Información - Práctico en máquina 1

Figueroa - Rios - Zalazar

Este programa valida un número de CUIT/CUIL utilizando el algoritmo
de Módulo 11. El programa recibe el número ingresado, elimina
caracteres no numéricos y verifica que contenga exactamente 11 dígitos.

Para obtener el dígito verificador se toman los primeros 10 dígitos
y se multiplican por los pesos oficiales:

    Pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

Luego se calcula la suma ponderada y su resto al dividir por 11:

    resto = Suma Ponderada % 11

El dígito verificador esperado se obtiene mediante:

    DV = 11 - resto

con los casos especiales:

    Si resto = 0, el DV es 0.

    Si resto = 1, el DV no puede determinarse mediante este algoritmo
    para los prefijos contemplados por el programa.

Finalmente, el dígito verificador calculado se compara con el
décimo primer dígito ingresado para determinar si el CUIT/CUIL
es válido o inválido.

El programa además muestra el desglose del cálculo realizado,
incluyendo los dígitos, pesos, productos ponderados, suma,
resto modular y dígitos verificador esperado e ingresado.
"""



def validar_cuit(cuit_ingresado: str):
    # 1. Limpieza de caracteres no numéricos (guiones, espacios, puntos)
    digitos = [c for c in cuit_ingresado if c.isdigit()]
    
    if len(digitos) != 11:
        return False, "Error: Debe ingresar exactamente 11 dígitos numéricos.", {}

    # Convertir a lista de enteros
    d = [int(x) for x in digitos]
    
    # 2. Separar los primeros 10 dígitos del dígito verificador ingresado
    primeros_10 = d[:10]
    dv_ingresado = d[10]
    
    # 3. Vector de ponderación oficial
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    # Cálculo de la suma ponderada
    productos = [num * peso for num, peso in zip(primeros_10, pesos)]
    suma_ponderada = sum(productos)
    resto = suma_ponderada % 11
    
    # 4. Cálculo del Dígito Verificador esperado
    if resto == 0:
        dv_esperado = 0
    elif resto == 1:
        # Caso especial AFIP: 11 - 1 = 10 (requiere cambio de prefijo a 23/24)
        dv_esperado = None
    else:
        dv_esperado = 11 - resto

    # 5. Comparación
    es_valido = (dv_esperado is not None) and (dv_esperado == dv_ingresado)
    
    detalles = {
        "primeros_10": primeros_10,
        "pesos": pesos,
        "productos": productos,
        "suma": suma_ponderada,
        "resto": resto,
        "dv_esperado": dv_esperado,
        "dv_ingresado": dv_ingresado
    }
    
    return es_valido, "OK", detalles


def main():
    print("=" * 60)
    print("  VALIDADOR DE CUIT / CUIL (Algoritmo Módulo 11)")
    print("=" * 60)
    
    cuit_usuario = input("Ingrese el número de CUIT/CUIL (ej: 20-38441703-6 o 20384417036): ").strip()
    
    es_valido, mensaje, det = validar_cuit(cuit_usuario)
    
    if mensaje != "OK":
        print(f"\n[!] {mensaje}")
        return
    
    print("\n--- Desglose del Cálculo ---")
    print(f"Dígitos de información : {det['primeros_10']}")
    print(f"Pesos aplicados        : {det['pesos']}")
    print(f"Productos ponderados   : {det['productos']}")
    print(f"Suma acumulada (S)     : {det['suma']}")
    print(f"Resto modular (S % 11) : {det['resto']}")
    
    if det['dv_esperado'] is None:
        print("Dígito esperado        : Indefinido (Resto 1 genera DV 10, prefijo no admitido)")
    else:
        print(f"Dígito esperado (DV)   : {det['dv_esperado']}")
        
    print(f"Dígito ingresado (d11) : {det['dv_ingresado']}")
    print("-" * 60)
    
    if es_valido:
        print("RESULTADO: >> VÁLIDO << (El dígito verificador coincide)")
    else:
        print("RESULTADO: >> INVÁLIDO << (Dígito verificador incorrecto o alteración en los datos)")
    print("=" * 60)


if __name__ == "__main__":
    main()