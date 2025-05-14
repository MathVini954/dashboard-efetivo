import streamlit as st
import pandas as pd

# Função para carregar os usuários
def carregar_usuarios():
    # Carregar dados dos usuários
    usuarios_df = pd.read_excel("usuarios.xlsx")
    usuarios_df['Usuário'] = usuarios_df['Usuário'].str.strip()  # Remover espaços extras
    usuarios_df['Senha'] = usuarios_df['Senha'].str.strip()  # Remover espaços extras
    return usuarios_df

# Função para verificar o login
def verificar_login(usuario, senha, usuarios_df):
    # Converter ambos para maiúsculas para comparação insensível a maiúsculas/minúsculas
    usuario = usuario.upper().strip()
    senha = senha.strip()
    
    # Verificar se o usuário e senha estão na planilha
    usuario_encontrado = usuarios_df[usuarios_df['Usuário'] == usuario]
    
    if not usuario_encontrado.empty:
        # Verificar se a senha corresponde
        if usuario_encontrado['Senha'].values[0] == senha:
            return True
        else:
            st.error("Senha incorreta!")
            return False
    else:
        st.error("Usuário não encontrado!")
        return False

# Página de login
def login_page():
    st.title("Página de Login")

    # Inputs de login
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type='password')

    # Carregar os usuários da planilha
    usuarios_df = carregar_usuarios()

    # Verificação de login
    if st.button("Entrar"):
        if verificar_login(usuario, senha, usuarios_df):
            st.success(f"Bem-vindo, {usuario}!")
            return usuario  # Retornar o nome do usuário autenticado
        else:
            return None

# Página após o login
def pagina_bem_vindo(usuario):
    st.title(f"Bem-vindo, {usuario}!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("PRODUTIVIDADE"):
            st.write("Carregando o dashboard de produtividade...")
            # Aqui você pode chamar a função do dashboard de produtividade
            app_produtividade()  # Substitua com o nome da função que você já tem para o dashboard de produtividade
    
    with col2:
        if st.button("ANÁLISE EFETIVO"):
            st.write("Carregando a análise de efetivo...")
            # Aqui você pode chamar a função do dashboard de análise de efetivo
            app_analise_efetivo()  # Substitua com o nome da função que você já tem para a análise de efetivo

# Função principal
def main():
    # Primeiramente, tentar realizar o login
    usuario_logado = login_page()

    if usuario_logado:
        # Após o login, exibir a página de boas-vindas
        pagina_bem_vindo(usuario_logado)

if __name__ == "__main__":
    main()
