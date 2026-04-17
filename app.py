import streamlit as st
import pandas as pd
from datetime import datetime
import ast

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# --- MEMORIA DE LA APP ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Detalle', 'Total', 'Estado'])
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# PRODUCTOS Y PRECIOS
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
st.markdown("<h2 style='text-align: center; color: #88B04B;'>Kéfit</h2>", unsafe_allow_html=True)

opcion = st.sidebar.radio("Navegación", ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"])

# --- FUNCIÓN PARA LIMPIAR EL DETALLE EN LAS TABLAS ---
def formatear_detalle(detalle_str):
    try:
        lista = ast.literal_eval(detalle_str)
        return ", ".join([f"{i['Cant']}x {i['Batido']} ({i['Pres']})" for i in lista])
    except:
        return detalle_str

# --- 1. PEDIDO NUEVO ---
if opcion == "Pedido Nuevo":
    st.header("🛒 Nuevo Pedido")
    nombres = ["-- Seleccionar / Registrar Nuevo --"] + st.session_state.clientes['Nombre'].tolist()
    cliente_sel = st.selectbox("Seleccionar Cliente", nombres)

    if cliente_sel == "-- Seleccionar / Registrar Nuevo --":
        with st.form("reg_cliente"):
            st.subheader("Registrar Nuevo Cliente")
            nombre_in = st.text_input("Nombre Completo (MAYÚSCULAS)").upper()
            ws_in = st.text_input("WhatsApp")
            nicho_in = st.selectbox("Nicho", NICHOS)
            if st.form_submit_button("Guardar Cliente"):
                if nombre_in:
                    nuevo_id = len(st.session_state.clientes) + 1
                    nuevo_c = pd.DataFrame([[nuevo_id, nombre_in, ws_in, nicho_in]], columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                    st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo_c], ignore_index=True)
                    st.rerun()
    else:
        c = st.session_state.clientes[st.session_state.clientes['Nombre'] == cliente_sel].iloc[0]
        st.success(f"Cliente: {c['Nombre']} | Nicho: {c['Nicho']}")
        
        col1, col2, col3 = st.columns(3)
        batido = col1.selectbox("Sabor", list(PRODUCTOS.keys()))
        pres = col2.selectbox("Tamaño", list(PRODUCTOS[batido].keys()))
        cant = col3.number_input("Cantidad", min_value=1, step=1)
        
        precio_u = PRODUCTOS[batido][pres]
        st.info(f"Precio Unitario: {precio_u} Bs")

        if st.button("Añadir al Carrito"):
            if batido == "Natural (Raíz)" and pres == "1000ml":
                sub = (int(cant) // 2 * 46) + (int(cant) % 2 * 24)
            else:
                sub = precio_u * cant
            st.session_state.carrito.append({
                "Batido": batido, "Pres": pres, "Cant": int(cant), "P.Unit": float(precio_u), "Subtotal": float(sub)
            })

        if st.session_state.carrito:
            st.subheader("Carrito Actual")
            df_car = pd.DataFrame(st.session_state.carrito)
            st.table(df_car)
            total_actual = df_car['Subtotal'].sum()
            st.markdown(f"### 💰 Total a pagar: {total_actual} Bs")
            
            if st.button("Confirmar Pedido Final"):
                nuevo_p = {
                    'ID_Pedido': len(st.session_state.pedidos) + 1, 
                    'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'ID_Cliente': c['ID'], 'Nombre': c['Nombre'], 'Nicho': c['Nicho'],
                    'Detalle': str(st.session_state.carrito), 
                    'Total': total_actual, 'Estado': "No Despachado"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success("Pedido guardado correctamente.")

# --- 2. DETALLE DEL PEDIDO ---
elif opcion == "Detalle del Pedido":
    st.header("🔍 Preparación del Pedido")
    if not st.session_state.pedidos.empty:
        p = st.session_state.pedidos.iloc[-1]
        st.subheader(f"Pedido #{p['ID_Pedido']} - {p['Nombre']}")
        
        nuevo_est = st.selectbox("Estado:", ["No Despachado", "Despachado"], index=0 if p['Estado'] == "No Despachado" else 1)
        if st.button("Actualizar Estado"):
            st.session_state.pedidos.at[st.session_state.pedidos.index[-1], 'Estado'] = nuevo_est
            st.rerun()

        st.divider()
        items = ast.literal_eval(p['Detalle'])
        for i in items:
            st.markdown(f"🥤 **{i['Cant']}x** {i['Batido']} ({i['Pres']}) - P.Unit: {i['P.Unit']} Bs | Sub: {i['Subtotal']} Bs")
        st.divider()
        st.markdown(f"## Total a Cobrar: {p['Total']} Bs")
    else: st.info("No hay pedidos.")

# --- 3. RESUMEN DE PEDIDOS ---
elif opcion == "Resumen de Pedidos":
    st.header("📋 Historial de Ventas")
    if not st.session_state.pedidos.empty:
        # Creamos una copia para mostrar el detalle legible
        df_mostrar = st.session_state.pedidos.copy()
        df_mostrar['Contenido'] = df_mostrar['Detalle'].apply(formatear_detalle)
        
        # Mostramos las columnas importantes incluyendo lo que pidió el cliente
        st.dataframe(df_mostrar[['ID_Pedido', 'Fecha', 'Nombre', 'Contenido', 'Total', 'Estado']])
        
        st.markdown(f"### Venta Total Acumulada: {st.session_state.pedidos['Total'].sum()} Bs")
        
        csv = st.session_state.pedidos.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte (Excel)", csv, "kefit_ventas.csv")
    else: st.info("Sin datos.")

# --- 4. RESUMEN POR ATRIBUTO ---
elif opcion == "Resumen por Atributo":
    st.header("📊 Rankings mosadiet.nutrition")
    if not st.session_state.pedidos.empty:
        # PRODUCTOS
        st.subheader("🥤 Batidos más pedidos")
        items_all = []
        for d in st.session_state.pedidos['Detalle']:
            for i in ast.literal_eval(d):
                items_all.append({"Producto": f"{i['Batido']} ({i['Pres']})", "Cantidad": i['Cant']})
        st.table(pd.DataFrame(items_all).groupby("Producto")["Cantidad"].sum().sort_values(ascending=False))

        # NICHOS
        st.subheader("📍 Ventas por Nicho")
        st.table(st.session_state.pedidos.groupby("Nicho")["Total"].sum().sort_values(ascending=False))

        # CLIENTES
        st.subheader("🏆 Clientes que más compran")
        st.table(st.session_state.pedidos.groupby("Nombre")["Total"].sum().sort_values(ascending=False))
