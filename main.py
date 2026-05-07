import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Control de Presupuesto", layout="centered")
st.title("💰 Seguimiento de Presupuesto y Gastos")
st.write("Fundación Masaveu - Control de Albaranes")

# 2. DEFINICIÓN DE PARTIDAS (Puedes cambiarlas por las tuyas)
partidas_presupuesto = [
    "Material Eléctrico",
    "Pequeño Material (tornillería, tacos)",
    "Equipos Domóticos / Sensores",
    "Cuadros y Protecciones",
    "Herramientas y Maquinaria",
    "Gastos de Desplazamiento",
    "Otros gastos"
]

# 3. BASE DE DATOS EN SESIÓN
if 'df_presupuesto' not in st.session_state:
    st.session_state.df_presupuesto = pd.DataFrame(columns=[
        "Nº Albarán", "Fecha", "Trabajador", "Partida", "Gasto (€)", "Comentarios"
    ])

# 4. FORMULARIO DE ENTRADA
with st.form("form_presupuesto", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        n_albaran = st.text_input("Número de Albarán")
        trabajador = st.text_input("Trabajador")
    with col2:
        fecha = st.date_input("Fecha", date.today())
        gasto = st.number_input("Gastos de esa partida (€)", min_value=0.0, step=0.01)
    
    partida = st.selectbox("Partida del presupuesto asociada:", partidas_presupuesto)
    comentarios = st.text_area("Comentarios / Detalles del gasto")
    
    boton_guardar = st.form_submit_button("Registrar Gasto")

# Lógica para añadir datos
if boton_guardar:
    if n_albaran == "" or trabajador == "":
        st.error("Por favor, rellena el número de albarán y el trabajador.")
    else:
        nueva_fila = pd.DataFrame([[n_albaran, fecha, trabajador, partida, gasto, comentarios]], 
                                  columns=["Nº Albarán", "Fecha", "Trabajador", "Partida", "Gasto (€)", "Comentarios"])
        st.session_state.df_presupuesto = pd.concat([st.session_state.df_presupuesto, nueva_fila], ignore_index=True)
        st.success("Gasto registrado correctamente.")

# 5. RESUMEN Y VISUALIZACIÓN
if not st.session_state.df_presupuesto.empty:
    st.divider()
    st.subheader("Resumen de Gastos")
    
    # Mostrar total acumulado
    total_gastado = st.session_state.df_presupuesto["Gasto (€)"].sum()
    st.metric("Total Gastado Acumulado", f"{total_gastado:,.2f} €")
    
    # Tabla de datos
    st.dataframe(st.session_state.df_presupuesto)

    # Preparar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.df_presupuesto.to_excel(writer, index=False, sheet_name='Gastos')
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Descargar Control de Gastos (Excel)",
        data=excel_data,
        file_name=f"presupuesto_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 6. ENVÍO POR CORREO
    st.divider()
    if st.button("📧 Enviar Reporte de Gastos por Email"):
        try:
            emisor = st.secrets["email_emisor"]
            password = st.secrets["password_app"]
            destino = st.secrets["email_profesor"]

            msg = MIMEMultipart()
            msg['From'] = emisor
            msg['To'] = f"{destino}, {emisor}"
            msg['Subject'] = f"Control Gastos - Albarán {n_albaran} - {trabajador}"

            part = MIMEBase('application', "octet-stream")
            part.set_payload(excel_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="gastos_presupuesto.xlsx"')
            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(emisor, password)
            server.send_message(msg)
            server.quit()
            st.success("✅ Reporte de presupuesto enviado correctamente.")
        except Exception as e:
            st.error("❌ Error al enviar. Revisa los 'Secrets' en Streamlit.")
