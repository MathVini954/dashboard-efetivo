import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuração da página ---
st.set_page_config(page_title="Dashboard Integrado", layout="wide")

# --- Estilo escuro e CSS customizado ---
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
    background-color: {cor_sidebar};
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Funções compartilhadas ---
@st.cache_data
def carregar_dados_produtividade():
    df = pd.read_excel("produtividade.xlsx")
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
    df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')
    return df

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['Tipo'] = df.get('DIRETO / INDIRETO', 'INDEFINIDO').astype(str).str.upper().str.strip()
    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
    return df

# --- Tabs do app ---
aba = st.tabs(["📈 Produtividade", "📊 Efetivo"])

# ========== PRODUTIVIDADE ==========
with aba[0]:
    st.title("📈 Dashboard de Produtividade")

    df_prod = carregar_dados_produtividade()

    tipo_obra_opcoes = ["Todos"] + df_prod['TIPO_OBRA'].unique().tolist()
    tipo_obra = st.sidebar.selectbox('Tipo de Obra', tipo_obra_opcoes)

    servicos_opcoes = df_prod['SERVIÇO'].unique().tolist()
    servico = st.sidebar.selectbox('Serviço', servicos_opcoes)

    datas_opcoes = ["Todos"] + df_prod['DATA_FORMATADA'].unique().tolist()
    datas_sel = st.sidebar.multiselect("Mês/Ano", datas_opcoes, default=datas_opcoes)

    # Filtro
    df_f = df_prod.copy()
    if tipo_obra != "Todos":
        df_f = df_f[df_f['TIPO_OBRA'] == tipo_obra]
    if servico:
        df_f = df_f[df_f['SERVIÇO'] == servico]
    if datas_sel and "Todos" not in datas_sel:
        df_f = df_f[df_f['DATA_FORMATADA'].isin(datas_sel)]

    # Gráficos
    df_mensal = df_f.groupby('DATA_FORMATADA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean',
        'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'
    }).reset_index()

    fig_linha = px.line(df_mensal, x='DATA_FORMATADA',
                        y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                        labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                        title="Produtividade Real x Orçada",
                        markers=True,
                        template='plotly_dark' if modo_escuro else 'plotly_white')
    fig_linha.update_layout(width=900, height=500)
    st.plotly_chart(fig_linha)

    df_tipo = df_f.groupby('TIPO_OBRA').agg({'PRODUTIVIDADE_PROF_DIAM2': 'mean'}).reset_index()
    fig_barra = px.bar(df_tipo, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                       title="Produtividade Média por Tipo de Obra",
                       template='plotly_dark' if modo_escuro else 'plotly_white')
    fig_barra.update_layout(width=900, height=500)
    st.plotly_chart(fig_barra)


 # ========== EFETIVO ==========
with aba[1]:
    # Este é o código de análise de "Efetivo"
    st.title("📊 Análise de Efetivo - Abril 2025")

    # Carregar os dados de efetivo
   uploaded_file = st.file_uploader("efetivo_abril", type="xlsx")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df.columns = df.columns.str.strip()
    # Restante do seu código


    # FILTROS
    st.sidebar.header("🔍 Filtros")
    lista_obras = sorted(df['Obra'].astype(str).unique())
    obras_selecionadas = st.sidebar.multiselect("Obras:", lista_obras, default=lista_obras)

    tipo_selecionado = st.sidebar.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
    tipo_analise = st.sidebar.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
    qtd_linhas = st.sidebar.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)

    # Aplicar filtros gerais
    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
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

        # Adicionar a coluna REFLEXO S PRODUÇÃO apenas quando Produção for selecionada
        if tipo_analise == 'Produção' and 'REFLEXO S PRODUÇÃO' in df.columns:
            df_filtrado['DSR'] = df_filtrado['REFLEXO S PRODUÇÃO']
            ranking = df_filtrado[['Funcionário', 'Função', 'Obra', 'Tipo', 'PRODUÇÃO', 'DSR']].sort_values(by='PRODUÇÃO', ascending=False)
        else:
            ranking = df_filtrado[['Funcionário', 'Função', 'Obra', 'Tipo', coluna_valor]].sort_values(by=coluna_valor, ascending=False)

        valor_total = df_filtrado[coluna_valor].sum()
        st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
        st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        if qtd_linhas != 'Todos':
            ranking = ranking.head(int(qtd_linhas))

        # Formatar como R$
        ranking[coluna_valor] = ranking[coluna_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if 'DSR' in ranking.columns:
            ranking['DSR'] = ranking['DSR'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

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
