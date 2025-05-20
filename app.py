import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import calendar
import yfinance as yf

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

@st.cache_data(show_spinner=False)
def load_data(dolar_value):
    # Carregue seus dados existentes
    df = pd.read_excel("vendas_cafe_em_reais.xlsx")
    #df_hist = pd.read_excel("vendas_cafe_em_reais.xlsx", sheet_name="medias_historicas")

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

    # Converter 'Data Pagamento' para datetime
    df['Data Pagamento'] = pd.to_datetime(df['Data Pagamento'], errors='coerce')

    return df

# Passar a cotação do dólar como parâmetro para a função load_data
df = load_data(cotacao_dolar)

    # # Função para obter dados do Yahoo Finance
    # @st.cache_data(ttl=3600)  # Cache por 1 hora
    # def get_yahoo_finance_data(ticker, start_date, end_date):
    #     data = yf.download(ticker, start=start_date, end=end_date)
    #     return data

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


st.sidebar.title("Filtros")

safras = st.sidebar.multiselect("Safras",
                                options=sorted(df['safra'].unique()),
                                default=[2024])

incluir_estimativas = st.sidebar.checkbox("📈 Incluir Estoque", value=False)

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

qualidades = st.sidebar.multiselect("Qualidades",
                                    options=sorted([str(p) for p in df['qualidade'].unique() if pd.notna(p)]),
                                    default=sorted([str(p) for p in df['qualidade'].unique() if pd.notna(p)]))

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


def create_market_comparison(data):
    # Verificar se há dados suficientes
    if data.empty or not data['tipo'].isin(['Exportação', 'Mercado Interno']).any():
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
    market_comp = data.groupby('tipo').agg({
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

    # Resto do código permanece igual...
    # Criar o gráfico de barras
    fig = px.bar(
        market_comp,
        x='tipo',
        y='# Sacas',
        color='tipo',
        title='Comparação entre Tipos de Mercado',
        text='text',
        hover_data={
            '# Sacas': False,
            'text': False,
            'tipo': True,
            'hover_text': True
        }
    )

    # Adicionar anotações com as porcentagens
    for i, row in market_comp.iterrows():
        fig.add_annotation(
            x=row['tipo'],
            y=row['# Sacas'] * 1.05,
            text=f"{row['Percentual']}%",
            showarrow=False,
            font=dict(size=14, color="black")
        )

    # Ajustar o layout
    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        xaxis_title="Tipo de Mercado",
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


tab1, tab4, tab5, tab7 = st.tabs([
    '📊 Consolidado',
    #'👥 Por Cliente',
    #'📏 Por Peneira',
    '✨ Por Qualidade',
    '🌍 Exportação vs Mercado Interno',
    '💰 CashFlow'
    #'📅 Análise Temporal',

])

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
        st.plotly_chart(create_volume_chart(df_filtered, 'qualidade'), key="vol_4", use_container_width=True)
    with col2:
        st.plotly_chart(create_pie_chart(df_filtered, 'qualidade'), key="pie_4", use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_revenue_chart(df_filtered, 'qualidade'), key="rev_4", use_container_width=True)
    with col4:
        st.plotly_chart(create_price_chart(df_filtered, 'qualidade'), key="price_4", use_container_width=True)

with tab5:
    # Verificar se há dados suficientes
    has_market_data = df_filtered['tipo'].isin(['Exportação', 'Mercado Interno']).any()

    if has_market_data:
        display_metrics(df_filtered[df_filtered['tipo'].isin(['Exportação', 'Mercado Interno'])])

        # Adicionar comparação de tipos de mercado
        st.plotly_chart(create_market_comparison(df_filtered), use_container_width=True)

        # Comparar preços médios por tipo
        col1, col2 = st.columns(2)

        export_data = df_filtered[df_filtered['tipo'] == 'Exportação']
        internal_data = df_filtered[df_filtered['tipo'] == 'Mercado Interno']

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
            "Não há dados suficientes para exibir a comparação entre Exportação e Mercado Interno. Verifique os filtros aplicados.")

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
                        'tipo': row['tipo'],
                        'safra': row['safra'],
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
            "Não há dados de fluxo de caixa disponíveis para os filtros selecionados. Verifique se as datas de pagamento estão preenchidas corretamente.")
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
                "Não há dados de fluxo de caixa disponíveis para os filtros selecionados. Verifique se as datas de pagamento estão preenchidas corretamente.")

if st.sidebar.checkbox("📋 Exibir tabela de dados"):
    st.dataframe(df_filtered)
