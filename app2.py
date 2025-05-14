import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da página ---
st.set_page_config(page_title="Dashboard de Efetivo e Produtividade", layout="wide")

# --- Carregar a logo no canto superior direito ---
logo = "caminho/para/sua/logo.png"  # Substitua pelo caminho real da sua logo
st.markdown(f'<img src="{logo}" style="position: absolute; top: 10px; right: 10px; width: 150px;">', unsafe_allow_html=True)

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

# --- Função para carregar os dados ---
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

# --- Página inicial para selecionar o serviço ---
pagina_selecionada = st.sidebar.radio("Escolha um serviço:", ["Efetivo", "Produtividade"])

# --- Carregar os dados para o Efetivo ---
if pagina_selecionada == "Efetivo":
    st.title("📊 Análise de Efetivo - Abril 2025")
    df_efetivo = carregar_dados("efetivo_abril.xlsx")

    # FILTROS
    st.sidebar.header("🔍 Filtros")
    lista_obras = sorted(df_efetivo['Obra'].astype(str).unique())
    obras_selecionadas = st.sidebar.multiselect("Obras:", lista_obras, default=lista_obras)

    tipo_selecionado = st.sidebar.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
    tipo_analise = st.sidebar.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
    qtd_linhas = st.sidebar.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)

    # Aplicar filtros gerais
    df_filtrado = df_efetivo[df_efetivo['Obra'].isin(obras_selecionadas)]
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
        df_pizza = df_efetivo[df_efetivo['Obra'].isin(obras_selecionadas)]
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
        if tipo_analise == 'Produção' and 'REFLEXO S PRODUÇÃO' in df_efetivo.columns:
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

# --- Carregar a página de Produtividade ---
if pagina_selecionada == "Produtividade":
    st.title("📊 Dashboard de Produtividade")

    # Carregar o arquivo Excel de produtividade
    df_produtividade = pd.read_excel("produtividade.xlsx", engine="openpyxl")

    # Seu código para visualização de dados de produtividade vai aqui...
    st.write("Aqui será exibido o dashboard de produtividade.")
    # Exemplo de gráfico de barras para produtividade
    fig_produtividade = px.bar(df_produtividade, x='Nome', y='Produtividade', title="Produtividade por Funcionário")
    st.plotly_chart(fig_produtividade, use_container_width=True)
