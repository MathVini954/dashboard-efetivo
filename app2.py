import streamlit as st
import pandas as pd

# Função para carregar dados
@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_excel(arquivo, engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)
    return df

# Função de Login
def login():
    usuarios_df = pd.read_excel("usuarios.xlsx")
    usuarios = usuarios_df[['usuario', 'senha']]
    
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Login"):
        if username in usuarios['usuario'].values and password in usuarios['senha'].values:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Usuário ou senha inválidos!")

# Função da página após login
def pagina_após_login():
    st.title(f"Bem-vindo, {st.session_state.username}!")

    # Botões de navegação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("PRODUTIVIDADE"):
            exibir_dashboard_produtividade()

    with col2:
        if st.button("ANÁLISE EFETIVO"):
            exibir_dashboard_efetivo()

# Função para exibir o dashboard de produtividade
def exibir_dashboard_produtividade():
    import plotly.express as px

    # Função para carregar dados de produtividade
    def carregar_dados_produtividade():
        df = pd.read_excel("produtividade.xlsx")
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')
        return df
    
    df = carregar_dados_produtividade()
    
    # Filtros
    tipo_obra_opcoes = ["Todos"] + df['TIPO_OBRA'].unique().tolist()
    tipo_obra = st.sidebar.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)
    
    servicos_opcoes = df['SERVIÇO'].unique().tolist()
    servico = st.sidebar.selectbox('Selecione o Serviço', servicos_opcoes)
    
    mes_ano_opcoes = ["Todos"] + df['DATA_FORMATADA'].unique().tolist()
    datas_selecionadas = st.sidebar.multiselect('Selecione o(s) Mês/Ano', mes_ano_opcoes, default=mes_ano_opcoes)
    
    # Filtro dos dados
    df_filtrado = df[(df['TIPO_OBRA'] == tipo_obra if tipo_obra != "Todos" else True) &
                     (df['SERVIÇO'] == servico if servico else True) &
                     (df['DATA_FORMATADA'].isin(datas_selecionadas) if datas_selecionadas else True)]
    
    # Gráficos
    fig_produtividade = px.line(df_filtrado, x='DATA_FORMATADA', y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                                labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                                title="Produtividade Profissional por M² (Real x Orçado)",
                                line_shape='linear', markers=True)
    st.plotly_chart(fig_produtividade)

# Função para exibir o dashboard de análise de efetivo
def exibir_dashboard_efetivo():
    import plotly.express as px

    st.title("📊 Análise de Efetivo - Abril 2025")

    # Carregar os dados de efetivo
    df = carregar_dados("efetivo_abril.xlsx")

    # Filtros
    obras_selecionadas = st.sidebar.multiselect("Obras:", df['Obra'].unique(), default=df['Obra'].unique())
    tipo_selecionado = st.sidebar.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'])
    
    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Direto", len(df_filtrado[df_filtrado['Tipo'] == 'DIRETO']))
    col2.metric("👷‍♂️ Indireto", len(df_filtrado[df_filtrado['Tipo'] == 'INDIRETO']))
    col3.metric("🏗️ Terceiro", len(df_filtrado[df_filtrado['Tipo'] == 'TERCEIRO']))
    col4.metric("👥 Total", len(df_filtrado))

    # Gráfico pizza
    df_pizza = df_filtrado['Tipo'].value_counts().reset_index()
    df_pizza.columns = ['Tipo', 'count']
    fig_pizza = px.pie(df_pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo')
    st.plotly_chart(fig_pizza)

    # Tabela de ranking
    ranking = df_filtrado[['Funcionário', 'Função', 'Obra', 'Tipo', 'PRODUÇÃO']].sort_values(by='PRODUÇÃO', ascending=False)
    st.dataframe(ranking)

# Função principal
def app():
    st.session_state.logged_in = st.session_state.get('logged_in', False)

    if not st.session_state.logged_in:
        login()
    else:
        pagina_após_login()

if __name__ == "__main__":
    app()
