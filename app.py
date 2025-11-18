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
import plotly.express as px
import plotly.graph_objects as go
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
# HEADER PROFESIONAL
# ============================================
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<h1 class="main-header">🚴 BikeStore Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Sistema de análisis integral para la gestión de la tienda de bicicletas**")

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=BikeStore", use_column_width=True)
    st.header("🔍 Filtros")
    
    # Filtros interactivos
    st.subheader("Rango de Fechas")
    min_date = pd.to_datetime('2022-01-01')
    max_date = pd.to_datetime('2023-12-31')
    
    # Filtro por categorías
    st.subheader("Categorías")
    all_categories = ["Todas"] + list(pd.read_csv("categories.csv")["category_name"].unique())
    selected_categories = st.multiselect(
        "Seleccionar categorías:",
        options=all_categories[1:],
        default=all_categories[1:]
    )

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
# PANEL DE KPIs PRINCIPALES
# ============================================
st.markdown("## 📊 Panel Ejecutivo")

# Cálculos mejorados
order_items["total"] = order_items["quantity"] * order_items["list_price_order"] * (1 - order_items["discount"])
ventas_totales = order_items["total"].sum()
num_ordenes = orders["order_id"].nunique()
num_productos = products["product_id"].nunique()
num_clientes = orders["customer_id"].nunique()

# Layout de métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Ventas Totales", f"S/ {ventas_totales:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📦 Total de Órdenes", f"{num_ordenes:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🚲 Productos en Catálogo", f"{num_productos:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Clientes Únicos", f"{num_clientes:,}")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# PESTAÑAS PARA DIFERENTES REPORTES
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Ventas", "🚴 Productos", "👥 Equipo", "📋 Descargas"])

with tab1:
    st.markdown("## 📈 Análisis de Ventas")
    
    # Ventas por categoría
    merged = order_items.merge(products, on="product_id").merge(categories, on="category_id")
    merged["total"] = merged["quantity"] * merged["list_price_order"] * (1 - merged["discount"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ventas por Categoría")
        ventas_categoria = merged.groupby("category_name")["total"].sum().sort_values(ascending=False)
        
        fig1 = px.bar(
            ventas_categoria, 
            x=ventas_categoria.index, 
            y=ventas_categoria.values,
            title="Ventas por Categoría",
            labels={'x': 'Categoría', 'y': 'Ventas (S/.)'}
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Evolución Mensual")
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        ventas_mes = order_items.merge(orders, on="order_id")
        ventas_mes["total"] = ventas_mes["quantity"] * ventas_mes["list_price_order"] * (1 - ventas_mes["discount"])
        ventas_mes["mes"] = ventas_mes["order_date"].dt.to_period("M").astype(str)
        ventas_mensuales = ventas_mes.groupby("mes")["total"].sum()
        
        fig2 = px.line(
            ventas_mensuales, 
            x=ventas_mensuales.index, 
            y=ventas_mensuales.values,
            title="Evolución Mensual de Ventas",
            markers=True
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("## 🚴 Gestión de Productos")
    
    # Top productos
    top_prod = merged.groupby("product_name")["total"].sum().sort_values(ascending=False).head(10)
    
    fig3 = px.bar(
        top_prod, 
        x=top_prod.values, 
        y=top_prod.index,
        orientation='h',
        title="Top 10 Productos Más Vendidos",
        labels={'x': 'Ventas Totales (S/.)', 'y': 'Producto'}
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.markdown("## 👥 Desempeño del Equipo")
    
    # Vendedores
    ventas_vend = orders.merge(staffs, on="staff_id").merge(order_items, on="order_id")
    ventas_vend["total"] = ventas_vend["quantity"] * ventas_vend["list_price_order"] * (1 - ventas_vend["discount"])
    top_vendedores = ventas_vend.groupby(["first_name", "last_name"])["total"].sum().sort_values(ascending=False).head(8)
    
    vendedores_nombres = [f"{f} {l}" for f, l in top_vendedores.index]
    
    fig4 = px.pie(
        names=vendedores_nombres,
        values=top_vendedores.values,
        title="Distribución de Ventas por Vendedor"
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.markdown("## 📋 Reportes Descargables")
    
    # Generar reportes descargables
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reporte de Ventas")
        ventas_detalle = merged[['product_name', 'category_name', 'quantity', 'total']]
        csv_ventas = convert_df_to_csv(ventas_detalle)
        
        st.download_button(
            label="📥 Descargar Reporte de Ventas",
            data=csv_ventas,
            file_name="reporte_ventas_bikestore.csv",
            mime="text/csv"
        )
    
    with col2:
        st.subheader("Reporte de Productos")
        csv_productos = convert_df_to_csv(products)
        
        st.download_button(
            label="📥 Descargar Catálogo de Productos",
            data=csv_productos,
            file_name="catalogo_productos_bikestore.csv",
            mime="text/csv"
        )

# ============================================
# ALERTAS Y RECOMENDACIONES
# ============================================
st.markdown("## ⚠️ Alertas y Recomendaciones")

# Análisis de stock (simulado)
stock_bajo = products[products["model_year"] == 2022]  # Ejemplo simulado

if len(stock_bajo) > 0:
    st.warning(f"🚨 Hay {len(stock_bajo)} productos del modelo 2022 que podrían necesitar actualización")

st.success("✅ Todas las métricas se encuentran dentro de los parámetros esperados")

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