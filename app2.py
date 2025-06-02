import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", sheet_name="EFETIVO", engine="openpyxl")
    return df

def carregar_dados_terceiros():
    df_terceiros = pd.read_excel("terceiros_abril.xlsx", sheet_name="TERCEIROS", engine="openpyxl")
    return df_terceiros

def dashboard_efetivo():
    st.title("Dashboard Efetivo e Peso Financeiro")

    df = carregar_dados_efetivo()
    df_terceiros = carregar_dados_terceiros()

    # Seleção de obras para filtro
    obras_disponiveis = sorted(df['Obra'].unique())
    obras_selecionadas = st.multiselect("Selecione as Obras:", obras_disponiveis, default=obras_disponiveis)

    # Tipo de peso financeiro
    tipo_peso = st.radio("Tipo de Peso Financeiro:", ['Peso sobre Produção', 'Peso sobre Horas Extras'])

    # Filtrar df pelo que o usuário selecionou nas obras
    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]

    # Cálculo do peso financeiro

    # Para diretos e indiretos filtrados nas obras selecionadas
    df_peso = df[df['Tipo'].isin(['DIRETO', 'INDIRETO']) & df['Obra'].isin(obras_selecionadas)].copy()
    df_peso['Total Extra'] = df_peso['Hora Extra 70% - Semana'] + df_peso['Hora Extra 70% - Sabado']
    df_peso['Base Remuneração'] = df_peso['Remuneração Líquida Folha'] + df_peso['Adiantamento']

    # Terceiros de todas as obras (sem filtro)
    df_terceiros_todos = df_terceiros.copy()

    if tipo_peso == 'Peso sobre Produção':
        df_peso_prod = df_peso[df_peso['Tipo'] == 'DIRETO']
        df_peso_prod['Índice'] = df_peso_prod['PRODUÇÃO']
        peso_direto_indireto = df_peso_prod.groupby('Obra').apply(
            lambda g: (g['Base Remuneração'] * g['Índice']).sum() / g['Índice'].sum() if g['Índice'].sum() > 0 else 0
        ).reset_index(name='Peso Financeiro')
    else:
        df_peso['Índice'] = df_peso['Total Extra']
        peso_direto_indireto = df_peso.groupby('Obra').apply(
            lambda g: (g['Base Remuneração'] * g['Índice']).sum() / g['Índice'].sum() if g['Índice'].sum() > 0 else 0
        ).reset_index(name='Peso Financeiro')

    # Somar quantidade de terceiros por obra (sem filtro)
    peso_terceiros = df_terceiros_todos.groupby('Obra')['QUANTIDADE'].sum().reset_index()

    # Juntar todas as obras que aparecem em peso direto/indireto ou terceiros
    obras_todas = pd.Index(peso_direto_indireto['Obra']).union(peso_terceiros['Obra'])
    df_peso_completo = pd.DataFrame({'Obra': obras_todas})

    # Merge dos dados
    df_peso_completo = df_peso_completo.merge(peso_direto_indireto, on='Obra', how='left')
    df_peso_completo = df_peso_completo.merge(peso_terceiros, on='Obra', how='left')

    # Preencher NaN com 0
    df_peso_completo['Peso Financeiro'] = df_peso_completo['Peso Financeiro'].fillna(0)
    df_peso_completo['QUANTIDADE'] = df_peso_completo['QUANTIDADE'].fillna(0)

    # Ordenar por Peso Financeiro
    df_peso_completo = df_peso_completo.sort_values(by='Peso Financeiro', ascending=False).reset_index(drop=True)

    # Calcular percentual para labels
    total_peso = df_peso_completo['Peso Financeiro'].sum()
    df_peso_completo['Percentual'] = 100 * df_peso_completo['Peso Financeiro'] / total_peso

    # Definir cores: azul escuro para obras filtradas, azul claro para as outras
    df_peso_completo['Cor'] = df_peso_completo['Obra'].apply(
        lambda x: 'darkblue' if x in obras_selecionadas else 'lightblue'
    )

    # Gráfico de barras com percentuais como texto
    fig_peso = go.Figure()

    fig_peso.add_trace(go.Bar(
        x=df_peso_completo['Obra'],
        y=df_peso_completo['Peso Financeiro'],
        marker_color=df_peso_completo['Cor'],
        text=df_peso_completo['Percentual'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        name='Peso Financeiro'
    ))

    fig_peso.update_layout(
        title=f"Peso Financeiro por Obra ({tipo_peso})",
        xaxis_title="Obra",
        yaxis_title="Peso Financeiro (R$)",
        xaxis_tickangle=-45,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        bargap=0.3,
        height=450
    )

    st.plotly_chart(fig_peso, use_container_width=True)

def main():
    dashboard_efetivo()

if __name__ == "__main__":
    main()
