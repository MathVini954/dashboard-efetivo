import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboards de Obra", layout="wide")

# --- Inserir Logo ---
st.image('logotipo.png', width=200)  # Insira o caminho da logo aqui

# --- ABA 1: DASHBOARD DE EFETIVO ---
def dashboard_efetivo():
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

 @st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas
    st.write(df.columns)  # Verifique as colunas carregadas
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
    df = carregar_dados_efetivo()

    st.sidebar.header("🔍 Filtros")
    lista_obras = sorted(df['Obra'].astype(str).unique())
    obras_selecionadas = st.sidebar.multiselect("Obras:", lista_obras, default=lista_obras)
    tipo_selecionado = st.sidebar.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
    tipo_analise = st.sidebar.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
    qtd_linhas = st.sidebar.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)

    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Direto", len(df_filtrado[df_filtrado['Tipo'] == 'DIRETO']))
    col2.metric("👷‍♂️ Indireto", len(df_filtrado[df_filtrado['Tipo'] == 'INDIRETO']))
    col3.metric("🏗️ Terceiro", len(df_filtrado[df_filtrado['Tipo'] == 'TERCEIRO']))
    col4.metric("👥 Total", len(df_filtrado))
    st.divider()

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

        ranking[coluna_valor] = ranking[coluna_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if 'DSR' in ranking.columns:
            ranking['DSR'] = ranking['DSR'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ranking, use_container_width=True)

    st.divider()
    graf_funcao = df_filtrado['Função'].value_counts().reset_index()
    graf_funcao.columns = ['Função', 'Qtd']
    fig_bar = px.bar(graf_funcao, x='Função', y='Qtd', title='Efetivo por Função', text='Qtd',
                     color='Qtd', color_continuous_scale='Blues')
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.markdown("### 🔍 Correlação: Produção vs. Hora Extra Total")
    fig_disp = px.scatter(df_filtrado, x="Total Extra", y="PRODUÇÃO", color="Tipo",
                          hover_data=["Funcionário", "Função", "Obra"], trendline="ols",
                          labels={"Total Extra": "Hora Extra Total", "PRODUÇÃO": "Produção"},
                          title="Dispersão: Hora Extra Total vs Produção")
    st.plotly_chart(fig_disp, use_container_width=True)

# --- ABA 2: DASHBOARD DE PRODUTIVIDADE ---
def dashboard_produtividade():
    def carregar_dados():
        df = pd.read_excel("produtividade.xlsx")
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')
        return df

    def filtrar_dados(df, tipo_obra, servico, datas_selecionadas):
        if tipo_obra != "Todos":
            df = df[df['TIPO_OBRA'] == tipo_obra]
        if servico:
            df = df[df['SERVIÇO'] == servico]
        if datas_selecionadas:
            df = df[df['DATA_FORMATADA'].isin(datas_selecionadas)]
        return df

    def criar_grafico_produtividade(df):
        df_mensal = df.groupby('DATA_FORMATADA').agg({
            'PRODUTIVIDADE_PROF_DIAM2': 'mean',
            'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'
        }).reset_index()
        fig = px.line(df_mensal, x='DATA_FORMATADA', y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                      labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                      title="Produtividade Profissional por M² (Real x Orçado)",
                      line_shape='linear', markers=True, template='plotly_dark')
        fig.update_layout(width=900, height=500)
        return fig

    def criar_grafico_barras(df):
        df_produtividade_obra = df.groupby('TIPO_OBRA').agg({
            'PRODUTIVIDADE_PROF_DIAM2': 'mean'
        }).reset_index()
        fig_barras = px.bar(df_produtividade_obra, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                            title="Produtividade Profissional Média por Tipo de Obra",
                            template='plotly_dark')
        fig_barras.update_layout(width=900, height=500)
        return fig_barras

    df = carregar_dados()

    tipo_obra_opcoes = ["Todos"] + df['TIPO_OBRA'].unique().tolist()
    tipo_obra = st.sidebar.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)

    servicos_opcoes = df['SERVIÇO'].unique().tolist()
    servico = st.sidebar.selectbox('Selecione o Serviço', servicos_opcoes)

    mes_ano_opcoes = df['DATA_FORMATADA'].unique().tolist()
    datas_selecionadas = st.sidebar.multiselect('Selecione o(s) Mês/Ano', mes_ano_opcoes, default=mes_ano_opcoes)

    df_filtrado = filtrar_dados(df, tipo_obra, servico, datas_selecionadas)
    fig_produtividade = criar_grafico_produtividade(df_filtrado)
    fig_barras = criar_grafico_barras(df_filtrado)

    st.title("📈 Dashboard de Produtividade")
    st.plotly_chart(fig_produtividade)
    st.plotly_chart(fig_barras)

# --- EXECUÇÃO COM TABS ---
aba1, aba2 = st.tabs(["📊 Efetivo", "📈 Produtividade"])
with aba1:
    dashboard_efetivo()

with aba2:
    dashboard_produtividade() 
