import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuração da página ---
st.set_page_config(page_title="Dashboard Integrado", layout="wide")

# --- Modo escuro e CSS customizado ---
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
    transition: width 0.3s ease-in-out;
    width: 80px;
    visibility: hidden;
}}
[data-testid="stSidebar"]:hover {{
    width: 300px;
    visibility: visible;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Inserir logo na sidebar ---
st.sidebar.image("logotipo.png", use_container_width=True)

# --- Funções de carregamento ---
@st.cache_data
def carregar_dados_produtividade():
    try:
        df = pd.read_excel("produtividade.xlsx")
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados de produtividade: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_efetivo():
    try:
        df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip()
        df = df.fillna(0)

        for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Tipo'] = df.get('DIRETO / INDIRETO', 'INDEFINIDO')
        df['Tipo'] = df['Tipo'].astype(str).str.upper().str.strip()
        df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados de efetivo: {e}")
        return pd.DataFrame()

# --- Tabs do app ---
aba = st.tabs(["📈 Produtividade", "📊 Efetivo"])

# ========== PRODUTIVIDADE ==========
with aba[0]:
    st.title("📈 Dashboard de Produtividade")
    df_prod = carregar_dados_produtividade()

    if df_prod.empty:
        st.warning("Não foi possível carregar os dados de produtividade.")
    else:
        tipo_obra_opcoes = ["Todos"] + df_prod['TIPO_OBRA'].dropna().unique().tolist()
        tipo_obra = st.sidebar.selectbox('Tipo de Obra', tipo_obra_opcoes)

        servicos_opcoes = df_prod['SERVIÇO'].dropna().unique().tolist()
        servico = st.sidebar.selectbox('Serviço', servicos_opcoes)

        datas_opcoes = ["Todos"] + df_prod['DATA_FORMATADA'].dropna().unique().tolist()
        datas_sel = st.sidebar.multiselect("Mês/Ano", datas_opcoes, default=datas_opcoes)

        # Filtragem
        df_f = df_prod.copy()
        if tipo_obra != "Todos":
            df_f = df_f[df_f['TIPO_OBRA'] == tipo_obra]
        if servico:
            df_f = df_f[df_f['SERVIÇO'] == servico]
        if datas_sel and "Todos" not in datas_sel:
            df_f = df_f[df_f['DATA_FORMATADA'].isin(datas_sel)]

        # Gráfico de linha
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

        # Gráfico de barras
        df_tipo = df_f.groupby('TIPO_OBRA').agg({'PRODUTIVIDADE_PROF_DIAM2': 'mean'}).reset_index()
        fig_barra = px.bar(df_tipo, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                           title="Produtividade Média por Tipo de Obra",
                           template='plotly_dark' if modo_escuro else 'plotly_white')
        fig_barra.update_layout(width=900, height=500)
        st.plotly_chart(fig_barra)

# ========== EFETIVO ==========
with aba[1]:
    st.title("📊 Dashboard de Efetivo")
    df_efetivo = carregar_dados_efetivo()

    if df_efetivo.empty:
        st.warning("Não foi possível carregar os dados de efetivo.")
    else:
        tipo_obra_opcoes = ["Todos"] + df_efetivo['Obra'].dropna().unique().tolist()
        tipo_obra = st.sidebar.selectbox("Obra", tipo_obra_opcoes)

        tipo_efetivo_opcoes = ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO']
        tipo_efetivo = st.sidebar.selectbox("Tipo de Efetivo", tipo_efetivo_opcoes)

        df_filt = df_efetivo.copy()
        if tipo_obra != "Todos":
            df_filt = df_filt[df_filt['Obra'] == tipo_obra]
        if tipo_efetivo != "Todos":
            df_filt = df_filt[df_filt['Tipo'] == tipo_efetivo]

        col1, col2 = st.columns(2)

        with col1:
            tipo_efetivo_count = df_filt['Tipo'].value_counts().reset_index()
            tipo_efetivo_count.columns = ['Tipo', 'Contagem']
            fig_pizza = px.pie(tipo_efetivo_count, names='Tipo', values='Contagem',
                               title="Distribuição por Tipo de Efetivo",
                               color_discrete_sequence=px.colors.sequential.Plasma)
            st.plotly_chart(fig_pizza, use_container_width=True)

        with col2:
            ranking = df_filt.groupby('Obra').size().reset_index(name='Total Funcionários')
            ranking = ranking.sort_values(by='Total Funcionários', ascending=False)
            st.dataframe(ranking, use_container_width=True)
