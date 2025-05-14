import streamlit as st
import pandas as pd

# Função para carregar os dados de produtividade
def carregar_dados():
    # Carregar dados de produtividade do Excel
    produtividade_df = pd.read_excel("produtividade.xlsx")

    return produtividade_df

# Função para exibir o dashboard
def exibir_dashboard():
    # Carregar dados
    produtividade_df = carregar_dados()

    # Título do Dashboard
    st.title("📊 Dashboard Central")

    # Exibindo o logotipo no canto superior
    st.image("logotipo.png", width=200)  # Ajuste o caminho da imagem conforme necessário

    # Exibindo as opções do dashboard
    st.header("Bem-vindo ao Dashboard de Produtividade!")

    # Exibindo os dados
    st.dataframe(produtividade_df)

# Chamando a função para exibir o dashboard
exibir_dashboard()
