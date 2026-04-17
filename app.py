import streamlit as st
import pandas as pd
from datetime import datetime
import ast

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# Inicialización de bases de datos
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

# ENCABEZADO
st.markdown("<h1 style='text-align: center; color: #4A4A4A;'>mosadiet.nutrition</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #88B04B;'>Kéfit</h2>", unsafe_allow_html=True)

# NAVEGACIÓN
opcion = st.sidebar.radio("Navegación", ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"])

# --- 1. PEDIDO NUEVO ---
if opcion == "Pedido Nuevo":
    st.header("🛒 Nuevo Pedido")
    nombres = ["-- Seleccionar / Registrar Nuevo --"] + st.session_state.clientes['Nombre'].tolist()
    cliente_sel = st.selectbox("Seleccionar Cliente", nombres)

    if cliente_sel == "-- Seleccionar / Registrar Nuevo --":
        with st.form("registro"):
            st.subheader("Registrar Nuevo Cliente")
            nombre_in = st.text_input("Nombre Completo (MAYÚSCULAS)").upper()
            ws_in = st.text_input("WhatsApp")
            nicho_in = st.selectbox("Nicho", NICHOS)
            if st.form_submit_button("Guardar Cliente"):
                if nombre_in:
                    nuevo_id = len(st.session_state.clientes) + 1
                    nuevo = pd.DataFrame([[nuevo_id, nombre_in, ws_in, nicho_in]], columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                    st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo], ignore_index=True)
                    st.success(f"Registrado como Cliente #{nuevo_id}.")
                    st.rerun()
    else:
        c = st.session_state.clientes[st.session_state.clientes['Nombre'] == cliente_sel].iloc[0]
        st.info(f"Cliente: {c['Nombre']} | Nicho: {c['Nicho']}")
        
        col1, col2, col3 = st.columns(3)
        batido = col1.selectbox("Sabor", list(PRODUCTOS.keys()))
        pres = col2.selectbox("Tamaño", list(PRODUCTOS[batido].keys()))
        cant = col3.number_input("Cantidad", min_value=1, step=1)

        if st.button("Añadir al carrito"):
            p_u = PRODUCTOS[batido][pres]
            if batido == "Natural (Raíz)" and pres == "1000ml":
                total_item = (cant // 2) * 46 + (cant % 2) * 24
            else:
                total_item = p_u * cant
            
            st.session_state.carrito.append({"Batido": batido, "Pres": pres, "Cant": int(cant), "Subtotal": float(total_item)})
            st.toast("Añadido al carrito")

        if st.session_state.carrito:
            st.subheader("Carrito Actual")
            st.table(pd.DataFrame(st.session_state.carrito))
            total_p = sum(item['Subtotal'] for item in st.session_state.carrito)
            st.write(f"### Total a pagar: {total_p} Bs")
            
            if st.button("Confirmar y Guardar Pedido"):
                id_p = len(st.session_state.pedidos) + 1
                nuevo_p = {
                    'ID_Pedido': id_p, 
                    'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"), 
                    'ID_Cliente': c['ID'], 
                    'Nombre': c['Nombre'], 
                    'Nicho': c['Nicho'], 
                    'Detalle': str(st.session_state.carrito), 
                    'Total': total_p, 
                    'Estado': "No Despachado"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success(f"¡Pedido #{id_p} registrado!")
                st.balloons()

# --- 2. DETALLE DEL PEDIDO (VISTA CON CAMBIO DE ESTADO) ---
elif opcion == "Detalle del Pedido":
    st.header("🔍 Seguimiento de Preparación")
    if not st.session_state.pedidos.empty:
        # Mostramos por defecto el último pedido realizado
        # Pero permitimos seleccionar otros pedidos por ID si se desea
        ids_pedidos = st.session_state.pedidos['ID_Pedido'].tolist()
        id_actual = st.selectbox("Ver Pedido Nro:", ids_pedidos, index=len(ids_pedidos)-1)
        
        p = st.session_state.pedidos[st.session_state.pedidos['ID_Pedido'] == id_actual].iloc[0]
        idx_original = st.session_state.pedidos[st.session_state.pedidos['ID_Pedido'] == id_actual].index[0]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Datos del Pedido")
            st.write(f"**Nro Pedido:** {p['ID_Pedido']}")
            st.write(f"**Fecha:** {p['Fecha']}")
            st.write(f"**Cliente:** {p['Nombre']}")
        
        with col_b:
            st.subheader("Gestión de Estado")
            # --- AQUÍ CAMBIA EL ESTADO ---
            nuevo_estado = st.selectbox("Estado del Pedido:", ["No Despachado", "Despachado"], 
                                      index=0 if p['Estado'] == "No Despachado" else 1)
            
            if st.button("Actualizar y Guardar Estado"):
                st.session_state.pedidos.at[idx_original, 'Estado'] = nuevo_estado
                st.success(f"Pedido #{id_actual} marcado como {nuevo_estado}")
                st.rerun()

        st.divider()
        st.subheader("Lista de Preparación:")
        items = ast.literal_eval(p['Detalle'])
        for item in items:
            st.markdown(f"🥤 **{item['Cant']}x** {item['Batido']} ({item['Pres']})")
        
        st.divider()
        st.markdown(f"## Total a Cobrar: {p['Total']} Bs")
    else: 
        st.info("No hay pedidos registrados todavía.")

# --- 3. RESUMEN DE PEDIDOS ---
elif opcion == "Resumen de Pedidos":
    st.header("📋 Historial de Ventas")
    if not st.session_state.pedidos.empty:
        st.dataframe(st.session_state.pedidos[['ID_Pedido', 'Fecha', 'Nombre', 'Nicho', 'Total', 'Estado']])
        st.write(f"### Venta Total Acumulada: {st.session_state.pedidos['Total'].sum()} Bs")
        
        csv = st.session_state.pedidos.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Base de Datos (Backup)", csv, "kefit_ventas.csv", "text/csv")
    else: st.info("Sin datos.")

# --- 4. RESUMEN POR ATRIBUTO ---
elif opcion == "Resumen por Atributo":
    st.header("📊 Análisis de Atributos")
    if not st.session_state.pedidos.empty:
        # Ranking de Clientes
        st.subheader("🏆 Mejores Clientes (Ventas totales)")
        ranking = st.session_state.pedidos.groupby('Nombre')['Total'].sum().sort_values(ascending=False)
        st.table(ranking)

        # Ranking de Nichos
        st.subheader("📍 Nichos con más movimiento")
        nicho_rank = st.session_state.pedidos.groupby('Nicho')['Total'].sum().sort_values(ascending=False)
        st.bar_chart(nicho_rank)
    else: 
        st.info("Se requiere información de pedidos para generar estadísticas.")
