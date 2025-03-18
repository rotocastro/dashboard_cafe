import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Vendas de Café", page_icon="☕", layout="wide")

st.markdown("""
   <style>
       .stTab {background-color: #f0f2f6; padding: 0.5rem 1rem; border-radius: 0.5rem;}
       .stTab [data-baseweb="tab-list"] button[aria-selected="true"] {background-color: #0f4c81; color: white;}
       .metric-container {padding: 1rem; border-radius: 0.5rem; border: 1px solid #e0e0e0; 
           background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
       .main {padding: 1rem;}
   </style>
""", unsafe_allow_html=True)

# Definição do client_info
client_info = {
    "Unroasted": {
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
    "Southland": {
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

# Adicionar controle para ajustar a cotação do dólar na sidebar
st.sidebar.title("Configurações")
cotacao_dolar = st.sidebar.number_input(
    "💱 Cotação do Dólar (R$)",
    min_value=1.0,
    max_value=10.0,
    value=5.80,
    step=0.05,
    format="%.2f",
    help="Ajuste a cotação do dólar para recalcular os valores em reais"
)

# Aviso sobre a atualização da cotação
#st.sidebar.info("ℹ️ Valores recalculados para contratos a receber.")

@st.cache_data(show_spinner=False)
def load_data(dolar_value):
    df = pd.read_excel("vendas_cafe_em_reais.xlsx")
    df["peneira"] = df["peneira"].astype(str)

    # Usar o valor do dólar definido pelo usuário
    df['PTAX'] = df['PTAX'].fillna(dolar_value)

    # Recalcular os preços em reais com base na cotação do dólar
    mask_preco_rs_vazio = df['Preço (R$/sc)'].isna()
    df.loc[mask_preco_rs_vazio, 'Preço (R$/sc)'] = df.loc[mask_preco_rs_vazio, 'Preço (u$/sc)'] * df.loc[
        mask_preco_rs_vazio, 'PTAX']

    # Calculando a Receita R$ onde está ausente
    mask_receita_rs_vazia = df['Receita R$'].isna()
    df.loc[mask_receita_rs_vazia, 'Receita R$'] = df.loc[mask_receita_rs_vazia, 'Preço (R$/sc)'] * df.loc[
        mask_receita_rs_vazia, '# Sacas']

    return df

# Passar a cotação do dólar como parâmetro para a função load_data
df = load_data(cotacao_dolar)

# Definir paletas de cores consistentes para todas as categorias
peneiras = sorted(list(df['peneira'].astype(str).unique()))
clientes = sorted(list(df['Cliente'].unique()))
qualidades = sorted(list(df['qualidade'].unique()))

# Usar paletas de cores fixas para garantir consistência
COLORS_PENEIRAS = (px.colors.qualitative.Prism + px.colors.qualitative.Safe)[:len(peneiras)]
COLORS_CLIENTES = px.colors.qualitative.Vivid[:len(clientes)]
COLORS_QUALIDADES = px.colors.qualitative.D3[:len(qualidades)]

# Criar um dicionário de cores para todas as categorias
COLOR_MAP = {}

COLOR_MAP.update(dict(zip(peneiras, COLORS_PENEIRAS)))
COLOR_MAP.update(dict(zip(clientes, COLORS_CLIENTES)))
COLOR_MAP.update(dict(zip(qualidades, COLORS_QUALIDADES)))

st.title("☕ Dashboard de Vendas de Café")

# Adicionar informação sobre a cotação atual
#st.markdown(f"**Cotação do dólar atual: R$ {cotacao_dolar:.2f}**")

st.sidebar.title("Filtros")

safras = st.sidebar.multiselect("Safras",
                                options=sorted(df['safra'].unique()),
                                default=sorted(df['safra'].unique())[1])

clientes = st.sidebar.multiselect("Clientes",
                                  options=sorted(df['Cliente'].unique()),
                                  default=sorted(df['Cliente'].unique()))

selected_clients_in_info = [cliente for cliente in clientes if cliente in client_info]
if selected_clients_in_info:
    mostrar_detalhes_cliente = st.sidebar.button("👥 Mostrar Detalhes dos Clientes")

    if mostrar_detalhes_cliente:
        st.sidebar.markdown("### Detalhes dos Clientes Selecionados")
        for cliente in selected_clients_in_info:
            info = client_info[cliente]
            with st.sidebar.expander(f"📊 {info['Nome']}", expanded=True):
                st.markdown(f"""
                    #### Informações Gerais
                    - 🏢 **Cidade:** {info['Cidade']}
                    - 🌍 **País:** {info['País']}
                    - 📦 **Movimentação:** {info['Movimentação']}
                    - 🎯 **Produto de Interesse:** {info['Produto de Interesse']}

                    #### Dados Financeiros
                    """)

                # Criar tabs para os anos
                anos = list(info['Financeiro'].keys())
                tabs_anos = st.tabs([str(ano) for ano in anos])

                for tab, ano in zip(tabs_anos, anos):
                    with tab:
                        fin_data = info['Financeiro'][ano]
                        st.markdown(f"""
                            - 💰 **Receita:** {fin_data['Receita']}
                            - 📈 **Lucro Líquido:** {fin_data['Lucro Líquido']}
                            - 📊 **Margem EBITDA:** {fin_data['Margem Ebitda']}
                            - 💵 **Dívida/EBITDA:** {fin_data['Dívida/EBITDA']}
                            - ⭐ **Credit Score:** {fin_data['Credit Score']}
                        """)

peneiras = st.sidebar.multiselect("Peneiras",
                                  options=sorted([str(p) for p in df['peneira'].unique() if pd.notna(p)]),
                                  default=sorted([str(p) for p in df['peneira'].unique() if pd.notna(p)]))

qualidades = st.sidebar.multiselect("Qualidades",
                                    options=sorted([str(p) for p in df['qualidade'].unique() if pd.notna(p)]),
                                    default=sorted([str(p) for p in df['qualidade'].unique() if pd.notna(p)]))

incluir_estimativas = st.sidebar.checkbox("📈 Incluir Estoque", value=False)

mask = (df['safra'].isin(safras) &
        df['Cliente'].isin(clientes) &
        df['peneira'].astype(str).isin(peneiras) &
        df['qualidade'].astype(str).isin(qualidades))
if not incluir_estimativas:
    mask &= df['Cliente'] != "Estoque"
df_filtered = df[mask]


def display_metrics(data):
    cols = st.columns(3)
    with cols[0]:
        total_sacas = int(data['# Sacas'].sum())
        st.metric("Total de Sacas", f"{total_sacas:,}")
    with cols[1]:
        total_revenue = data['Receita R$'].sum()
        st.metric("Faturamento Total", f"R$ {total_revenue:,.0f}")
    with cols[2]:
        avg_price = total_revenue / total_sacas if total_sacas > 0 else 0
        st.metric("Valor médio da saca", f"R$ {avg_price:.2f}/sc")


def create_volume_chart(data, dimension):
    # Garantir que usamos o COLOR_MAP global para consistência de cores
    volume_data = data.groupby(dimension)['# Sacas'].sum().sort_values(ascending=True).reset_index()

    # Usar mapeamento de cores explícito para garantir consistência
    fig = px.bar(volume_data,
                 x='# Sacas',
                 y=dimension,
                 title=f"Sacas Vendidas por {dimension}",
                 orientation='h',
                 color=dimension,
                 color_discrete_map=COLOR_MAP)

    fig.update_layout(showlegend=False)
    return fig


def create_price_chart(data, dimension):
    # Garantir que usamos o COLOR_MAP global para consistência de cores
    price_data = data.groupby(dimension).agg({
        '# Sacas': 'sum',
        'Receita R$': 'sum'
    }).reset_index()

    price_data['Preço Médio'] = price_data['Receita R$'] / price_data['# Sacas']
    price_data['Preço Médio'] = price_data['Preço Médio'].round(2)

    # Usar mapeamento de cores explícito para garantir consistência
    fig = px.scatter(price_data,
                     x=dimension,
                     y='Preço Médio',
                     title=f"Valor médio da saca (R$/sc) por {dimension}",
                     size='# Sacas',
                     color=dimension,
                     size_max=60,
                     color_discrete_map=COLOR_MAP)

    fig.update_traces(marker=dict(opacity=0.8))
    fig.update_layout(showlegend=False)
    return fig


def create_revenue_chart(data, dimension):
    # Garantir que usamos o COLOR_MAP global para consistência de cores
    revenue_data = data.groupby(dimension)['Receita R$'].sum().sort_values(ascending=True).reset_index()

    # Usar mapeamento de cores explícito para garantir consistência
    fig = px.bar(revenue_data,
                 x='Receita R$',
                 y=dimension,
                 title=f"Faturamento Total por {dimension}",
                 orientation='h',
                 color=dimension,
                 color_discrete_map=COLOR_MAP)

    fig.update_layout(showlegend=False)
    return fig


def create_pie_chart(data, dimension):
    # Garantir que usamos o COLOR_MAP global para consistência de cores
    pie_data = data.groupby(dimension)['# Sacas'].sum().reset_index()
    total = pie_data['# Sacas'].sum()
    pie_data['Percentual'] = (pie_data['# Sacas'] / total * 100).round(0)

    # Obter cores explicitamente na ordem das categorias no gráfico
    colors_in_order = [COLOR_MAP.get(cat, '#DDDDDD') for cat in pie_data[dimension]]

    # Usar mapeamento de cores explícito para garantir consistência
    fig = px.pie(pie_data,
                 values='# Sacas',
                 names=dimension,
                 title=f"Participação por {dimension} (%)",
                 hover_data=['Percentual'],
                 labels={'# Sacas': 'Sacas'},
                 color=dimension,
                 color_discrete_sequence=colors_in_order)

    fig.update_traces(textposition='inside', textinfo='percent')
    return fig


tab1, tab2, tab3, tab4 = st.tabs(['📊 Consolidado', '👥 Por Cliente', '📏 Por Peneira', '✨ Por Qualidade'])

# Organize os gráficos em 2 linhas de 2 colunas ao invés de 4 colunas
with tab1:
    display_metrics(df_filtered)
    st.markdown("### Visão Geral")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'Cliente'), key="vol_1", use_container_width=True)
    with col2:
        st.plotly_chart(create_pie_chart(df_filtered, 'Cliente'), key="pie_1", use_container_width=True)
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_revenue_chart(df_filtered, 'Cliente'), key="rev_1", use_container_width=True)
    with col4:
        st.plotly_chart(create_price_chart(df_filtered, 'Cliente'), key="price_1", use_container_width=True)

with tab2:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'Cliente'), key="vol_2", use_container_width=True)
    with col2:
        st.plotly_chart(create_pie_chart(df_filtered, 'Cliente'), key="pie_2", use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_revenue_chart(df_filtered, 'Cliente'), key="rev_2", use_container_width=True)
    with col4:
        st.plotly_chart(create_price_chart(df_filtered, 'Cliente'), key="price_2", use_container_width=True)

with tab3:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'peneira'), key="vol_3", use_container_width=True)
    with col2:
        st.plotly_chart(create_pie_chart(df_filtered, 'peneira'), key="pie_3", use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_revenue_chart(df_filtered, 'peneira'), key="rev_3", use_container_width=True)
    with col4:
        st.plotly_chart(create_price_chart(df_filtered, 'peneira'), key="price_3", use_container_width=True)

with tab4:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'qualidade'), key="vol_4", use_container_width=True)
    with col2:
        st.plotly_chart(create_pie_chart(df_filtered, 'qualidade'), key="pie_4", use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_revenue_chart(df_filtered, 'qualidade'), key="rev_4", use_container_width=True)
    with col4:
        st.plotly_chart(create_price_chart(df_filtered, 'qualidade'), key="price_4", use_container_width=True)

if st.sidebar.checkbox("📋 Exibir tabela de dados"):
    st.dataframe(df_filtered)
