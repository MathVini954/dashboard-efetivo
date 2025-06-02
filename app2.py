import streamlit as st
import pandas as pd
import plotly.express as px

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

    # Cálculo da coluna Total Extra
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
            df_filtrado = df_filtrado[0:0]

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

    # Pizza
    pizza_base = df[df['Obra'].isin(obras_selecionadas)]
    pizza_diretos_indiretos = pizza_base['Tipo'].value_counts().reset_index()
    pizza_diretos_indiretos.columns = ['Tipo', 'count']
    pizza_terceiros = pd.DataFrame({'Tipo': ['TERCEIRO'], 'count': [total_terceiros]})
    pizza = pd.concat([pizza_diretos_indiretos, pizza_terceiros], ignore_index=True)

    fig_pizza = px.pie(pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo')
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

    if tipo_analise == 'Produção' and 'REFLEXO S PRODUÇÃO' in df.columns:
        df_ranking['DSR'] = df_ranking['REFLEXO S PRODUÇÃO']
        ranking = df_ranking[['Nome do Funcionário', 'Funçao', 'Obra', 'Tipo', 'PRODUÇÃO', 'DSR']].sort_values(by='PRODUÇÃO', ascending=False)
    else:
        ranking = df_ranking[['Nome do Funcionário', 'Funçao', 'Obra', 'Tipo', coluna_valor]].sort_values(by=coluna_valor, ascending=False)

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
    graf_funcao = df_ranking['Funçao'].value_counts().reset_index()
    graf_funcao.columns = ['Funçao', 'Qtd']

    fig_bar = px.bar(
        graf_funcao,
        x='Funçao',
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
        hover_data=['Nome do Funcionário', 'Funçao', 'Obra'],
        title="Quadrantes de Eficiência - Produção vs Hora Extra"
    )
    st.plotly_chart(fig_quadrantes, use_container_width=True)

    st.divider()
    st.markdown("### 📈 Peso Financeiro por Obra")

    # Cálculos para gráficos novos
    df_peso = df[df['Tipo'].isin(['DIRETO', 'INDIRETO'])].copy()
    df_peso['Total Extra'] = df_peso['Hora Extra 70% - Semana'] + df_peso['Hora Extra 70% - Sabado']
    df_peso['Base Remuneração'] = df_peso['Remuneração Líquida Folha'] + df_peso['Adiantamento']

    if tipo_peso == 'Peso sobre Produção':
        df_peso['Índice'] = (df_peso['PRODUÇÃO'] + df_peso['REFLEXO S PRODUÇÃO']) / df_peso['Base Remuneração']
        titulo_peso = 'Peso sobre Produção por Obra'
    else:
        df_peso['Índice'] = (df_peso['Total Extra'] + df_peso['Repouso Remunerado']) / df_peso['Base Remuneração']
        titulo_peso = 'Peso sobre Hora Extra por Obra'

    df_peso = df_peso[df_peso['Base Remuneração'] > 0]
    media_por_obra = df_peso.groupby('Obra')['Índice'].mean().reset_index()

    # Destaque da obra selecionada
    media_por_obra['Cor'] = media_por_obra['Obra'].apply(
        lambda x: 'Obra Selecionada' if x in obras_selecionadas else 'Outras Obras'
    )

    fig_peso = px.bar(
        media_por_obra,
        x='Obra',
        y='Índice',
        color='Cor',
        title=titulo_peso,
        text=media_por_obra['Índice'].apply(lambda x: f"{x:.2f}")
    )
    fig_peso.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_peso, use_container_width=True)

    st.divider()
    st.markdown("### 🏗️ Funcionários Terceirizados por Empresa e Obra")
    tabela_terceiros = df_terceiros_filtrado.groupby(['Obra', 'EMPRESA'])['QUANTIDADE'].sum().reset_index()
    st.dataframe(tabela_terceiros, use_container_width=True)

# Dicionário para mapear meses em inglês para abreviações em português
MES_POR_PT = {
    'Jan': 'Jan',
    'Feb': 'Fev',
    'Mar': 'Mar',
    'Apr': 'Abr',
    'May': 'Mai',
    'Jun': 'Jun',
    'Jul': 'Jul',
    'Aug': 'Ago',
    'Sep': 'Set',
    'Oct': 'Out',
    'Nov': 'Nov',
    'Dec': 'Dez'
}

# Mapeamento mês português para número do mês
MES_PT_PARA_NUM = {
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
}

def mes_ano_pt(dt):
    # Retorna string formatada em português tipo 'Abr/24'
    mes_eng = dt.strftime('%b')  # abreviação em inglês
    mes_pt = MES_POR_PT.get(mes_eng, mes_eng)
    ano = dt.strftime('%y')
    return f"{mes_pt}/{ano}"

def data_pt_para_datetime(mes_ano_pt_str):
    # Recebe string tipo "Abr/24" e converte para pd.Timestamp(ano, mes, dia=1)
    mes_pt, ano_str = mes_ano_pt_str.split('/')
    mes = MES_PT_PARA_NUM[mes_pt]
    ano = 2000 + int(ano_str)  # exemplo: '24' vira 2024
    return pd.Timestamp(year=ano, month=mes, day=1)

def dashboard_produtividade():
    def carregar_dados():
        df = pd.read_excel("produtividade.xlsx")
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        return df

    def filtrar_dados(df, tipo_obra, servico, datas_selecionadas):
        if tipo_obra != "Todos":
            df = df[df['TIPO_OBRA'] == tipo_obra]
        if servico:
            df = df[df['SERVIÇO'] == servico]
        if datas_selecionadas:
            datas_dt = [data_pt_para_datetime(d) for d in datas_selecionadas]
            df = df[df['DATA'].dt.to_period('M').isin(pd.to_datetime(datas_dt).to_period('M'))]
        return df

    def criar_grafico_produtividade(df):
        df_mensal = df.groupby(pd.Grouper(key='DATA', freq='M')).agg({
            'PRODUTIVIDADE_PROF_DIAM2': 'mean',
            'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'
        }).reset_index()

        df_mensal['DATA_FORMATADA_PT'] = df_mensal['DATA'].apply(mes_ano_pt)

        fig = px.line(df_mensal, x='DATA', y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                      labels={'value': 'Produtividade', 'DATA': 'Mês/Ano'},
                      title="Produtividade Profissional por M² (Real x Orçado)",
                      line_shape='linear', markers=True)

        fig.update_xaxes(
            tickformat="%b/%y",
            tickmode='array',
            tickvals=df_mensal['DATA'],
            ticktext=df_mensal['DATA_FORMATADA_PT']
        )

        return fig

    def criar_grafico_barras(df):
        df_produtividade_obra = df.groupby('TIPO_OBRA').agg({
            'PRODUTIVIDADE_PROF_DIAM2': 'mean'
        }).reset_index()
        fig_barras = px.bar(df_produtividade_obra, x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                            title="Produtividade Profissional Média por Tipo de Obra")
        return fig_barras

   df = carregar_dados()

    with st.sidebar:
        st.header("🔍 Filtros - Produtividade")
        tipo_obra_opcoes = ["Todos"] + df['TIPO_OBRA'].unique().tolist()
        tipo_obra = st.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)
        servicos_opcoes = df['SERVIÇO'].unique().tolist()
        servico = st.selectbox('Selecione o Serviço', servicos_opcoes)

        meses_unicos = df['DATA'].dt.to_period('M').drop_duplicates().sort_values()
        mes_ano_opcoes = [mes_ano_pt(pd.Timestamp(m.start_time)) for m in meses_unicos]

        datas_selecionadas = st.multiselect('Selecione o(s) Mês/Ano', mes_ano_opcoes, default=mes_ano_opcoes)

    # Aplica todos os filtros (tipo_obra, serviço, datas) para o gráfico principal
    df_filtrado = filtrar_dados(df, tipo_obra, servico, datas_selecionadas)

    # Aplica só o filtro de serviço e datas para o gráfico de barras, ignorando tipo_obra
    df_filtrado_barras = filtrar_dados(df, "Todos", servico, datas_selecionadas)

    fig_produtividade = criar_grafico_produtividade(df_filtrado)
    fig_barras = criar_grafico_barras(df_filtrado_barras)

    st.title("📈 Dashboard de Produtividade")
    st.plotly_chart(fig_produtividade)
    st.plotly_chart(fig_barras)
# ---------- Execução Principal ----------
def main():
    st.set_page_config(page_title="Dashboards de Obra", layout="wide")

    col1, col2 = st.columns([1, 4])

    with col1:
        st.image("logotipo.png", width=400)

    with col2:
        st.markdown(
            "<h1 style='margin-top: 30px; vertical-align: middle;'>SISTEMA DE CUSTO E PLANEJAMENTO</h1>",
            unsafe_allow_html=True,
        )

    st.sidebar.title("👋 Bem-vindo")

    aba1, aba2, aba3 = st.tabs(["📊 Efetivo", "📈 Produtividade", "🏗️ Análise Custo e Planejamento"])

    with aba1:
        dashboard_efetivo()

    with aba2:
        dashboard_produtividade()

    with aba3:
        st.title("🏗️ ANÁLISE CUSTO E PLANEJAMENTO")
        st.markdown(
            """
            <div style="text-align: center; margin-top: 100px;">
                <h2>ESTAMOS EM DESENVOLVIMENTO</h2>
                <div style="font-size: 50px; color: grey;">👷‍♂️🚧</div>
            </div>
            """, unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
