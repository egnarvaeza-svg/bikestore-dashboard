# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 19:47:51 2025

@author: elias
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from datetime import datetime
import io

# ============================================
# CONFIGURACIÓN GENERAL MEJORADA
# ============================================
st.set_page_config(
    page_title="BikeStore Analytics",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CARGA DE DATOS CON CACHE
# ============================================
@st.cache_data
def load_data():
    products = pd.read_csv("products.csv")
    order_items = pd.read_csv("order_items.csv")
    orders = pd.read_csv("orders.csv")
    categories = pd.read_csv("categories.csv")
    staffs = pd.read_csv("staffs.csv")
    
    # Arreglo de columnas duplicadas
    order_items = order_items.rename(columns={"list_price": "list_price_order"})
    products = products.rename(columns={"list_price": "list_price_product"})
    
    return products, order_items, orders, categories, staffs

products, order_items, orders, categories, staffs = load_data()

# ============================================
# PREPARAR DATOS PARA FILTROS
# ============================================
# Crear dataset combinado
orders["order_date"] = pd.to_datetime(orders["order_date"])
merged_data = order_items.merge(products, on="product_id").merge(categories, on="category_id").merge(orders, on="order_id")
merged_data["total"] = merged_data["quantity"] * merged_data["list_price_order"] * (1 - merged_data["discount"])
merged_data["mes"] = merged_data["order_date"].dt.to_period("M").astype(str)

# ============================================
# SIDEBAR CON FILTROS FUNCIONALES
# ============================================
with st.sidebar:
    st.markdown("### 🔍 Filtros Interactivos")
    
    # Filtro por rango de fechas
    st.subheader("📅 Rango de Fechas")
    min_date = merged_data["order_date"].min()
    max_date = merged_data["order_date"].max()
    
    fecha_inicio = st.date_input(
        "Fecha inicio:",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    fecha_fin = st.date_input(
        "Fecha fin:",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro por categorías
    st.subheader("🚴 Categorías")
    todas_categorias = merged_data["category_name"].unique()
    categorias_seleccionadas = st.multiselect(
        "Seleccionar categorías:",
        options=todas_categorias,
        default=todas_categorias
    )
    
    # Filtro por monto mínimo
    st.subheader("💰 Monto Mínimo")
    monto_minimo = st.slider(
        "Ventas mínimas por producto:",
        min_value=0,
        max_value=int(merged_data["total"].max()),
        value=0,
        step=100
    )

# ============================================
# APLICAR FILTROS AL DATASET
# ============================================
def aplicar_filtros(df, categorias, fecha_ini, fecha_fin, monto_min):
    # Filtrar por categorías
    df_filtrado = df[df["category_name"].isin(categorias)]
    
    # Filtrar por fechas
    df_filtrado = df_filtrado[
        (df_filtrado["order_date"] >= pd.to_datetime(fecha_ini)) & 
        (df_filtrado["order_date"] <= pd.to_datetime(fecha_fin))
    ]
    
    # Filtrar por monto mínimo (para gráficos específicos)
    return df_filtrado

# Aplicar filtros
datos_filtrados = aplicar_filtros(
    merged_data, 
    categorias_seleccionadas, 
    fecha_inicio, 
    fecha_fin, 
    monto_minimo
)

# ============================================
# HEADER PROFESIONAL
# ============================================
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<h1 class="main-header">🚴 BikeStore Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"**Período analizado: {fecha_inicio} al {fecha_fin}**")

# ============================================
# PANEL DE KPIs PRINCIPALES (CON FILTROS)
# ============================================
st.markdown("## 📊 Panel Ejecutivo")

# Cálculos con datos filtrados
ventas_totales_filtradas = datos_filtrados["total"].sum()
num_ordenes_filtradas = datos_filtrados["order_id"].nunique()
num_productos_filtrados = datos_filtrados["product_id"].nunique()
num_clientes_filtrados = datos_filtrados["customer_id"].nunique()

# Layout de métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Ventas Totales", f"S/ {ventas_totales_filtradas:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📦 Total de Órdenes", f"{num_ordenes_filtradas:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🚲 Productos Vendidos", f"{num_productos_filtrados:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Clientes Atendidos", f"{num_clientes_filtrados:,}")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# PESTAÑAS CON GRÁFICOS FILTRADOS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Ventas", "🚴 Productos", "👥 Equipo", "📋 Descargas"])

with tab1:
    st.markdown("## 📈 Análisis de Ventas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ventas por Categoría")
        ventas_categoria = datos_filtrados.groupby("category_name")["total"].sum().sort_values(ascending=False)
        
        if not ventas_categoria.empty:
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(ventas_categoria)))
            ventas_categoria.plot(kind='bar', ax=ax1, color=colors)
            ax1.set_title("Ventas por Categoría", fontsize=14, fontweight='bold')
            ax1.set_ylabel("Ventas Totales (S/.)")
            ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig1)
        else:
            st.info("No hay datos para las categorías seleccionadas")
    
    with col2:
        st.subheader("Evolución Mensual")
        ventas_mensuales = datos_filtrados.groupby("mes")["total"].sum()
        
        if not ventas_mensuales.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.plot(ventas_mensuales.index, ventas_mensuales.values, marker='o', linewidth=3, color='#2E8B57')
            ax2.set_title("Evolución Mensual de Ventas", fontsize=14, fontweight='bold')
            ax2.set_ylabel("Ventas Totales (S/.)")
            ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info("No hay datos para el período seleccionado")

with tab2:
    st.markdown("## 🚴 Gestión de Productos")
    
    # Top productos con filtro de monto mínimo
    top_prod = datos_filtrados.groupby("product_name")["total"].sum()
    top_prod = top_prod[top_prod >= monto_minimo].sort_values(ascending=False).head(10)
    
    if not top_prod.empty:
        fig3, ax3 = plt.subplots(figsize=(12, 8))
        colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(top_prod)))
        top_prod.plot(kind='barh', ax=ax3, color=colors)
        ax3.set_title("Top Productos Más Vendidos", fontsize=14, fontweight='bold')
        ax3.set_xlabel("Ventas Totales (S/.)")
        ax3.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
        plt.tight_layout()
        st.pyplot(fig3)
    else:
        st.info("No hay productos que cumplan con el monto mínimo seleccionado")

with tab3:
    st.markdown("## 👥 Desempeño del Equipo")
    
    # Vendedores con datos filtrados
    ventas_vendedores = datos_filtrados.groupby(["first_name", "last_name"])["total"].sum().sort_values(ascending=False).head(8)
    
    if not ventas_vendedores.empty:
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(ventas_vendedores)))
        ventas_vendedores.plot(kind='bar', ax=ax4, color=colors)
        ax4.set_title("Top Vendedores por Ventas", fontsize=14, fontweight='bold')
        ax4.set_ylabel("Ventas Totales (S/.)")
        ax4.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
        
        # Formatear nombres en el eje X
        nombres_vendedores = [f"{f} {l}" for f, l in ventas_vendedores.index]
        ax4.set_xticklabels(nombres_vendedores, rotation=45, ha='right')
        
        plt.tight_layout()
        st.pyplot(fig4)
    else:
        st.info("No hay datos de vendedores para los filtros seleccionados")

with tab4:
    st.markdown("## 📋 Reportes Descargables")
    
    # Generar reportes descargables con datos filtrados
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reporte de Ventas Filtrado")
        ventas_detalle = datos_filtrados[['product_name', 'category_name', 'quantity', 'total', 'order_date']]
        csv_ventas = convert_df_to_csv(ventas_detalle)
        
        st.download_button(
            label="📥 Descargar Reporte de Ventas",
            data=csv_ventas,
            file_name=f"reporte_ventas_{fecha_inicio}_a_{fecha_fin}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.subheader("Resumen Ejecutivo")
        resumen_data = {
            'Métrica': ['Ventas Totales', 'Órdenes', 'Productos', 'Clientes'],
            'Valor': [
                f"S/ {ventas_totales_filtradas:,.0f}",
                f"{num_ordenes_filtradas:,}",
                f"{num_productos_filtrados:,}", 
                f"{num_clientes_filtrados:,}"
            ]
        }
        resumen_df = pd.DataFrame(resumen_data)
        csv_resumen = convert_df_to_csv(resumen_df)
        
        st.download_button(
            label="📥 Descargar Resumen Ejecutivo",
            data=csv_resumen,
            file_name=f"resumen_ejecutivo_{fecha_inicio}_a_{fecha_fin}.csv",
            mime="text/csv"
        )

# ============================================
# ALERTAS Y RECOMENDACIONES INTELIGENTES
# ============================================
st.markdown("## ⚠️ Alertas y Recomendaciones")

# Alertas basadas en datos filtrados
if len(datos_filtrados) == 0:
    st.error("🚨 No hay datos para los filtros seleccionados. Amplía el rango de fechas o categorías.")
elif ventas_totales_filtradas == 0:
    st.warning("⚠️ Las ventas son cero para los filtros seleccionados")
else:
    # Análisis de categorías sin ventas
    todas_cats = set(categorias_seleccionadas)
    cats_con_ventas = set(datos_filtrados["category_name"].unique())
    cats_sin_ventas = todas_cats - cats_con_ventas
    
    if cats_sin_ventas:
        st.warning(f"ℹ️ Las siguientes categorías no tienen ventas en el período seleccionado: {', '.join(cats_sin_ventas)}")
    
    st.success(f"✅ Período analizado: {fecha_inicio} a {fecha_fin} | {len(categorias_seleccionadas)} categorías seleccionadas")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "BikeStore Analytics Dashboard • Última actualización: " + 
    datetime.now().strftime("%d/%m/%Y") +
    "</div>", 
    unsafe_allow_html=True
)
)
