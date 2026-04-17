import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="mosadiet.nutrition - Kéfit", layout="wide")

# --- BASE DE DATOS SIMULADA (En una app real, usaría SQLite o Google Sheets) ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Detalle', 'Total', 'Estado'])

# --- DATOS DE PRODUCTOS Y PRECIOS ---
PRODUCTOS = {
    "Natural (Raíz)": {"350ml": 0, "1000ml": 24}, # Especial: 2x46 
    "Sol de energía (Vitalidad)": {"350ml": 8, "1000ml": 28}, [cite: 5]
    "Fresa radiante (Vitalidad)": {"350ml": 8, "1000ml": 28}, [cite: 5]
    "Rocío de Trópico (Vitalidad)": {"350ml": 8, "1000ml": 28}, [cite: 5]
    "Fresca hidratación (Vitalidad)": {"350ml": 8, "1000ml": 28}, [cite: 5]
    "Serenidad tropical (Premium)": {"350ml": 10, "1000ml": 30}, [cite: 7]
    "Esencia de Bosque (Premium)": {"350ml": 10, "1000ml": 30}, [cite: 7]
    "Cacao armonía (Premium)": {"350ml": 10, "1000ml": 30}, [cite: 7]
    "Despertar cremoso (Premium)": {"350ml": 10, "1000ml": 30}, [cite: 7]
}

# --- NAVEGACIÓN INFERIOR ---
menu = ["Nuevo Pedido", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"]
choice = st.sidebar.radio("Menú de Navegación", menu) # Simula la botonera inferior 

# --- PANTALLA DE INICIO (LOGO) ---
st.image("https://via.placeholder.com/150", caption="mosadiet.nutrition - Kéfit") # Aquí iría el logo [cite: 14, 49]
st.title("Kéfit - Gestión de Ventas")

# --- LÓGICA DE LAS PANTALLAS ---

if choice == "Nuevo Pedido":
    st.header("📝 Nuevo Pedido")
    
    # Selección de Cliente [cite: 16]
    nombres_clientes = ["Registrar Nuevo Cliente"] + st.session_state.clientes['Nombre'].tolist()
    cliente_sel = st.selectbox("Seleccionar Cliente", nombres_clientes)

    if cliente_sel == "Registrar Nuevo Cliente":
        with st.form("registro_cliente"):
            st.subheader("Registro de Cliente")
            nuevo_id = len(st.session_state.clientes) + 1 [cite: 19]
            st.write(f"Número de Cliente: {nuevo_id}")
            nombre = st.text_input("Nombre Completo (MAYÚSCULAS)").upper() [cite: 20]
            whatsapp = st.text_input("Número de WhatsApp") [cite: 21]
            nicho = st.selectbox("Nicho", ["Saludable", "Deportivo", "Gourmet", "Familiar"]) [cite: 22]
            
            if st.form_submit_button("Guardar Cliente"):
                nuevo_cliente = pd.DataFrame([[nuevo_id, nombre, whatsapp, nicho]], columns=['ID', 'Nombre', 'WhatsApp', 'Nicho'])
                st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo_cliente], ignore_index=True)
                st.success("Cliente registrado con éxito")
                st.rerun()
    else:
        # Llenado de Pedido [cite: 23, 24]
        cliente_data = st.session_state.clientes[st.session_state.clientes['Nombre'] == cliente_sel].iloc[0]
        
        st.write(f"**Cliente:** {cliente_data['Nombre']} | **Nicho:** {cliente_data['Nicho']}")
        
        if 'carrito' not in st.session_state: st.session_state.carrito = []
        
        with st.expander("Agregar Batidos al Pedido"):
            batido = st.selectbox("Elige el batido", list(PRODUCTOS.keys()))
            presentacion = st.selectbox("Presentación", ["350ml", "1000ml"])
            cantidad = st.number_input("Cantidad", min_value=1, step=1)
            
            if st.button("Agregar al carrito"):
                precio_unitario = PRODUCTOS[batido][presentacion]
                # Lógica especial Natural 2x46 
                subtotal = precio_unitario * cantidad
                if batido == "Natural (Raíz)" and presentacion == "1000ml" and cantidad == 2:
                    subtotal = 46
                
                st.session_state.carrito.append({
                    "Batido": batido,
                    "Presentación": presentacion,
                    "Cantidad": cantidad,
                    "Precio": subtotal
                })

        # Mostrar detalle y costo actual [cite: 26]
        if st.session_state.carrito:
            df_carrito = pd.DataFrame(st.session_state.carrito)
            st.table(df_carrito)
            total_pedido = df_carrito['Precio'].sum()
            st.subheader(f"Total: {total_pedido} Bs")
            
            if st.button("Confirmar Pedido"):
                id_pedido = len(st.session_state.pedidos) + 1 [cite: 27]
                nuevo_p = {
                    'ID_Pedido': id_pedido,
                    'Fecha': datetime.now().strftime("%d/%m/%Y"),
                    'ID_Cliente': cliente_data['ID'],
                    'Nombre': cliente_data['Nombre'],
                    'Nicho': cliente_data['Nicho'],
                    'Detalle': str(st.session_state.carrito),
                    'Total': total_pedido,
                    'Estado': "Pendiente"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success(f"Pedido #{id_pedido} registrado.")

elif choice == "Detalle del Pedido":
    st.header("🔍 Detalle del Pedido")
    if not st.session_state.pedidos.empty:
        # Muestra el último pedido o permite buscar uno [cite: 28]
        pedido_view = st.session_state.pedidos.iloc[-1]
        st.write(f"**ID Pedido:** {pedido_view['ID_Pedido']}") [cite: 29]
        st.write(f"**Fecha:** {pedido_view['Fecha']}") [cite: 30]
        st.write(f"**Cliente:** {pedido_view['Nombre']} (ID: {pedido_view['ID_Cliente']})") [cite: 31, 32]
        st.write(f"**Nicho:** {pedido_view['Nicho']}") [cite: 33]
        st.write(f"**Contenido:** {pedido_view['Detalle']}") [cite: 34]
        st.write(f"**Costo Total:** {pedido_view['Total']} Bs") [cite: 35]
    else:
        st.info("No hay pedidos registrados.")

elif choice == "Resumen de Pedidos":
    st.header("📊 Listado General")
    # Tabla resumen con estado editable [cite: 36, 43]
    if not st.session_state.pedidos.empty:
        st.dataframe(st.session_state.pedidos[['ID_Pedido', 'Fecha', 'ID_Cliente', 'Nombre', 'Nicho', 'Total', 'Estado']]) [cite: 37-42]
        total_ventas = st.session_state.pedidos['Total'].sum()
        st.write(f"### Suma Total de Ventas: {total_ventas} Bs") [cite: 44]
    else:
        st.info("Sin datos.")

elif choice == "Resumen por Atributo":
    st.header("📈 Análisis de Negocio")
    if not st.session_state.pedidos.empty:
        # Aquí se aplicarían los cálculos de orden descendente [cite: 45]
        st.subheader("Batidos más pedidos") [cite: 46]
        # (Lógica de conteo y ordenamiento...)
        
        st.subheader("Nichos más activos") [cite: 47]
        # (Lógica de agrupamiento por nicho...)
        
        st.subheader("Mejores Clientes") [cite: 48]
        # (Lógica de suma por cliente...)
