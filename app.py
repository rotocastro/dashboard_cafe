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

# Definição do client_info (mantido do código original)
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


# Adicionar controle para ajustar a cotação do dólar na sidebar
st.sidebar.title("Configurações")

cotacao_dolar = st.sidebar.number_input(
    "💱 Cotação do Dólar (R$)",
    min_value=1.0,
    max_value=10.0,
    value=5.70,
    step=0.05,
    format="%.2f",
    help="Ajuste a cotação do dólar para recalcular os valores em reais"
)


# Função para buscar a data da última atualização
@st.cache_data(show_spinner=False)
def get_last_update_date():
    try:
        # Ler a célula A1 da aba "futuros"
        df_futuros = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="futuros", header=None, nrows=1, usecols=[0])
        last_update = df_futuros.iloc[0, 0]

        # Tentar converter para datetime se for string
        if isinstance(last_update, str):
            try:
                last_update = pd.to_datetime(last_update)
            except:
                return last_update  # Retorna como string se não conseguir converter

        # Se for datetime, formatar para exibição
        if isinstance(last_update, pd.Timestamp):
            return last_update.strftime("%d/%m/%Y")
        else:
            return str(last_update)
    except Exception as e:
        return "Data não disponível"


# Buscar e exibir a data da última atualização
ultima_atualizacao = get_last_update_date()
st.sidebar.markdown(f"<small>📅 Última atualização: {ultima_atualizacao}</small>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data(dolar_value):
    # Carregue seus dados existentes
    df = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="Sheet2")
    df_hist = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="medias_diarias")

    df["Peneira"] = df["Peneira"].astype(str)

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

    # Converter 'Data Pagamento' para datetime
    df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce')


    return df, df_hist

# Passar a cotação do dólar como parâmetro para a função load_data
df, df_hist = load_data(cotacao_dolar)

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
                                default=[2024, 2025])

incluir_estimativas = st.sidebar.checkbox("📈 Incluir Estoque", value=False)


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


def create_temporal_analysis(data, historico):
    # Verificar se temos dados de pagamento e preço:
    if data.empty or data["Data Pagamento"].isna().all() or historico.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Sem dados suficientes para análise temporal",
            annotations=[dict(
                text="Não há dados de pagamento ou histórico para os filtros selecionados",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=16)
            )]
        )
        return fig

    fig = go.Figure()

    # Verificar qual coluna usar para o preço médio histórico
    price_column = None
    if 'Preco_medio' in historico.columns:
        price_column = 'Preco_medio'
    elif 'Saca (R$)' in historico.columns:
        price_column = 'Saca (R$)'

    # Garantir que a Data existe e está em formato datetime
    if 'Data' in historico.columns and price_column and not historico.empty:
        # Certificar que a Data está em formato datetime
        if not pd.api.types.is_datetime64_any_dtype(historico['Data']):
            historico['Data'] = pd.to_datetime(historico['Data'], errors='coerce')

        # Ordenar os dados históricos por data
        historico_sorted = historico.sort_values('Data')

        # Verificar se existem valores NaN e remover ou preencher conforme necessário
        historico_sorted = historico_sorted.dropna(subset=['Data', price_column])

        # Verificar se ainda temos dados após a limpeza
        if not historico_sorted.empty:
            # Adicionar a linha de média histórica
            fig.add_trace(go.Scatter(
                x=historico_sorted['Data'],
                y=historico_sorted[price_column],
                mode='lines',
                name='NY * Dólar',
                line=dict(color='rgba(31, 119, 180, 0.8)', width=2),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Preço Médio: R$ %{y:.2f}/sc<extra></extra>'
            ))

        # Filtrar apenas os dados com data de pagamento
        data_com_data = data.dropna(subset=['Data Pagamento'])

        if not data_com_data.empty:
            # Certificar que a Data Pagamento está em formato datetime
            if not pd.api.types.is_datetime64_any_dtype(data_com_data['Data Pagamento']):
                data_com_data['Data Pagamento'] = pd.to_datetime(data_com_data['Data Pagamento'], errors='coerce')

            # Remover linhas onde Data Pagamento for NaT após a conversão
            data_com_data = data_com_data.dropna(subset=['Data Pagamento'])

            if not data_com_data.empty:
                # Para cada contrato, criar um ponto no scatter
                scatter_data = data_com_data.copy()

                # Usar a coluna 'Código' existente, ou criar um ID temporário se não existir
                if 'Código' not in scatter_data.columns:
                    scatter_data['codigo_display'] = scatter_data.index.astype(str)
                else:
                    scatter_data['codigo_display'] = scatter_data['Código']

                # Calcular preço médio para cada contrato
                scatter_data['preco_medio_contrato'] = scatter_data['Preço (R$/sc)']

                # Verificar se os valores são numéricos
                if not pd.api.types.is_numeric_dtype(scatter_data['preco_medio_contrato']):
                    # Tentar converter para numérico
                    scatter_data['preco_medio_contrato'] = pd.to_numeric(
                        scatter_data['preco_medio_contrato'], errors='coerce')

                # Remover linhas com preços não numéricos
                scatter_data = scatter_data.dropna(subset=['preco_medio_contrato'])

                if not scatter_data.empty:
                    # Criar o texto para hover incluindo a qualidade
                    scatter_data['hover_text'] = scatter_data.apply(
                        lambda row: f"Código: {row['codigo_display']}<br>" +
                                    f"Cliente: {row['Cliente']}<br>" +
                                    f"Qualidade: {row.get('Qualidade', 'N/A')}<br>" +
                                    f"Diferencial: {row.get('Diferencial'):.0f}<br>" +
                                    f"Sacas: {int(row['# Sacas']):,}<br>" +
                                    f"Valor Médio: R$ {row['preco_medio_contrato']:.2f}/sc",
                        axis=1
                    )

                    # Calcular tamanho dos pontos (proporcional ao número de sacas)
                    # Garantir que '# Sacas' seja numérico
                    if not pd.api.types.is_numeric_dtype(scatter_data['# Sacas']):
                        scatter_data['# Sacas'] = pd.to_numeric(scatter_data['# Sacas'], errors='coerce')
                        scatter_data = scatter_data.dropna(subset=['# Sacas'])

                    if not scatter_data.empty:
                        min_size = 5  # Tamanho mínimo
                        max_size = scatter_data['# Sacas'].max()

                        # Evitar divisão por zero se todas as sacas tiverem o mesmo valor
                        if max_size > 0:
                            scatter_data['marker_size'] = (scatter_data['# Sacas'] / max_size * 30) + min_size
                        else:
                            scatter_data['marker_size'] = min_size

                        # Adicionar scatter para os contratos
                        fig.add_trace(go.Scatter(
                            x=scatter_data['Data Pagamento'],
                            y=scatter_data['preco_medio_contrato'],
                            mode='markers',
                            name='Contratos',
                            marker=dict(
                                size=scatter_data['marker_size'],
                                color=scatter_data['# Sacas'],
                                colorscale='Viridis',
                                opacity=0.7,
                                colorbar=dict(title="Sacas"),
                                line=dict(width=1, color='DarkSlateGrey')
                            ),
                            text=scatter_data['hover_text'],
                            hoverinfo='text'
                        ))

        # Configurar o layout
        fig.update_layout(
            title='Análise Temporal de Preços',
            xaxis_title='Data',
            yaxis_title='Preço Médio (R$/sc)',
            hovermode='closest',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=40, b=10),
            height=600
        )

        return fig


tab1, tab4, tab5, tab7 = st.tabs([
    '📊 Consolidado',
    #'👥 Por Cliente',
    #'📏 Por Peneira',
    '✨ Por Qualidade',
    '🌍 Exportação vs Mercado Interno',
    '💰 CashFlow',
    #'📅 Análise Temporal',

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

#with tab6:
    st.markdown("### Análise Temporal de Preços")

    display_metrics(df_filtered)

    # Determinar qual coluna usar para o preço médio histórico
    price_column = None
    if not df_hist.empty:
        if 'Preco_medio' in df_hist.columns:
            price_column = 'Preco_medio'
        elif 'Saca (R$)' in df_hist.columns:
            price_column = 'Saca (R$)'

    # Verificar se temos dados suficientes
    has_temporal_data = (
            not df_filtered.empty and
            df_filtered['Data Pagamento'].notna().any() and
            not df_hist.empty and
            'Data' in df_hist.columns and
            price_column is not None
    )

    if has_temporal_data:
        # Certificar que as datas estão em formato datetime
        if not pd.api.types.is_datetime64_any_dtype(df_hist['Data']):
            df_hist['Data'] = pd.to_datetime(df_hist['Data'], errors='coerce')

        if not pd.api.types.is_datetime64_any_dtype(df_filtered['Data Pagamento']):
            df_filtered['Data Pagamento'] = pd.to_datetime(df_filtered['Data Pagamento'], errors='coerce')

        # Remover valores NaT
        df_hist_clean = df_hist.dropna(subset=['Data'])
        df_filtered_clean = df_filtered.dropna(subset=['Data Pagamento'])

        # Calcular data mínima para a visualização (3 meses antes do primeiro pagamento)
        first_payment_date = df_filtered_clean['Data Pagamento'].min() if not df_filtered_clean.empty else None

        if first_payment_date:
            # Calcular data 3 meses antes do primeiro pagamento
            first_date_minus_3months = (first_payment_date - pd.DateOffset(months=3)).date()
            # Garantir que a data mínima não seja anterior ao primeiro dado histórico
            hist_min_date = df_hist_clean['Data'].min().date() if not df_hist_clean.empty else None
            if hist_min_date:
                # Usar a data mais recente entre o histórico mínimo e 3 meses antes do primeiro pagamento
                min_date = max(hist_min_date, first_date_minus_3months)
            else:
                min_date = first_date_minus_3months
        else:
            # Se não houver pagamentos, usar o mínimo histórico
            min_date = df_hist_clean['Data'].min().date() if not df_hist_clean.empty else None

        max_date = df_hist_clean['Data'].max().date() if not df_hist_clean.empty else None

        # Criar o slider para seleção de período apenas se tivermos datas válidas
        if min_date and max_date:
            # Verificar se min_date não é maior que max_date
            if min_date <= max_date:
                date_range = st.slider(
                    "Selecione o período para visualização da análise temporal",
                    min_value=min_date,
                    max_value=max_date,
                    value=(min_date, max_date),
                    format="MMM/YY"
                )

                # Obter as datas do slider
                start_date, end_date = date_range

                # Filtrar dados históricos pelo período selecionado
                filtered_hist = df_hist_clean.copy()
                filtered_hist = filtered_hist[
                    (filtered_hist['Data'].dt.date >= start_date) &
                    (filtered_hist['Data'].dt.date <= end_date)
                    ]

                # Exibir gráfico apenas se existirem dados no período
                if not filtered_hist.empty:
                    # Exibir o gráfico de análise temporal
                    temporal_chart = create_temporal_analysis(df_filtered_clean, filtered_hist)
                    st.plotly_chart(temporal_chart, use_container_width=True)

                    # Adicionar estatísticas complementares
                    st.markdown("### Estatísticas do Período Selecionado")

                    # Calcular estatísticas dos dados históricos (removendo mediana e desvio padrão)
                    if price_column in filtered_hist.columns:
                        hist_stats = {
                            'Média': filtered_hist[price_column].mean(),
                            'Mínimo': filtered_hist[price_column].min(),
                            'Máximo': filtered_hist[price_column].max()
                        }

                        # Filtrar contratos do período selecionado
                        contratos_periodo = df_filtered_clean[
                            (df_filtered_clean['Data Pagamento'].dt.date >= start_date) &
                            (df_filtered_clean['Data Pagamento'].dt.date <= end_date)
                            ]

                        if not contratos_periodo.empty:
                            # Verificar se Preço (R$/sc) é numérico
                            if not pd.api.types.is_numeric_dtype(contratos_periodo['Preço (R$/sc)']):
                                contratos_periodo['Preço (R$/sc)'] = pd.to_numeric(
                                    contratos_periodo['Preço (R$/sc)'], errors='coerce')

                            # Ignorar valores não numéricos
                            contratos_periodo = contratos_periodo.dropna(subset=['Preço (R$/sc)'])

                            if not contratos_periodo.empty:
                                contratos_stats = {
                                    'Média': contratos_periodo['Preço (R$/sc)'].mean(),
                                    'Mínimo': contratos_periodo['Preço (R$/sc)'].min(),
                                    'Máximo': contratos_periodo['Preço (R$/sc)'].max(),
                                    'Total de Contratos': len(contratos_periodo),
                                    'Total de Sacas': contratos_periodo['# Sacas'].sum()
                                }

                                # Exibir estatísticas em colunas
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("#### Dados históricos")
                                    for label, value in hist_stats.items():
                                        if label in ['Média', 'Mínimo', 'Máximo']:
                                            st.metric(label, f"R$ {value:.2f}/sc")

                                with col2:
                                    st.markdown("#### Contratos no período")
                                    for label, value in contratos_stats.items():
                                        if label in ['Média', 'Mínimo', 'Máximo']:
                                            st.metric(label, f"R$ {value:.2f}/sc")
                                        elif label == 'Total de Sacas':
                                            st.metric(label, f"{int(value):,}")
                                        elif label == 'Total de Contratos':
                                            st.metric(label, f"{int(value)}")

                                # Exibir tabela de contratos
                                if st.checkbox("Exibir tabela de contratos"):
                                    # Selecionar e formatar colunas relevantes
                                    contratos_table = contratos_periodo[[
                                        'Cliente', 'Data Pagamento', '# Sacas', 'Preço (R$/sc)', 'Receita R$', 'tipo'
                                    ]].copy()

                                    # Ordenar por data
                                    contratos_table = contratos_table.sort_values('Data Pagamento')

                                    # Formatar colunas numéricas
                                    contratos_table['# Sacas'] = contratos_table['# Sacas'].apply(
                                        lambda x: f"{int(x):,}")
                                    contratos_table['Preço (R$/sc)'] = contratos_table['Preço (R$/sc)'].apply(
                                        lambda x: f"R$ {x:.2f}")
                                    contratos_table['Receita R$'] = contratos_table['Receita R$'].apply(
                                        lambda x: f"R$ {x:,.2f}")

                                    # Renomear colunas para melhor visualização
                                    contratos_table.columns = [
                                        'Cliente', 'Data Pagamento', 'Sacas', 'Valor/Saca', 'Receita Total', 'Tipo'
                                    ]

                                    # Exibir tabela
                                    st.dataframe(contratos_table, use_container_width=True)
                        else:
                            st.warning("Não há contratos no período selecionado.")
                else:
                    st.warning(
                        "Não há dados históricos disponíveis para o período selecionado."
                    )
            else:
                st.warning(
                    "Problema com as datas: a data mínima é maior que a data máxima."
                )
        else:
            st.warning(
                "Não foi possível determinar o período de análise devido a problemas com as datas."
            )
    else:
        st.warning(
            "Não há dados suficientes para exibir a análise temporal. Verifique se existem dados históricos e contratos com datas de pagamento."
        )

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
