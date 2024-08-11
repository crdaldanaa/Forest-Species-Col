# Forest Species Data Colombia
Código para Scrappear los datos de cada una de las especies reportadas por el [Cátalogo de Plantas y Liquenes](http://catalogoplantasdecolombia.unal.edu.co/es/).

La base de datos resultante posee las siguientes columnas:

1. Hábito de Crecimiento
2. Distribución Geográfica (Municipios)
3. Estado de Amenaza UICN
4. Origen
5. Nombre Común
6. Nombre Cientifico

## Prerequisitos
```bash
.env/bin/activate

pip install requirements

```

## Contenido

1. <u>Info_Species</u>. Delimita el nombre común y cientifico de las especies presentes en la página
2. <u>Commonname_data.py</u>. Extrae los datos adicionales presentes en la página teniendo en cuenta cada especie y guarda el Dataframe resultante en un archivo xls