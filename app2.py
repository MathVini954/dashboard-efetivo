import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Imports necessários (adicione no início do seu arquivo)
import plotly.graph_objects as go
import plotly.express as px

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", sheet_name="EFETIVO", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df[df['Obra'].notna()]  # NOVO: Remove linhas com 'Obra' vazia/nan
    
    df['Hora Extra 70% - Semana'] = pd.to_numeric(df['Hora Extra 70% - Semana'], errors='coerce').fillna(0)
    df['Hora Extra 70% - Sabado'] = pd.to_numeric(df['Hora Extra 70% - Sabado'], errors='coerce').fillna(0)
    if 'Repouso Remunerado' not in df.columns:
        df['Repouso Remunerado'] = 0
    else:
        df['Repouso Remunerado'] = pd.to_numeric(df['Repouso Remunerado'], errors='coerce').fillna(0)
    df['Remuneração Líquida Folha'] = pd.to_numeric(df['Remuneração Líquida Folha'], errors='coerce').fillna(0)
    df['Adiantamento'] = pd.to_numeric(df['Adiantamento'], errors='coerce').fillna(0)
    return df

@st.cache_data
def carregar_terceiros():
    df_terceiros = pd.read_excel("efetivo_abril.xlsx", sheet_name="TERCEIROS", engine="openpyxl")
    df_terceiros.columns = df_terceiros.columns.str.strip()
    df_terceiros = df_terceiros[df_terceiros['Obra'].notna()]  # NOVO: Remove linhas com 'Obra' vazia/nan
    df_terceiros['QUANTIDADE'] = pd.to_numeric(df_terceiros['QUANTIDADE'], errors='coerce').fillna(0).astype(int)
    return df_terceiros

def definir_colunas_ganhos_descontos():
    """Define as colunas de ganhos e descontos"""
    ganhos = [
  'SALÁRIO',
    'Periculosidade',
    'Dias De Atestado',
    'Gratificação',
    'Adicional noturno 20%',
    'Ajuda De Saude',
    'Auxilio Creche',
    'Auxilio Educacao',
    'EQUIP. TRAB/FERRAMENTA',
    'Auxilio Moradia',
    'Auxilio Transporte',
    'Adicional Noturno 20%',
    'Dev.desc.indevido',
    'Salário Substituiçã',
    'Reflexo S/ He Produção',
    'Reembolso V. Transporte',
    'Prêmio',
    'Premio-gestao Desempenho',
    'Passagem Interior',
    'Passagem Interior Adiantamento',
    'Hora Extra 70% - Sabado',
    'Hora Extra 70% - Semana',
    'Salário Maternidade',
    'Adicional H.e S/ Producao 70%',
    'PRODUÇÃO',
    'AJUDA DE CUSTO',
    'Ajuda de Custo Combustivel',
    'REFLEXO S PRODUÇÃO',
    'Hora Extra 100%',
    'Repouso Remunerado',
    'Periculosidade',
    'Salário Família',
    'Insuficiência de Saldo',
    'Auxilio Transporte Retroativo',
    'Insuficiência de Saldo'
    ]
    
    descontos = [
 'Atrasos',
    'Faltas em Dias',
    'Assistencia Medica',
    'Coparticipacao Dependente',
    'Coparticipacao Titular',
    'Desconto Empréstimo',
    'Diferenca Plano De Saude',
    'Desconto Ótica',
    'Plano Odontologico',
    'Plano Odontologico Dependente',
    'Pensão Alimentícia  Salário Mínimo',
    'Assitência Médica Dependente',
    'Dsr sobre falta',
    'INSS Folha',
    'IRRF Folha',
    'Pensão Alimentícia', 'DESCONTO DE ALIMENTAÇÃO',
    'MENSALIDADE SINDICAL',
    'Vale Transporte','Correção adiantamento'


    ]

    
    return ganhos, descontos

def criar_grafico_cascata(df_filtrado, ganhos, descontos):
    """Cria o gráfico de cascata"""
    # Calcula totais
    total_ganhos = 0
    total_descontos = 0
    
    # Soma ganhos (colunas que existem no DataFrame)
    for col in ganhos:
        if col in df_filtrado.columns:
            total_ganhos += pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum()
    
    # Soma descontos (colunas que existem no DataFrame)
    for col in descontos:
        if col in df_filtrado.columns:
            total_descontos -= pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum()
    
    # Remuneração líquida
    remuneracao_liquida = total_ganhos - total_descontos
    
    # Dados para o gráfico de cascata
    categorias = ['Ganhos', 'Descontos', 'Remuneração Líquida']
    valores = [total_ganhos, total_descontos, remuneracao_liquida]
    cores = ['green', 'red', 'blue']
    
    fig_cascata = go.Figure()
    
    # Adiciona as barras
    fig_cascata.add_trace(go.Waterfall(
        name="Fluxo Financeiro",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=categorias,
        textposition="outside",
        text=[f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in [total_ganhos, total_descontos, remuneracao_liquida]],
        y=[total_ganhos, -total_descontos, 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))
    
    fig_cascata.update_layout(
        title="Análise Financeira - Ganhos vs Descontos",
        showlegend=False,
        yaxis_title="Valor (R$)",
        xaxis_title="Categoria"
    )
    
    return fig_cascata, total_ganhos, total_descontos, remuneracao_liquida

def criar_grafico_detalhado(df_filtrado, colunas, titulo, cor):
    """Cria gráfico de colunas detalhado para ganhos ou descontos"""
    dados_detalhados = []
    
    for col in colunas:
        if col in df_filtrado.columns:
            valor = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum()
            if valor != 0:  # Só inclui se houver valor
                dados_detalhados.append({'Categoria': col, 'Valor': valor})
    
    if not dados_detalhados:
        return None
    
    df_detalhado = pd.DataFrame(dados_detalhados)
    df_detalhado = df_detalhado.sort_values('Valor', ascending=False)
    
    fig_detalhado = px.bar(
        df_detalhado,
        x='Categoria',
        y='Valor',
        title=titulo,
        color_discrete_sequence=[cor],
        text=df_detalhado['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    )
    
    fig_detalhado.update_traces(textposition='outside')
    fig_detalhado.update_layout(xaxis_tickangle=-45)
    
    return fig_detalhado

# ======================================
# DASHBOARD DE EFETIVO
# ======================================

def dashboard_efetivo():
    st.title("📊 Análise de Efetivo - Abril 2025")

    df = carregar_dados_efetivo()
    df_terceiros = carregar_terceiros()
    ganhos, descontos = definir_colunas_ganhos_descontos()

    df['Total Extra'] = df['Hora Extra 70% - Semana'] + df['Hora Extra 70% - Sabado']

    with st.sidebar:
        st.header("🔍 Filtros - Efetivo")
        lista_obras = sorted(df['Obra'].astype(str).unique())
        obras_selecionadas = st.multiselect("Obras:", lista_obras, default=lista_obras)
        tipo_selecionado = st.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
        tipo_analise = st.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
        qtd_linhas = st.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)
        tipo_peso = st.radio("Tipo de Peso (Gráficos Novos):", ['Peso sobre Produção', 'Peso sobre Hora Extra'])
        
        st.divider()
        st.header("💰 Análise Financeira")
        analise_financeira = st.radio("Análise Financeira:", ['Geral', 'Ganhos', 'Descontos'])

    # Filtra obras selecionadas (já sem 'nan')
    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
    df_terceiros_filtrado = df_terceiros[df_terceiros['Obra'].isin(obras_selecionadas)]

    # Filtra por tipo
    if tipo_selecionado != 'Todos':
        if tipo_selecionado in ['DIRETO', 'INDIRETO']:
            df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]
        elif tipo_selecionado == 'TERCEIRO':
            df_filtrado = df_filtrado[0:0]  # vazio, terceiros estão em outro DF

    # Métricas principais
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

    # NOVO: Análise Financeira
    if not df_filtrado.empty and tipo_selecionado != 'TERCEIRO':
        st.markdown("### 💰 Análise Financeira")
        
        if analise_financeira == 'Geral':
            # Gráfico de cascata
            fig_cascata, total_ganhos, total_descontos, remuneracao_liquida = criar_grafico_cascata(df_filtrado, ganhos, descontos)
            st.plotly_chart(fig_cascata, use_container_width=True)
            
            # Métricas financeiras
            col_fin1, col_fin2, col_fin3 = st.columns(3)
            col_fin1.metric("💚 Total Ganhos", f"R$ {total_ganhos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            col_fin2.metric("💸 Total Descontos", f"R$ {total_descontos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            col_fin3.metric("💰 Remuneração Líquida", f"R$ {remuneracao_liquida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
        elif analise_financeira == 'Ganhos':
            fig_ganhos = criar_grafico_detalhado(df_filtrado, ganhos, "Detalhamento dos Ganhos", "green")
            if fig_ganhos:
                st.plotly_chart(fig_ganhos, use_container_width=True)
            else:
                st.warning("Nenhum dado de ganhos encontrado para os filtros selecionados.")
                
        elif analise_financeira == 'Descontos':
            fig_descontos = criar_grafico_detalhado(df_filtrado, descontos, "Detalhamento dos Descontos", "red")
            if fig_descontos:
                st.plotly_chart(fig_descontos, use_container_width=True)
            else:
                st.warning("Nenhum dado de descontos encontrado para os filtros selecionados.")
        
        st.divider()

    # Pizza - Distribuição por tipo
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

    nome_col_funcao = 'Função' if 'Função' in df_ranking.columns else 'Funçao' if 'Funçao' in df_ranking.columns else None

    # Define colunas a exibir e calcula DSR se necessário
    if tipo_analise == 'Produção' and 'REFLEXO S PRODUÇÃO' in df_ranking.columns:
        df_ranking['DSR'] = df_ranking['REFLEXO S PRODUÇÃO']
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Obra', 'Tipo', 'PRODUÇÃO', 'DSR']
        valor_coluna = 'PRODUÇÃO'
    else:
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Obra', 'Tipo', coluna_valor]
        valor_coluna = coluna_valor

    # Garante que as colunas existem
    cols_rank = [c for c in cols_rank if c is not None and c in df_ranking.columns]

    # 🔹 CÓPIA segura do df_ranking só para o ranking
    df_ranking_limp = df_ranking[cols_rank].copy()
    df_ranking_limp = df_ranking_limp[pd.to_numeric(df_ranking_limp[valor_coluna], errors='coerce').notna()]
    df_ranking_limp = df_ranking_limp[df_ranking_limp[valor_coluna] > 0]

    # Ordena
    ranking = df_ranking_limp.sort_values(by=valor_coluna, ascending=False)

    # Mostra total
    valor_total = df_ranking_limp[valor_coluna].sum()
    st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
    st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Filtra quantidade
    if qtd_linhas != 'Todos':
        ranking = ranking.head(int(qtd_linhas))

    # Formata valores
    def formatar_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    ranking[valor_coluna] = ranking[valor_coluna].apply(formatar_valor)
    if 'DSR' in ranking.columns:
        ranking['DSR'] = ranking['DSR'].apply(formatar_valor)

    st.dataframe(ranking, use_container_width=True)
    st.divider()
    
    if nome_col_funcao and nome_col_funcao in df_ranking.columns:
        graf_funcao = df_ranking[nome_col_funcao].value_counts().reset_index()
        graf_funcao.columns = [nome_col_funcao, 'Qtd']

        fig_bar = px.bar(
            graf_funcao,
            x=nome_col_funcao,
            y='Qtd',
            color='Qtd',
            color_continuous_scale='Blues',
            title='Quantidade por Função',
            labels={'Qtd': 'Quantidade', nome_col_funcao: 'Função'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

      # ---- INÍCIO da parte corrigida ----
    todas_obras = sorted(df['Obra'].astype(str).unique())  # <-- dentro da função!

    peso_lista = []
    for obra in todas_obras:
        # Base da obra
        df_obra = df[df['Obra'] == obra]

        # Produção: só DIRETO
        df_direto = df_obra[df_obra['Tipo'] == 'DIRETO']
        prod_numerador = df_direto['PRODUÇÃO'].sum() if 'PRODUÇÃO' in df_direto.columns else 0
        prod_denominador = df_obra['PRODUÇÃO'].sum() if 'PRODUÇÃO' in df_obra.columns else 0
        peso_producao = prod_numerador / prod_denominador if prod_denominador != 0 else 0

        # Hora extra: só DIRETO
        he_numerador = df_direto['Hora Extra 70% - Semana'].sum() + df_direto['Hora Extra 70% - Sabado'].sum()
        he_denominador = df_obra['Hora Extra 70% - Semana'].sum() + df_obra['Hora Extra 70% - Sabado'].sum()
        peso_he = he_numerador / he_denominador if he_denominador != 0 else 0

        if tipo_peso == 'Peso sobre Produção':
            peso = peso_producao
        else:
            peso = peso_he

        peso_lista.append({'Obra': obra, 'Peso Financeiro': peso})

    df_peso = pd.DataFrame(peso_lista)

    # Gráfico barra peso financeiro - todas as barras com mesma cor escura
    fig_peso = px.bar(
        df_peso,
        x='Obra',
        y='Peso Financeiro',
        title=f'Peso Financeiro por Obra ({tipo_peso})',
        labels={'Peso Financeiro': 'Índice', 'Obra': 'Obra'},
        text=df_peso['Peso Financeiro'].apply(lambda x: f"{x:.2%}"),
        color_discrete_sequence=['darkblue']  # cor fixa para todas as barras
    )
    fig_peso.update_traces(textposition='outside')
    fig_peso.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig_peso, use_container_width=True)
    # ---- FIM da parte corrigida ----


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


