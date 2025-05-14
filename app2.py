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
                  title="Produtividade Profissional por M² (Real x Orçado)")
    
    st.plotly_chart(fig)

# Função para exibir o dashboard
def exibir_dashboard():
    # Carregar dados
    produtividade_df = carregar_dados()

    # Título do Dashboard
    st.title("📊 Dashboard Central de Produtividade")

    # Exibindo o logotipo no canto superior
    st.image("logotipo.png", width=200)  # Ajuste o caminho da imagem conforme necessário

    # Layout de filtros na esquerda
    st.sidebar.header("Filtros de Seleção")

    # Filtros de seleção
    tipo_obra = st.sidebar.selectbox('Selecione o Tipo de Obra:', ['Todos'] + list(produtividade_df['TIPO_OBRA'].unique()))
    servico = st.sidebar.selectbox('Selecione o Serviço:', [''] + list(produtividade_df['SERVIÇO'].unique()))  # Servicos
    mes_ano = st.sidebar.selectbox('Selecione o Período (Mês/Ano):', sorted(produtividade_df['DATA_FORMATADA'].unique(), reverse=True))

    # Filtrando os dados com base nas seleções
    df_filtrado = filtrar_dados(produtividade_df, tipo_obra, servico, mes_ano)

    # Verificando se há dados para o período e tipo de obra
    if not df_filtrado.empty:
        # Exibindo gráficos de produtividade
        criar_grafico_produtividade(df_filtrado)
    else:
        st.warning("Não há dados disponíveis para o filtro selecionado.")

    # Gráficos adicionais: Exemplo de gráfico de barras de produtividade por obra
    df_produtividade_obra = df_filtrado.groupby('TIPO_OBRA').agg({
        'PRODUTIVIDADE_PROF_DIAM2': 'mean'
    }).reset_index()
    
    fig_barras = px.bar(df_produtividade_obra, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                        title="Produtividade Profissional Média por Tipo de Obra",
                        labels={'TIPO_OBRA': 'Tipo de Obra', 'PRODUTIVIDADE_PROF_DIAM2': 'Produtividade Média'},
                        color='TIPO_OBRA')
    st.plotly_chart(fig_barras)

    # Gráfico de pizza para distribuição de serviços
    if servico:
        df_servico = df_filtrado.groupby('SERVIÇO').size().reset_index(name='Contagem')
        fig_pizza = px.pie(df_servico, names='SERVIÇO', values='Contagem', title="Distribuição de Serviços")
        st.plotly_chart(fig_pizza)

# Chamando a função para exibir o dashboard
exibir_dashboard()
