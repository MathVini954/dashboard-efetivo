import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Função para carregar dados de efetivo
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()  # Remove espaços extras nas colunas
    df = df.fillna(0)
    
    # Convertendo colunas específicas para numérico
    for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Criando coluna de Tipo (Direto / Indireto) se existir
    if 'DIRETO / INDIRETO' in df.columns:
        df['Tipo'] = df['DIRETO / INDIRETO'].astype(str).str.upper().str.strip()
    else:
        df['Tipo'] = 'INDEFINIDO'
    
    # Calculando o total de hora extra
    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
    
    return df

# Função para mostrar o dashboard de efetivo
def dashboard_efetivo(df):
    st.title("Dashboard de Efetivo")

    # Filtro de obras
    lista_obras = sorted(df['OBRA'].astype(str).unique())
    obras_selecionadas = st.sidebar.multiselect("Obras:", lista_obras, default=lista_obras)
    
    # Filtrando dados pelas obras selecionadas
    df_filtrado = df[df['OBRA'].isin(obras_selecionadas)]
    
    # Exibindo métricas de efetivo
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Direto", len(df_filtrado[df_filtrado['Tipo'] == 'DIRETO']))
    col2.metric("👷‍♂️ Indireto", len(df_filtrado[df_filtrado['Tipo'] == 'INDIRETO']))
    col3.metric("🏗️ Terceiro", len(df_filtrado[df_filtrado['Tipo'] == 'TERCEIRO']))
    col4.metric("👥 Total", len(df_filtrado))
    
    # Exibindo gráficos de produtividade
    fig = px.pie(df_filtrado, names='Tipo', title="Distribuição de Efetivo")
    st.plotly_chart(fig)

# Função para mostrar o relatório de efetivo
def relatorio_efetivo(df):
    st.title("Relatório de Efetivo por Obra")

    # Filtro de obras
    lista_obras = sorted(df['OBRA'].astype(str).unique())
    obras_selecionadas = st.sidebar.multiselect("Obras:", lista_obras, default=lista_obras)
    
    # Filtrando dados pelas obras selecionadas
    df_filtrado = df[df['OBRA'].isin(obras_selecionadas)]
    
    # Exibindo dados filtrados
    st.write(df_filtrado)

    # Exibindo o gráfico de produtividade
    fig = px.bar(df_filtrado, x='OBRA', y='PRODUÇÃO', color='Tipo', title="Produtividade por Obra")
    st.plotly_chart(fig)

# Função para gerar o relatório de produtividade
def gerar_relatorio_produtividade(df):
    st.title("Relatório de Produtividade")
    
    lista_obras = sorted(df['OBRA'].astype(str).unique())
    obras_selecionadas = st.sidebar.multiselect("Obras:", lista_obras, default=lista_obras)
    
    df_filtrado = df[df['OBRA'].isin(obras_selecionadas)]
    
    # Gerando o relatório de produtividade por obra
    df_relatorio = df_filtrado.groupby('OBRA').agg({'PRODUÇÃO': 'sum', 'Total Extra': 'sum'})
    st.write(df_relatorio)

# Função principal
def main():
    # Carregar os dados
    df = carregar_dados_efetivo()
    
    # Seleção de opções no sidebar
    opcao = st.sidebar.selectbox("Escolha uma opção", ["Dashboard de Efetivo", "Relatório de Efetivo", "Relatório de Produtividade"])

    if opcao == "Dashboard de Efetivo":
        dashboard_efetivo(df)
    elif opcao == "Relatório de Efetivo":
        relatorio_efetivo(df)
    elif opcao == "Relatório de Produtividade":
        gerar_relatorio_produtividade(df)

if __name__ == "__main__":
    main()
