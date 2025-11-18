# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 16:30:26 2025

@author: elias
"""

###########
# Manera creativa: Dashboard web con Streamlit
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

# ============================================
# CONFIGURACIÓN GENERAL
# ============================================
st.set_page_config(page_title="BikeStore Dashboard", layout="wide")

st.title("🚲 Bike Store – Dashboard Analítico")
st.markdown(
    "Este dashboard visualiza reportes basados en los requerimientos de la base de datos del proyecto BikeStore."
)

# ============================================
# CARGA DE DATOS (solo desde archivos del repo)
# ============================================

products = pd.read_csv("products.csv")
order_items = pd.read_csv("order_items.csv")
orders = pd.read_csv("orders.csv")
categories = pd.read_csv("categories.csv")
staffs = pd.read_csv("staffs.csv")

# ============================================
# ARREGLO DE COLUMNAS DUPLICADAS
# ============================================
order_items = order_items.rename(columns={"list_price": "list_price_order"})
products = products.rename(columns={"list_price": "list_price_product"})

# ============================================
# KPI PRINCIPALES
# ============================================
order_items["total"] = order_items["quantity"] * order_items["list_price_order"] * (1 - order_items["discount"])
ventas_totales = order_items["total"].sum()
num_ordenes = orders["order_id"].nunique()
num_productos = products["product_id"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Ventas Totales", f"S/ {ventas_totales:,.0f}")
col2.metric("📦 Total de Órdenes", f"{num_ordenes:,}")
col3.metric("🚲 Productos en Catálogo", f"{num_productos:,}")

# ============================================
# REPORTE 1: Ventas por Categoría
# ============================================

st.header("1️⃣ Ventas por Categoría")

merged = order_items.merge(products, on="product_id").merge(categories, on="category_id")
merged["total"] = merged["quantity"] * merged["list_price_order"] * (1 - merged["discount"])

ventas_categoria = merged.groupby("category_name")["total"].sum().sort_values(ascending=False)

fig1, ax1 = plt.subplots(figsize=(10, 5))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(ventas_categoria)))

ventas_categoria.plot(kind="bar", ax=ax1, color=colors)
ax1.set_title("Ventas por Categoría de Producto")
ax1.set_ylabel("Ventas Totales (S/.)")
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig1)

# ============================================
# REPORTE 2: Ventas Mensuales
# ============================================

st.header("2️⃣ Ventas Mensuales")

orders["order_date"] = pd.to_datetime(orders["order_date"])
ventas_mes = order_items.merge(orders, on="order_id")
ventas_mes["total"] = ventas_mes["quantity"] * ventas_mes["list_price_order"] * (1 - ventas_mes["discount"])
ventas_mes["mes"] = ventas_mes["order_date"].dt.to_period("M").astype(str)

ventas_mensuales = ventas_mes.groupby("mes")["total"].sum()

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(ventas_mensuales.index, ventas_mensuales.values, marker="o", linewidth=3)
ax2.set_title("Evolución Mensual de Ventas")
ax2.set_ylabel("Ventas Totales (S/.)")
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig2)

# ============================================
# REPORTE 3: Top 10 Productos
# ============================================

st.header("3️⃣ Top 10 Productos Más Vendidos")

top_prod = merged.groupby("product_name")["total"].sum().sort_values(ascending=False).head(10)

fig3, ax3 = plt.subplots(figsize=(10, 5))
colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(top_prod)))

top_prod.plot(kind="bar", color=colors, ax=ax3)
ax3.set_title("Top 10 Productos Más Vendidos")
ax3.set_ylabel("Ingresos Totales (S/.)")
ax3.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig3)

# ============================================
# REPORTE 4: Ventas por Vendedor
# ============================================

st.header("4️⃣ Vendedores con Más Ventas")

ventas_vend = orders.merge(staffs, on="staff_id").merge(order_items, on="order_id")
ventas_vend["total"] = ventas_vend["quantity"] * ventas_vend["list_price_order"] * (1 - ventas_vend["discount"])

top_vendedores = ventas_vend.groupby("first_name")["total"].sum().sort_values(ascending=False)

fig4, ax4 = plt.subplots(figsize=(10, 5))
colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(top_vendedores)))

top_vendedores.plot(kind="barh", color=colors, ax=ax4)
ax4.set_title("Top Vendedores por Ingresos")
ax4.set_xlabel("Ingresos Totales (S/.)")
ax4.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"S/ {x:,.0f}"))
plt.tight_layout()

st.pyplot(fig4)
