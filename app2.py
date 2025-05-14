import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar os dados de produtividade
def carregar_dados():
    # Carregar dados de produtividade do Excel
    # Assumindo que a planilha tenha as colunas: TIPO_OBRA, SERVIÇO, DATA, PRODUTIVIDADE_PROF_DIAM2, PRODUTIVIDADE_ORCADA_DIAM2
    produtividade_df = pd.read_excel("produtividade.xlsx")
    
    # Garantir que a coluna de data esteja no formato datetime
    produtividade_df['DATA'] = pd.to_datetime(produtividade_df['DATA'], format='%d/%m/%Y')
    # Converter para o formato 'Mai/25'
    produtividade_df['DATA_FORMATADA'] = produtividade_df['DATA'].dt.strftime('%b/%y')
    
    return produtividade_df

# Função para filtrar os dados com base nos filtros de tipo de obra, serviço e mês/ano
def filtrar_dados(df, tipo_obra, servico, mes_ano):
    if tipo_obra != "Todos":
        df_filtrado = df[df['TIPO_OBRA'] == tipo_obra]
    else:
        df_filtrado = df
    
    if servico:
        df_filtrado = df_filtrado[df_filtrado['SERVIÇO'] == servico]
    
    # Filtrar pelo mês e ano selecionado
    if mes_ano != "Todos":
        df_filtrado = df_filtrado[df_filtrado['DATA_FORMATADA'] == mes_ano]
    
    return df_filtrado

# Função para criar gráfico de produtividade (real vs orçado)
def criar_grafico_produtividade(df):
    # Calcular a média de produtividade para o mês
    df_mensal = df.groupby('DATA_FORMATADA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean',  # Produtividade Prof. Dia/M²
        'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'  # Produtividade Prof. Dia/M²2 (Orçado)
    }).reset_index()

    # Gráfico de linha para Produtividade Prof. Dia/M² e Produtividade Orçada
    fig = px.line(df_mensal, x='DATA_FORMATADA', y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                  labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                  title="Produtividade Profissional por M² (Real x Orçado)",
                  line_shape='linear',  # Linha mais suave
                  markers=True,  # Adiciona marcadores nos pontos
                  template='plotly_dark')  # Estilo de fundo moderno
    
    # Aumentando o tamanho do gráfico
    fig.update_layout(width=900, height=500)
    
    return fig

# Função para criar gráfico de barras de produtividade por tipo de obra
def criar_grafico_barras(df):
    df_produtividade_obra = df.groupby('TIPO_OBRA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean'
    }).reset_index()
    
    fig_barras = px.bar(df_produtividade_obra, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                        title="Produtividade Profissional Média por Tipo de Obra",
                        template='plotly_dark')  # Estilo moderno
    
    fig_barras.update_layout(width=900, height=500)
    
    return fig_barras

# Função principal para exibir tudo
def app():
    st.set_page_config(page_title="Dashboard de Produtividade", layout="wide")
    
    # Exibir logo no canto superior direito
    st.sidebar.image("logotipo.png", width=200)  # Ajuste o caminho da imagem conforme necessário

    # Carregar dados
    df = carregar_dados()
    
    # Filtros para seleção de tipo de obra, serviço e mês/ano
    tipo_obra_opcoes = ["Todos"] + df['TIPO_OBRA'].unique().tolist()
    tipo_obra = st.sidebar.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)
    
    servicos_opcoes = df['SERVIÇO'].unique().tolist()
    servico = st.sidebar.selectbox('Selecione o Serviço', servicos_opcoes)
    
    mes_ano_opcoes = ["Todos"] + df['DATA_FORMATADA'].unique().tolist()
    mes_ano = st.sidebar.selectbox('Selecione o Mês/Ano', mes_ano_opcoes)
    
    # Filtrar os dados com base nos filtros aplicados
    df_filtrado = filtrar_dados(df, tipo_obra, servico, mes_ano)
    
    # Criar gráficos
    fig_produtividade = criar_grafico_produtividade(df_filtrado)
    fig_barras = criar_grafico_barras(df_filtrado)
    
    # Exibir os gráficos
    st.title("Dashboard de Produtividade")
    
    # Exibir gráfico de produtividade em linha
    st.plotly_chart(fig_produtividade)
    
    # Exibir gráfico de barras de produtividade por tipo de obra
    st.plotly_chart(fig_barras)

# Chamar a função principal
if __name__ == "__main__":
    app()
