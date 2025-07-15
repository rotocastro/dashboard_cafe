# ☕ Dashboard de Vendas de Café

Um dashboard interativo desenvolvido em Streamlit para análise e visualização de vendas de café, incluindo controle de hedge e fluxo de caixa.

## 🚀 Funcionalidades

### 📊 Análises Principais
- **Consolidado Geral**: Visão completa das vendas com métricas principais
- **Análise por Qualidade**: Segmentação detalhada por tipo de café
- **Comparação de Mercados**: Exportação vs Mercado Interno
- **Fluxo de Caixa**: Projeção de recebimentos com distribuição em parcelas
- **Controle de Hedge**: Acompanhamento de contratos futuros e resultados

### 🎯 Métricas Principais
- Total de sacas vendidas
- Faturamento total em R$
- Valor médio por saca
- Comparação de preços entre mercados
- Resultados de operações de hedge

### 📈 Visualizações
- Gráficos de volume por cliente/qualidade
- Análise de participação (pizza)
- Comparação de faturamento
- Evolução de preços
- Gráfico de futuros vs hedge
- Fluxo de caixa mensal e acumulado

## 🛠️ Tecnologias Utilizadas

- **Python 3.7+**
- **Streamlit** - Framework web para dashboards
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **OpenPyXL** - Leitura de arquivos Excel

## 📋 Pré-requisitos

### Arquivo de Dados
O dashboard requer um arquivo Excel (`vendas_cafe_em_reais.xlsx`) com as seguintes abas:

1. **Sheet2** (dados principais):
   - Safra, Cliente, Mercado, Qualidade, Peneira
   - # Sacas, Preço (u$/sc), Preço (R$/sc)
   - PTAX, Receita R$, Data Pagamento, Parcelas

2. **hedge** (contratos de hedge):
   - Cliente, Status, Código, # Sacas
   - Preço (cts/lb), Liq. (cts/lb)
   - Vencimento, Data Liq., Resultado R$

3. **futuros** (cotações futuras):
   - Data, KC=F (preços futuros)

## 🚀 Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/rotocastro/dashboard_cafe.git
cd dashboard_cafe
```

2. **Instale as dependências**:
```bash
pip install streamlit pandas plotly openpyxl
```

3. **Adicione o arquivo de dados**:
   - Coloque o arquivo `vendas_cafe_em_reais.xlsx` na pasta raiz do projeto

## ▶️ Como Executar

1. **Execute o dashboard**:
```bash
streamlit run app.py
```

2. **Acesse no navegador**:
   - O dashboard será aberto automaticamente em `http://localhost:8501`

## 🎛️ Como Usar

### Configurações Laterais
- **Cotação do Dólar**: Ajuste para recalcular valores em reais
- **Filtros**: Selecione safras, mercados, clientes e qualidades
- **Incluir Estoque**: Opção para incluir/excluir dados de estoque

### Navegação por Abas
1. **📊 Consolidado**: Visão geral de todas as vendas
2. **✨ Por Qualidade**: Análise segmentada por tipo de café
3. **🌍 Exportação vs Mercado Interno**: Comparação entre mercados
4. **💰 CashFlow**: Projeção de recebimentos
5. **🔄 Hedge**: Controle de operações financeiras

### Detalhes dos Clientes
- Clique em "👥 Mostrar Detalhes dos Clientes" para ver:
  - Informações gerais (localização, movimentação)
  - Dados financeiros históricos
  - Credit score e métricas de performance

## 📊 Estrutura dos Dados

### Campos Principais
- **Safra**: Ano da safra do café
- **Cliente**: Nome do comprador
- **Mercado**: Exportação ou Mercado Interno
- **Qualidade**: Tipo/qualidade do café
- **Peneira**: Classificação por tamanho
- **# Sacas**: Quantidade vendida
- **Preços**: Em USD e BRL por saca
- **PTAX**: Taxa de câmbio utilizada

### Campos de Hedge
- **Status**: Liquidado, Financeiro, Físico
- **Preços**: Em centavos por libra
- **Resultado**: Ganho/perda da operação

## 🔧 Personalização

### Adicionar Novos Clientes
Para incluir informações detalhadas de novos clientes, edite a variável `client_info` no código:

```python
client_info = {
    "Nome_Cliente": {
        "Nome": "Razão Social",
        "Cidade": "Cidade",
        "País": "País",
        "Movimentação": "Volume estimado",
        "Produto de Interesse": "Tipo de café",
        "Financeiro": {
            2024: {"Receita": "...", "Lucro Líquido": "..."}
        }
    }
}
```

### Modificar Cores
As paletas de cores são definidas nas variáveis:
- `COLORS_PENEIRAS`
- `COLORS_CLIENTES`
- `COLORS_QUALIDADES`

## 📈 Funcionalidades Avançadas

### Cálculo Automático de Hedge
- Contratos liquidados usam resultado real
- Contratos ativos calculam resultado com cotação atual
- Fórmula: `(Preço - Liquidação) × Sacas × Dólar × 1.3228`

### Fluxo de Caixa Inteligente
- Distribui automaticamente valores em parcelas mensais
- Considera data de pagamento e número de parcelas
- Gera projeção acumulada

### Cache Inteligente
- Dados são cached para melhor performance
- Recalculo automático quando cotação muda

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Contato

Para dúvidas ou sugestões, entre em contato através do GitHub.

---

**Desenvolvido com ☕ por [rotocastro](https://github.com/rotocastro)**
