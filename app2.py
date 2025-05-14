import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da página ---
st.set_page_config(page_title="Dashboard de Efetivo", layout="wide")

# --- Estilos CSS com tema e sidebar flutuante ---
modo_escuro = st.sidebar.toggle("🌙 Modo Escuro", value=False)

cor_fundo = "#0e1117" if modo_escuro else "#ffffff"
cor_texto = "#ffffff" if modo_escuro else "#000000"
cor_sidebar = "#161b22" if modo_escuro else "#f0f2f6"

css = f"""
<style>
body {{
    background-color: {cor_fundo};
    color: {cor_texto};
}}

[data-testid="stSidebar"] {{
    position: fixed;
    left: -300px;
    top: 0;
    width: 300px;
    height: 100%;
    background-color: {cor_sidebar};
    transition: left 0.3s ease;
    z-index: 100;
}}

[data-testid="stSidebar"]:hover {{
    left: 0;
}}

[data-testid="stSidebar"]::before {{
    content: '';
    position: fixed;
    left: 0;
    top: 0;
    width: 20px;
    height: 100%;
    background: transparent;
    z-index: 101;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Carregamento dos dados ---
@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_excel(arquivo, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'DIRETO / INDIRETO' in df.columns:
        df['Tipo'] = df['DIRETO / INDIRETO'].astype(str).str.upper().str.strip()
    else:
        df['Tipo'] = 'INDEFINIDO'

    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
    return df

st.title("📊 Análise de Efetivo - Abril 2025")

# Carregar o arquivo Excel diretamente
df = carregar_dados("efetivo_abril.xlsx")

# --- Filtros ---
st.sidebar.header("🔍 Filtros")
lista_obras = sorted(df['Obra'].astype(str).unique())
lista_obras.insert(0, 'Todos')  # Adiciona a opção "Todos" no início
obra_selecionada = st.sidebar.radio("Obra:", lista_obras, horizontal=True)

# Outros filtros
tipo_selecionado = st.sidebar.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
tipo_analise = st.sidebar.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
qtd_linhas = st.sidebar.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)

# Aplicar filtros gerais
if obra_selecionada == 'Todos':
    df_filtrado = df  # Não filtra por obra se "Todos" for selecionado
else:
    df_filtrado = df[df['Obra'] == obra_selecionada]

if tipo_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("👷 Direto", len(df_filtrado[df_filtrado['Tipo'] == 'DIRETO']))
col2.metric("👷‍♂️ Indireto", len(df_filtrado[df_filtrado['Tipo'] == 'INDIRETO']))
col3.metric("🏗️ Terceiro", len(df_filtrado[df_filtrado['Tipo'] == 'TERCEIRO']))
col4.metric("👥 Total", len(df_filtrado))

st.divider()

# --- GRÁFICO PIZZA + TABELA ---
col_g1, col_g2 = st.columns([1, 2])

with col_g1:
    df_pizza = df[df['Obra'].isin(obras_selecionadas)]
    pizza = df_pizza['Tipo'].value_counts().reset_index()
    pizza.columns = ['Tipo', 'count']
    fig_pizza = px.pie(pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo',
                       color_discrete_sequence=px.colors.sequential.Plasma)
    st.plotly_chart(fig_pizza, use_container_width=True)

with col_g2:
    coluna_valor = {
        'Produção': 'PRODUÇÃO',
        'Hora Extra Semana': 'Hora Extra 70% - Semana',
        'Hora Extra Sábado': 'Hora Extra 70% - Sabado'
    }[tipo_analise]

    valor_total = df_filtrado[coluna_valor].sum()
    st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
    st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    ranking = df_filtrado.groupby(['Funcionário', 'Função', 'Obra', 'Tipo'])[coluna_valor] \
                         .sum().reset_index().sort_values(by=coluna_valor, ascending=False)

    if qtd_linhas != 'Todos':
        ranking = ranking.head(int(qtd_linhas))

    # Formatar como R$
    ranking[coluna_valor] = ranking[coluna_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(ranking, use_container_width=True)

# --- GRÁFICO DE BARRAS (embaixo) ---
st.divider()
col_bar = st.container()
with col_bar:
    graf_funcao = df_filtrado['Função'].value_counts().reset_index()
    graf_funcao.columns = ['Função', 'Qtd']
    fig_bar = px.bar(graf_funcao, x='Função', y='Qtd', title='Efetivo por Função', text='Qtd',
                     color='Qtd', color_continuous_scale='Blues')
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# --- GRÁFICO DE DISPERSÃO ---
st.divider()
st.markdown("### 🔍 Correlação: Produção vs. Hora Extra Total")
fig_disp = px.scatter(df_filtrado,
                      x="Total Extra",
                      y="PRODUÇÃO",
                      color="Tipo",
                      hover_data=["Funcionário", "Função", "Obra"],
                      trendline="ols",
                      labels={"Total Extra": "Hora Extra Total", "PRODUÇÃO": "Produção"},
                      title="Dispersão: Hora Extra Total vs Produção")
st.plotly_chart(fig_disp, use_container_width=True)
