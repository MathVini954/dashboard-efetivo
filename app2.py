import streamlit as st
import pandas as pd

# Função para verificar o login
def verificar_login(usuario, senha):
    # Carregar a planilha de usuários
    usuarios_df = pd.read_excel('usuarios.xlsx')

    # Verificar se o usuário e senha existem
    if usuario in usuarios_df['usuario'].values:
        usuario_info = usuarios_df[usuarios_df['usuario'] == usuario]
        senha_correta = usuario_info['senha'].values[0]
        if senha == senha_correta:
            return True
    return False

# Página de Login
def pagina_login():
    st.title("Login")
    
    # Campos para o login
    usuario = st.text_input("usuario")
    senha = st.text_input("senha", type='password')
    
    # Verificar login ao pressionar o botão
    if st.button("Entrar"):
        if verificar_login(usuario, senha):
            st.session_state.usuario = usuario  # Salvar o usuário na sessão
            st.session_state.autenticado = True  # Marcar como autenticado
            st.success("Login bem-sucedido!")
            exibir_pagina_navegacao()
        else:
            st.error("Usuário ou senha incorretos")

# Página de Navegação após o Login
def exibir_pagina_navegacao():
    st.title(f"Bem-vindo, {st.session_state.usuario}!")
    
    # Opções de navegação
    opcao = st.selectbox(
        'Escolha uma opção:',
        ['Custos e Planejamento', 'Dashboard de Produtividade', 'Análise Efetivo']
    )
    
    if opcao == 'Custos e Planejamento':
        exibir_custos_planejamento()
    elif opcao == 'Dashboard de Produtividade':
        app_produtividade()
    elif opcao == 'Análise Efetivo':
        app_analise_efetivo()

# Função para exibir os custos e planejamento
def exibir_custos_planejamento():
    st.header("Custos e Planejamento")
    # Exemplo de exibição de dados de custos e planejamento
    st.write("Aqui você pode visualizar e planejar os custos.")

    # Simulação de leitura de planilha de custos
    custos_df = pd.read_excel('custos_planejamento.xlsx')
    st.dataframe(custos_df)

# Função para o Dashboard de Produtividade
def app_produtividade():
    st.header("Dashboard de Produtividade")
    
    # Carregar e exibir os dados do dashboard de produtividade
    try:
        produtividade_df = pd.read_excel('produtividade.xlsx')
        st.write("Dados de produtividade do mês:")
        st.dataframe(produtividade_df)
    except Exception as e:
        st.error(f"Erro ao carregar os dados de produtividade: {e}")

# Função para o Dashboard de Análise Efetivo
def app_analise_efetivo():
    st.header("Análise Efetivo")
    
    # Carregar e exibir os dados da análise de efetivo
    try:
        efetivo_df = pd.read_excel('efetivo.xlsx')
        st.write("Análise de efetivo do mês:")
        st.dataframe(efetivo_df)
    except Exception as e:
        st.error(f"Erro ao carregar os dados de efetivo: {e}")

# Função principal que controla o fluxo do aplicativo
def main():
    if 'autenticado' not in st.session_state or not st.session_state.autenticado:
        pagina_login()  # Se o usuário não estiver autenticado, exibe o login
    else:
        exibir_pagina_navegacao()  # Se autenticado, exibe as opções de navegação

if __name__ == "__main__":
    main()
