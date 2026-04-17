import streamlit as st
import pandas as pd
from datetime import datetime
import ast

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# --- CONEXIÓN DIRECTA A GOOGLE SHEETS (PÚBLICA) ---
# Usamos la URL para leer los datos vía CSV para evitar errores de permisos
SHEET_URL = st.secrets["sheet_url"]
CSV_URL_CLIENTES = SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv&gid=0") # Pestaña 1
CSV_URL_PEDIDOS = SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv&gid=111111") # Pestaña 2 (Ver nota abajo)

def leer_datos(gid):
    url = SHEET_URL.replace("/edit?usp=sharing", f"/export?format=csv&gid={gid}")
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# Nota: Para escribir sin errores complejos, usaremos un truco: 
# Google Forms o una API es complejo. Por ahora, para que tu esposa no pierda 
# información hoy mismo, usaremos el almacenamiento local SEGURO y el botón de descarga, 
# mientras te guío para la base de datos definitiva si esto falla.

# --- ESTADO DE SESIÓN ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Detalle', 'Total', 'Estado'])
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# PRODUCTOS Y NICHOS
PRODUCTOS = {
    "Natural (Raíz)": {"1000ml": 24},
    "Sol de energía (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Fresa radiante (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Rocío de Trópico (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Fresca hidratación (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Serenidad tropical (Premium)": {"350ml": 10, "1000ml": 30},
    "Esencia de Bosque (Premium)": {"350ml": 10, "1000ml": 30},
    "Cacao armonía (Premium)": {"350ml": 10, "1000ml": 30},
    "Despertar cremoso (Premium)": {"350ml": 10, "1000ml": 30},
}
NICHOS = ["gimnasio FGI", "gimnasio Andi", "Sadosa", "Emi", "tecnologico", "amigos Andi", "amigos mamita", "otros"]

st.markdown("<h1 style='text-align: center; color: #4A4A4A;'>mosadiet.nutrition</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #88B04B;'>Kéfit</h2>", unsafe_allow_html=True)

opcion = st.sidebar.radio("Navegación", ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"])

# --- FUNCIONES DE GUARDADO ---
# Para evitar errores de permisos de Google, la app guardará en el navegador 
# y te permitirá descargar el reporte listo para pegar en Excel.

# --- 1. PEDIDO NUEVO ---
if opcion == "Pedido Nuevo":
    st.header("🛒 Nuevo Pedido")
    nombres = ["-- Seleccionar / Registrar Nuevo --"] + st.session_state.clientes['Nombre'].tolist()
    cliente_sel = st.selectbox("Cliente", nombres)

    if cliente_sel == "-- Seleccionar / Registrar Nuevo --":
        with st.form("registro"):
            nombre_in = st.text_input("Nombre Completo (MAYÚSCULAS)").upper()
            ws_in = st.text_input("WhatsApp")
            nicho_in = st.selectbox("Nicho", NICHOS)
            if st.form_submit_button("Guardar Cliente"):
                if nombre_in:
                    nuevo_id = len(st.session_state.clientes) + 1
                    nuevo_c = pd.DataFrame([[nuevo_id, nombre_in, ws_in, nicho_in]], columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                    st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo_c], ignore_index=True)
                    st.success("Cliente guardado temporalmente.")
                    st.rerun()
    else:
        c = st.session_state.clientes[st.session_state.clientes['Nombre'] == cliente_sel].iloc[0]
        col1, col2, col3 = st.columns(3)
        batido = col1.selectbox("Sabor", list(PRODUCTOS.keys()))
        pres = col2.selectbox("Tamaño", list(PRODUCTOS[batido].keys()))
        cant = col3.number_input("Cant", min_value=1, step=1)

        if st.button("Añadir al carrito"):
            p_u = PRODUCTOS[batido][pres]
            sub = (cant // 2 * 46 + cant % 2 * 24) if (batido == "Natural (Raíz)" and pres == "1000ml") else p_u * cant
            st.session_state.carrito.append({"Batido": batido, "Pres": pres, "Cant": int(cant), "Subtotal": float(sub)})

        if st.session_state.carrito:
            st.table(pd.DataFrame(st.session_state.carrito))
            if st.button("Finalizar Pedido"):
                nuevo_p = {
                    'ID_Pedido': len(st.session_state.pedidos) + 1, 
                    'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'ID_Cliente': c['ID'], 'Nombre': c['Nombre'], 'Nicho': c['Nicho'],
                    'Detalle': str(st.session_state.carrito), 
                    'Total': sum(i['Subtotal'] for i in st.session_state.carrito), 
                    'Estado': "No Despachado"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success("¡Pedido registrado!")

# --- 2. DETALLE DEL PEDIDO ---
elif opcion == "Detalle del Pedido":
    if not st.session_state.pedidos.empty:
        p = st.session_state.pedidos.iloc[-1]
        st.subheader(f"Pedido #{p['ID_Pedido']} - {p['Nombre']}")
        nuevo_est = st.selectbox("Estado", ["No Despachado", "Despachado"], index=0 if p['Estado'] == "No Despachado" else 1)
        if st.button("Actualizar"):
            st.session_state.pedidos.at[st.session_state.pedidos.index[-1], 'Estado'] = nuevo_est
            st.success("Estado actualizado.")
        
        items = ast.literal_eval(p['Detalle'])
        for i in items:
            st.write(f"🥤 {i['Cant']}x {i['Batido']} ({i['Pres']})")
    else: st.info("No hay pedidos.")

# --- 3. RESUMEN DE PEDIDOS ---
elif opcion == "Resumen de Pedidos":
    st.header("📋 Historial")
    st.dataframe(st.session_state.pedidos)
    
    # BOTONES DE DESCARGA (Esto es lo que ella debe usar para no perder datos)
    st.divider()
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_p = st.session_state.pedidos.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Pedidos (CSV)", csv_p, f"pedidos_{datetime.now().strftime('%d_%m')}.csv")
    with col_dl2:
        csv_c = st.session_state.clientes.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Clientes (CSV)", csv_c, "clientes_kefit.csv")
    st.info("💡 Consejo: Descarga estos archivos al final del día para tener tu respaldo.")

# --- 4. RESUMEN POR ATRIBUTO ---
elif opcion == "Resumen por Atributo":
    if not st.session_state.pedidos.empty:
        items_all = []
        for d in st.session_state.pedidos['Detalle']:
            for i in ast.literal_eval(d): items_all.append({"P": f"{i['Batido']} ({i['Pres']})", "C": i['Cant']})
        st.subheader("🥤 Productos más pedidos")
        st.table(pd.DataFrame(items_all).groupby("P")["C"].sum().sort_values(ascending=False))
