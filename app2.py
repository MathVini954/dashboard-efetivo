import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import os

# ---------- Funções de autenticação ----------
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha, hash_s):
    return hash_senha(senha) == hash_s

def carregar_usuarios():
    if os.path.exists("usuarios.csv"):
        return pd.read_csv("usuarios.csv")
    else:
        return pd.DataFrame(columns=["usuario", "senha_hash"])

def salvar_usuario(usuario, senha_hash):
    df = carregar_usuarios()
    novo_usuario = pd.DataFrame([[usuario, senha_hash]], columns=["usuario", "senha_hash"])
    df = pd.concat([df, novo_usuario], ignore_index=True)
    df.to_csv("usuarios.csv", index=False)

# ---------- Tela de login/cadastro ----------
def tela_login():
    st.title("🔐 Login")

    menu = st.radio("Escolha uma opção:", ["Login", "Cadastrar"])

    if menu == "Login":
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            df_usuarios = carregar_usuarios()
            if usuario in df_usuarios['usuario'].values:
                senha_hash = df_usuarios[df_usuarios['usuario'] == usuario]['senha_hash'].values[0]
                if verificar_senha(senha, senha_hash):
                    st.success("✅ Login bem-sucedido!")
                    st.session_state['logado'] = True
                    st.session_state['usuario'] = usuario
                else:
                    st.error("❌ Senha incorreta.")
            else:
                st.error("❌ Usuário não encontrado.")

    else:
        st.subheader("📋 Cadastro de Novo Usuário")
        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirme a senha", type="password")

        if st.button("Cadastrar"):
            if nova_senha != confirmar_senha:
                st.warning("⚠️ As senhas não coincidem.")
            elif novo_usuario.strip() == "":
                st.warning("⚠️ O nome de usuário não pode estar vazio.")
            else:
                df = carregar_usuarios()
                if novo_usuario in df['usuario'].values:
                    st.warning("⚠️ Usuário já existe.")
                else:
                    salvar_usuario(novo_usuario, hash_senha(nova_senha))
                    st.success("✅ Usuário cadastrado com sucesso! Faça login.")

# ---------- Seu dashboard (copiado da sua estrutura) ----------
def dashboard_efetivo():
    st.title("📊 Análise de Efetivo - Abril 2025")
    st.write("Conteúdo da aba de efetivo aqui...")

def dashboard_produtividade():
    st.title("📈 Dashboard de Produtividade")
    st.write("Conteúdo da aba de produtividade aqui...")

# ---------- Execução ----------
def main():
    if "logado" not in st.session_state:
        st.session_state['logado'] = False

    if not st.session_state['logado']:
        tela_login()
    else:
        st.sidebar.title(f"👋 Bem-vindo, {st.session_state['usuario']}")
        aba1, aba2 = st.tabs(["📊 Efetivo", "📈 Produtividade"])
        with aba1:
            dashboard_efetivo()
        with aba2:
            dashboard_produtividade()

        if st.sidebar.button("Sair"):
            st.session_state['logado'] = False
            st.experimental_rerun()

# ---------- Rodar app ----------
if __name__ == "__main__":
    main()
