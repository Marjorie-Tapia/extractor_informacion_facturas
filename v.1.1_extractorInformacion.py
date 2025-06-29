import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import zipfile
import tempfile
import os
from io import BytesIO

st.set_page_config(page_title="Procesador XML a Excel", layout="centered")

st.title("📁 Procesador de XML a Excel")
st.write("Sube un archivo `.zip` con tus archivos XML y descarga la tabla procesada.")

uploaded_file = st.file_uploader("Sube tu archivo .zip", type=["zip"])

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "archivos.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        archivos_xml = [f for f in os.listdir(temp_dir) if f.endswith(".xml")]
        data_total = []

        for archivo in archivos_xml:
            ruta_archivo = os.path.join(temp_dir, archivo)
            with open(ruta_archivo, "r") as f:
                contenido = f.read()

            soup = BeautifulSoup(contenido, "xml")
            envio = soup.find("EnvioDTE")
            if envio is None:
                continue

            folio = int(envio.find("Folio").text) if envio.find("Folio") else None
            tipo_dte = int(envio.find("TipoDTE").text) if envio.find("TipoDTE") else None
            fecha = envio.find("TmstFirmaEnv").text if envio.find("TmstFirmaEnv") else None
            despacho = int(envio.find("TipoDespacho").text) if envio.find("TipoDespacho") else None

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

        if data_total:
            df = pd.DataFrame(data_total)
            df["Fecha de Emisión"] = pd.to_datetime(df["Fecha de Emisión"], errors="coerce")

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.success("✅ Procesamiento completo")

            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name="tabla_datos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No se encontraron datos válidos en los XML.")
