import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import holidays
import unicodedata

# --- CONFIGURACIÓN ---
festivos_euskadi = holidays.Spain(subdiv='PV')
festivos_euskadi.append({"2026-08-28": "Viernes Grande Bilbao"})

st.set_page_config(
    page_title="Auditoría Acústica Bilbao - Abando", 
    page_icon="🔊",
    layout="wide"
)

SENSORES_ABANDO = {
    'BI-RUI-001': 'RODRIGUEZ ARIAS 71bis', 'BI-RUI-020': 'POZA 48', 'BI-RUI-021': 'POZA 53',
    'BI-RUI-022': 'POZA 30', 'BI-RUI-025': 'PRINCIPE 1', 'BI-RUI-BR15': 'ALAMEDA URQUIJO',
    'BI-RUI-BR2': 'FRENTE IGLESIA', 'BI-RUI-C001': 'URIBITARTE 1', 'BI-RUI-C002': 'URIBITARTE 6',
    'BI-RUI-C003': 'MUELLE RIPA', 'BI-RUI-C004': 'ESCALINATAS DE URIBITARTE', 'BI-RUI-C008': 'RIPA 5',
    'BI-RUI-C010': 'ARBOLANTXA', 'BI-RUI-C011': 'JARDINES DE ALBIA', 'BI-RUI-C012': 'IBAÑEZ DE BILBAO',
    'BI-RUI-C013': 'COLÓN DE LARREÁTEGUI', 'BI-RUI-C014': 'IPARRAGUIRRE 16', 'BI-RUI-C015': 'JUAN DE AJURIAGUERRA',
    'BI-RUI-C016': 'DIPUTACIÓN 4', 'BI-RUI-C017': 'BERASTEGUI 4', 'BI-RUI-C018': 'LEDESMA 6',
    'BI-RUI-C019': 'LEDESMA 7', 'BI-RUI-C020': 'LEDESMA 10 bis', 'BI-RUI-C021': 'LEDESMA 30',
    'BI-RUI-C022': 'VILLARIAS 2', 'BI-RUI-C025': 'LUIS BRIÑAS', 'BI-RUI-C030': 'EGAÑA KALEA 6',
    'BI-RUI-C031': 'EGAÑA KALEA 2', 'BI-RUI-C032': 'PARTICULAR INDAUTXU', 'BI-RUI-C033': 'MAESTRO GARCÍA RIVERO',
    'BI-RUI-C034': 'ARETXABALETA 6', 'BI-RUI-P009': 'ALAMEDA RECALDE'
}

COLORES_ESTADO = {
    'Óptimos': '#2ecc71', 'Regulares': '#f1c40f', 'Malos': '#e67e22', 'Sin Datos': '#95a5a6'
}

# --- FUNCIONES DE APOYO ---
def clasificar_periodo(dt):
    return "DIA" if 7 <= dt.hour < 23 else "NOCHE"

def es_dia_especial(dt):
    fecha_hoy = dt.date()
    fecha_manana = fecha_hoy + timedelta(days=1)
    if fecha_hoy in festivos_euskadi or fecha_manana in festivos_euskadi or dt.weekday() in [4, 5, 6]:
        return True
    return False
# --- MOTOR GRÁFICO ---
def aplicar_estetica_ejes(ax, titulo, f_ini, f_fin, ylabel="dB(A)"):
    ax.set_title(titulo, fontsize=10, fontweight='bold', pad=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_ylim(30, 95)
    ax.set_xlim(f_ini, f_fin)
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.tick_params(labelsize=8)

def sombrear_especiales(ax, f_ini, f_fin):
    """Dibuja las franjas grises en findes y festivos."""
    curr = f_ini.replace(hour=0, minute=0, second=0, microsecond=0)
    while curr <= f_fin:
        if es_dia_especial(curr):
            ax.axvspan(curr, curr + timedelta(days=1), color='gray', alpha=0.1)
        curr += timedelta(days=1)

def generar_grafico_unificado(df_sel, f_ini, f_fin):
    fig, ax = plt.subplots(figsize=(12, 5))
    df_p = df_sel.sort_values('FECHA_DT')
    
    # Sombreado de fondos
    sombrear_especiales(ax, f_ini, f_fin)
    
    if not df_p.empty:
        tiempos = df_p['FECHA_DT'].values
        valores = df_p['DECIBELIOS'].values
        periodos = df_p['PERIODO'].values
        
        # Dibujo por segmentos para evitar líneas locas y poner colores
        for i in range(len(tiempos) - 1):
            t1, t2 = tiempos[i], tiempos[i+1]
            v1, v2 = valores[i], valores[i+1]
            p1 = periodos[i]
            
            diff = (t2 - t1).astype('timedelta64[m]').astype(int)
            
            if diff <= 20: # Si hay hueco de más de 20min, no dibuja línea
                color = '#e67e22' if p1 == "DIA" else '#2980b9'
                ax.plot([t1, t2], [v1, v2], color=color, linewidth=1.2, alpha=0.8)
    
    # Leyendas y límites
    ax.plot([], [], color='#e67e22', label="Nivel Día")
    ax.plot([], [], color='#2980b9', label="Nivel Noche")
    ax.axhline(65, color='red', linestyle='--', linewidth=0.8, alpha=0.5, label="Límite Día (65dB)")
    ax.axhline(55, color='darkblue', linestyle='--', linewidth=0.8, alpha=0.5, label="Límite Noche (55dB)")
    
    aplicar_estetica_ejes(ax, "Evolución Acústica 24h", f_ini, f_fin)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
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
            if diff > 25:
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

    try:
        # 1. Carga de datos
        df_all = pd.read_csv("datos_sonometros.csv", sep=None, engine='python', encoding='utf-8-sig')
        
        # 2. Identificación de columnas
        col_fecha = next(c for c in df_all.columns if 'FECHA' in c.upper())
        c_id = next(c for c in df_all.columns if any(x in c.upper() for x in ['CODIGO', 'ID', 'EXPEDIENTE']))
        col_ruido = next(c for c in df_all.columns if any(x in c.upper() for x in ['DECIBEL', 'VALOR', 'LAEQ']))
        
        # 3. Limpieza
        df_all['FECHA_DT'] = pd.to_datetime(df_all[col_fecha], errors='coerce')
        df_all['DECIBELIOS'] = pd.to_numeric(df_all[col_ruido].astype(str).str.replace(',', '.'), errors='coerce')
        df_all = df_all.dropna(subset=['FECHA_DT', 'DECIBELIOS'])
        df_all['PERIODO'] = df_all['FECHA_DT'].apply(clasificar_periodo)
        
        # 4. Filtro lateral
        f_min, f_max = df_all['FECHA_DT'].min(), df_all['FECHA_DT'].max()
        st.sidebar.header("🗓️ Filtro Temporal")
        rango = st.sidebar.date_input("Selecciona rango:", value=(f_min.date(), f_max.date()), min_value=f_min.date(), max_value=f_max.date())
        
        if isinstance(rango, tuple) and len(rango) == 2:
            # Inicio: El mayor entre lo seleccionado y el primer dato que tenemos
            sel_ini = pd.to_datetime(rango[0])
            f_ini_dt = max(sel_ini, f_min) 
            
            # Fin: El menor entre el final del día seleccionado y el momento actual (ahora)
            sel_fin = pd.to_datetime(rango[1]).replace(hour=23, minute=59, second=59)
            ahora = datetime.now()
            f_fin_dt = min(sel_fin, ahora)
            
            df_f = df_all[(df_all['FECHA_DT'] >= f_ini_dt) & (df_all['FECHA_DT'] <= f_fin_dt)]
        else:
            df_f = df_all
            f_ini_dt, f_fin_dt = f_min, f_max      
  # --- PESTAÑAS ---
        tabs = st.tabs(["📊 Integridad", "📈 Gráficos", "🚩 Máximos"])

        with tabs[0]:
            st.subheader("Control de Calidad y Salud de la Red")
            
            # 1. CÁLCULO PRECISO DE EXPECTATIVAS
            # Calculamos las horas totales entre el inicio y el fin seleccionado
            horas_totales = (f_fin_dt - f_ini_dt).total_seconds() / 3600
            # Cada hora debe tener 4 lecturas (una cada 15 min)
            esperados_total = int(horas_totales * 4)
            
            st.caption(f"Análisis desde {f_ini_dt.strftime('%d/%m %H:%M')} hasta {f_fin_dt.strftime('%d/%m %H:%M')} ({int(horas_totales)} horas evaluadas)")
            
            salud_stats = {'Óptimos': 0, 'Regulares': 0, 'Malos': 0, 'Sin Datos': 0}
            cobertura_data = []
            
            for sid, calle in SENSORES_ABANDO.items():
                df_sensor = df_f[df_f[c_id] == sid]
                actual = len(df_sensor)
                
                # Cálculo de cobertura real basado en el tiempo exacto transcurrido
                pct = min((actual / esperados_total) * 100, 100.0) if esperados_total > 0 else 0
                
                # Clasificación de salud
                if pct > 90: estado = 'Óptimos'
                elif pct > 50: estado = 'Regulares'
                elif pct > 0: estado = 'Malos'
                else: estado = 'Sin Datos'
                
                salud_stats[estado] += 1
                
                # Datos extra: ¿Cuántos hay de día y cuántos de noche?
                lecturas_dia = len(df_sensor[df_sensor['PERIODO'] == 'DIA'])
                lecturas_noche = len(df_sensor[df_sensor['PERIODO'] == 'NOCHE'])
                
                cobertura_data.append({
                    'Calle': calle, 
                    'Cobertura %': pct, 
                    'Día': lecturas_dia,
                    'Noche': lecturas_noche,
                    'Color': COLORES_ESTADO[estado]
                })

            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("**Distribución de Calidad**")
                fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
                labels = [k for k, v in salud_stats.items() if v > 0]
                values = [v for k, v in salud_stats.items() if v > 0]
                ax_pie.pie(values, labels=labels, autopct='%1.1f%%', colors=[COLORES_ESTADO[l] for l in labels], startangle=90)
                st.pyplot(fig_pie)

            with col2:
                st.write("**Ranking de Integridad por Sensor**")
                df_cob = pd.DataFrame(cobertura_data).sort_values('Cobertura %', ascending=True)
                
                # Mostramos una tabla detallada para ver el desglose
                st.dataframe(
                    df_cob[['Calle', 'Cobertura %', 'Día', 'Noche']].sort_values('Cobertura %', ascending=False),
                    hide_index=True, use_container_width=True
                )
                
                # Gráfico de barras de cobertura
                fig_bar, ax_bar = plt.subplots(figsize=(10, 8))
                ax_bar.barh(df_cob['Calle'], df_cob['Cobertura %'], color=df_cob['Color'])
                ax_bar.set_xlim(0, 105)
                ax_bar.set_xlabel("Integridad del flujo de datos (%)")
                st.pyplot(fig_bar)      
        with tabs[1]:
            sensores_con_datos = df_f[c_id].unique()
            opciones_sensor = [sid for sid in SENSORES_ABANDO.keys() if sid in sensores_con_datos]
            if opciones_sensor:
                sel_id = st.selectbox("Seleccionar Sensor:", opciones_sensor, format_func=lambda x: f"{SENSORES_ABANDO[x]} ({x})")
                df_s = df_f[df_f[c_id] == sel_id]
                st.markdown(f"### Ubicación: {SENSORES_ABANDO[sel_id]}")
                delta_dias = (f_fin_dt - f_ini_dt).days
                if delta_dias < 7:
                    st.info("Visualización Unificada: Día (Naranja), Noche (Azul).")
                    fig_uni = generar_grafico_unificado(df_s, f_ini_dt, f_fin_dt)
                    if fig_uni: st.pyplot(fig_uni)
                else:
                    st.info("Visualización por Periodos: Día y Noche independientes con misma escala.")
                    fig_day = generar_grafico_periodo(df_s, "DIA", "#e67e22", 65, f_ini_dt, f_fin_dt)
                    if fig_day: st.pyplot(fig_day)
                    fig_night = generar_grafico_periodo(df_s, "NOCHE", "#2980b9", 55, f_ini_dt, f_fin_dt)
                    if fig_night: st.pyplot(fig_night)
            else:
    
                    st.warning("No hay datos para el rango seleccionado.")      
        with tabs[2]:
            st.subheader("Top 5 Impactos Críticos")
            
            # Creamos la copia
            df_rank = df_f.copy()
            
            # CORRECCIÓN DEL ERROR: Usamos .astype(str) y luego .str.upper()
            # Esto evita el error "'Series' object has no attribute 'upper'"
            df_rank[c_id] = df_rank[c_id].astype(str).str.strip().str.upper()
            
            # Mapeamos la ubicación
            df_rank['Ubicación'] = df_rank[c_id].map(SENSORES_ABANDO)
            
            # Si no está en el diccionario, ponemos el ID original para que no salga "None"
            df_rank['Ubicación'] = df_rank['Ubicación'].fillna(df_rank[c_id])
            
            # Formateamos la fecha para la tabla
            df_rank['Instante'] = df_rank['FECHA_DT'].dt.strftime('%d/%m %H:%M')
            
            def get_top_5(data):
                if data.empty: 
                    return pd.DataFrame(columns=['Ubicación', 'DECIBELIOS', 'Instante'])
                # Ordenar por ruido y quitar duplicados de sensor
                return data.sort_values('DECIBELIOS', ascending=False)\
                           .drop_duplicates(subset=[c_id])\
                           .head(5)[['Ubicación', 'DECIBELIOS', 'Instante']]
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("☀️ Día")
                df_dia = get_top_5(df_rank[df_rank['PERIODO'] == "DIA"])
                st.dataframe(df_dia, use_container_width=True, hide_index=True)
            with c2:
                st.write("🌙 Noche")
                df_noche = get_top_5(df_rank[df_rank['PERIODO'] == "NOCHE"])
                st.dataframe(df_noche, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Asegúrate de que el archivo 'datos_sonometros.csv' esté en la misma carpeta.")

if __name__ == "__main__":
    main()     
        