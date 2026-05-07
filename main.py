import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Control de Presupuesto - Fundación Masaveu", page_icon="💰")

st.title("📦 Seguimiento de Albaranes y Presupuesto")
st.markdown("Introduzca los datos del albarán recibido en obra.")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULARIO DE ENTRADA ---
with st.form(key="presupuesto_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        n_albaran = st.text_input("Número de Albarán*")
        fecha = st.date_input("Fecha", datetime.now())
        trabajador = st.selectbox("Trabajador", ["Juan Pérez", "Ana García", "Carlos Rodríguez"])
    
    with col2:
        partida = st.selectbox("Partida Presupuestaria", [
            "Cimentación", 
            "Estructura", 
            "Instalaciones", 
            "Acabados",
            "Maquinaria"
        ])
        gasto = st.number_input("Gastos de esta partida (€)", min_value=0.0, step=0.01)
    
    comentarios = st.text_area("Comentarios")
    
    submit_button = st.form_submit_button(label="Registrar Albarán")

    if submit_button:
        if not n_albaran:
            st.error("El número de albarán es obligatorio")
        else:
            # Crear un nuevo registro
            nuevo_albaran = pd.DataFrame([{
                "n_albaran": n_albaran,
                "fecha": str(fecha),
                "trabajador": trabajador,
                "partida": partida,
                "gasto": gasto,
                "comentarios": comentarios
            }])
            
            # Obtener datos existentes y añadir el nuevo
            data_existente = conn.read(worksheet="Sheet1")
            updated_df = pd.concat([data_existente, nuevo_albaran], ignore_index=True)
            
            # Actualizar Google Sheets
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success(f"Albarán {n_albaran} registrado correctamente en el presupuesto.")
            st.balloons()

# --- VISUALIZACIÓN ---
if st.checkbox("Mostrar histórico de gastos"):
    df_visualizar = conn.read(worksheet="Sheet1")
    st.dataframe(df_visualizar)
    
    # Resumen por partida
    st.subheader("Gasto acumulado por Partida")
    resumen = df_visualizar.groupby("partida")["gasto"].sum()
    st.bar_chart(resumen)
