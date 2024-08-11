import requests
from bs4 import BeautifulSoup
import re
import openpyxl
from lxml import etree
import pandas as pd

# Cargar el archivo de Excel con openpyxl
archivo_excel = 'Species_URL.xlsx'
libro_excel = openpyxl.load_workbook(archivo_excel)
# o puedes seleccionar una hoja específica si lo deseas
hoja_excel = libro_excel.active

# Obtener los valores de la tabla
tabla = hoja_excel.values

# Convertir la tabla a una única lista
sp_list = [valor for fila in tabla for valor in fila]
sp_list = sp_list[1:]

# Imprimir la lista resultante
print(sp_list)

# COLORS
blue = "\33[1;36m"  # Texto azul claro
gray = "\33[0;37m"  # Texto gris
white = "\33[1;37m"  # Texto blanco


def data_sp(list, path_dest, name_archive):
    """Devuelve información de la página de especies de la UNAL"""

    # Inicializamos el diccionario de salida
    df = pd.DataFrame(columns=[
        'Name Specie',
        'Life Form',
        'threat',
        'Elevation Min (msnm)',
        'Elevation Max (msnm)',
        'Departamentos'
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
                return {"ERROR": f"{req.reason}", "status_code": f"{req.status_code}"}
            # creamos el objeto bs4 a partir del código HTML
            soup = BeautifulSoup(req.text, "html.parser")

            try:
                # Encontrar un nombre de la especie
                name_sp = soup.find("div", class_="title").text.strip()
                name_sp = re.findall(r'\b[A-Za-z|-]+\b', name_sp)

                # Tomar los dos primeros elementos
                name_sp = name_sp[:2]

                # Juntar los elementos con espacio como separador
                name_sp = [' '.join(name_sp)]

            except:
                name_sp = None

            try:
                # Encontrar hábito de la especie
                # Convertir el objeto BeautifulSoup en un objeto de árbol lxml
                html = etree.HTML(str(soup))
                # Utilizar XPath para seleccionar todas las palabras en la clase 'Hábito'
                habits = html.xpath(
                    "//div[@class='title' and text()='Hábito']/following-sibling::text()[1]")[0].strip()
                life_form = [' '.join(habits.split())]

            except:
                life_form = None

            try:
                # Encontrar el estado de evaluación de la especie
                # Utilizar XPath para seleccionar todas las palabras en la clase 'Estado Conservación'
                EC = str(html.xpath(
                    "//div[@class='title' and text()='Hábito']/following-sibling::text()[3]")[0].strip())

                categories = {
                    "extinta en estado silvestre": "EW",
                    "extinta": "EX",
                    "en peligro crítico de extinción": "CR",
                    "en peligro de extinción": "EN",
                    "vulnerable": "VU",
                    "casi amenazada": "NT",
                    "preocupación menor": "LC",
                    "datos insuficientes": "DD",
                    "no evaluada": "NE"
                }

                # Obtener la sigla de amenaza

                def sigla_uicn(diccionario, palabra):
                    p_lower = palabra.lower()
                    if p_lower in diccionario:
                        return diccionario[p_lower]

                EC_sigla = [sigla_uicn(categories, EC)]

            except:
                EC_sigla = None

            try:
                # Encontrar los rangos de elevación de la especie
                # Rango de elevación minima
                range_min = html.xpath(
                    "//div[@class='title' and text()='Elevación']/following-sibling::text()[1]")[0].strip()

                if len(range_min.split("-")) > 1:
                    min_elevation = [range_min.split("-")[0].strip()]
                else:
                    min_elevation = ['0']
            except:
                min_elevation = None

            try:
                # Encontrar los rangos de elevación de la especie
                # Rango de elevación máximo
                range_max = html.xpath(
                    "//div[@class='title' and text()='Elevación']/following-sibling::text()[1]")[0].strip()
                try:
                    max_elevation = [range_max.split(" ")[2].strip()]
                except IndexError:
                    max_elevation = [range_max.split("m")[0].strip()]

            except:
                max_elevation = None

            try:
                # Encontrar la distribución de la especie
                list_dptos = html.xpath(
                    "//div[@class='title' and text()='Elevación']/following-sibling::text()[2]")[0].strip()
                dptos = ''.join(list_dptos)
                # Eliminar los espacios sobrantes en la cadena unida
                dptos_f = [re.sub(r'\s+', ' ', dptos)]

            except:
                dptos_f = None

            # Almacenar las variables en un diccionario
            data = {
                'Name Specie': name_sp,
                'Life Form': life_form,
                'threat': EC_sigla,
                'Elevation Min (msnm)': min_elevation,
                'Elevation Max (msnm)': max_elevation,
                'Departamentos': dptos_f
            }

            # Agregar el diccionario de variables al DataFrame
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            # return df

    except TimeoutError:
        print(f"El timeout se agoto")

    # Especificar la ruta de destino del archivo Excel
    ruta_destino = path_dest + "/" + name_archive

    # Exportar el DataFrame a un archivo Excel en la ruta especificada
    # El argumento index=False evita que se escriba el índice en el archivo
    df.to_excel(ruta_destino, index=False)

    print(f"El DataFrame se ha exportado a '{ruta_destino}'")


if __name__ == '__main__':
    datos = data_sp(
        sp_list, "D:/OneDrive/01_Automatizaciones y Modelos/04_Species_COL/Scripts/Results", "DB_SpeciesUNAL_V1.0.xlsx")
    exit(0)
