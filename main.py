import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Seguimiento de Presupuesto", layout="centered")

st.title("🏗️ Seguimiento de Presupuesto de Obra")
st.markdown("Introduce los datos del albarán para actualizar el presupuesto.")

# 1. Conexión con Google Sheets
# Nota: Los errores previos ocurrían porque 'spreadsheet' no estaba definido en Secrets.
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Función para leer datos de forma segura
def cargar_datos():
    try:
        # Intentamos leer la hoja "Sheet1" (asegúrate que se llame así en tu Excel)
        return conn.read(worksheet="Sheet1", ttl="0")
    except Exception as e:
        # Si la hoja está vacía o no existe, creamos un DataFrame con las columnas necesarias
        return pd.DataFrame(columns=[
            "Numero_Albaran", "Fecha", "Trabajador", "Partida", "Gastos", "Comentarios"
        ])

data = cargar_datos()

# 3. Formulario de entrada de datos
with st.form(key="presupuesto_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        n_albaran = st.text_input("Número de Albarán*")
        fecha = st.date_input("Fecha")
        trabajador = st.text_input("Trabajador*")
    
    with col2:
        # Partidas personalizables
        partida = st.selectbox("Partida asociada", [
            "Cimentación", 
            "Estructura", 
            "Instalaciones", 
            "Acabados", 
            "Mano de Obra", 
            "Maquinaria",
            "Otros"
        ])
        gastos = st.number_input("Gastos del albarán (€)", min_value=0.0, step=0.01, format="%.2f")
    
    comentarios = st.text_area("Comentarios")
    
    submit_button = st.form_submit_button(label="Registrar Albarán")

# 4. Lógica para guardar datos
if submit_button:
    if not n_albaran or not trabajador:
        st.error("⚠️ Por favor, rellena los campos obligatorios (Albarán y Trabajador).")
    else:
        try:
            # Crear la nueva fila de datos
            nueva_fila = pd.DataFrame([{
                "Numero_Albaran": n_albaran,
                "Fecha": str(fecha),
                "Trabajador": trabajador,
                "Partida": partida,
                "Gastos": gastos,
                "Comentarios": comentarios
            }])
            
            # Unir con los datos existentes
            updated_df = pd.concat([data, nueva_fila], ignore_index=True)
            
            # Subir a Google Sheets
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success("✅ ¡Datos guardados correctamente en Google Sheets!")
            # Forzar recarga de los datos mostrados
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")

# 5. Visualización del histórico y resumen
st.divider()
st.subheader("📊 Histórico de Gastos")

if not data.empty:
    # Mostrar tabla
    st.dataframe(data, use_container_width=True)
    
    # Mostrar total acumulado
    total = data["Gastos"].astype(float).sum()
    st.metric("Gasto Total Acumulado", f"{total:,.2f} €")
else:
    st.info("Aún no hay registros en la base de datos.")
