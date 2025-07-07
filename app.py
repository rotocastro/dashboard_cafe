import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configurações da página
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
    "AW Trading - Unroasted": {
        "Nome": "AW TRADING SP. Z.O.O",
        "Cidade": "Varsóvia",
        "País": "Polônia",
        "Movimentação": "500MT (est.)",
        "Produto de Interesse": "82+",
        "Financeiro": {
            2024: {"Receita": "U$ 26.677", "Lucro Líquido": "U$ 1.810", "Margem Ebitda": "8%", "Dívida/EBITDA": "1.54",
                   "Credit Score": 3},
            2023: {"Receita": "U$ 15.243", "Lucro Líquido": "U$ 1.051", "Margem Ebitda": "9%", "Dívida/EBITDA": "1.50",
                   "Credit Score": 3},
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


#Cotação do dólar na sidebar
st.sidebar.title("Configurações")

cotacao_dolar = st.sidebar.number_input(
    "💱 Cotação do Dólar (R$)",
    min_value=1.0, max_value=10.0, value=5.50, step=0.05,
    format="%.2f", help="Ajuste a cotação do dólar para recalcular os valores em reais"
)


# Função para buscar a data da última atualização
@st.cache_data(show_spinner=False)
def get_last_update_date():
    try:
        df_futuros = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="futuros")
        # Pegar o nome da coluna D (que é onde está a data)
        last_update = df_futuros.columns[3]  # Nome da coluna D

        # Tentar converter para datetime
        try:
            last_update = pd.to_datetime(last_update, format='%d/%m/%y')
            return last_update.strftime("%d/%m/%Y")
        except:
            return str(last_update)
    except Exception as e:
        return "Data não disponível"

# Buscar e exibir a data da última atualização
ultima_atualizacao = get_last_update_date()
st.sidebar.markdown(f"<small>📅 Última atualização: {ultima_atualizacao}</small>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data(dolar_value):
    df = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="Sheet2")

    df["Peneira"] = df["Peneira"].astype(str)
    df['PTAX'] = df['PTAX'].fillna(dolar_value)

    # Recalcular os preços em reais com base na cotação do dólar
    mask_preco_rs_vazio = df['Preço (R$/sc)'].isna()
    df.loc[mask_preco_rs_vazio, 'Preço (R$/sc)'] = df.loc[mask_preco_rs_vazio, 'Preço (u$/sc)'] * df.loc[
        mask_preco_rs_vazio, 'PTAX']

    # Calculando a Receita R$ onde está ausente
    mask_receita_rs_vazia = df['Receita R$'].isna()
    df.loc[mask_receita_rs_vazia, 'Receita R$'] = df.loc[mask_receita_rs_vazia, 'Preço (R$/sc)'] * df.loc[
        mask_receita_rs_vazia, '# Sacas']

    # Converter 'Data Pagamento' para datetime
    df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce')

    return df

@st.cache_data(show_spinner=False)
def load_hedge_data():
    try:
        df_hedge = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="hedge")
        return df_hedge
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_futures_data():
    try:
        df_futuros = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="futuros")
        return df_futuros
    except Exception as e:
        return pd.DataFrame()



# Passar a cotação do dólar como parâmetro para a função load_data
df = load_data(cotacao_dolar)

# Definir paletas de cores consistentes para todas as categorias
peneiras = sorted(list(df['Peneira'].astype(str).unique()))
clientes = sorted(list(df['Cliente'].unique()))
qualidades = sorted(list(df['Qualidade'].unique()))

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

st.sidebar.title("Filtros")

safras = st.sidebar.multiselect("Safras",
                                options=sorted(df['Safra'].unique()),
                                default=[2025])

incluir_estimativas = st.sidebar.checkbox("📈 Incluir Estoque", value=True)

mercado = st.sidebar.multiselect("Mercado",
                                 options=sorted(df['Mercado'].unique()),
                                 default=sorted(df['Mercado'].unique()))

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

# peneiras = st.sidebar.multiselect("Peneiras",
#                                   options=sorted([str(p) for p in df['peneira'].unique() if pd.notna(p)]),
#                                   default=sorted([str(p) for p in df['peneira'].unique() if pd.notna(p)]))

qualidades = st.sidebar.multiselect("Qualidade",
                                    options=sorted([str(p) for p in df['Qualidade'].unique() if pd.notna(p)]),
                                    default=sorted([str(p) for p in df['Qualidade'].unique() if pd.notna(p)]))

mask = (df['Safra'].isin(safras) &
        df['Cliente'].isin(clientes) &
        df['Peneira'].astype(str).isin(peneiras) &
        df['Qualidade'].astype(str).isin(qualidades) &
        df['Mercado'].isin(mercado))
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

def create_market_comparison(data):
    # Verificar se há dados suficientes
    if data.empty or not data['Mercado'].isin(['Exportação', 'Mercado Interno']).any():
        # Retornar uma mensagem ou um gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title="Sem dados suficientes para comparação entre tipos de mercado",
            annotations=[dict(
                text="Não há dados para os filtros selecionados",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=16)
            )]
        )
        return fig

    # Agrupar por tipo de mercado (resto do código permanece igual)
    market_comp = data.groupby('Mercado').agg({
        '# Sacas': 'sum',
        'Receita R$': 'sum'
    }).reset_index()

    # Calcular preço médio
    market_comp['Preço Médio (R$/sc)'] = (market_comp['Receita R$'] / market_comp['# Sacas']).round(2)

    # Calcular o total de sacas para percentuais
    total_sacas = market_comp['# Sacas'].sum()
    market_comp['Percentual'] = ((market_comp['# Sacas'] / total_sacas) * 100).round(1)

    # Formatar o texto para exibição
    market_comp['text'] = market_comp['# Sacas'].apply(lambda x: f"{int(x):,}")  # Formatar como inteiro
    market_comp['hover_text'] = market_comp.apply(
        lambda
            row: f"{int(row['# Sacas']):,} sacas<br>{row['Percentual']}% do total<br>R$ {row['Preço Médio (R$/sc)']:.2f}/sc",
        axis=1
    )

    # Criar o gráfico de barras
    fig = px.bar(
        market_comp,
        x='Mercado',
        y='# Sacas',
        color='Mercado',
        title='Comparação entre Tipos de Mercado',
        text='text',
        hover_data={
            '# Sacas': False,
            'text': False,
            'Mercado': True,
            'hover_text': True
        }
    )

    # Adicionar anotações com as porcentagens
    for i, row in market_comp.iterrows():
        fig.add_annotation(
            x=row['Mercado'],
            y=row['# Sacas'] * 1.05,
            text=f"{row['Percentual']}%",
            showarrow=False,
            font=dict(size=14, color="black")
        )

    # Ajustar o layout
    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        xaxis_title="Tipos de Mercado",
        yaxis_title="Número de Sacas",
        bargap=0.4
    )

    # Formatar os textos das barras
    fig.update_traces(
        texttemplate='%{text}',
        textposition='inside',
        textfont_size=14,
        marker_line_color='rgba(0,0,0,0)',
        marker_line_width=1.5
    )

    return fig

def calculate_hedge_results(df_hedge, cotacao_dolar):
    if df_hedge.empty:
        return df_hedge

    df_result = df_hedge.copy()

    # Criar coluna de resultado se não existir
    if 'Resultado Calculado R$' not in df_result.columns:
        df_result['Resultado Calculado R$'] = 0.0

    # Para operações LIQUIDADAS - usar coluna 'Resultado R$' se existir
    if 'Status' in df_result.columns and 'Resultado R$' in df_result.columns:
        mask_liquidado = df_result['Status'] == 'Liquidado'
        df_result.loc[mask_liquidado, 'Resultado Calculado R$'] = df_result.loc[mask_liquidado, 'Resultado R$']

    # Para operações Não Liquidadas - calcular com cotação atual
    if 'Status' in df_result.columns:
        mask_ativo = df_result['Status'] != 'Liquidado'

        # Verificar se tem as colunas necessárias para cálculo
        if all(col in df_result.columns for col in ['Preço (cts/lb)', 'Liq. (cts/lb)', '# Sacas']):
            # Cálculo: (Liq - Preço) * Sacas * Dólar / 100
            df_result.loc[mask_ativo, 'Resultado Calculado R$'] = (
                    (df_result.loc[mask_ativo, 'Preço (cts/lb)']-df_result.loc[mask_ativo, 'Liq. (cts/lb)']) *
                    df_result.loc[mask_ativo, '# Sacas'] * cotacao_dolar * 1.3228
            )

    return df_result

def create_hedge_chart(df_hedge, df_futuros):
    fig = go.Figure()

    # === LINHA AZUL: Contratos Futuros ===
    if not df_futuros.empty:
        try:
            # Ver o que realmente tem na coluna
            print(df_futuros['Data'].head(10))
            print(df_futuros['Data'].dtype)

            df_futuros_clean = df_futuros.copy()
            df_futuros_clean['Data'] = pd.to_datetime(
                df_futuros_clean['Data'],
                infer_datetime_format=True,  # Deixa o pandas tentar identificar
                errors='coerce'
            )

            df_futuros_clean = df_futuros_clean.dropna(subset=['Data', 'KC=F'])

            fig.add_trace(go.Scatter(
                x=df_futuros_clean['Data'],
                y=df_futuros_clean['KC=F'],
                mode='lines',
                name='Futuros NY',
                line=dict(color='gray', width=4),
                hoverinfo='x+y'
            ))


        except Exception as e:
            st.warning(f"Erro ao processar futuros: {e}")

    # === PONTOS DOS CONTRATOS DE HEDGE ===
    if not df_hedge.empty and 'Preço (cts/lb)' in df_hedge.columns:
        try:
            # Verificar se tem resultado calculado
            if 'Resultado Calculado R$' not in df_hedge.columns:
                # Se não tem resultado, mostrar pontos neutros
                colors = ['gray'] * len(df_hedge)
            else:
                # Cores baseadas no resultado
                colors = []
                for resultado in df_hedge['Resultado Calculado R$']:
                    if pd.isna(resultado) or resultado == 0:
                        colors.append('gray')
                    elif resultado >= 0:
                        colors.append('green')
                    else:
                        colors.append('red')

            # Tamanhos baseados nas sacas
            sizes = [25] * len(df_hedge)  # Tamanho padrão
            if '# Sacas' in df_hedge.columns:
                sacas = pd.to_numeric(df_hedge['# Sacas'], errors='coerce').fillna(0)
                if sacas.max() > sacas.min():
                    sizes = [15 + 35 * (x - sacas.min()) / (sacas.max() - sacas.min()) for x in sacas]

            # Determinar valores do eixo X para os hedge
            x_values = None
            possible_x_cols = ['Vencimento', 'Data Liq.', 'Data', 'Código']

            for col in possible_x_cols:
                if col in df_hedge.columns:
                    x_values = df_hedge[col]
                    # Se for data, tentar converter
                    if 'Data' in col or 'Vencimento' in col:
                        try:
                            x_values = pd.to_datetime(x_values, errors='coerce')
                        except:
                            pass
                    break

            if x_values is None:
                x_values = df_hedge.index

            # Criar hover text detalhado
            hover_texts = []
            for _, row in df_hedge.iterrows():
                texto = f"<b>Contrato Hedge</b><br>"

                if 'Cliente' in row and pd.notna(row['Cliente']):
                    texto += f"<b>Cliente:</b> {row['Cliente']}<br>"

                if '# Sacas' in row and pd.notna(row['# Sacas']):
                    texto += f"<b># Sacas:</b> {row['# Sacas']:,.0f}<br>"

                if 'Preço (cts/lb)' in row and pd.notna(row['Preço (cts/lb)']):
                    texto += f"<b>Preço:</b> {row['Preço (cts/lb)']:.2f} cts/lb<br>"

                if 'Liq. (cts/lb)' in row and pd.notna(row['Liq. (cts/lb)']):
                    texto += f"<b>Liquidação:</b> {row['Liq. (cts/lb)']:.2f} cts/lb<br>"

                if 'Vencimento' in row and pd.notna(row['Vencimento']):
                    try:
                        venc_formatado = pd.to_datetime(row['Vencimento']).strftime('%d/%m/%Y')
                        texto += f"<b>Vencimento:</b> {venc_formatado}<br>"
                    except:
                        texto += f"<b>Vencimento:</b> {row['Vencimento']}<br>"

                if 'Resultado Calculado R$' in row and pd.notna(row['Resultado Calculado R$']):
                    texto += f"<b>Resultado:</b> R$ {row['Resultado Calculado R$']:,.0f}"

                hover_texts.append(texto)

            # Adicionar os pontos dos contratos hedge
            fig.add_trace(go.Scatter(
                x=x_values,
                y=df_hedge['Preço (cts/lb)'],
                mode='markers',
                name='Contratos Hedge',
                marker=dict(
                    color=colors,
                    size=sizes,
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=hover_texts,
                hovertemplate='%{text}<extra></extra>'
            ))

        except Exception as e:
            st.warning(f"Aviso: Problema ao processar contratos hedge: {e}")

    # === CONFIGURAÇÕES DO LAYOUT ===
    fig.update_layout(
        title="Futuros vs Hedge",
        xaxis_title="Período",
        yaxis_title="Preço (cts/lb)",
        height=500,
        hovermode='closest',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig


tab1, tab4, tab5, tab7, tab6 = st.tabs([
    '📊 Consolidado',
    #'👥 Por Cliente',
    #'📏 Por Peneira',
    '✨ Por Qualidade',
    '🌍 Exportação vs Mercado Interno',
    '💰 CashFlow',
    '🔄 Hedge',
])

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

# with tab2:
#     display_metrics(df_filtered)
#     col1, col2 = st.columns(2)
#     with col1:
#         st.plotly_chart(create_volume_chart(df_filtered, 'Cliente'), key="vol_2", use_container_width=True)
#     with col2:
#         st.plotly_chart(create_pie_chart(df_filtered, 'Cliente'), key="pie_2", use_container_width=True)
#
#     col3, col4 = st.columns(2)
#     with col3:
#         st.plotly_chart(create_revenue_chart(df_filtered, 'Cliente'), key="rev_2", use_container_width=True)
#     with col4:
#         st.plotly_chart(create_price_chart(df_filtered, 'Cliente'), key="price_2", use_container_width=True)
#
# with tab3:
#     display_metrics(df_filtered)
#     col1, col2 = st.columns(2)
#     with col1:
#         st.plotly_chart(create_volume_chart(df_filtered, 'peneira'), key="vol_3", use_container_width=True)
#     with col2:
#         st.plotly_chart(create_pie_chart(df_filtered, 'peneira'), key="pie_3", use_container_width=True)
#
#     col3, col4 = st.columns(2)
#     with col3:
#         st.plotly_chart(create_revenue_chart(df_filtered, 'peneira'), key="rev_3", use_container_width=True)
#     with col4:
#         st.plotly_chart(create_price_chart(df_filtered, 'peneira'), key="price_3", use_container_width=True)

with tab4:
    display_metrics(df_filtered)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_volume_chart(df_filtered, 'Qualidade'), key="vol_4", use_container_width=True)
    with col2:
        st.plotly_chart(create_pie_chart(df_filtered, 'Qualidade'), key="pie_4", use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_revenue_chart(df_filtered, 'Qualidade'), key="rev_4", use_container_width=True)
    with col4:
        st.plotly_chart(create_price_chart(df_filtered, 'Qualidade'), key="price_4", use_container_width=True)

with tab5:
    # Verificar se há dados suficientes
    has_market_data = df_filtered['Mercado'].isin(['Exportação', 'Mercado Interno']).any()

    if has_market_data:
        display_metrics(df_filtered[df_filtered['Mercado'].isin(['Exportação', 'Mercado Interno'])])

        # Adicionar comparação de tipos de mercado
        st.plotly_chart(create_market_comparison(df_filtered), use_container_width=True)

        # Comparar preços médios por tipo
        col1, col2 = st.columns(2)

        export_data = df_filtered[df_filtered['Mercado'] == 'Exportação']
        internal_data = df_filtered[df_filtered['Mercado'] == 'Mercado Interno']

        if not export_data.empty:
            with col1:
                export_price = export_data['Preço (R$/sc)'].mean()
                st.metric("Preço Médio (Exportação)",
                          f"R$ {export_price:.2f}/sc")
        else:
            with col1:
                st.metric("Preço Médio (Exportação)", "N/A")
                export_price = 0

        if not internal_data.empty:
            with col2:
                internal_price = internal_data['Preço (R$/sc)'].mean()
                st.metric("Preço Médio (Mercado Interno)",
                          f"R$ {internal_price:.2f}/sc")
        else:
            with col2:
                st.metric("Preço Médio (Mercado Interno)", "N/A")
                internal_price = 0

        # Adicionar comparativo de diferença percentual apenas se ambos existirem
        if not export_data.empty and not internal_data.empty and internal_price > 0:
            price_diff_pct = ((export_price - internal_price) / internal_price * 100)
            st.info(
                f"Café para exportação tem preço {price_diff_pct:.1f}% {'maior' if price_diff_pct > 0 else 'menor'} que o mercado interno.")
    else:
        st.warning(
            "Não há dados suficientes para exibir a comparação.")

with tab6:
    st.markdown("### Hedge")

    # Carregar dados da planilha hedge
    df_hedge_raw = load_hedge_data()
    df_futuros_raw = load_futures_data()

    if df_hedge_raw.empty:
        st.warning("⚠️ Não foi possível carregar dados da aba 'hedge'")

    else:
        # Calcular resultados
        df_hedge_processed = calculate_hedge_results(df_hedge_raw, cotacao_dolar)

        # === FILTRO SIMPLES ===
        st.markdown("#### 🔍 Filtros")

        if 'Status' in df_hedge_processed.columns:
            status_selected = st.selectbox(
                "Status dos Contratos",
                options=['Todos', 'Liquidado', 'Financeiro', 'Físico'],
                index=2,
                key="hedge_status_simple"
            )

            if status_selected == 'Todos':
                df_hedge_filtered = df_hedge_processed
            else:
                df_hedge_filtered = df_hedge_processed[df_hedge_processed['Status'] == status_selected]
        else:
            df_hedge_filtered = df_hedge_processed

        # === MÉTRICAS CORRIGIDAS ===
        col1, col2, col3 = st.columns(3)

        with col1:
            # Contratos ativos baseado no filtro
            if 'Status' in df_hedge_filtered.columns:
                if status_selected == 'Financeiro':
                    ativos = len(df_hedge_filtered[df_hedge_filtered['Status'] == 'Financeiro'])
                elif status_selected == 'Liquidado':
                    ativos = len(df_hedge_filtered[df_hedge_filtered['Status'] == 'Liquidado'])
                elif status_selected == 'Físico':
                    ativos = len(df_hedge_filtered[df_hedge_filtered['Status'] == 'Físico'])
                else:  # Todos
                    ativos = len(df_hedge_filtered['Status'])
            else:
                ativos = len(df_hedge_filtered)
            st.metric("Contratos", ativos)

        with col2:
            # Total de sacas baseado no filtro selecionado
            if '# Sacas' in df_hedge_filtered.columns:
                if status_selected == 'Financeiro':
                    total_sacas = int(df_hedge_filtered['# Sacas'].sum()) if not df_hedge_filtered.empty else 0
                elif status_selected == 'Liquidado':
                    total_sacas = int(df_hedge_filtered['# Sacas'].sum()) if not df_hedge_filtered.empty else 0
                elif status_selected == 'Físico':
                    total_sacas = int(df_hedge_filtered['# Sacas'].sum()) if not df_hedge_filtered.empty else 0
                else:
                    total_sacas = int(df_hedge_processed['# Sacas'].sum()) if not df_hedge_processed.empty else 0
                st.metric("Total de Sacas", f"{total_sacas:,}")
            else:
                st.metric("Total de Sacas", "N/A")

        with col3:
            # Resultado baseado no filtro
            if 'Resultado Calculado R$' in df_hedge_filtered.columns:
                resultado = df_hedge_filtered['Resultado Calculado R$'].sum()
                st.metric("Resultado", f"R$ {resultado:,.0f}")
            else:
                st.metric("Resultado", "N/A")

        # === GRÁFICO ===
        st.markdown("#### 📈 Comparação: Futuros vs Hedge")
        try:
            fig = create_hedge_chart(df_hedge_filtered, df_futuros_raw)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao criar gráfico: {e}")

        # === TABELA ===
        st.markdown("#### 📋 Detalhes dos Contratos")

        if not df_hedge_filtered.empty:
            # Selecionar colunas para exibir
            display_cols = []
            possible_cols = ['Cliente', 'Status', 'Código', '# Sacas', 'Preço (cts/lb)', 'Liq. (cts/lb)', 'Vencimento', 'Data Liq.']

            for col in possible_cols:
                if col in df_hedge_filtered.columns:
                    display_cols.append(col)

            if 'Resultado Calculado R$' in df_hedge_filtered.columns:
                display_cols.append('Resultado Calculado R$')

            # Mostrar info de debug
            st.info(f"Debug: Mostrando {len(df_hedge_filtered)} contratos com filtro '{status_selected}'")

            if display_cols:
                df_display = df_hedge_filtered[display_cols].copy()

                if 'Vencimento' in df_display.columns:
                    df_display['Vencimento'] = pd.to_datetime(df_display['Vencimento'], errors='coerce').dt.strftime(
                        '%d/%m/%Y')
                if 'Data Liq.' in df_display.columns:
                    df_display['Data Liq.'] = pd.to_datetime(df_display['Data Liq.'], errors='coerce').dt.strftime(
                        '%d/%m/%Y')

                # Dicionário de formatação para números
                format_dict = {}
                if 'Resultado Calculado R$' in display_cols:
                    format_dict['Resultado Calculado R$'] = 'R$ {:,.0f}'
                if '# Sacas' in display_cols:
                    format_dict['# Sacas'] = '{:,.0f}'
                if 'Preço (cts/lb)' in display_cols:
                    format_dict['Preço (cts/lb)'] = '{:.2f}'
                if 'Liq. (cts/lb)' in display_cols:
                    format_dict['Liq. (cts/lb)'] = '{:.2f}'

                st.dataframe(
                    df_display.style.format(format_dict),
                    use_container_width=True
                )

            else:
                st.dataframe(df_hedge_filtered, use_container_width=True)
        else:
            st.info("📝 Nenhum contrato encontrado com os filtros selecionados")

with tab7:
    st.markdown("### Fluxo de Caixa")

    # Função para distribuir os valores em parcelas mensais (mantida igual)
    @st.cache_data
    def calculate_cashflow(data):
        # Cópia do dataframe para não alterar o original
        df_cashflow = data.copy()

        # Converter Data Pagamento para datetime (garantir formato correto)
        df_cashflow['Data Pagamento'] = pd.to_datetime(df_cashflow['Data Pagamento'], errors='coerce')

        # Criar um DataFrame para armazenar todos os fluxos de caixa
        cashflow_entries = []

        for _, row in df_cashflow.iterrows():
            if pd.notna(row['Data Pagamento']):
                num_parcelas = row['Parcelas'] if pd.notna(row['Parcelas']) and row['Parcelas'] > 0 else 1
                valor_por_parcela = row['Receita R$'] / num_parcelas

                # Para cada parcela, criar uma entrada no fluxo de caixa
                data_base = row['Data Pagamento']
                for i in range(int(num_parcelas)):
                    data_parcela = data_base + pd.DateOffset(months=i)

                    cashflow_entries.append({
                        'Data': data_parcela,
                        'Valor': valor_por_parcela,
                        'Cliente': row['Cliente'],
                        'Mercado': row['Mercado'],
                        'Safra': row['Safra'],
                        'Parcela': i + 1,
                        'Total Parcelas': num_parcelas
                    })

        # Criar DataFrame com todas as entradas de fluxo de caixa
        if cashflow_entries:
            df_result = pd.DataFrame(cashflow_entries)

            # Agrupar por mês para visualização mensal
            df_result['Ano-Mês'] = df_result['Data'].dt.strftime('%b/%y')
            monthly_cashflow = df_result.groupby('Ano-Mês').agg({
                'Valor': 'sum',
                'Data': 'min'  # Usamos min para preservar a ordem cronológica
            }).reset_index()

            # Garantir que os meses estejam em ordem cronológica
            monthly_cashflow = monthly_cashflow.sort_values('Data')

            return df_result, monthly_cashflow
        else:
            return pd.DataFrame(), pd.DataFrame()


    # Verificar se há dados com Data Pagamento
    if df_filtered.empty or df_filtered['Data Pagamento'].notna().sum() == 0:
        st.warning(
            "Não há dados de fluxo de caixa disponíveis para os filtros selecionados.")
    else:
        # Calcular o fluxo de caixa
        df_cashflow_detailed, monthly_cashflow = calculate_cashflow(df_filtered)

        if not monthly_cashflow.empty:
            # Adicionar seletor de período para filtrar o gráfico
            min_date = monthly_cashflow['Data'].min().date()
            max_date = monthly_cashflow['Data'].max().date()

            # Adicionar margem de 1 mês para visualização melhor
            min_date_with_margin = (min_date - pd.DateOffset(months=1)).date()
            max_date_with_margin = (max_date + pd.DateOffset(months=1)).date()

            # Seletor de período
            date_range = st.slider(
                "Selecione o período para visualização do fluxo de caixa",
                min_value=min_date_with_margin,
                max_value=max_date_with_margin,
                value=(min_date_with_margin, max_date_with_margin),
                format="MMM/YY"
            )

            # Filtrar os dados pelo período selecionado
            start_date, end_date = date_range
            filtered_cashflow = monthly_cashflow[
                (monthly_cashflow['Data'].dt.date >= start_date) &
                (monthly_cashflow['Data'].dt.date <= end_date)
                ]

            # Adicionar métricas na barra superior
            total_sacas = int(df_filtered['# Sacas'].sum())
            total_revenue_periodo = filtered_cashflow['Valor'].sum()
            avg_price = total_revenue_periodo / total_sacas if total_sacas > 0 else 0

            cols = st.columns(3)
            with cols[0]:
                st.metric("Sacas Vendidas no Período Selecionado", f"{total_sacas:,}")
            with cols[1]:
                st.metric("Faturamento no Período Selecionado", f"R$ {total_revenue_periodo:,.0f}")
            with cols[2]:
                st.metric("Valor médio da saca", f"R$ {avg_price:.2f}/sc")

            # Criar o gráfico de barras para o fluxo de caixa mensal
            fig_cashflow = px.bar(
                filtered_cashflow,
                x='Ano-Mês',
                y='Valor',
                title='Fluxo de Caixa Mensal (R$)',
                labels={'Valor': 'Valor (R$)', 'Ano-Mês': 'Mês'}
            )

            fig_cashflow.update_layout(
                xaxis=dict(tickangle=45),
                yaxis=dict(title='Valor (R$)'),
                height=500
            )

            # Mostrar o gráfico
            st.plotly_chart(fig_cashflow, use_container_width=True)

            # Adicionar gráfico de fluxo de caixa acumulado
            filtered_cashflow['Valor Acumulado'] = filtered_cashflow['Valor'].cumsum()

            fig_cumulative = px.area(
                filtered_cashflow,
                x='Ano-Mês',
                y='Valor Acumulado',
                title='Fluxo de Caixa Acumulado (R$)',
                markers=True,
                labels={'Valor Acumulado': 'Valor Acumulado (R$)', 'Ano-Mês': 'Mês'}
            )

            # Configurações adicionais para melhorar a aparência
            fig_cumulative.update_traces(
                line=dict(width=2, color='blue'),  # Cor e espessura da linha
                marker=dict(size=5, color='blue'),  # Tamanho e cor dos marcadores
                fill='tozeroy',  # Preencher até o eixo y=0
                fillcolor='rgba(0, 123, 255, 0.7)'  # Cor para o preenchimento
            )

            fig_cumulative.update_layout(
                xaxis=dict(tickangle=45),
                yaxis=dict(title='Valor Acumulado (R$)'),
                height=500,
                hovermode='x unified'  # Mostra todos os pontos ao passar o mouse sobre uma data
            )

            st.plotly_chart(fig_cumulative, use_container_width=True)

            # Adicionar tabela detalhada por cliente
            if st.checkbox("Exibir detalhes por cliente"):
                # Obter dados filtrados para o período selecionado
                cliente_cashflow_data = df_cashflow_detailed[
                    (df_cashflow_detailed['Data'].dt.date >= start_date) &
                    (df_cashflow_detailed['Data'].dt.date <= end_date)
                    ]

                # Adicionar uma coluna para ordenação de meses
                cliente_cashflow_data['Mês_Ordem'] = cliente_cashflow_data['Data'].dt.strftime('%Y%m')

                # Criar um dicionário para mapear 'Ano-Mês' para 'Mês_Ordem'
                mes_para_ordem = cliente_cashflow_data.groupby('Ano-Mês')['Mês_Ordem'].first().to_dict()

                # Agrupar por cliente e mês
                cliente_cashflow = cliente_cashflow_data.groupby(['Cliente', 'Ano-Mês']).agg({
                    'Valor': 'sum'
                }).reset_index()

                # Pivotar a tabela
                cliente_pivot = cliente_cashflow.pivot(
                    index='Cliente',
                    columns='Ano-Mês',
                    values='Valor'
                ).fillna(0)

                # Obter uma lista ordenada dos meses baseada na data real
                meses_ordenados = sorted(
                    cliente_cashflow['Ano-Mês'].unique(),
                    key=lambda x: mes_para_ordem.get(x, '999999')  # Usar o dicionário para ordenação
                )

                # Reordenar as colunas conforme a ordem cronológica dos meses
                cliente_pivot = cliente_pivot[meses_ordenados]

                # Adicionar total por cliente
                cliente_pivot['Total'] = cliente_pivot.sum(axis=1)

                # Ordenar por total
                cliente_pivot = cliente_pivot.sort_values('Total', ascending=False)

                # Adicionar linha de total por mês
                total_por_mes = pd.DataFrame(cliente_pivot.sum(axis=0)).T
                total_por_mes.index = ['Total por Mês']

                # Concatenar com a tabela principal
                tabela_final = pd.concat([cliente_pivot, total_por_mes])

                # Exibir a tabela formatada
                st.dataframe(
                    tabela_final.style.format("{:,.0f}").apply(
                        lambda x: ['background-color: #f0f2f6' if x.name == 'Total por Mês' else '' for i in x],
                        axis=1
                    ),
                    use_container_width=True
                )

        else:
            st.warning(
                "Não há dados de fluxo de caixa disponíveis para os filtros selecionados.")

if st.sidebar.checkbox("📋 Exibir tabela de dados"):
    st.dataframe(df_filtered)
