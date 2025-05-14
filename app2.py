import streamlit as st
import pandas as pd
import plotly.express as px

# Função de autenticação
def autenticar(usuario, senha):
    df_usuarios = pd.read_excel('usuarios.xlsx')
    usuario = usuario.strip().lower()
    senha = senha.strip()
    df_usuarios['usuario'] = df_usuarios['usuario'].str.strip().str.lower()
    df_usuarios['senha'] = df_usuarios['senha'].astype(str).str.strip()
    autenticado = df_usuarios[
        (df_usuarios['usuario'] == usuario) &
        (df_usuarios['senha'] == senha)
    ]
    return not autenticado.empty

# Gráfico de produtividade
def criar_grafico_produtividade(df):
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    df['DATA_FORMATADA'] = df['DATA'].dt.to_period('M').astype(str)

    df_mensal = df.groupby('DATA_FORMATADA').agg({
        'PRODUTIVIDADE MENSAL': 'sum',
        'PRODUTIVIDADE ORÇADA': 'sum'
    }).reset_index()

    fig = px.bar(df_mensal, x='DATA_FORMATADA',
                 y=['PRODUTIVIDADE MENSAL', 'PRODUTIVIDADE ORÇADA'],
                 barmode='group',
                 title='Produtividade Mensal x Orçada')

    return fig

# Página de dashboard de produtividade
def pagina_produtividade(nome_usuario):
    st.title("Dashboard de Produtividade")
    st.write(f"Bem-vindo, {nome_usuario}!")

    df_produtividade = pd.read_excel('produtividade.xlsx')

    # Verifica se todas as colunas esperadas estão presentes
    colunas_esperadas = [
        'TIPO_OBRA', 'SERVIÇO', 'DATA', 'QUANT. DIAS', 'TEMPO (H.)',
        'PROFISSIONAL', 'AJUDANTE', 'QUANT.', 'PRODUTIVIDADE MENSAL', 'PRODUTIVIDADE ORÇADA'
    ]
    faltando = [col for col in colunas_esperadas if col not in df_produtividade.columns]
    if faltando:
        st.error(f"As seguintes colunas estão faltando na planilha: {faltando}")
        return

    df_produtividade['DATA'] = pd.to_datetime(df_produtividade['DATA'], errors='coerce')
    df_produtividade['DATA_FORMATADA'] = df_produtividade['DATA'].dt.to_period('M').astype(str)

    tipo_obra = st.selectbox("Filtrar por Tipo de Obra", ["Todos"] + list(df_produtividade['TIPO_OBRA'].unique()))

    if tipo_obra != "Todos":
        df_filtrado = df_produtividade[df_produtividade['TIPO_OBRA'] == tipo_obra]
    else:
        df_filtrado = df_produtividade

    fig_produtividade = criar_grafico_produtividade(df_filtrado)
    st.plotly_chart(fig_produtividade, use_container_width=True)

# Página de dashboard de custos (placeholder)
def pagina_custos(nome_usuario):
    st.title("Dashboard de Custos e Planejamento")
    st.write(f"Bem-vindo, {nome_usuario}!")
    st.info("Conteúdo em desenvolvimento...")

# Página principal (login e navegação)
def app():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario' not in st.session_state:
        st.session_state['usuario'] = ''

    if not st.session_state['autenticado']:
        st.title("Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar(usuario, senha):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = usuario
                st.success("Login bem-sucedido!")
            else:
                st.error("Usuário ou senha incorretos.")
        return

    st.sidebar.title("Navegação")
    opcao = st.sidebar.radio("Escolha uma opção", ["Dashboard de Produtividade", "Custos e Planejamento"])

    if opcao == "Dashboard de Produtividade":
        pagina_produtividade(st.session_state['usuario'])
    elif opcao == "Custos e Planejamento":
        pagina_custos(st.session_state['usuario'])

if __name__ == "__main__":
    app()
