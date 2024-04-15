import csv

def leer_archivo_puc():
    puc = {}
    with open('data/PUC.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Saltar la primera fila que contiene los encabezados
        for row in reader:
            codigo = row[0]
            nombre = row[1]
            puc[codigo] = nombre
    return puc

def clasificar_codigo(codigo):
    primer_digito = int(codigo[0])
    clasificacion = {
        1: "Activo",
        2: "Pasivo",
        3: "Patrimonio",
        4: "Ingresos",
        5: "Gastos",
        6: "Costos de venta",
        7: "Costos de producción o de operación",
        8: "Cuentas de orden deudoras"
    }
    return clasificacion.get(primer_digito, "No clasificado")

def leer_csv():
    datos = []
    with open('data/Test.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Saltar la primera fila que contiene los encabezados
        for row in reader:
            datos.append(row)
    return datos


def procesar_archivo_csv():
    puc = leer_archivo_puc()
    resultado = []

    with open('data/Test.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Saltar la primera fila que contiene los encabezados
        for row in reader:
            if not all(cell == '' for cell in row):  # Verificar si la línea está vacía
                codigo_usuario = row[0]
                descripcion = row[1]

                if codigo_usuario in puc:
                    nombre_puc = puc[codigo_usuario]
                    clasificacion = clasificar_codigo(codigo_usuario)
                    resultado.append(row + [codigo_usuario, nombre_puc, clasificacion])
                else:
                    # Si no se encuentra por código, buscar por descripción
                    for codigo_puc, nombre_puc in puc.items():
                        if descripcion.lower() in nombre_puc.lower():
                            clasificacion = clasificar_codigo(codigo_puc)
                            resultado.append(row + [codigo_puc, nombre_puc, clasificacion])
                            break

    return resultado

def guardar_resultado(resultado):
    with open('output/resultado.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(resultado)


def calcular_sumatoria(clasificacion, resultado):
    sumatoria = {}
    for row in resultado:
        if row[-1] == clasificacion:
            for i in range(2, len(row) - 3):
                try:
                    valor_numerico = float(row[i].replace(',', ''))
                    sumatoria[i] = sumatoria.get(i, 0) + valor_numerico
                except ValueError:
                    pass  # Ignorar valores que no se pueden convertir a flotantes
    return sumatoria

def generar_estado_resultados(resultado):
    ingresos_operativos = 0
    gastos_operativos = 0
    costo_ventas = 0
    gastos_administracion = 0
    gastos_ventas = 0
    otros_gastos_operativos = 0
    utilidad_bruta = 0
    gastos_financieros = 0
    resultado_operativo = 0

    for row in resultado:
        clasificacion = row[-1]
        monto = row[3].replace(',', '').strip()  # Eliminar comas y espacios y verificar si está vacía
        if not monto:
            continue  # Ignorar filas sin monto

        if clasificacion == "Ingresos":
            ingresos_operativos += float(monto)
        elif clasificacion == "Gastos":
            gastos_operativos += float(monto)
        elif clasificacion == "Costos de venta":
            costo_ventas += float(monto)
        elif clasificacion == "Gastos de administración":
            gastos_administracion += float(monto)
        elif clasificacion == "Gastos de ventas":
            gastos_ventas += float(monto)
        elif clasificacion == "Otros gastos operativos":
            otros_gastos_operativos += float(monto)
        elif clasificacion == "Gastos financieros":
            gastos_financieros += float(monto)

    utilidad_bruta = ingresos_operativos - costo_ventas - gastos_administracion - gastos_ventas - otros_gastos_operativos
    resultado_operativo = utilidad_bruta - gastos_financieros

    with open('output/estado_resultados_integral.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Concepto', 'Monto'])
        writer.writerow(['Ingresos operativos', ingresos_operativos])
        writer.writerow(['Gastos operativos', gastos_operativos])
        writer.writerow(['Costo de ventas', costo_ventas])
        writer.writerow(['Gastos de administración', gastos_administracion])
        writer.writerow(['Gastos de ventas', gastos_ventas])
        writer.writerow(['Otros gastos operativos', otros_gastos_operativos])
        writer.writerow(['Utilidad bruta', utilidad_bruta])
        writer.writerow(['Gastos financieros', gastos_financieros])
        writer.writerow(['Resultado operativo', resultado_operativo])



def generar_estado_financiero(resultado):
    activo = calcular_sumatoria("Activo", resultado)
    pasivo = calcular_sumatoria("Pasivo", resultado)
    patrimonio = calcular_sumatoria("Patrimonio", resultado)

    with open('output/estado_financiero.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Clasificacion', 'Total'])
        writer.writerow(['Activo', sum(activo.values())])
        writer.writerow(['Pasivo', sum(pasivo.values())])
        writer.writerow(['Patrimonio', sum(patrimonio.values())])

def generar_estado_comparativo(datos):
    saldo_anterior = 0
    saldo_nuevo = 0

    for row in datos:
        saldo_anterior_str = row[2].replace(',', '').strip()
        saldo_nuevo_str = row[5].replace(',', '').strip()

        # Verificar que las cadenas no estén vacías antes de convertirlas a float
        if saldo_anterior_str:
            saldo_anterior += float(saldo_anterior_str)
        if saldo_nuevo_str:
            saldo_nuevo += float(saldo_nuevo_str)

    cambio_saldo = saldo_nuevo - saldo_anterior

    with open('output/estado_comparativo.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Concepto', 'SALDO ANTERIOR', 'SALDO NUEVO', 'CAMBIO'])
        writer.writerow(['', saldo_anterior, saldo_nuevo, cambio_saldo])



def main():
    resultado = procesar_archivo_csv()
    guardar_resultado(resultado)
    print("Proceso completado. Se ha generado el archivo 'resultado.csv'.")

    generar_estado_financiero(resultado)
    print("Se ha generado el estado financiero en el archivo 'estado_financiero.csv'.")

    generar_estado_resultados(resultado)
    print("Se ha generado el estado de resultados en el archivo 'estado_resultados.csv'.")
    datos=leer_csv()
    generar_estado_comparativo(datos)



if __name__ == "__main__":
    main()
