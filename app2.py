import streamlit as st
import pandas as pd
import plotly.express as px

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
# ========== EFETIVO ==========
with aba[1]:
    st.title("📊 Dashboard de Efetivo - Abril 2025")

    df_efetivo = carregar_dados_efetivo()

    obras = sorted(df_efetivo['Obra'].astype(str).unique())
    obras_sel = st.sidebar.multiselect("Obras:", obras, default=obras)

    tipo = st.sidebar.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
    tipo_tabela = st.sidebar.radio("Análise:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
    qtd = st.sidebar.radio("Qtd. na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)

    df_e = df_efetivo[df_efetivo['Obra'].isin(obras_sel)]
    if tipo != 'Todos':
        df_e = df_e[df_e['Tipo'] == tipo]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Direto", len(df_e[df_e['Tipo'] == 'DIRETO']))
    col2.metric("👷‍♂️ Indireto", len(df_e[df_e['Tipo'] == 'INDIRETO']))
    col3.metric("🏗️ Terceiro", len(df_e[df_e['Tipo'] == 'TERCEIRO']))
    col4.metric("👥 Total", len(df_e))

    st.divider()

    col_g1, col_g2 = st.columns([1, 2])

    with col_g1:
        pizza_df = df_e['Tipo'].value_counts().reset_index()
        pizza_df.columns = ['Tipo', 'count']
        fig_pie = px.pie(pizza_df, names='Tipo', values='count',
                         title="Distribuição por Tipo",
                         color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g2:
        coluna = {
            'Produção': 'PRODUÇÃO',
            'Hora Extra Semana': 'Hora Extra 70% - Semana',
            'Hora Extra Sábado': 'Hora Extra 70% - Sabado'
        }[tipo_tabela]

        df_tabela = df_e[['Funcionário', 'Função', 'Obra', 'Tipo', coluna]]
        if tipo_tabela == 'Produção' and 'REFLEXO S PRODUÇÃO' in df_e.columns:
            df_tabela['DSR'] = df_e['REFLEXO S PRODUÇÃO']

        df_tabela = df_tabela.sort_values(by=coluna, ascending=False)
        if qtd != 'Todos':
            df_tabela = df_tabela.head(int(qtd))

        st.dataframe(df_tabela, use_container_width=True)

    st.divider()

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
