import requests
import re
from bs4 import BeautifulSoup
import openpyxl
import pandas as pd

# Cargar el archivo de Excel con openpyxl
archivo_excel = 'Names_URL.xlsx'
libro_excel = openpyxl.load_workbook(archivo_excel)
# o puedes seleccionar una hoja específica si lo deseas
hoja_excel = libro_excel.active

# Obtener los valores de la tabla
tabla = hoja_excel.values

# Convertir la tabla a una única lista
name_list = [valor for fila in tabla for valor in fila]
name_list = name_list[1:]

# Imprimir la lista resultante
print(name_list)

# COLORS
blue = "\33[1;36m"  # Texto azul claro
gray = "\33[0;37m"  # Texto gris
white = "\33[1;37m"
red = "\33[31m"
green = "\33[32m"  # Texto blanco


def data_sp(list, path_dest, name_archive):
    """Devuelve información de la página de especies de la UNAL"""

    # Inicializamos el diccionario de salida
    df = pd.DataFrame(columns=[
        'Name Specie',
        'Common Name',
        'Location'
    ])
    # Cabeceras de la petición HTTP
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    }

    try:
        # Realizamos la petición
        for item in list:
            print(f'{blue}Realizando la petición: {white}{item}{gray}')
            req = requests.get(item, headers=headers, timeout=10)
            print(f'{blue}Código de respuesta...: {white}{
                req.status_code} {req.reason}{gray}')
            # Si la petición no fue correcta, se devuelve un error
            if req.status_code != 200:
                print(f'{red}"ERROR": f"{
                    req.reason}", "status_code": f"{req.status_code}"')
                continue

            # creamos el objeto bs4 a partir del código HTML
            soup = BeautifulSoup(req.text, "html.parser")

            filtrar_existentes = soup.find(
                "div", class_="titulo-nombre").text.strip()
            clean_text = re.findall(r'[A-Za-zúÚ]+', filtrar_existentes)
            list_espacios = []
            # Iterar a través de la lista y agregar espacios a todas las palabras excepto la última
            for i in range(len(clean_text)):
                if i < len(clean_text) - 1:
                    list_espacios.append(clean_text[i] + " ")
                else:
                    list_espacios.append(clean_text[i])

            # Convertir la lista en una cadena si es necesario
            resultado = "".join(list_espacios)

            if resultado.lower() == 'búsqueda sin resultados':
                print(f'{red} La URL {item} no tiene datos')
                continue

            else:
                try:
                    # Encontrar un nombre común de la especie
                    list_commonames = [a.p.text.strip().capitalize() for a in soup.find(
                        "div", class_="listado-genero").find_all('a')]

                except:
                    list_commonames = None

                try:
                    # Encontrar los diferentes departamentos que tiene nombre común
                    dptos = soup.find("div", class_="listado-genero").find_all(
                        'p', style="border-left-width: 60px; margin-left: 30px;")
                    # Obtener el texto de estos elementos y limpiarlo
                    list_dptos = []
                    for element in dptos:
                        texto = element.get_text()
                        texto_limpio = ' '.join(texto.split())
                        list_dptos.append(texto_limpio)
                except:
                    list_dptos = None

                try:
                    name_sp = [soup.find(
                        "div", class_="titulo-nombre").text.strip().split(" (")[0]]
                    # Generar un listado con igual longitud que las otras dos cadenas
                    name_sp *= len(list_dptos)
                except:
                    name_sp = None

                # Almacenar las variables en un diccionario
                data = {
                    'Name Specie': name_sp,
                    'Common Name': list_commonames,
                    'Location': list_dptos
                }

                # Agregar el diccionario de variables al DataFrame
                df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
                # return df

    except TimeoutError:
        print(f"{white}El timeout se agoto")

    # Especificar la ruta de destino del archivo Excel
    ruta_destino = path_dest + "/" + name_archive

    # Exportar el DataFrame a un archivo Excel en la ruta especificada
    # El argumento index=False evita que se escriba el índice en el archivo
    df.to_excel(ruta_destino, index=False)

    print(f"{green}El DataFrame se ha exportado a '{ruta_destino}'")


if __name__ == '__main__':
    datos = data_sp(
        name_list, "D:/OneDrive/01_Automatizaciones y Modelos/04_Species_COL/Scripts/Results", "DB_CommonNamesUNAL_V1.0.xlsx")
    exit(0)
