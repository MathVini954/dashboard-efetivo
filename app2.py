
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

    # Remover obra '0'
    df = df[df['Obra'].astype(str) != "0"]
    df_terceiros = df_terceiros[df_terceiros['Obra'].astype(str) != "0"]

    with st.sidebar:
        st.header("🔍 Filtros - Efetivo")
        lista_obras = sorted(df['Obra'].astype(str).unique())
        obras_selecionadas = st.multiselect("Obras:", lista_obras, default=lista_obras)
        tipo_selecionado = st.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
        tipo_analise = st.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
        qtd_linhas = st.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)
        tipo_peso = st.radio("Peso a Exibir:", ['Peso sobre Produção', 'Peso sobre Hora Extra'], horizontal=True)

    # Filtrar dados para obras selecionadas e tipo
    df_filtrado = df[df['Obra'].isin(obras_selecionadas)].copy()
    df_terceiros_filtrado = df_terceiros[df_terceiros['Obra'].isin(obras_selecionadas)]

    if tipo_selecionado != 'Todos':
        if tipo_selecionado in ['DIRETO', 'INDIRETO']:
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]
        elif tipo_selecionado == 'TERCEIRO':
            df_filtrado = df_filtrado[0:0]  # vazio

    # Calcular Total Extra se não existir
    if 'Total Extra' not in df_filtrado.columns:
        df_filtrado['Total Extra'] = df_filtrado['Hora Extra 70% - Semana'] + df_filtrado['Hora Extra 70% - Sabado']

    # Garantir soma correta do Adiantamento com valores negativos
    df_filtrado['Remuneração Líquida Folha'] = pd.to_numeric(df_filtrado['Remuneração Líquida Folha'], errors='coerce').fillna(0)
    df_filtrado['Adiantamento'] = pd.to_numeric(df_filtrado['Adiantamento'], errors='coerce').fillna(0)
    df_filtrado['Remuneração Líquida Total'] = df_filtrado['Remuneração Líquida Folha'] + df_filtrado['Adiantamento']

    # Agrupar soma por obra
    grouped = df_filtrado.groupby('Obra').agg({
        'PRODUÇÃO': 'sum',
        'REFLEXO S PRODUÇÃO': 'sum',
        'Total Extra': 'sum',
        'Repouso Remunerado': 'sum',
        'Remuneração Líquida Total': 'sum',
    }).reset_index()

    grouped['Peso Produção'] = (grouped['PRODUÇÃO'] + grouped['REFLEXO S PRODUÇÃO']) / grouped['Remuneração Líquida Total'].replace(0, 1)
    grouped['Peso Hora Extra'] = (grouped['Total Extra'] + grouped['Repouso Remunerado']) / grouped['Remuneração Líquida Total'].replace(0, 1)

    # Cores para gráfico: azul escuro para todas as obras, laranja para obras selecionadas (destaque)
    cor_padrao = '#003366'  # Azul escuro
    cor_destaque = '#FFA500'  # Laranja

    cores = []
    for obra in grouped['Obra']:
        if obra in obras_selecionadas:
            cores.append(cor_destaque)
        else:
            cores.append(cor_padrao)

    if tipo_peso == 'Peso sobre Produção':
        y = grouped['Peso Produção']
        titulo = 'Peso sobre Produção ( (PRODUÇÃO + DSR) / Remuneração Líquida Total )'
    else:
        y = grouped['Peso Hora Extra']
        titulo = 'Peso sobre Hora Extra ( (Total Extra + Repouso Remunerado) / Remuneração Líquida Total )'

    fig = go.Figure(data=[go.Bar(
        x=grouped['Obra'],
        y=y,
        marker_color=cores,
        text=[f"{v:.2%}" for v in y],
        textposition='auto'
    )])
    fig.update_layout(
        title=titulo,
        xaxis_title='Obra',
        yaxis_title='Peso (proporção)',
        yaxis_tickformat='.0%',
        xaxis_tickangle=-45,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Métricas resumo
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

    # Se for tipo terceiro, mostrar somente tabela de terceiros e sair
    if tipo_selecionado == 'TERCEIRO':
        st.markdown("### 🏗️ Funcionários Terceirizados por Empresa e Obra")
        tabela_terceiros = df_terceiros_filtrado.groupby(['Obra', 'EMPRESA'])['QUANTIDADE'].sum().reset_index()
        st.dataframe(tabela_terceiros, use_container_width=True)
        return

    # Gráfico de pizza após o gráfico de pesos e antes da tabela de terceiros
    pizza_base = df[df['Obra'].isin(obras_selecionadas)]
    pizza_diretos_indiretos = pizza_base['Tipo'].value_counts().reset_index()
    pizza_diretos_indiretos.columns = ['Tipo', 'count']
    pizza_terceiros = pd.DataFrame({'Tipo': ['TERCEIRO'], 'count': [total_terceiros]})
    pizza = pd.concat([pizza_diretos_indiretos, pizza_terceiros], ignore_index=True)

    fig_pizza = px.pie(
        pizza,
        names='Tipo',
        values='count',
        title='Distribuição por Tipo de Efetivo',
        hole=0
    )
    fig_pizza.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pizza, use_container_width=True)

    st.divider()
    st.markdown("### 🏗️ Funcionários Terceirizados por Empresa e Obra")
    tabela_terceiros = df_terceiros_filtrado.groupby(['Obra', 'EMPRESA'])['QUANTIDADE'].sum().reset_index()
    st.dataframe(tabela_terceiros, use_container_width=True)

    # ... resto do código continua normalmente

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
