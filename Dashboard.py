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

# Checkbox para exibir/ocultar tabela
mostrar_tabela = st.sidebar.checkbox("Exibir tabela de resultados")
# Checkbox para incluir estimativa
incluir_estimativas = st.sidebar.checkbox("Incluir Estimativas", value=True)

# Aplicando filtros
df_filtered = df[df['safra'].isin(safras_selecionadas)]

if clients != "Todos":
    df_filtered = df_filtered[df_filtered["cliente"] == clients]

if not incluir_estimativas:
    df_filtered = df_filtered[df_filtered["cliente"] != "ESTIMATIVA"]

# Agregação por mês/ano
df_filtered['Month_Year'] = df_filtered['Date'].dt.to_period('M')
df_monthly = df_filtered.groupby(['Month_Year', 'cliente']).agg({
    '# sacas': 'sum',
    'Faturamento Mil R$': 'sum'
}).reset_index()

df_monthly['Month_Year'] = df_monthly['Month_Year'].astype(str)

# Exibição dos gráficos
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

# Exibição da tabela de resultados
if mostrar_tabela:
    st.header("Tabela de Resultados")
    st.dataframe(df_filtered)

# Exibindo as safras selecionadas
st.sidebar.write(f"Safras selecionadas: {', '.join(map(str, safras_selecionadas))}")