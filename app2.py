import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", sheet_name="EFETIVO", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df['Hora Extra 70% - Semana'] = pd.to_numeric(df['Hora Extra 70% - Semana'], errors='coerce').fillna(0)
    df['Hora Extra 70% - Sabado'] = pd.to_numeric(df['Hora Extra 70% - Sabado'], errors='coerce').fillna(0)
    return df

@st.cache_data
def carregar_terceiros():
    df_terceiros = pd.read_excel("efetivo_abril.xlsx", sheet_name="TERCEIROS", engine="openpyxl")
    df_terceiros.columns = df_terceiros.columns.str.strip()
    df_terceiros['QUANTIDADE'] = pd.to_numeric(df_terceiros['QUANTIDADE'], errors='coerce').fillna(0).astype(int)
    return df_terceiros

def dashboard_efetivo():
    st.title("📊 Análise de Efetivo - Abril 2025")

    df = carregar_dados_efetivo()
    df_terceiros = carregar_terceiros()

    df['Total Extra'] = df['Hora Extra 70% - Semana'] + df['Hora Extra 70% - Sabado']

    with st.sidebar:
        st.header("🔍 Filtros - Efetivo")
        lista_obras = sorted(df['Obra'].astype(str).unique())
        obras_selecionadas = st.multiselect("Obras:", lista_obras, default=lista_obras)
        tipo_selecionado = st.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
        tipo_analise = st.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
        qtd_linhas = st.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)
        tipo_peso = st.radio("Tipo de Peso (Gráficos Novos):", ['Peso sobre Produção', 'Peso sobre Hora Extra'])

    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
    df_terceiros_filtrado = df_terceiros[df_terceiros['Obra'].isin(obras_selecionadas)]

    if tipo_selecionado != 'Todos':
        if tipo_selecionado in ['DIRETO', 'INDIRETO']:
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]
        elif tipo_selecionado == 'TERCEIRO':
            df_filtrado = df_filtrado[0:0]  # vazio, pois terceiros estão em outro DF

    direto_count = len(df[df['Obra'].isin(obras_selecionadas) & (df['Tipo'] == 'DIRETO')])
    indireto_count = len(df[df['Obra'].isin(obras_selecionadas) & (df['Tipo'] == 'INDIRETO')])
    total_terceiros = df_terceiros_filtrado['QUANTIDADE'].sum()
    total_geral = direto_count + indireto_count + total_terceiros

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Direto", direto_count)
    col2.metric("👷‍♂️ Indireto", indireto_count)
    col3.metric("🏗️ Terceiro", total_terceiros)
    col4.metric("👥 Total", total_geral)

    st.divider()

    # Pizza - Distribuição por tipo
    pizza_base = df[df['Obra'].isin(obras_selecionadas)]
    pizza_diretos_indiretos = pizza_base['Tipo'].value_counts().reset_index()
    pizza_diretos_indiretos.columns = ['Tipo', 'count']
    pizza_terceiros = pd.DataFrame({'Tipo': ['TERCEIRO'], 'count': [total_terceiros]})
    pizza = pd.concat([pizza_diretos_indiretos, pizza_terceiros], ignore_index=True)

    fig_pizza = px.pie(pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo', 
                       labels={'count':'Quantidade', 'Tipo':'Tipo'})
    st.plotly_chart(fig_pizza, use_container_width=True)

    if tipo_selecionado == 'TERCEIRO':
        st.divider()
        st.markdown("### 🏗️ Funcionários Terceirizados por Empresa e Obra")
        tabela_terceiros = df_terceiros_filtrado.groupby(['Obra', 'EMPRESA'])['QUANTIDADE'].sum().reset_index()
        st.dataframe(tabela_terceiros, use_container_width=True)
        return

    coluna_valor = {
        'Produção': 'PRODUÇÃO',
        'Hora Extra Semana': 'Hora Extra 70% - Semana',
        'Hora Extra Sábado': 'Hora Extra 70% - Sabado'
    }[tipo_analise]

    if tipo_selecionado == 'Todos':
        df_ranking = df_filtrado[df_filtrado['Tipo'].isin(['DIRETO', 'INDIRETO'])]
    else:
        df_ranking = df_filtrado

    nome_col_funcao = 'Função' if 'Função' in df_ranking.columns else 'Funçao' if 'Funçao' in df_ranking.columns else None

    if tipo_analise == 'Produção' and 'REFLEXO S PRODUÇÃO' in df_ranking.columns:
        df_ranking['DSR'] = df_ranking['REFLEXO S PRODUÇÃO']
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Obra', 'Tipo', 'PRODUÇÃO', 'DSR']
        cols_rank = [c for c in cols_rank if c is not None]
        ranking = df_ranking[cols_rank].sort_values(by='PRODUÇÃO', ascending=False)
    else:
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Obra', 'Tipo', coluna_valor]
        cols_rank = [c for c in cols_rank if c is not None]
        ranking = df_ranking[cols_rank].sort_values(by=coluna_valor, ascending=False)

    valor_total = df_ranking[coluna_valor].sum()
    st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
    st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if qtd_linhas != 'Todos':
        ranking = ranking.head(int(qtd_linhas))

    ranking[coluna_valor] = ranking[coluna_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    if 'DSR' in ranking.columns:
        ranking['DSR'] = ranking['DSR'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(ranking, use_container_width=True)

    st.divider()
    graf_funcao = df_ranking[nome_col_funcao].value_counts().reset_index()
    graf_funcao.columns = [nome_col_funcao, 'Qtd']

    fig_bar = px.bar(
        graf_funcao,
        x=nome_col_funcao,
        y='Qtd',
        color='Qtd',
        color_continuous_scale='Blues',
        title='Efetivo por Função',
        text='Qtd'
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.markdown("### 🎯 Quadrantes de Eficiência (Produção vs Hora Extra)")

    fig_quadrantes = px.scatter(
        df_ranking, x='Total Extra', y='PRODUÇÃO', color='Tipo',
        hover_data=['Nome do Funcionário', nome_col_funcao, 'Obra'],
        title="Quadrantes de Eficiência - Produção vs Hora Extra"
    )
    st.plotly_chart(fig_quadrantes, use_container_width=True)

    st.divider()
    st.markdown("### 📈 Peso Financeiro por Obra")

    df_peso = df[df['Tipo'].isin(['DIRETO', 'INDIRETO'])].copy()
    df_peso['Total Extra'] = df_peso['Hora Extra 70% - Semana'] + df_peso['Hora Extra 70% - Sabado']
    df_peso['Base Remuneração'] = df_peso['Remuneração Líquida Folha'] + df_peso['Adiantamento']

    if tipo_peso == 'Peso sobre Produção':
        # Usar só DIRETO para PRODUÇÃO (corrigido)
        df_peso = df_peso[df_peso['Tipo'] == 'DIRETO']
        df_peso['Índice'] = df_peso['PRODUÇÃO']
    else:
        # Peso sobre hora extra soma DIRETO + INDIRETO
        df_peso['Índice'] = df_peso['Total Extra']

    peso_financeiro = df_peso.groupby('Obra').apply(
        lambda g: (g['Base Remuneração'] * g['Índice']).sum() / g['Índice'].sum() if g['Índice'].sum() > 0 else 0
    ).reset_index(name='Peso Financeiro')

    # Para porcentagem:
    peso_financeiro['Percentual'] = 100 * peso_financeiro['Peso Financeiro'] / peso_financeiro['Peso Financeiro'].sum()

    fig_peso = px.bar(
        peso_financeiro,
        x='Obra',
        y='Peso Financeiro',
        title=f"Peso Financeiro por Obra ({tipo_peso})",
        text=peso_financeiro['Percentual'].apply(lambda x: f"{x:.1f}%"),
        labels={'Peso Financeiro': 'Peso Financeiro (R$)', 'Obra': 'Obra'}
    )
    fig_peso.update_traces(textposition='outside')
    st.plotly_chart(fig_peso, use_container_width=True)

def main():
    dashboard_efetivo()

if __name__ == '__main__':
    main()
