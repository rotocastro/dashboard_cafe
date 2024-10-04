import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

df = pd.read_excel("resultado_vendas.xlsx")

colunas_filtradas = ['código', 'safra', 'data', 'cliente', '# sacas', 'entrega',
                     'futuro_mais_próximo', 'diferencial', 'padrao','Fechamento (US$/sc)',
                     'Resultado Mil USD', 'Resultado Mil BRL']

df = df[colunas_filtradas]
df = df.dropna()
df = df.rename(columns={'Resultado Mil USD': 'Faturamento Mil U$',
                        'Resultado Mil BRL': 'Faturamento Mil R$'})

df["Date"] = pd.to_datetime(df["entrega"], format='%d/%m/%y', errors='coerce')
df = df.sort_values("Date")

# Dados de exemplo para os clientes

# Inicializar o estado para exibir detalhes do cliente
if 'mostrar_detalhes_cliente' not in st.session_state:
    st.session_state.mostrar_detalhes_cliente = False

client_info = {
    "AW TRADING": {
        "Nome": "AW TRADING SP. Z.O.O",
        "Cidade": "Varsóvia",
        "País": "Polônia",
        "Movimentação": "500MT (est.)",
        "Produto de Interesse": "82+",
        "Financeiro": {
            2023: {"Receita": "U$ 15.243", "Lucro Líquido": "U$ 1.051", "Margem Ebitda": "9%", "Dívida/EBITDA": "1.50", "Credit Score": 3},
            2022: {"Receita": "U$ 10.893", "Lucro Líquido": "U$ 108", "Margem Ebitda": "-1%", "Dívida/EBITDA": "-26.3", "Credit Score": 4},
        }},
    "SOUTHLAND": {
            "Nome": "SLM Coffee Pty Ltd T/AS Southland Merchants Trust",
            "Cidade": "Hazelwood Park SA",
            "País": "Austrália",
            "Movimentação": "480MT",
            "Produto de Interesse": "82+",
            "Financeiro": {
                2023: {"Receita": "U$ 3.642", "Lucro Líquido": "U$ 583", "Margem Ebitda": "15%", "Dívida/EBITDA": "0.61", "Credit Score": 4},
                2022: {"Receita": "U$ 2.713", "Lucro Líquido": "U$ 556", "Margem Ebitda": "21%", "Dívida/EBITDA": "0.67", "Credit Score": 5},
            }},
}

# Filtros na barra lateral
st.sidebar.header("Filtros")

# Filtro de clientes
clients_option = ["Todos"] + list(df["cliente"].unique())
clients = st.sidebar.selectbox("Cliente", clients_option)

# Seletor múltiplo para safras
safras_disponiveis = [2023, 2024]
safras_selecionadas = st.sidebar.multiselect(
    "Escolha as safras",
    options=safras_disponiveis,
    default=safras_disponiveis
)

# Checkboxs
mostrar_tabela = st.sidebar.checkbox("Exibir tabela de resultados")
incluir_estimativas = st.sidebar.checkbox("Incluir Estimativas", value=True)
if clients != "Todos" and clients in client_info:
    if st.sidebar.button("Exibir detalhes"):
        st.session_state.mostrar_detalhes_cliente = not st.session_state.mostrar_detalhes_cliente

# Aplicando filtros
df_filtered = df[df['safra'].isin(safras_selecionadas)]

if clients != "Todos":
    df_filtered = df_filtered[df_filtered["cliente"] == clients]

if not incluir_estimativas:
    df_filtered = df_filtered[df_filtered["cliente"] != "ESTIMATIVA"]

# Exibição dos detalhes do cliente (no início)
if st.session_state.mostrar_detalhes_cliente and clients != "Todos" and clients in client_info:
    st.header(f"Detalhes de {clients}")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Informações Gerais")
        st.write(f"**Nome:** {clients}")
        st.write(f"**Cidade:** {client_info[clients]['Cidade']}")
        st.write(f"**País:** {client_info[clients]['País']}")
        st.write(f"**Movimentação:** {client_info[clients]['Movimentação']}")
        st.write(f"**Produto de interesse:** {client_info[clients]['Produto de Interesse']}")

    with col2:
        st.subheader("Informações Financeiras 2023")
        st.write(f"**Receita:** {client_info[clients]['Financeiro'][2023]['Receita']}")
        st.write(f"**Lucro Líquido:** {client_info[clients]['Financeiro'][2023]['Lucro Líquido']}")
        st.write(f"**Margem Ebitda:** {client_info[clients]['Financeiro'][2023]['Margem Ebitda']}")
        st.write(f"**Dívida/Ebitda:** {client_info[clients]['Financeiro'][2023]['Dívida/EBITDA']}")
        st.write(f"**Credit Score:** {client_info[clients]['Financeiro'][2023]['Credit Score']}")


    with col3:
        st.subheader("Informações Financeiras 2022")
        st.write(f"**Receita:** {client_info[clients]['Financeiro'][2022]['Receita']}")
        st.write(f"**Lucro Líquido:** {client_info[clients]['Financeiro'][2022]['Lucro Líquido']}")
        st.write(f"**Margem Ebitda:** {client_info[clients]['Financeiro'][2022]['Margem Ebitda']}")
        st.write(f"**Dívida/Ebitda:** {client_info[clients]['Financeiro'][2022]['Dívida/EBITDA']}")
        st.write(f"**Credit Score:** {client_info[clients]['Financeiro'][2022]['Credit Score']}")

    st.markdown("---")  # Adiciona uma linha horizontal para separar os detalhes dos gráficos

# Agregação por mês/ano
df_filtered['Month_Year'] = df_filtered['Date'].dt.to_period('M')
df_monthly = df_filtered.groupby(['Month_Year', 'cliente']).agg({
    '# sacas': 'sum',
    'Faturamento Mil R$': 'sum'
}).reset_index()

df_monthly['Month_Year'] = df_monthly['Month_Year'].astype(str)

# Exibição dos gráficos
st.header("Painel de Vendas")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Gráfico de volume de sacas vendidas
fig_volume = px.bar(df_monthly, x="Month_Year", y="# sacas", title="Sacas vendidas")
fig_volume.update_layout(xaxis_title="Data", yaxis_title="Sacas vendidas")
col1.plotly_chart(fig_volume, use_container_width=True)

# Gráfico de vendas por cliente (pizza)
df_pie = df_monthly.groupby("cliente")["# sacas"].sum().reset_index()
df_pie = df_pie.sort_values("# sacas", ascending=False)
df_pie["percentage"] = df_pie["# sacas"] / df_pie["# sacas"].sum() * 100

fig_client = px.pie(df_pie, names="cliente", values="# sacas", title="Vendas por cliente")
fig_client.update_traces(textposition='inside', textinfo='percent+label')
fig_client.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
col2.plotly_chart(fig_client, use_container_width=True)

# Gráfico de cash flow (Faturamento Mil U$)
fig_cashflow = px.bar(df_monthly, x="Month_Year", y="Faturamento Mil R$", title="Cash Flow")
fig_cashflow.update_layout(xaxis_title="Data", yaxis_title="Faturamento (Mil R$)")
col3.plotly_chart(fig_cashflow, use_container_width=True)

# Gráfico de faturamento por cliente
fig_revenue = px.bar(df_monthly.groupby("cliente")["Faturamento Mil R$"].sum().reset_index(),
                     x="cliente", y="Faturamento Mil R$", title="Faturamento por cliente", color="cliente")
fig_revenue.update_layout(xaxis_title="Cliente", yaxis_title="Faturamento (Mil R$)")
col4.plotly_chart(fig_revenue, use_container_width=True)

# Exibindo as safras selecionadas
st.sidebar.write(f"Safras selecionadas: {', '.join(map(str, safras_selecionadas))}")