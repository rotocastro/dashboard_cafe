import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Vendas de Café", page_icon="☕", layout="wide")

st.markdown("""
   <style>
       .stTab {background-color: #f0f2f6; padding: 0.5rem 1rem; border-radius: 0.5rem;}
       .stTab [data-baseweb="tab-list"] button[aria-selected="true"] {
           background-color: #0f4c81;
           color: white;
       }
       .metric-container {padding: 1rem; border-radius: 0.5rem; border: 1px solid #e0e0e0; 
           background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
       .main {padding: 1rem;}
   </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return pd.read_excel("/Users/rotocastro/Desktop/vendas_cafe.xlsx")


df = load_data()

st.title("☕ Dashboard de Vendas de Café")

st.sidebar.title("Filtros")

clientes = st.sidebar.multiselect("Clientes",
                                  options=sorted(df['Cliente'].unique()),
                                  default=sorted(df['Cliente'].unique()))

peneiras = st.sidebar.multiselect("Peneiras",
                                  options=sorted([str(p) for p in df['peneira'].unique() if pd.notna(p)]),
                                  default=sorted([str(p) for p in df['peneira'].unique() if pd.notna(p)]))

qualidades = st.sidebar.multiselect("Qualidades",
                                    options=sorted([str(p) for p in df['qualidade'].unique() if pd.notna(p)]),
                                    default=sorted([str(p) for p in df['qualidade'].unique() if pd.notna(p)]))

safras = st.sidebar.multiselect("Safras",
                                options=sorted(df['safra'].unique()),
                                default=sorted(df['safra'].unique())[0])

mask = (df['Cliente'].isin(clientes) &
        df['peneira'].astype(str).isin(peneiras) &
        df['qualidade'].astype(str).isin(qualidades) &
        df['safra'].isin(safras))
df_filtered = df[mask]


def display_metrics(data):
    cols = st.columns(3)
    with cols[0]:
        total_sacas = int(data['# Sacas'].sum())
        st.metric("Total de Sacas", f"{total_sacas:,}")
    with cols[1]:
        total_revenue = data['Resultado U$'].sum()
        st.metric("Faturamento Total", f"U$ {total_revenue:,.2f}")
    with cols[2]:
        avg_price = total_revenue / total_sacas if total_sacas > 0 else 0
        st.metric("Valor médio da saca", f"U$ {avg_price:.2f}/sc")


def create_volume_chart(data, dimension, key_suffix=''):
    volume_data = data.groupby(dimension)['# Sacas'].sum().sort_values(ascending=True).reset_index()
    fig = px.bar(volume_data,
                 x='# Sacas',
                 y=dimension,
                 title=f"Sacas Vendidas por {dimension}",
                 orientation='h',
                 color=dimension)
    fig.update_layout(showlegend=False)
    return fig


def create_price_chart(data, dimension, key_suffix=''):
    if dimension == 'peneira':
        data = data.copy()
        data['peneira'] = data['peneira'].astype(str)

    price_data = data.groupby(dimension).agg({
        '# Sacas': 'sum',
        'Resultado U$': 'sum'
    }).reset_index()
    price_data['Preço Médio'] = price_data['Resultado U$'] / price_data['# Sacas']

    fig = px.scatter(price_data,
                     x=dimension,
                     y='Preço Médio',
                     title=f"Valor médio da saca (U$/sc) por {dimension}",
                     size='# Sacas',
                     color=dimension)
    fig.update_layout(showlegend=False)
    return fig


def create_cashflow_chart(data, key_suffix=''):
    month_columns = ['Sep-24', 'Oct-24', 'Nov-24', 'Dec-24',
                     'Jan-25', 'Feb-25', 'Mar-25', 'Apr-25', 'May-25']

    print("Colunas:", data.columns.tolist())  # Debug
    print("Meses encontrados:", [col for col in month_columns if col in data.columns])  # Debug

    cashflow_data = []
    for cliente in data['Cliente'].unique():
        cliente_data = data[data['Cliente'] == cliente]
        for month in month_columns:
            if month in data.columns:
                valor = cliente_data[month].sum()
                cashflow_data.append({
                    'Mes': month,
                    'Cliente': cliente,
                    'Valor': valor
                })

    monthly_data = pd.DataFrame(cashflow_data)

    if monthly_data.empty or monthly_data['Valor'].sum() == 0:
        return None

    fig = px.bar(monthly_data,
                 x='Mes',
                 y='Valor',
                 color='Cliente',
                 title="Fluxo de Caixa Mensal por Cliente",
                 barmode='stack')

    return fig


tab1, tab2, tab3, tab4 = st.tabs(['📊 Consolidado', '👥 Por Cliente', '📏 Por Peneira', '✨ Por Qualidade'])

# Na seção das tabs, ajuste para:

with tab1:
    display_metrics(df_filtered)
    st.markdown("### Visão Geral")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'Cliente'), key="vol_chart_1", use_container_width=True)
    with col2:
        st.plotly_chart(create_price_chart(df_filtered, 'Cliente'), key="price_chart_1", use_container_width=True)

    cashflow_fig = create_cashflow_chart(df_filtered)
    if cashflow_fig:
        st.plotly_chart(cashflow_fig, key="cashflow_1", use_container_width=True)

with tab2:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'Cliente'), key="vol_chart_2", use_container_width=True)
    with col2:
        st.plotly_chart(create_price_chart(df_filtered, 'Cliente'), key="price_chart_2", use_container_width=True)

with tab3:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'peneira'), key="vol_chart_3", use_container_width=True)
    with col2:
        st.plotly_chart(create_price_chart(df_filtered, 'peneira'), key="price_chart_3", use_container_width=True)

with tab4:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'qualidade'), key="vol_chart_4", use_container_width=True)
    with col2:
        st.plotly_chart(create_price_chart(df_filtered, 'qualidade'), key="price_chart_4", use_container_width=True)

if st.sidebar.checkbox("📋 Exibir tabela de dados"):
    st.dataframe(df_filtered)