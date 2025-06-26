from bs4 import BeautifulSoup
import pandas as pd
import os

# 🟡 Pedir al usuario la ruta de la carpeta
carpeta = input("Ingresa la ruta completa de la carpeta con los archivos XML: ")

# Validar carpeta
if not os.path.isdir(carpeta):
    print("La ruta ingresada no es válida.")
    exit()

# Lista de archivos XML en la carpeta
archivos_xml = [f for f in os.listdir(carpeta) if f.endswith(".xml")]

# Lista para guardar todas las filas
data_total = []

# Procesar cada archivo XML
for archivo in archivos_xml:
    ruta_archivo = os.path.join(carpeta, archivo)

    with open(ruta_archivo, "r") as f:
        contenido = f.read()

    soup = BeautifulSoup(contenido, "xml")
    envio = soup.find("EnvioDTE")

    # Evitar errores si el archivo no contiene la etiqueta principal
    if envio is None:
        print(f"Archivo {archivo} omitido (no contiene <EnvioDTE>)")
        continue

    # Datos generales
    folio = int(envio.find("Folio").text) if envio.find("Folio") else None
    tipo_dte = int(envio.find("TipoDTE").text) if envio.find("TipoDTE") else None
    fecha = envio.find("TmstFirmaEnv").text if envio.find("TmstFirmaEnv") else None
    despacho = int(envio.find("TipoDespacho").text) if envio.find("TipoDespacho") else None

    # Detalles del producto
    detalles = envio.find_all("Detalle")
    for i, detalle in enumerate(detalles, start=1):
        fila = {
            "Archivo": archivo,
            "Folio": folio,
            "Tipo DTE": tipo_dte,
            "Fecha de Emisión": fecha,
            "Tipo de despacho": despacho,
            "indice_producto": int(detalle.find("NroLinDet").text) if detalle.find("NroLinDet") else i,
            "codigo": int(detalle.find("VlrCodigo").text) if detalle.find("VlrCodigo") else None,
            "nombre": detalle.find("NmbItem").text if detalle.find("NmbItem") else None,
            "precio_unitario": float(detalle.find("PrcItem").text) if detalle.find("PrcItem") else None,
            "precio_total": float(detalle.find("MontoItem").text) if detalle.find("MontoItem") else None
        }
        data_total.append(fila)

# Crear DataFrame general
df = pd.DataFrame(data_total)

# Convertir fecha a tipo datetime
df["Fecha de Emisión"] = pd.to_datetime(df["Fecha de Emisión"])

# Guardar Excel en la misma carpeta de origen
nombre_salida = "datosExtraidos.xlsx"
ruta_salida = os.path.join(carpeta, nombre_salida)
df.to_excel(ruta_salida, index=False)

print(f"\n✅ Todos los archivos fueron procesados.")
print(f"📄 Archivo Excel guardado como: {ruta_salida}")
