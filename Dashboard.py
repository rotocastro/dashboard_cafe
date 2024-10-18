import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

st.set_page_config(layout="wide")

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


df, colunas_fluxo = load_data()

# Filtros na barra lateral
st.sidebar.header("Filtros")

# Filtro de clientes
clients_option = ["Todos"] + sorted(df["cliente"].unique().tolist())
clients = st.sidebar.selectbox("Cliente", clients_option)

# Seletor múltiplo para safras
safras_disponiveis = sorted(df["safra"].unique())
safras_selecionadas = st.sidebar.multiselect(
    "Escolha as safras",
    options=safras_disponiveis,
    default=safras_disponiveis
)

# Checkboxes
mostrar_tabela = st.sidebar.checkbox("Exibir tabela de resultados")
incluir_estimativas = st.sidebar.checkbox("Incluir Estimativas", value=True)

# Botão para exibir detalhes do cliente
if clients != "Todos" and clients in client_info:
    mostrar_detalhes_cliente = st.sidebar.button("Mostrar Detalhes do Cliente")

# Aplicando filtros
df_filtered = df[df['safra'].isin(safras_selecionadas)]

if clients != "Todos":
    df_filtered = df_filtered[df_filtered["cliente"] == clients]

if not incluir_estimativas:
    df_filtered = df_filtered[df_filtered["cliente"] != "ESTIMATIVA"]

# Layout do dashboard
st.title("Painel de Vendas de Café")

# Exibição dos detalhes do cliente
if clients != "Todos" and clients in client_info and mostrar_detalhes_cliente:
    st.header(f"Detalhes de {clients}")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Informações Gerais")
        for key, value in client_info[clients].items():
            if key != "Financeiro":
                st.write(f"**{key}:** {value}")

    with col2:
        st.subheader("Infos. Financeiras 2023")
        for key, value in client_info[clients]["Financeiro"][2023].items():
            st.write(f"**{key}:** {value}")

    with col3:
        st.subheader("Infos. Financeiras 2022")
        for key, value in client_info[clients]["Financeiro"][2022].items():
            st.write(f"**{key}:** {value}")

    st.markdown("---")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Gráfico de volume de sacas vendidas
with col1:
    df_volume = df_filtered.groupby(df_filtered['Date'].dt.to_period('M')).agg({'# sacas': 'sum'}).reset_index()
    df_volume['Date'] = df_volume['Date'].dt.strftime('%Y-%m')
    total_sacas = df_volume['# sacas'].sum()
    fig_volume = px.bar(df_volume, x="Date", y="# sacas", title=f"Sacas vendidas (Total: {total_sacas:,.0f})")
    fig_volume.update_layout(xaxis_title="Data", yaxis_title="Sacas vendidas")
    st.plotly_chart(fig_volume, use_container_width=True)

# Gráfico de vendas por safra
with col2:
    df_safra = df_filtered.groupby("safra")["# sacas"].sum().reset_index()
    df_safra["# sacas"] = df_safra["# sacas"].astype(int)
    fig_safra = px.pie(df_safra, names="safra", values="# sacas",
                       title=f"Vendas por safra (Total: {total_sacas:,.0f} sacas)")
    fig_safra.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_safra.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    st.plotly_chart(fig_safra, use_container_width=True)

# Gráfico de cash flow
with col3:
    df_fluxo = df_filtered[colunas_fluxo].melt(var_name='Month', value_name='Payment')
    df_fluxo['Month'] = pd.to_datetime(df_fluxo['Month'], format='%b/%Y')
    df_fluxo = df_fluxo.groupby('Month')['Payment'].sum().reset_index()
    total_pagamentos = df_fluxo['Payment'].sum()
    fig_cashflow = px.bar(df_fluxo, x="Month", y="Payment", title=f"Cash Flow (Total: R$ {total_pagamentos:,.2f})")
    fig_cashflow.update_layout(xaxis_title="Data", yaxis_title="Pagamento (R$)")
    st.plotly_chart(fig_cashflow, use_container_width=True)

# Gráfico de faturamento por cliente
with col4:
    df_revenue = df_filtered.groupby("cliente")[colunas_fluxo].sum().sum(axis=1).reset_index(name="Faturamento")
    fig_revenue = px.bar(df_revenue, x="cliente", y="Faturamento",
                         title=f"Faturamento por cliente (Total: R$ {total_pagamentos:,.2f})",
                         color="cliente")
    fig_revenue.update_layout(xaxis_title="Cliente", yaxis_title="Faturamento (R$)")
    fig_revenue.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    st.plotly_chart(fig_revenue, use_container_width=True)

# Exibição da tabela de resultados
if mostrar_tabela:
    st.subheader("Tabela de Resultados")
    st.dataframe(df_filtered)

# Exibindo as safras selecionadas
st.sidebar.write(f"Safras selecionadas: {', '.join(map(str, safras_selecionadas))}")