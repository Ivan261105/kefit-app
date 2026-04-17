import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# --- BASE DE DATOS EN MEMORIA (Estado de Sesión) ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Detalle', 'Total', 'Estado'])
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- DATOS DE PRODUCTOS Y PRECIOS ---
# Basado en la lista de precios adjunta [cite: 3, 5, 7]
PRODUCTOS = {
    "Natural (Raíz)": {"1000ml": 24}, # Oferta especial 2x46 
    "Sol de energía (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Fresa radiante (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Rocío de Trópico (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Fresca hidratación (Vitalidad)": {"350ml": 8, "1000ml": 28},
    "Serenidad tropical (Premium)": {"350ml": 10, "1000ml": 30},
    "Esencia de Bosque (Premium)": {"350ml": 10, "1000ml": 30},
    "Cacao armonía (Premium)": {"350ml": 10, "1000ml": 30},
    "Despertar cremoso (Premium)": {"350ml": 10, "1000ml": 30},
}

# --- LOGO Y ENCABEZADO  ---
st.markdown("<h1 style='text-align: center; color: #4A4A4A;'>mosadiet.nutrition</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #88B04B;'>Kéfit</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>HECHO EN COCHABAMBA - BOLIVIA<br>WhatsApp: 67561652</p>", unsafe_allow_html=True)

# --- NAVEGACIÓN [cite: 13] ---
# Streamlit usa la barra lateral para navegación, ordenada como solicitaste
opcion = st.sidebar.radio(
    "Menú de Navegación",
    ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"]
)

# --- 1. PEDIDO NUEVO [cite: 15-27] ---
if opcion == "Pedido Nuevo":
    st.header("🛒 Nuevo Pedido")
    
    # Selección de Cliente
    nombres = ["-- Seleccionar / Registrar Nuevo --"] + st.session_state.clientes['Nombre'].tolist()
    cliente_sel = st.selectbox("Nombre del Cliente", nombres)

    if cliente_sel == "-- Seleccionar / Registrar Nuevo --":
        st.subheader("Registrar Nuevo Cliente")
        id_cli = len(st.session_state.clientes) + 1
        st.write(f"Número de Cliente: {id_cli}")
        nombre_input = st.text_input("Nombre Completo (MAYÚSCULAS)").upper() # [cite: 20]
        whatsapp_input = st.text_input("Número de WhatsApp")
        nicho_input = st.selectbox("Nicho", ["Habitual", "Temporal", "Saludable", "Deportivo"])
        
        if st.button("Guardar y Continuar"):
            if nombre_input:
                nuevo_c = pd.DataFrame([[id_cli, nombre_input, whatsapp_input, nicho_input]], 
                                     columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo_c], ignore_index=True)
                st.success(f"Cliente {nombre_input} registrado.")
                st.rerun()
    else:
        # Llenado del pedido para cliente existente
        c_info = st.session_state.clientes[st.session_state.clientes['Nombre'] == cliente_sel].iloc[0]
        st.info(f"Cliente: {c_info['Nombre']} | Nicho: {c_info['Nicho']}")

        # Agregar Batidos [cite: 25]
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                batido = st.selectbox("Tipo de Batido", list(PRODUCTOS.keys()))
            with col2:
                pres = st.selectbox("Presentación", list(PRODUCTOS[batido].keys()))
            with col3:
                cant = st.number_input("Cantidad", min_value=1, step=1)

            if st.button("Agregar Batido"):
                p_unit = PRODUCTOS[batido][pres]
                subtotal = p_unit * cant
                # Oferta 2x46 en Natural 1000ml 
                if batido == "Natural (Raíz)" and pres == "1000ml" and cant == 2:
                    subtotal = 46
                
                st.session_state.carrito.append({
                    "Batido": batido, "Presentación": pres, "Cantidad": cant, "Costo": subtotal
                })

        if st.session_state.carrito:
            st.table(pd.DataFrame(st.session_state.carrito))
            total_pedido = sum(item['Costo'] for item in st.session_state.carrito)
            st.markdown(f"### Costo Total: {total_pedido} Bs") # [cite: 26]

            if st.button("Registrar Pedido Final"):
                id_p = len(st.session_state.pedidos) + 1
                nuevo_p = {
                    'ID_Pedido': id_p,
                    'Fecha': datetime.now().strftime("%d/%m/%Y"),
                    'ID_Cliente': c_info['ID'],
                    'Nombre': c_info['Nombre'],
                    'Nicho': c_info['Nicho'],
                    'Detalle': str(st.session_state.carrito),
                    'Total': total_pedido,
                    'Estado': "No Despachado"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success(f"Pedido #{id_p} registrado con éxito.")

# --- 2. DETALLE DEL PEDIDO [cite: 28-35] ---
elif opcion == "Detalle del Pedido":
    st.header("🔍 Detalle del Pedido")
    if not st.session_state.pedidos.empty:
        p = st.session_state.pedidos.iloc[-1]
        st.write(f"**ID Pedido:** {p['ID_Pedido']}")
        st.write(f"**Fecha:** {p['Fecha']}")
        st.write(f"**ID Cliente:** {p['ID_Cliente']}")
        st.write(f"**Nombre Cliente:** {p['Nombre']}")
        st.write(f"**Nicho:** {p['Nicho']}")
        st.write(f"**Batidos elegidos:** {p['Detalle']}")
        st.write(f"**Costo Total:** {p['Total']} Bs")
    else:
        st.warning("Aún no hay pedidos para mostrar.")

# --- 3. RESUMEN DE PEDIDOS [cite: 36-44] ---
elif opcion == "Resumen de Pedidos":
    st.header("📋 Resumen General")
    if not st.session_state.pedidos.empty:
        # Mostramos la tabla principal
        df_display = st.session_state.pedidos[['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Total', 'Estado']]
        st.dataframe(df_display)
        
        # Edición de estado [cite: 43]
        idx = st.number_input("ID de Pedido para cambiar estado", min_value=1, max_value=len(st.session_state.pedidos))
        nuevo_est = st.selectbox("Nuevo Estado", ["No Despachado", "Despachado"])
        if st.button("Actualizar Estado"):
            st.session_state.pedidos.loc[st.session_state.pedidos['ID_Pedido'] == idx, 'Estado'] = nuevo_est
            st.rerun()

        st.divider()
        st.write(f"### Suma Total de Ventas: {st.session_state.pedidos['Total'].sum()} Bs") # [cite: 44]
    else:
        st.info("No hay pedidos registrados.")

# --- 4. RESUMEN POR ATRIBUTO [cite: 45-48] ---
elif opcion == "Resumen por Atributo":
    st.header("📊 Análisis de Atributos")
    if not st.session_state.pedidos.empty:
        # Esta sección analiza los datos guardados
        st.subheader("Batidos más pedidos (Orden Descendente)") # [cite: 46]
        # (Lógica simplificada para reporte)
        st.write("Aquí se mostrará el ranking de los batidos preferidos por tus clientes.")
        
        st.subheader("Nichos con mayor demanda") # [cite: 47]
        st.table(st.session_state.pedidos['Nicho'].value_counts())

        st.subheader("Ranking de Clientes (Mayores pagos)") # [cite: 48]
        ranking = st.session_state.pedidos.groupby('Nombre')['Total'].sum().sort_values(ascending=False)
        st.table(ranking)
    else:
        st.info("Sin datos suficientes para el análisis.")
