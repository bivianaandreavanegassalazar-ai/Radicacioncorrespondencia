##importamos las librerias necesarias#
import streamlit as st
import pandas as pd
import numpy as np
from pandasql import sqldf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Radicación de Correspondencia", page_icon="📧", layout="wide")

# CSS personalizado para estilos
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Calibri:wght@400;700&display=swap');
    
    body {
        font-family: 'Calibri', sans-serif;
        background-color: #fef7e0; /* Color cálido */
        color: #5d4e37; /* Marrón cálido */
    }
    
    .title {
        font-size: 2.5em;
        font-weight: bold;
        color: #8b4513; /* Marrón oscuro */
        text-align: center;
        margin-bottom: 20px;
    }
    
    .subtitle {
        font-size: 1.5em;
        font-weight: bold;
        color: #a0522d; /* Sienna */
        margin-top: 30px;
        margin-bottom: 15px;
    }
    
    .metric-card {
        background-color: #fff8dc; /* Cornsilk */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px;
    }
    
    .stButton>button {
        background-color: #dda0dd; /* Plum */
        color: black;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-family: 'Calibri', sans-serif;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ffc0cb; /* Pink */
    }
    
    .analysis-text {
        font-size: 1.1em;
        line-height: 1.6;
        margin-top: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Vamos a crear el dataframe con los datos de la correspondencia
df_radicacion_correspondencia = pd.read_csv('BD Registros Correspondencia Bootcamp Prueba.csv', sep=';', encoding='latin-1')

# Convertir fecha_radicado a datetime
df_radicacion_correspondencia['fecha_radicado'] = pd.to_datetime(df_radicacion_correspondencia['fecha_radicado'], format='%d/%m/%Y')

# CONSULTAS CON PANDASQL

# 1. Cuántos radicados tiene el destinatario "Maria Gomez"
radicados_maria_gomez = sqldf("""
    SELECT COUNT(*) as total_radicados
    FROM df_radicacion_correspondencia
    WHERE destinatarios = 'Maria Gomez'
""")

# 2. Cuántos radicados están en estado "Finalizado"
radicados_tramite_finalizado = sqldf("""
    SELECT COUNT(*) as total_radicados_finalizados
    FROM df_radicacion_correspondencia
    WHERE estado_tramite = 'Finalizado'
""")

# 3. Cuántas demandas del remitente "Alcaldia de Yumbo" se han radicado
demandas_alcaldia_yumbo = sqldf("""
    SELECT COUNT(*) as total_demandas
    FROM df_radicacion_correspondencia
    WHERE remitente LIKE '%Alcaldia de Yumbo%'
    AND asunto = 'Demanda'
""")

# 4. Qué porcentaje corresponde la categoría "Correo" en la columna "medio_recepcion"
porcentaje_correo_recepcion = sqldf("""
    SELECT 
        medio_recepcion,
        COUNT(*) as cantidad,
        ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM df_radicacion_correspondencia)), 2) as porcentaje
    FROM df_radicacion_correspondencia
    WHERE medio_recepcion = 'Correo'
    GROUP BY medio_recepcion
""")

# 5. Del remitente "Superintendencia Financiera" cuánta correspondencia se ha recibido
correspondencia_superintendencia_financiera = sqldf("""
    SELECT COUNT(*) as total_correspondencia
    FROM df_radicacion_correspondencia
    WHERE remitente = 'Superintendencia Financiera'
""")

# Función para mostrar imágenes (simuladas con emojis ya que no tenemos archivos)
def mostrar_imagenes_inicio():
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.markdown("📧")  # Imagen de carta
    with col2:
        st.markdown("<h1 class='title'>Sistema de Radicación de Correspondencia</h1>", unsafe_allow_html=True)
    with col3:
        st.markdown("👤💻")  # Persona en computador

# Página principal
mostrar_imagenes_inicio()

# Métricas principales
st.markdown("<h2 class='subtitle'>Resumen General</h2>", unsafe_allow_html=True)

total_radicados = len(df_radicacion_correspondencia)
radicados_pendientes = len(df_radicacion_correspondencia[df_radicacion_correspondencia['estado_tramite'] == 'Pendiente'])
radicados_finalizados = len(df_radicacion_correspondencia[df_radicacion_correspondencia['estado_tramite'] == 'Finalizado'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Radicados", total_radicados)
with col2:
    st.metric("Pendientes", radicados_pendientes)
with col3:
    st.metric("Finalizados", radicados_finalizados)

# Botones para empresas
st.markdown("<h3>Distribución por Empresa</h3>", unsafe_allow_html=True)
empresas = ['Ceme', 'Concre', 'Odi']
cols = st.columns(len(empresas))
for i, empresa in enumerate(empresas):
    with cols[i]:
        count = len(df_radicacion_correspondencia[df_radicacion_correspondencia['empresa_grupo'] == empresa])
        if st.button(f"{empresa}: {count} radicados"):
            st.write(f"Detalles de {empresa}: {count} radicados")

# Diagrama de pastel para asuntos
st.markdown("<h3>Distribución por Asunto</h3>", unsafe_allow_html=True)
asuntos_count = df_radicacion_correspondencia['asunto'].value_counts().reset_index()
asuntos_count.columns = ['Asunto', 'Cantidad']
fig_asuntos = px.pie(asuntos_count, values='Cantidad', names='Asunto', title='Asuntos de Correspondencia',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig_asuntos)

# Selector de rango de fechas
st.markdown("<h3>Filtrar por Rango de Fechas</h3>", unsafe_allow_html=True)
fecha_min = df_radicacion_correspondencia['fecha_radicado'].min().date()
fecha_max = df_radicacion_correspondencia['fecha_radicado'].max().date()
rango_fechas = st.slider("Selecciona el rango de fechas:", min_value=fecha_min, max_value=fecha_max, value=(fecha_min, fecha_max))
df_filtrado = df_radicacion_correspondencia[(df_radicacion_correspondencia['fecha_radicado'].dt.date >= rango_fechas[0]) & (df_radicacion_correspondencia['fecha_radicado'].dt.date <= rango_fechas[1])]
st.write(f"Radicados en el rango seleccionado: {len(df_filtrado)}")

# Texto descriptivo del porcentaje de correos
porcentaje_correo = porcentaje_correo_recepcion['porcentaje'].iloc[0] if not porcentaje_correo_recepcion.empty else 0
if st.button(f"Porcentaje de Correos: {porcentaje_correo}%"):
    st.write(f"El {porcentaje_correo}% de la correspondencia se recibe por correo, lo que representa la mayoría de los medios de recepción.")

# Sección de consultas específicas
st.markdown("<h2 class='subtitle'>Análisis Detallado</h2>", unsafe_allow_html=True)

# 1. Gráfico de barras para radicados de Maria Gomez vs otros
st.markdown("<h3>1. Radicados por Destinatario</h3>", unsafe_allow_html=True)
destinatarios_count = df_radicacion_correspondencia['destinatarios'].value_counts().reset_index()
destinatarios_count.columns = ['Destinatario', 'Cantidad']
fig_destinatarios = px.bar(destinatarios_count, x='Destinatario', y='Cantidad', title='Radicados por Destinatario')
st.plotly_chart(fig_destinatarios)
st.markdown("<p class='analysis-text'>María Gómez tiene el mayor número de radicados, lo que indica que es un destinatario frecuente. Esto podría requerir atención especial en la gestión de su correspondencia.</p>", unsafe_allow_html=True)

# 2. Tarjeta para radicados finalizados
st.markdown("<h3>2. Estado de Trámites Finalizados</h3>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("✅")  # Imagen de verificado
with col2:
    st.markdown(f"<div class='metric-card'><h4>{radicados_tramite_finalizado['total_radicados_finalizados'].iloc[0]} Radicados Finalizados</h4></div>", unsafe_allow_html=True)
st.markdown("<p class='analysis-text'>Con {radicados_finalizados} trámites finalizados de un total de {total_radicados}, se observa que el {round(radicados_finalizados/total_radicados*100, 2)}% de los procesos están completos. Sin embargo, aún quedan {radicados_pendientes} pendientes, lo que sugiere la necesidad de acelerar los procesos de tramitación para mejorar la eficiencia.</p>", unsafe_allow_html=True)

# 3. Diagrama de pastel para demandas de Alcaldia de Yumbo
st.markdown("<h3>3. Demandas de Alcaldia de Yumbo</h3>", unsafe_allow_html=True)
demandas_count = sqldf("""
    SELECT remitente, COUNT(*) as cantidad
    FROM df_radicacion_correspondencia
    WHERE asunto = 'Demanda'
    GROUP BY remitente
""")
fig_demandas = px.pie(demandas_count, values='cantidad', names='remitente', title='Distribución General de Demandas')
st.plotly_chart(fig_demandas)
st.markdown("<p class='analysis-text'>La Alcaldia de Yumbo ha presentado {demandas_alcaldia_yumbo['total_demandas'].iloc[0]} demandas, representando una porción significativa de las demandas totales. Esto indica una actividad considerable en asuntos legales relacionados con esta entidad.</p>", unsafe_allow_html=True)

# 4. Barra horizontal para porcentaje de correo
st.markdown("<h3>4. Porcentaje de Recepción por Correo</h3>", unsafe_allow_html=True)
fig_correo = go.Figure(go.Bar(
    x=[porcentaje_correo],
    y=['Correo'],
    orientation='h',
    marker=dict(color='#dda0dd')
))
fig_correo.update_layout(title='Porcentaje de Recepción por Correo', xaxis_title='Porcentaje (%)', yaxis_title='')
st.plotly_chart(fig_correo)
st.markdown("<p class='analysis-text'>El {porcentaje_correo}% de la correspondencia se recibe por correo, lo que destaca la importancia de este medio de recepción. Una alta dependencia del correo postal podría indicar oportunidades para digitalizar más procesos.</p>", unsafe_allow_html=True)

# 5. Gráfico para Superintendencia Financiera (usando gauge)
st.markdown("<h3>5. Correspondencia de Superintendencia Financiera</h3>", unsafe_allow_html=True)
total_super = correspondencia_superintendencia_financiera['total_correspondencia'].iloc[0]
fig_super = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_super,
    title={'text': "Correspondencia Recibida"},
    gauge={'axis': {'range': [None, total_radicados]},
           'bar': {'color': "#dda0dd"},
           'steps': [
               {'range': [0, total_radicados//3], 'color': "#fff8dc"},
               {'range': [total_radicados//3, 2*total_radicados//3], 'color': "#fef7e0"},
               {'range': [2*total_radicados//3, total_radicados], 'color': "#f5deb3"}
           ]}
))
st.plotly_chart(fig_super)
st.markdown("<p class='analysis-text'>La Superintendencia Financiera ha enviado {total_super} correspondencias, lo que representa el {round(total_super/total_radicados*100, 2)}% del total. Esta entidad es uno de los remitentes más activos, lo que sugiere una relación estrecha con la organización receptora.</p>", unsafe_allow_html=True)
