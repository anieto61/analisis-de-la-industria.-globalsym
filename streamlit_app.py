import streamlit as st
import pandas as pd
import os
from data_processor import FinancialDataProcessor

st.set_page_config(page_title="Analizador Financiero Industrial", layout="wide")
st.title("📊 Tablero de Análisis Financiero")

file_path = 'informe_industria08.xlsx'

if not os.path.exists(file_path):
    st.error(f"❌ Archivo '{file_path}' no encontrado.")
    st.stop()

try:
    processor = FinancialDataProcessor(file_path)
    df = processor.get_cleaned_data()

    st.sidebar.header("🔍 Filtros de Búsqueda")
    paises = df['Country'].unique().tolist()
    pais_sel = st.sidebar.multiselect("Seleccione País", paises, default=paises)
    lineas = df['Line'].unique().tolist()
    linea_sel = st.sidebar.multiselect("Seleccione Línea", lineas, default=lineas)
    empresas = df['Company'].unique().tolist()
    empresa_sel = st.sidebar.selectbox("Seleccione Empresa", ["Todas"] + empresas)

    df_filtered = df[df['Country'].isin(pais_sel) & df['Line'].isin(linea_sel)]
    if empresa_sel != "Todas":
        df_filtered = df_filtered[df_filtered['Company'] == empresa_sel]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # CAMBIO AQUÍ: Ahora cuenta cuántos nombres de productos únicos hay
        total_variedad = df_filtered['Product'].nunique()
        st.metric("Variedad de Productos", total_variedad)
    with col2:
        st.metric("Promedio Costo", f"${df_filtered['Cost'].mean():.2f}")
    with col3:
        st.metric("Promedio Venta Ind.", f"${df_filtered['Industry_Price'].mean():.2f}")
    with col4:
        st.metric("Promedio Venta Cons.", f"${df_filtered['Consumer_Price'].mean():.2f}")

    st.divider()
    st.subheader("⚡ Análisis Rápidos")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    if btn_col1.button("Ver Productos más Caros"):
        st.table(df_filtered.nlargest(5, 'Consumer_Price')[['Product', 'Company', 'Consumer_Price']])
    if btn_col2.button("Ver Empresas con más Stock"):
        stock_emp = df_filtered.groupby('Company')['Quantity'].sum().sort_values(ascending=False)
        st.bar_chart(stock_emp)
    if btn_col3.button("Comparar Margen Ind vs Cons"):
        df_filtered['Margen'] = df_filtered['Consumer_Price'] - df_filtered['Industry_Price']
        st.write(df_filtered[['Product', 'Industry_Price', 'Consumer_Price', 'Margen']].head(10))

    st.subheader("📋 Detalle de Información")
    st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error(f"Error inesperado: {e}")
