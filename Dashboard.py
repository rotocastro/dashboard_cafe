import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout = "wide")

df = pd.read_excel("resultado_vendas.xlsx")

df = df.dropna()
df = df.rename(columns={'Resultado Mil USD': 'Faturamento Mil U$',
                        'Resultado Mil BRL': 'Faturamento Mil R$'})

# Dicionário de mapeamento para renomear
mapeamento = {
    'AW TRADING SP. Z.O.O': 'AW TRADING',
    'EXPOCACCER - COOP CAFEICULTORES DO CERRADO': 'EXPOCACCER',
    'SLM COFFEE PTY LTDA T/AS - SOUTHLAND MERCHANTS TRUST': 'SOUTHLAND',
    'LOS BARISTAS CASA DE CAFES ELTDA': 'LOS BARISTAS'
}

# Função para renomear
def renomear(nome):
    for chave, valor in mapeamento.items():
        if chave in nome:
            return valor
    return nome  # Se não encontrar correspondência, mantém o nome original

# Aplicar a função à coluna 'cliente'
df['cliente'] = df['cliente'].apply(renomear)

df["Date"] = pd.to_datetime(df["entrega"])
df = df.sort_values("Date")

df["Month"] = df["Date"].apply(lambda x: f"{x.year}-{x.month:02d}")

# Adicionando a opção "Todos" no selectbox da sidebar
clients_option = ["Todos"] + list(df["cliente"].unique())
clients = st.sidebar.selectbox("cliente", clients_option)

# Filtrando os dados de acordo com o mês selecionado
if clients != "Todos":
    df_filtered = df[df["cliente"] == clients]
else:
    df_filtered = df  # Mostra todos os dados se "Todos" for selecionado

# Mostra o DataFrame filtrado (ou completo)
#st.write(df_filtered)

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Gráfico de volume de sacas vendidas
fig_volume = px.bar(df_filtered, x="Date", y="# sacas", title="Sacas vendidas", labels={"# sacas": "Quantidade de Sacas"})
fig_volume.update_layout(xaxis_title="Data", yaxis_title="Sacas vendidas")
col1.plotly_chart(fig_volume)

# Gráfico de vendas por cliente (pizza)
fig_client = px.pie(df_filtered, names="cliente", title="Vendas por cliente")
col2.plotly_chart(fig_client)

# Gráfico de cash flow (Faturamento Mil U$)
fig_cashflow = px.bar(df_filtered, x="Date", y="Faturamento Mil U$", title="Cash Flow", labels={"Faturamento Mil U$": "Faturamento (Mil U$)"})
fig_cashflow.update_layout(xaxis_title="Data", yaxis_title="Faturamento (Mil U$)")
col3.plotly_chart(fig_cashflow)

# Gráfico de faturamento por cliente
fig_revenue = px.bar(df_filtered, x="cliente", y="Faturamento Mil U$", title="Faturamento por cliente", color="cliente", labels={"Faturamento Mil U$": "Faturamento (Mil U$)"})
fig_revenue.update_layout(xaxis_title="Cliente", yaxis_title="Faturamento (Mil U$)")
col4.plotly_chart(fig_revenue)
