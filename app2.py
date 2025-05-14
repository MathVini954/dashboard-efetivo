import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# Função para carregar os dados
# -----------------------------
def carregar_dados():
    if not os.path.exists("produtividade.xlsx"):
        st.error("Arquivo 'produtividade.xlsx' não foi encontrado no diretório.")
        return pd.DataFrame()

    try:
        produtividade_df = pd.read_excel("produtividade.xlsx")
        produtividade_df['DATA'] = pd.to_datetime(produtividade_df['DATA'], format='%d/%m/%Y', errors='coerce')
        produtividade_df.dropna(subset=['DATA'], inplace=True)
        produtividade_df['DATA_FORMATADA'] = produtividade_df['DATA'].dt.strftime('%b/%y')
        return produtividade_df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

# -----------------------------
# Função para filtrar os dados
# -----------------------------
def filtrar_dados(df, tipo_obra, servico, datas_selecionadas):
    if tipo_obra != "Todos":
        df = df[df['TIPO_OBRA'] == tipo_obra]
    if servico:
        df = df[df['SERVIÇO'] == servico]
    if "Todos" not in datas_selecionadas:
        df = df[df['DATA_FORMATADA'].isin(datas_selecionadas)]
    return df

# --------------------------------------------
# Função para gráfico de produtividade (linha)
# --------------------------------------------
def criar_grafico_produtividade(df):
    df_mensal = df.groupby('DATA_FORMATADA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean',
        'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'
    }).reset_index()

    fig = px.line(df_mensal, x='DATA_FORMATADA',
                  y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                  labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                  title="Produtividade Profissional por M² (Real x Orçado)",
                  markers=True,
                  template='plotly_dark')

    fig.update_layout(width=900, height=500)
    return fig

# -------------------------------------------------------
# Função para gráfico de barras (produtividade por obra)
# -------------------------------------------------------
def criar_grafico_barras(df):
    df_obra = df.groupby('TIPO_OBRA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean'
    }).reset_index()

    fig = px.bar(df_obra, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                 title="Produtividade Média por Tipo de Obra",
                 template='plotly_dark')

    fig.update_layout(width=900, height=500)
    return fig

# ------------------------
# Função principal do app
# ------------------------
def app():
    st.set_page_config(page_title="Dashboard de Produtividade", layout="wide")
    st.sidebar.image("logotipo.png", width=200)

    # Carrega os dados
    df = carregar_dados()

    if df.empty:
        return

    # Filtros
    tipo_obra_opcoes = ["Todos"] + sorted(df['TIPO_OBRA'].dropna().unique().tolist())
    servicos_opcoes = sorted(df['SERVIÇO'].dropna().unique().tolist())
    mes_ano_opcoes = ["Todos"] + sorted(df['DATA_FORMATADA'].dropna().unique().tolist())

    tipo_obra = st.sidebar.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)
    servico = st.sidebar.selectbox('Selecione o Serviço', servicos_opcoes)
    datas_selecionadas = st.sidebar.multiselect('Selecione o(s) Mês/Ano', mes_ano_opcoes, default=mes_ano_opcoes)

    # Filtro para qual gráfico será mostrado
    dashboard_opcao = st.sidebar.radio("Selecionar Dashboard", ["Produtividade Mensal", "Produtividade por Obra"])

    # Filtra os dados conforme seleção
    df_filtrado = filtrar_dados(df, tipo_obra, servico, datas_selecionadas)

    st.title("Dashboard de Produtividade")

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    # Exibe o gráfico de acordo com a seleção
    if dashboard_opcao == "Produtividade Mensal":
        st.subheader("Gráfico de Linha - Produtividade Real x Orçada")
        fig = criar_grafico_produtividade(df_filtrado)
        st.plotly_chart(fig)

    elif dashboard_opcao == "Produtividade por Obra":
        st.subheader("Gráfico de Barras - Produtividade Média por Tipo de Obra")
        fig = criar_grafico_barras(df_filtrado)
        st.plotly_chart(fig)

# -------------------------------
# Executa o app Streamlit
# -------------------------------
if __name__ == "__main__":
    app()
