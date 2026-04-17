import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import ast

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes (o crear vacíos si falla)
try:
    df_clientes = conn.read(worksheet="Clientes", ttl=0)
    df_pedidos = conn.read(worksheet="Pedidos", ttl=0)
except:
    df_clientes = pd.DataFrame(columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
    df_pedidos = pd.DataFrame(columns=['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Detalle', 'Total', 'Estado'])

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

st.markdown("<h1 style='text-align: center;'>mosadiet.nutrition</h1>", unsafe_allow_html=True)

opcion = st.sidebar.radio("Navegación", ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"])

# --- 1. PEDIDO NUEVO ---
if opcion == "Pedido Nuevo":
    st.header("🛒 Nuevo Pedido")
    nombres = ["-- Seleccionar / Registrar Nuevo --"] + df_clientes['Nombre'].tolist()
    cliente_sel = st.selectbox("Cliente", nombres)

    if cliente_sel == "-- Seleccionar / Registrar Nuevo --":
        with st.form("reg"):
            nombre_in = st.text_input("Nombre Completo (MAYÚSCULAS)").upper()
            ws_in = st.text_input("WhatsApp")
            nicho_in = st.selectbox("Nicho", NICHOS)
            if st.form_submit_button("Guardar"):
                nuevo_id = len(df_clientes) + 1
                nuevo_c = pd.DataFrame([[nuevo_id, nombre_in, ws_in, nicho_in]], columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                df_actualizado = pd.concat([df_clientes, nuevo_c], ignore_index=True)
                conn.update(worksheet="Clientes", data=df_actualizado)
                st.success("Registrado. Refresca la página.")
                st.rerun()
    else:
        c = df_clientes[df_clientes['Nombre'] == cliente_sel].iloc[0]
        col1, col2, col3 = st.columns(3)
        batido = col1.selectbox("Sabor", list(PRODUCTOS.keys()))
        pres = col2.selectbox("Tamaño", list(PRODUCTOS[batido].keys()))
        cant = col3.number_input("Cant", min_value=1, step=1)

        if st.button("Añadir"):
            p_u = PRODUCTOS[batido][pres]
            sub = (cant // 2 * 46 + cant % 2 * 24) if (batido == "Natural (Raíz)" and pres == "1000ml") else p_u * cant
            st.session_state.carrito.append({"Batido": batido, "Pres": pres, "Cant": int(cant), "Subtotal": sub})

        if st.session_state.carrito:
            st.table(pd.DataFrame(st.session_state.carrito))
            if st.button("Finalizar Pedido"):
                nuevo_p = {
                    'ID_Pedido': len(df_pedidos) + 1, 'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'ID_Cliente': c['ID'], 'Nombre': c['Nombre'], 'Nicho': c['Nicho'],
                    'Detalle': str(st.session_state.carrito), 'Total': sum(i['Subtotal'] for i in st.session_state.carrito), 'Estado': "No Despachado"
                }
                df_p_act = pd.concat([df_pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                conn.update(worksheet="Pedidos", data=df_p_act)
                st.session_state.carrito = []
                st.success("Guardado en Google Sheets.")

# --- 2. DETALLE DEL PEDIDO ---
elif opcion == "Detalle del Pedido":
    if not df_pedidos.empty:
        p = df_pedidos.iloc[-1]
        st.subheader(f"Pedido #{p['ID_Pedido']} - {p['Nombre']}")
        nuevo_est = st.selectbox("Estado", ["No Despachado", "Despachado"], index=0 if p['Estado'] == "No Despachado" else 1)
        if st.button("Actualizar"):
            df_pedidos.at[df_pedidos.index[-1], 'Estado'] = nuevo_est
            conn.update(worksheet="Pedidos", data=df_pedidos)
            st.success("Actualizado")
        
        items = ast.literal_eval(p['Detalle'])
        for i in items:
            st.write(f"🥤 {i['Cant']}x {i['Batido']} ({i['Pres']})")
    else: st.info("Vacio")

# --- 3. RESUMEN DE PEDIDOS ---
elif opcion == "Resumen de Pedidos":
    st.dataframe(df_pedidos)

# --- 4. RESUMEN POR ATRIBUTO ---
elif opcion == "Resumen por Atributo":
    if not df_pedidos.empty:
        st.subheader("Ranking Productos")
        items_all = []
        for d in df_pedidos['Detalle']:
            for i in ast.literal_eval(d): items_all.append({"P": f"{i['Batido']} ({i['Pres']})", "C": i['Cant']})
        st.table(pd.DataFrame(items_all).groupby("P")["C"].sum().sort_values(ascending=False))
