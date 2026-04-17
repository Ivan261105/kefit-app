import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# --- BASE DE DATOS EN MEMORIA ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Detalle', 'Total', 'Estado'])
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- DATOS DE PRODUCTOS ---
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

# --- LOGO Y TÍTULO ---
st.markdown("<h1 style='text-align: center;'>mosadiet.nutrition</h1>", unsafe_content_html=True)
st.markdown("<h3 style='text-align: center;'>Kéfit</h3>", unsafe_content_html=True)

# --- NAVEGACIÓN (Simula la parte inferior) ---
st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"])

# --- 1. PEDIDO NUEVO ---
if opcion == "Pedido Nuevo":
    st.header("🛒 Nuevo Pedido")
    
    # Selección de Cliente
    lista_clientes = ["-- Registrar Nuevo --"] + st.session_state.clientes['Nombre'].tolist()
    cliente_seleccionado = st.selectbox("Seleccionar Cliente", lista_clientes)

    if cliente_seleccionado == "-- Registrar Nuevo --":
        with st.expander("Datos del Nuevo Cliente", expanded=True):
            nuevo_id = len(st.session_state.clientes) + 1
            st.write(f"Número de Cliente: {nuevo_id}")
            nombre = st.text_input("Nombre Completo (MAYÚSCULAS)").upper()
            whatsapp = st.text_input("Número de WhatsApp")
            nicho = st.selectbox("Nicho", ["Saludable", "Deportivo", "Gourmet", "Familiar", "Temporal", "Habitual"])
            
            if st.button("Registrar Cliente"):
                if nombre and whatsapp:
                    nuevo_c = pd.DataFrame([[nuevo_id, nombre, whatsapp, nicho]], columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                    st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo_c], ignore_index=True)
                    st.success("Cliente registrado con éxito. Selecciona su nombre arriba.")
                    st.rerun()
    else:
        # Llenado de Pedido
        cliente_row = st.session_state.clientes[st.session_state.clientes['Nombre'] == cliente_seleccionado].iloc[0]
        st.info(f"Pedido para: {cliente_row['Nombre']} | WhatsApp: {cliente_row['WhatsApp']}")

        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                batido = st.selectbox("Batido", list(PRODUCTOS.keys()))
            with col2:
                presentaciones = list(PRODUCTOS[batido].keys())
                pres = st.selectbox("Presentación", presentaciones)
            with col3:
                cant = st.number_input("Cantidad", min_value=1, step=1)

            if st.button("Agregar al Pedido"):
                precio_u = PRODUCTOS[batido][pres]
                costo = precio_u * cant
                # Oferta Raíz 2x46
                if batido == "Natural (Raíz)" and pres == "1000ml" and cant == 2:
                    costo = 46
                
                st.session_state.carrito.append({
                    "Batido": batido, "Presentación": pres, "Cantidad": cant, "Costo": costo
                })

        if st.session_state.carrito:
            st.subheader("Detalle Actual")
            df_cart = pd.DataFrame(st.session_state.carrito)
            st.table(df_cart)
            total_actual = df_cart['Costo'].sum()
            st.markdown(f"### **Total acumulado: {total_actual} Bs**")

            if st.button("Finalizar y Registrar Pedido"):
                id_p = len(st.session_state.pedidos) + 1
                nuevo_p = {
                    'ID_Pedido': id_p,
                    'Fecha': datetime.now().strftime("%d/%m/%Y"),
                    'ID_Cliente': cliente_row['ID'],
                    'Nombre': cliente_row['Nombre'],
                    'Nicho': cliente_row['Nicho'],
                    'Detalle': str(st.session_state.carrito),
                    'Total': total_actual,
                    'Estado': "No Despachado"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success(f"Pedido #{id_p} guardado correctamente.")

# --- 2. DETALLE DEL PEDIDO ---
elif opcion == "Detalle del Pedido":
    st.header("📄 Último Pedido Realizado")
    if not st.session_state.pedidos.empty:
        p = st.session_state.pedidos.iloc[-1]
        st.write(f"**ID Pedido:** {p['ID_Pedido']}")
        st.write(f"**Fecha:** {p['Fecha']}")
        st.write(f"**ID Cliente:** {p['ID_Cliente']}")
        st.write(f"**Nombre:** {p['Nombre']}")
        st.write(f"**Nicho:** {p['Nicho']}")
        st.write(f"**Productos:** {p['Detalle']}")
        st.write(f"**Costo Total:** {p['Total']} Bs")
    else:
        st.warning("No hay pedidos registrados aún.")

# --- 3. RESUMEN DE PEDIDOS ---
elif opcion == "Resumen de Pedidos":
    st.header("📋 Todos los Pedidos")
    if not st.session_state.pedidos.empty:
        # Mostrar tabla y permitir edición de estado
        for index, row in st.session_state.pedidos.iterrows():
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"Pedido {row['ID_Pedido']} - {row['Nombre']} - {row['Total']} Bs")
            nuevo_estado = col_b.selectbox("Estado", ["No Despachado", "Despachado"], key=f"p_{index}")
            st.session_state.pedidos.at[index, 'Estado'] = nuevo_estado
        
        st.divider()
        total_global = st.session_state.pedidos['Total'].sum()
        st.markdown(f"## **SUMA TOTAL VENTAS: {total_global} Bs**")
    else:
        st.info("Lista vacía.")

# --- 4. RESUMEN POR ATRIBUTO ---
elif opcion == "Resumen por Atributo":
    st.header("📊 Análisis de Ventas")
    if not st.session_state.pedidos.empty:
        st.subheader("Clientes que más piden")
        ranking_clientes = st.session_state.pedidos.groupby('Nombre')['Total'].sum().sort_values(ascending=False)
        st.table(ranking_clientes)
        
        st.subheader("Nichos más populares")
        ranking_nicho = st.session_state.pedidos['Nicho'].value_counts()
        st.table(ranking_nicho)
    else:
        st.info("Sin datos para analizar.")
