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
    "Natural (Raíz)": {"1000ml": 24.00},
    "Sol de energía (Vitalidad)": {"350ml": 8.00, "1000ml": 28.00},
    "Fresa radiante (Vitalidad)": {"350ml": 8.00, "1000ml": 28.00},
    "Rocío de Trópico (Vitalidad)": {"350ml": 8.00, "1000ml": 28.00},
    "Fresca hidratación (Vitalidad)": {"350ml": 8.00, "1000ml": 28.00},
    "Serenidad tropical (Premium)": {"350ml": 10.00, "1000ml": 30.00},
    "Esencia de Bosque (Premium)": {"350ml": 10.00, "1000ml": 30.00},
    "Cacao armonía (Premium)": {"350ml": 10.00, "1000ml": 30.00},
    "Despertar cremoso (Premium)": {"350ml": 10.00, "1000ml": 30.00},
}
NICHOS = ["gimnasio FGI", "gimnasio Andi", "Sadosa", "Emi", "tecnologico", "amigos Andi", "amigos mamita", "otros"]

st.markdown("<h1 style='text-align: center;'>mosadiet.nutrition</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #88B04B;'>Kéfit</h2>", unsafe_allow_html=True)

opcion = st.sidebar.radio("Navegación", ["Pedido Nuevo", "Detalle del Pedido", "Resumen de Pedidos", "Resumen por Atributo"])

def formatear_detalle_texto(detalle_str):
    try:
        lista = ast.literal_eval(detalle_str)
        return "\n".join([f"• {i['Cant']}x {i['Batido']} ({i['Pres']})" for i in lista])
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
        
        precio_u = float(PRODUCTOS[batido][pres])
        st.info(f"Precio Unitario: {precio_u:.2f} Bs")

        if st.button("Añadir al Carrito"):
            if batido == "Natural (Raíz)" and pres == "1000ml":
                sub = (int(cant) // 2 * 46.00) + (int(cant) % 2 * 24.00)
            else:
                sub = precio_u * cant
            st.session_state.carrito.append({
                "Batido": batido, "Pres": pres, "Cant": int(cant), "P.Unit": precio_u, "Subtotal": float(sub)
            })

        if st.session_state.carrito:
            st.subheader("Carrito Actual")
            df_car = pd.DataFrame(st.session_state.carrito)
            st.table(df_car.style.format({"P.Unit": "{:.2f}", "Subtotal": "{:.2f}"}))
            
            total_actual = sum(i['Subtotal'] for i in st.session_state.carrito)
            st.markdown(f"### 💰 Total a pagar: {total_actual:.2f} Bs")
            
            if st.button("Confirmar Pedido Final"):
                nuevo_p = {
                    'ID_Pedido': len(st.session_state.pedidos) + 1, 
                    'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'ID_Cliente': c['ID'], 'Nombre': c['Nombre'], 'Nicho': c['Nicho'],
                    'Detalle': str(st.session_state.carrito), 
                    'Total': float(total_actual), 'Estado': "No Despachado"
                }
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, pd.DataFrame([nuevo_p])], ignore_index=True)
                st.session_state.carrito = []
                st.success("¡Pedido guardado!")

# --- 2. DETALLE DEL PEDIDO (SIN CAMBIO DE ESTADO) ---
elif opcion == "Detalle del Pedido":
    st.header("🔍 Ficha de Preparación")
    if not st.session_state.pedidos.empty:
        p = st.session_state.pedidos.iloc[-1]
        st.subheader(f"Pedido #{p['ID_Pedido']} - {p['Nombre']}")
        
        st.write(f"**Nicho:** {p['Nicho']} | **Fecha:** {p['Fecha']} | **Estado Actual:** {p['Estado']}")
        
        st.divider()
        items = ast.literal_eval(p['Detalle'])
        df_items = pd.DataFrame(items)
        st.table(df_items[['Cant', 'Batido', 'Pres', 'P.Unit', 'Subtotal']].style.format({"P.Unit": "{:.2f}", "Subtotal": "{:.2f}"}))
        
        st.markdown(f"## Total a Cobrar: {p['Total']:.2f} Bs")
    else: st.info("No hay pedidos registrados.")

# --- 3. RESUMEN DE PEDIDOS (CON OPCIÓN DE CAMBIAR ESTADO) ---
elif opcion == "Resumen de Pedidos":
    st.header("📋 Gestión de Ventas")
    if not st.session_state.pedidos.empty:
        
        # --- MENÚ DESPLEGABLE PARA CAMBIAR ESTADO ---
        st.markdown("### ⚙️ Actualizar Estado de Entrega")
        with st.container():
            col_sel, col_est, col_acc = st.columns([2,2,1])
            id_lista = st.session_state.pedidos['ID_Pedido'].tolist()
            id_a_editar = col_sel.selectbox("Seleccionar Nro de Pedido", id_lista)
            
            # Obtener estado actual para el valor por defecto
            estado_actual = st.session_state.pedidos[st.session_state.pedidos['ID_Pedido'] == id_a_editar]['Estado'].values[0]
            opciones_estado = ["No Despachado", "Despachado"]
            idx_defecto = opciones_estado.index(estado_actual)
            
            nuevo_estado = col_est.selectbox("Cambiar a:", opciones_estado, index=idx_defecto)
            
            if col_acc.button("Actualizar"):
                idx_original = st.session_state.pedidos[st.session_state.pedidos['ID_Pedido'] == id_a_editar].index[0]
                st.session_state.pedidos.at[idx_original, 'Estado'] = nuevo_estado
                st.toast(f"Pedido #{id_a_editar} actualizado a {nuevo_estado}")
                st.rerun()

        st.divider()
        
        # TABLA DE RESUMEN
        df_resumen = st.session_state.pedidos.copy()
        df_resumen['Contenido'] = df_resumen['Detalle'].apply(formatear_detalle_texto)
        
        st.dataframe(
            df_resumen[['ID_Pedido', 'Fecha', 'Nombre', 'Contenido', 'Total', 'Estado']].style.format({"Total": "{:.2f}"}), 
            height=400,
            use_container_width=True
        )
        
        st.markdown(f"### Venta Total Acumulada: {st.session_state.pedidos['Total'].sum():.2f} Bs")
        
        csv = st.session_state.pedidos.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Excel", csv, "ventas_kefit.csv")
    else: st.info("Sin pedidos.")

# --- 4. RESUMEN POR ATRIBUTO ---
elif opcion == "Resumen por Atributo":
    st.header("📊 Estadísticas de Negocio")
    if not st.session_state.pedidos.empty:
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            st.subheader("🥤 Productos más pedidos")
            items_all = []
            for d in st.session_state.pedidos['Detalle']:
                for i in ast.literal_eval(d):
                    items_all.append({"Producto": f"{i['Batido']} ({i['Pres']})", "Cant": i['Cant']})
            st.table(pd.DataFrame(items_all).groupby("Producto")["Cant"].sum().sort_values(ascending=False))

        with col_r2:
            st.subheader("📍 Ventas por Nicho")
            rank_nicho = st.session_state.pedidos.groupby("Nicho")["Total"].sum().sort_values(ascending=False)
            st.table(rank_nicho.map("{:.2f} Bs".format))

        st.subheader("🏆 Clientes VIP")
        rank_cli = st.session_state.pedidos.groupby("Nombre")["Total"].sum().sort_values(ascending=False)
        st.table(rank_cli.map("{:.2f} Bs".format))
    else: st.info("Sin datos suficientes.")
