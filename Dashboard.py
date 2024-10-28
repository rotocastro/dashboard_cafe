import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas de Café",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicando estilo CSS personalizado
st.markdown("""
    <style>
        .main {
            padding: 1rem;
        }
        .stButton button {
            width: 100%;
            background-color: #0f4c81;
            color: white;
        }
        .stSelectbox label, .stMultiSelect label {
            color: #0f4c81;
            font-weight: bold;
        }
        div[data-testid="stSidebarNav"] {
            background-color: #f0f2f6;
            padding: 1rem;
        }
        .reportview-container .main .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3 {
            color: #0f4c81;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Definição do client_info
client_info = {
    "AW TRADING": {
        "Nome": "AW TRADING SP. Z.O.O",
        "Cidade": "Varsóvia",
        "País": "Polônia",
        "Movimentação": "500MT (est.)",
        "Produto de Interesse": "82+",
        "Financeiro": {
            2023: {"Receita": "U$ 15.243", "Lucro Líquido": "U$ 1.051", "Margem Ebitda": "9%", "Dívida/EBITDA": "1.50",
                   "Credit Score": 3},
            2022: {"Receita": "U$ 10.893", "Lucro Líquido": "U$ 108", "Margem Ebitda": "-1%", "Dívida/EBITDA": "-26.3",
                   "Credit Score": 4},
        }
    },
    "SOUTHLAND": {
        "Nome": "SLM Coffee Pty Ltd T/AS Southland Merchants Trust",
        "Cidade": "Hazelwood Park SA",
        "País": "Austrália",
        "Movimentação": "480MT",
        "Produto de Interesse": "82+",
        "Financeiro": {
            2023: {"Receita": "U$ 3.642", "Lucro Líquido": "U$ 583", "Margem Ebitda": "15%", "Dívida/EBITDA": "0.61",
                   "Credit Score": 4},
            2022: {"Receita": "U$ 2.713", "Lucro Líquido": "U$ 556", "Margem Ebitda": "21%", "Dívida/EBITDA": "0.67",
                   "Credit Score": 5},
        }
    },
}


@st.cache_data
def load_data():
    df = pd.read_excel("resultado_vendas_com_fluxo.xlsx")

    # Identificando dinamicamente as colunas de fluxo de pagamento
    colunas_fluxo = [col for col in df.columns if
                     re.match(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/\d{4}', col)]

    # Convertendo datas para datetime
    df["Date"] = pd.to_datetime(df["entrega"], format='%d/%m/%y', errors='coerce')

    # Limpando dados nulos
    df = df.dropna(subset=['cliente', 'safra'])
    df['safra'] = df['safra'].astype(int)

    return df, colunas_fluxo


# Carregando dados
df, colunas_fluxo = load_data()

# Sidebar com filtros
st.sidebar.image("https://via.placeholder.com/150x50.png?text=Coffee+Sales", use_column_width=True)
st.sidebar.title("Filtros")

# Multi-select para clientes
clients = st.sidebar.multiselect(
    "Selecione os Clientes",
    options=sorted(df["cliente"].unique()),
    default=sorted(df["cliente"].unique()),
    help="Selecione um ou mais clientes para filtrar os dados"
)

# Botão para detalhes do cliente
selected_clients_in_info = [client for client in clients if client in client_info]
if selected_clients_in_info:
    mostrar_detalhes_cliente = st.sidebar.button("📋 Mostrar Detalhes dos Clientes")
else:
    mostrar_detalhes_cliente = False

# Seletor múltiplo para safras
safras_disponiveis = sorted(df["safra"].unique())
safras_selecionadas = st.sidebar.multiselect(
    "Escolha as safras",
    options=safras_disponiveis,
    default=safras_disponiveis,
    help="Selecione as safras que deseja visualizar"
)

# Checkboxes com ícones
col1_sidebar, col2_sidebar = st.sidebar.columns(2)
with col1_sidebar:
    mostrar_tabela = st.checkbox("📊 Exibir tabela", value=False)
with col2_sidebar:
    incluir_estimativas = st.checkbox("📈 Incluir Estimativas", value=True)

# Aplicando filtros
df_filtered = df[
    (df['safra'].isin(safras_selecionadas)) &
    (df['cliente'].isin(clients))
    ]

if not incluir_estimativas:
    df_filtered = df_filtered[df_filtered["cliente"] != "ESTIMATIVA"]

# Header principal com métricas
st.title("☕ Dashboard de Vendas de Café")

# Exibição dos detalhes do cliente
if mostrar_detalhes_cliente and selected_clients_in_info:
    st.markdown("## 📋 Detalhes dos Clientes Selecionados")

    for client in selected_clients_in_info:
        st.markdown(f"### {client}")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📌 Informações Gerais")
            for key, value in client_info[client].items():
                if key != "Financeiro":
                    st.write(f"**{key}:** {value}")

        with col2:
            st.markdown("#### 📊 Infos. Financeiras 2023")
            for key, value in client_info[client]["Financeiro"][2023].items():
                icon = "💰" if "Receita" in key else "📈" if "Lucro" in key else "📊"
                st.write(f"{icon} **{key}:** {value}")

        with col3:
            st.markdown("#### 📊 Infos. Financeiras 2022")
            for key, value in client_info[client]["Financeiro"][2022].items():
                icon = "💰" if "Receita" in key else "📈" if "Lucro" in key else "📊"
                st.write(f"{icon} **{key}:** {value}")

        st.markdown("---")

# Métricas principais
col1_metrics, col2_metrics, col3_metrics, col4_metrics = st.columns(4)

with col1_metrics:
    total_sacas = df_filtered['# sacas'].sum()
    st.metric(
        label="Total de Sacas",
        value=f"{total_sacas:,.0f}",
        #delta=f"{total_sacas / 1000:.1f}k"
    )

with col2_metrics:
    total_clientes = len(df_filtered['cliente'].unique())
    st.metric(
        label="Número de Clientes",
        value=total_clientes
    )

with col3_metrics:
    media_sacas = df_filtered['# sacas'].mean()
    st.metric(
        label="Média de Sacas/Venda",
        value=f"{media_sacas:,.0f}"
    )

with col4_metrics:
    total_pagamentos = df_filtered[colunas_fluxo].sum().sum()
    st.metric(
        label="Faturamento Total",
        value=f"R$ {total_pagamentos:,.2f}",
        #delta=f"{(total_pagamentos / 1000000):.1f}M"
    )

st.markdown("---")

# Gráficos principais
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Gráfico de volume de sacas vendidas
with col1:
    df_volume = df_filtered.groupby(df_filtered['Date'].dt.to_period('M')).agg({'# sacas': 'sum'}).reset_index()
    df_volume['Date'] = df_volume['Date'].dt.strftime('%Y-%m')
    fig_volume = px.bar(
        df_volume,
        x="Date",
        y="# sacas",
        title="Volume de Vendas Mensais",
        template="plotly_white"
    )
    fig_volume.update_layout(
        xaxis_title="Data",
        yaxis_title="Sacas vendidas",
        showlegend=False,
        hovermode='x unified'
    )
    st.plotly_chart(fig_volume, use_container_width=True)

# Gráfico de vendas por safra
with col2:
    df_safra = df_filtered.groupby("safra")["# sacas"].sum().reset_index()
    fig_safra = px.pie(
        df_safra,
        names="safra",
        values="# sacas",
        title="Distribuição por Safra",
        template="plotly_white",
        hole=0.4
    )
    fig_safra.update_traces(
        textposition='inside',
        textinfo='percent+label+value'
    )
    st.plotly_chart(fig_safra, use_container_width=True)

# Gráfico de cash flow
with col3:
    df_fluxo = df_filtered[colunas_fluxo].melt(var_name='Month', value_name='Payment')
    df_fluxo['Month'] = pd.to_datetime(df_fluxo['Month'], format='%b/%Y')
    df_fluxo = df_fluxo.groupby('Month')['Payment'].sum().reset_index()

    fig_cashflow = px.bar(
        df_fluxo,
        x="Month",
        y="Payment",
        title="Fluxo de Caixa",
        template="plotly_white",
        color_discrete_sequence=['#0f4c81']
    )
    fig_cashflow.update_layout(
        xaxis_title="Data",
        yaxis_title="Pagamento (R$)",
        showlegend=False,
        hovermode='x unified',
        bargap=0.05
    )
    st.plotly_chart(fig_cashflow, use_container_width=True)

# Gráfico de faturamento por cliente
with col4:
    df_revenue = df_filtered.groupby("cliente")[colunas_fluxo].sum().sum(axis=1).reset_index(name="Faturamento")
    fig_revenue = px.bar(
        df_revenue,
        x="cliente",
        y="Faturamento",
        title="Faturamento por Cliente",
        color="cliente",
        template="plotly_white"
    )
    fig_revenue.update_layout(
        xaxis_title="Cliente",
        yaxis_title="Faturamento (R$)",
        showlegend=False,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Exibição da tabela de resultados
if mostrar_tabela:
    st.markdown("---")
    st.subheader("📋 Tabela Detalhada de Resultados")
    st.dataframe(
        df_filtered.style.background_gradient(subset=['# sacas'], cmap='Blues'),
        use_container_width=True
    )

# Informações sobre as safras selecionadas
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Resumo da Seleção")
st.sidebar.write(f"**Safras:** {', '.join(map(str, safras_selecionadas))}")
st.sidebar.write(f"**Clientes:** {', '.join(clients)}")
