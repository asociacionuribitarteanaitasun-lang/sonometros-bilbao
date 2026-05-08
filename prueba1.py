import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import holidays  # <--- Mantenla para el sombreado de fiestas

# Configuramos los festivos de España y específicamente del País Vasco
# 'PV' aplica los festivos autonómicos (como el Lunes de Pascua)
festivos_euskadi = holidays.Spain(subdiv='PV')

def es_dia_especial(fecha):
    """
    Detecta si es festivo o fin de semana.
    """
    # Si la fecha es un festivo oficial en Euskadi o es Sábado (5) o Domingo (6)
    if fecha in festivos_euskadi or fecha.weekday() >= 5:
        return True
    return False
    # Añadir un festivo local a mano si no viene en la librería
festivos_euskadi.append({"2026-08-28": "Viernes Grande Bilbao"})
# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Auditoría Acústica Bilbao - Abando", 
    page_icon="🔊",
    layout="wide"
)

# --- DICCIONARIO MAESTRO: 32 SENSORES DE ABANDO ---
SENSORES_ABANDO = {
    'BI-RUI-001': 'RODRIGUEZ ARIAS', 'BI-RUI-020': 'POZA 48', 'BI-RUI-021': 'POZA 53',
    'BI-RUI-022': 'POZA 30', 'BI-RUI-025': 'PRINCIPE 1', 'BI-RUI-BR15': 'ALAMEDA URQUIJO',
    'BI-RUI-BR2': 'FRENTE IGLESIA', 'BI-RUI-C001': 'URIBITARTE 1', 'BI-RUI-C002': 'URIBITARTE 6',
    'BI-RUI-C003': 'MUELLE RIPA', 'BI-RUI-C004': 'ESCALINATAS DE URIBITARTE', 'BI-RUI-C008': 'RIPA 5',
    'BI-RUI-C010': 'ARBOLANTXA', 'BI-RUI-C011': 'JARDINES DE ALBIA', 'BI-RUI-C012': 'IBAÑEZ DE BILBAO',
    'BI-RUI-C013': 'COLÓN DE LARREÁTEGUI', 'BI-RUI-C014': 'IPARRAGUIRRE 16', 'BI-RUI-C015': 'JUAN DE AJURIAGUERRA',
    'BI-RUI-C016': 'DIPUTACIÓN 4', 'BI-RUI-C017': 'BERASTEGUI 4', 'BI-RUI-C018': 'LEDESMA 6',
    'BI-RUI-C019': 'LEDESMA 7', 'BI-RUI-C020': 'LEDESMA 10 bis', 'BI-RUI-C021': 'LEDESMA 30',
    'BI-RUI-C022': 'VILLARIAS 2', 'BI-RUI-C025': 'LUIS BRIÑAS', 'BI-RUI-C030': 'EGAÑA KALEA 6',
    'BI-RUI-C031': 'EGAÑA KALEA 22', 'BI-RUI-C032': 'PARTICULAR INDAUTXU', 'BI-RUI-C033': 'MAESTRO GARCÍA RIVERO',
    'BI-RUI-C034': 'ARETXABALETA 6', 'BI-RUI-P009': 'ALAMEDA RECALDE'
}

COLORES_ESTADO = {
    'Óptimos': '#2ecc71', 
    'Regulares': '#f1c40f', 
    'Malos': '#e67e22', 
    'Sin Datos': '#95a5a6'
}

# --- UTILIDADES DE PROCESAMIENTO ---
def limpiar_texto(texto):
    if not isinstance(texto, str): return texto
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode("utf-8")
    return texto.strip().upper()

def clasificar_periodo(dt):
    if not isinstance(dt, datetime): return "N/A"
    return "DIA" if 7 <= dt.hour < 23 else "NOCHE"

def es_dia_especial(dt):
    """
    Detecta si es festivo, víspera de festivo o fin de semana.
    """
    # Convertimos a objeto date (solo día, sin hora)
    fecha_hoy = dt.date() if hasattr(dt, 'date') else dt
    fecha_manana = fecha_hoy + timedelta(days=1)
    
    # 1. ¿Es festivo hoy?
    if fecha_hoy in festivos_euskadi:
        return True
    
    # 2. ¿Es víspera (mañana es festivo)?
    if fecha_manana in festivos_euskadi:
        return True
    
    # 3. ¿Es fin de semana? (Viernes=4, Sábado=5, Domingo=6)
    # Incluimos el viernes porque su noche es víspera de sábado
    if dt.weekday() in [4, 5, 6]: 
        return True
        
    return False@st.cache_data(show_spinner=False)
def procesar_datos_cache(csv_content):
    try:
        df = pd.read_csv(StringIO(csv_content), sep=';', encoding='utf-8-sig')
        if len(df.columns) < 2:
            df = pd.read_csv(StringIO(csv_content), sep=',', encoding='utf-8-sig')
    except:
        df = pd.read_csv(StringIO(csv_content), sep=None, engine='python', encoding='utf-8-sig')
        
    df.columns = [limpiar_texto(c) for c in df.columns]
    c_t = next(c for c in ['FECHA/HORA MEDICION', 'HORA', 'FECHA'] if c in df.columns)
    c_v = next(c for c in ['DECIBELIOS MEDIDOS', 'LAEQ', 'DECIBELIOS'] if c in df.columns)
    c_id = next(c for c in ['CODIGO', 'ID_SONOMETRO', 'ID'] if c in df.columns)
    
    df['FECHA_DT'] = pd.to_datetime(df[c_t], errors='coerce')
    df['DECIBELIOS'] = pd.to_numeric(df[c_v].astype(str).str.replace(',', '.'), errors='coerce')
    
    df = df[df[c_id].isin(SENSORES_ABANDO.keys())]
    df = df.dropna(subset=['FECHA_DT', 'DECIBELIOS'])
    df['PERIODO'] = df['FECHA_DT'].apply(clasificar_periodo)
    
    return df.sort_values('FECHA_DT'), c_id

# --- MOTOR GRÁFICO ---
def aplicar_estetica_ejes(ax, titulo, f_ini, f_fin, ylabel="dB(A)"):
    ax.set_title(titulo, fontsize=10, fontweight='bold', pad=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_ylim(30, 95)
    ax.set_xlim(f_ini, f_fin)
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.tick_params(labelsize=8)

def sombrear_especiales(ax, f_ini, f_fin):
    curr = f_ini.replace(hour=0, minute=0, second=0, microsecond=0)
    while curr <= f_fin:
        if es_dia_especial(curr):
            ax.axvspan(curr, curr + timedelta(days=1), color='gray', alpha=0.1)
        curr += timedelta(days=1)

def generar_grafico_unificado(df_sel, f_ini, f_fin):
    fig, ax = plt.subplots(figsize=(12, 5))
    df_p = df_sel.sort_values('FECHA_DT')
    sombrear_especiales(ax, f_ini, f_fin)
    if not df_p.empty:
        tiempos = df_p['FECHA_DT'].values
        valores = df_p['DECIBELIOS'].values
        periodos = df_p['PERIODO'].values
        for i in range(len(tiempos) - 1):
            t1, t2 = tiempos[i], tiempos[i+1]
            v1, v2 = valores[i], valores[i+1]
            p1 = periodos[i]
            diff = (t2 - t1).astype('timedelta64[m]').astype(int)
            if diff <= 20:
                color = '#e67e22' if p1 == "DIA" else '#2980b9'
                ax.plot([t1, t2], [v1, v2], color=color, linewidth=1.2, alpha=0.8)
    ax.plot([], [], color='#e67e22', label="Nivel Día")
    ax.plot([], [], color='#2980b9', label="Nivel Noche")
    ax.axhline(65, color='red', linestyle='--', linewidth=0.8, alpha=0.5, label="Límite Día (65dB)")
    ax.axhline(55, color='darkblue', linestyle='--', linewidth=0.8, alpha=0.5, label="Límite Noche (55dB)")
    aplicar_estetica_ejes(ax, "Evolución Acústica 24h", f_ini, f_fin)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    ax.legend(fontsize=8, loc='upper right', ncol=2)
    plt.tight_layout()
    return fig

def generar_grafico_periodo(df_sel, periodo, color, limite, f_ini, f_fin):
    fig, ax = plt.subplots(figsize=(12, 4))
    sombrear_especiales(ax, f_ini, f_fin)
    df_p = df_sel[df_sel['PERIODO'] == periodo].copy().sort_values('FECHA_DT')
    if not df_p.empty:
        tiempos = df_p['FECHA_DT'].values
        valores = df_p['DECIBELIOS'].values
        new_tiempos, new_valores = [tiempos[0]], [valores[0]]
        for i in range(1, len(tiempos)):
            diff = (tiempos[i] - tiempos[i-1]).astype('timedelta64[m]').astype(int)
            if diff > 20:
                new_tiempos.append(tiempos[i-1] + (tiempos[i] - tiempos[i-1]) / 2)
                new_valores.append(np.nan)
            new_tiempos.append(tiempos[i])
            new_valores.append(valores[i])
        ax.plot(new_tiempos, new_valores, color=color, linewidth=1.5, alpha=0.8, label=f"Nivel {periodo}")
    ax.axhline(limite, color='red', linestyle='--', linewidth=1, alpha=0.7, label=f"Límite {limite}dB")
    aplicar_estetica_ejes(ax, f"Análisis Temporal: Periodo {periodo}", f_ini, f_fin)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.legend(fontsize=8, loc='upper right')
    plt.tight_layout()
    return fig

# --- APP PRINCIPAL ---
def main():
    st.title("🔊 Auditoría Acústica Bilbao - Distrito Abando")
    
    if 'df_master' not in st.session_state:
        st.session_state.df_master = None
        st.session_state.col_id = None

    # --- 1. CARGA CON DETECCIÓN AUTOMÁTICA ---
try:
    df_all = pd.read_csv("datos_sonometros.csv", encoding='utf-8-sig')

    # Buscamos qué columna contiene la palabra 'FECHA' (sin importar mayúsculas)
    col_fecha = None
    for col in df_all.columns:
        if 'FECHA' in col.upper():
            col_fecha = col
            break

    if col_fecha is None:
        st.error("⚠️ No se encontró ninguna columna de fecha en el archivo.")
        st.stop()

    # Convertimos la columna encontrada a formato fecha
    df_all[col_fecha] = pd.to_datetime(df_all[col_fecha])
    
    # --- 2. LÍMITES REALES ---
    f_min_real = df_all[col_fecha].min()
    f_max_real = df_all[col_fecha].max()

    # --- 3. FILTRO TEMPORAL ---
    st.sidebar.header("🗓️ Filtro Temporal")
    rango = st.sidebar.date_input(
        "Selecciona el rango:",
        value=(f_min_real.date(), f_max_real.date()),
        min_value=f_min_real.date(),
        max_value=f_max_real.date()
    )

    # --- 4. APLICAR FILTRO ---
    if isinstance(rango, tuple) and len(rango) == 2:
        f_ini, f_fin = rango
        # Usamos la columna detectada dinámicamente
        mask = (df_all[col_fecha].dt.date >= f_ini) & (df_all[col_fecha].dt.date <= f_fin)
        df_f = df_all.loc[mask]
    else:
        df_f = df_all

    st.sidebar.info(f"Última lectura: {f_max_real.strftime('%d/%m/%Y %H:%M')}")

except Exception as e:
    st.error(f"❌ Error al procesar los datos: {e}")
    st.stop()
        # --- AQUÍ ESTÁN LAS FUNCIONALIDADES QUE TE FALTABAN ---
tabs = st.tabs(["📊 Integridad de la Red", "📈 Series Temporales", "🚩 Impactos Máximos"])

with tabs[0]:
    col1, col2 = st.columns([1, 2])
    dias_total = max((f_fin - f_ini).days + 1, 1)
    esperados = dias_total * 96 
    salud_stats = {'Óptimos': 0, 'Regulares': 0, 'Malos': 0, 'Sin Datos': 0}
    cobertura_data = []
    
    for sid, calle in SENSORES_ABANDO.items():
        # Usamos c_id y col_fecha que detectamos en el bloque de carga
        actual = len(df_f[df_f[c_id] == sid])
        pct = min((actual / esperados) * 100, 100.0)
        estado = 'Óptimos' if pct > 90 else ('Regulares' if pct > 50 else ('Malos' if pct > 0 else 'Sin Datos'))
        salud_stats[estado] += 1
        cobertura_data.append({'Calle': calle, 'Cobertura %': pct, 'Color': COLORES_ESTADO[estado]})

    with col1:
        st.subheader("Estado de Integridad")
        fig_pie, ax_pie = plt.subplots()
        labels = [k for k, v in salud_stats.items() if v > 0]
        values = [v for k, v in salud_stats.items() if v > 0]
        if values:
            ax_pie.pie(values, labels=labels, autopct='%1.1f%%', colors=[COLORES_ESTADO[l] for l in labels], startangle=90)
            st.pyplot(fig_pie)

    with col2:
        st.subheader("Continuidad por Sensor")
        if cobertura_data:
            df_cob = pd.DataFrame(cobertura_data).sort_values('Cobertura %', ascending=True)
            fig_bar, ax_bar = plt.subplots(figsize=(10, 8))
            ax_bar.barh(df_cob['Calle'], df_cob['Cobertura %'], color=df_cob['Color'])
            ax_bar.set_xlabel("Cobertura (%)")
            st.pyplot(fig_bar)

with tabs[1]:
    sensores_con_datos = df_f[c_id].unique()
    opciones_sensor = [sid for sid in SENSORES_ABANDO.keys() if sid in sensores_con_datos]
    if opciones_sensor:
        sel_id = st.selectbox("Seleccionar Sensor:", opciones_sensor, format_func=lambda x: f"{SENSORES_ABANDO[x]} ({x})")
        df_s = df_f[df_f[c_id] == sel_id]
        delta_dias = (f_fin - f_ini).days
        if delta_dias < 7:
            st.pyplot(generar_grafico_unificado(df_s, f_ini_dt, f_fin_dt))
        else:
            st.pyplot(generar_grafico_periodo(df_s, "DIA", "#e67e22", 65, f_ini_dt, f_fin_dt))
            st.pyplot(generar_grafico_periodo(df_s, "NOCHE", "#2980b9", 55, f_ini_dt, f_fin_dt))

with tabs[2]:
    st.subheader("Top 5 Impactos Críticos")
    df_rank = df_f.copy()
    df_rank['Ubicación'] = df_rank[c_id].map(SENSORES_ABANDO)
    # Usamos FECHA_DT que es la columna estandarizada que creamos en la carga
    df_rank['Instante'] = df_rank['FECHA_DT'].dt.strftime('%d/%m %H:%M')
    
    def get_top_5(data):
        if data.empty: return pd.DataFrame()
        return data.sort_values('DECIBELIOS', ascending=False).drop_duplicates(subset=[c_id]).head(5)[['Ubicación', 'DECIBELIOS', 'Instante']]
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("☀️ Día")
        st.dataframe(get_top_5(df_rank[df_rank['PERIODO'] == 'DIA']), use_container_width=True, hide_index=True)
    with c2:
        st.write("🌙 Noche")
        st.dataframe(get_top_5(df_rank[df_rank['PERIODO'] == 'NOCHE']), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()