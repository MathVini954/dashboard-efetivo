import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time    

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
            total_descontos += pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum()
    
    # Remuneração líquida
    remuneracao_liquida = total_ganhos + total_descontos
    
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
    st.title("📊 Análise de Efetivo - Obra")

    df = carregar_dados_efetivo()
    df_terceiros = carregar_terceiros()

    # 🔴 Excluir obra "ESCRITÓRIO ENGENHARIA"
    df = df[df['Obra'] != 'ESCRITÓRIO ENGENHARIA']
    df_terceiros = df_terceiros[df_terceiros['Obra'] != 'ESCRITÓRIO ENGENHARIA']

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

    # Filtra obras selecionadas
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

    # Análise Financeira
    if not df_filtrado.empty and tipo_selecionado != 'TERCEIRO':
        st.markdown("### 💰 Análise Financeira")
        
        if analise_financeira == 'Geral':
            fig_cascata, total_ganhos, total_descontos, remuneracao_liquida = criar_grafico_cascata(df_filtrado, ganhos, descontos)
            st.plotly_chart(fig_cascata, use_container_width=True)
            
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

    fig_pizza = px.pie(pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo', hole=0.3)
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
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
        valor_coluna = 'PRODUÇÃO'
    else:
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Obra', 'Tipo', coluna_valor]
        valor_coluna = coluna_valor

    cols_rank = [c for c in cols_rank if c is not None and c in df_ranking.columns]
    df_ranking_limp = df_ranking[cols_rank].copy()
    df_ranking_limp = df_ranking_limp[pd.to_numeric(df_ranking_limp[valor_coluna], errors='coerce').notna()]
    df_ranking_limp = df_ranking_limp[df_ranking_limp[valor_coluna] > 0]
    ranking = df_ranking_limp.sort_values(by=valor_coluna, ascending=False)

    valor_total = df_ranking_limp[valor_coluna].sum()
    st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
    st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if qtd_linhas != 'Todos':
        ranking = ranking.head(int(qtd_linhas))

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

    todas_obras = sorted(df['Obra'].astype(str).unique())
    peso_lista = []
    for obra in todas_obras:
        df_obra = df[df['Obra'] == obra]
        df_direto = df_obra[df_obra['Tipo'] == 'DIRETO']
        prod_numerador = df_direto['PRODUÇÃO'].sum() + df_direto['REFLEXO S PRODUÇÃO'].sum()
        prod_denominador = df_direto['Remuneração Líquida Folha'].sum() + df_direto['Adiantamento'].sum()
        df_dir_ind = df_obra[df_obra['Tipo'].isin(['DIRETO', 'INDIRETO'])]
        total_extra = df_dir_ind['Total Extra'].sum()
        reposo_remunerado = df_dir_ind['Repouso Remunerado'].sum()
        hor_extra_denominador = df_dir_ind['Remuneração Líquida Folha'].sum() + df_dir_ind['Adiantamento'].sum()

        if tipo_peso == 'Peso sobre Produção':
            peso = (prod_numerador / prod_denominador) if prod_denominador > 0 else 0
        else:
            peso = ((total_extra + reposo_remunerado) / hor_extra_denominador) if hor_extra_denominador > 0 else 0

        peso_lista.append({'Obra': obra, 'Peso Financeiro': peso})

    df_peso = pd.DataFrame(peso_lista)
    df_peso = df_peso.sort_values(by='Peso Financeiro', ascending=False)
    df_peso['Selecionada'] = df_peso['Obra'].apply(lambda x: x in obras_selecionadas)
    colors = df_peso['Selecionada'].map({True: 'darkblue', False: 'lightblue'})

    fig_peso = px.bar(
        df_peso,
        x='Obra',
        y='Peso Financeiro',
        title=f'Peso Financeiro por Obra ({tipo_peso})',
        labels={'Peso Financeiro': 'Índice', 'Obra': 'Obra'},
        text=df_peso['Peso Financeiro'].apply(lambda x: f"{x:.2%}"),
    )

    fig_peso.update_traces(
        marker_color=colors,
        textposition='outside',
        marker_line_color='black',
        marker_line_width=0.5
    )
    
    fig_peso.update_layout(
        yaxis_tickformat='.0%',
        showlegend=False,
        xaxis={'categoryorder': 'array', 'categoryarray': df_peso['Obra']}
    )

    st.plotly_chart(fig_peso, use_container_width=True)


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

    def criar_grafico_indices_completos(df, servico):
        df['MÊS'] = df['DATA'].dt.to_period('M')
        df_mensal = df.groupby('MÊS').agg({
            'ÍNDICE S/ (PP+HH EXT.)': 'mean',
            'ÍNDICE + PP': 'mean',
            'ÍNDICE + PP + HH EXT': 'mean',
            'ÍNDICE ORÇADO': 'mean',
            'ÍNDICE + PP + HH EXT ACUMULADO': 'mean'
        }).reset_index()

        df_mensal['DATA'] = df_mensal['MÊS'].dt.to_timestamp()
        df_mensal['DATA_FORMATADA_PT'] = df_mensal['DATA'].apply(mes_ano_pt)

        # Renomear colunas com prefixo do serviço
        df_mensal_renomeado = df_mensal.rename(columns={
            'ÍNDICE S/ (PP+HH EXT.)': f'{servico} - ÍNDICE S/ (PP+HH EXT.)',
            'ÍNDICE + PP': f'{servico} - ÍNDICE + PP',
            'ÍNDICE + PP + HH EXT': f'{servico} - ÍNDICE + PP + HH EXT',
            'ÍNDICE ORÇADO': f'{servico} - ÍNDICE ORÇADO',
            'ÍNDICE + PP + HH EXT ACUMULADO': f'{servico} - ÍNDICE + PP + HH EXT ACUMULADO'
        })

        colunas_plot = [col for col in df_mensal_renomeado.columns if col.startswith(servico)]

        fig = px.line(
            df_mensal_renomeado,
            x='DATA',
            y=colunas_plot,
            labels={'value': 'Índice', 'DATA': 'Mês/Ano'},
            title=f"📈 Evolução dos Índices - {servico}",
            markers=True
        )

        fig.update_xaxes(
            tickformat="%b/%y",
            tickmode='array',
            tickvals=df_mensal_renomeado['DATA'],
            ticktext=df_mensal_renomeado['DATA_FORMATADA_PT']
        )

        return fig, df_mensal

    df = carregar_dados()

    with st.sidebar:
        st.header("🔍 Filtros - Produtividade")
        tipo_obra_opcoes = ["Todos"] + df['TIPO_OBRA'].dropna().unique().tolist()
        tipo_obra = st.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)

        servicos_opcoes = sorted(df['SERVIÇO'].dropna().unique().tolist())
        servico = st.selectbox('Selecione o Serviço (1 por vez)', servicos_opcoes)

        meses_unicos = df['DATA'].dt.to_period('M').drop_duplicates().sort_values()
        mes_ano_opcoes = [mes_ano_pt(pd.Timestamp(m.start_time)) for m in meses_unicos]
        datas_selecionadas = st.multiselect('Selecione o(s) Mês/Ano', mes_ano_opcoes, default=mes_ano_opcoes)

    # Aplicar filtros
    df_filtrado = filtrar_dados(df, tipo_obra, servico, datas_selecionadas)

    # Criar gráfico de linha com todas as colunas de índice
    fig_indices, df_mensal = criar_grafico_indices_completos(df_filtrado, servico)
    st.title("📈 Dashboard de Produtividade")
    st.plotly_chart(fig_indices, use_container_width=True)

    # Tabela com colunas específicas + desvio (positiva = economia de HH)
    df_mensal['MÊS/ANO'] = df_mensal['DATA'].apply(mes_ano_pt)
    df_tabela = df_mensal[['MÊS/ANO', 'ÍNDICE ORÇADO', 'ÍNDICE + PP + HH EXT']].copy()
    df_tabela['DESVIO'] = df_tabela['ÍNDICE ORÇADO'] - df_tabela['ÍNDICE + PP + HH EXT']
    df_tabela = df_tabela.round(2)

    st.markdown("### 📊 Tabela de Índices e Desvio (Orçado - Real)")
    st.dataframe(df_tabela, use_container_width=True)


# ======================================
# FUNÇÕES DE CARREGAMENTO DE DADOS (COMPARTILHADAS)
# ======================================

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", sheet_name="EFETIVO", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df[df['Obra'].notna()]  # Remove linhas com 'Obra' vazia/nan
    
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
    df_terceiros = df_terceiros[df_terceiros['Obra'].notna()]  # Remove linhas com 'Obra' vazia/nan
    df_terceiros['QUANTIDADE'] = pd.to_numeric(df_terceiros['QUANTIDADE'], errors='coerce').fillna(0).astype(int)
    return df_terceiros

def definir_colunas_ganhos_descontos():
    """Define as colunas de ganhos e descontos (compartilhada)"""
    ganhos = [
        'SALÁRIO', 'Periculosidade', 'Dias De Atestado', 'Gratificação', 
        'Adicional noturno 20%', 'Ajuda De Saude', 'Auxilio Creche', 
        'Auxilio Educacao', 'EQUIP. TRAB/FERRAMENTA', 'Auxilio Moradia',
        'Auxilio Transporte', 'Adicional Noturno 20%', 'Dev.desc.indevido',
        'Salário Substituiçã', 'Reflexo S/ He Produção', 'Reembolso V. Transporte',
        'Prêmio', 'Premio-gestao Desempenho', 'Passagem Interior',
        'Passagem Interior Adiantamento', 'Hora Extra 70% - Sabado',
        'Hora Extra 70% - Semana', 'Salário Maternidade', 'Adicional H.e S/ Producao 70%',
        'PRODUÇÃO', 'AJUDA DE CUSTO', 'Ajuda de Custo Combustivel', 'REFLEXO S PRODUÇÃO',
        'Hora Extra 100%', 'Repouso Remunerado', 'Periculosidade', 'Salário Família',
        'Insuficiência de Saldo', 'Auxilio Transporte Retroativo', 'Insuficiência de Saldo'
    ]
    
    descontos = [
        'Atrasos', 'Faltas em Dias', 'Assistencia Medica', 'Coparticipacao Dependente',
        'Coparticipacao Titular', 'Desconto Empréstimo', 'Diferenca Plano De Saude',
        'Desconto Ótica', 'Plano Odontologico', 'Plano Odontologico Dependente',
        'Pensão Alimentícia  Salário Mínimo', 'Assitência Médica Dependente',
        'Dsr sobre falta', 'INSS Folha', 'IRRF Folha', 'Pensão Alimentícia', 
        'DESCONTO DE ALIMENTAÇÃO', 'MENSALIDADE SINDICAL', 'Vale Transporte',
        'Correção adiantamento'
    ]
    return ganhos, descontos

# ======================================
# DASHBOARD ESCRITÓRIO (NOVO)
# ======================================
# Adicione esta função ao seu código existente

def dashboard_escritorio():
    st.title("🏢 Análise de Efetivo - Escritório")

    # Carrega dados
    df = carregar_dados_efetivo()
    
    # Filtra apenas escritório engenharia
    df = df[df['Obra'] == 'ESCRITÓRIO ENGENHARIA']
    
    # Verifica se existe coluna Departamento
    if 'Departamento' not in df.columns:
        st.error("Coluna 'Departamento' não encontrada!")
        return

    lista_departamentos = sorted(df['Departamento'].astype(str).unique())
    lista_funcionarios = sorted(df['Nome do Funcionário'].unique())  # Lista para o novo filtro
    
    ganhos, descontos = definir_colunas_ganhos_descontos()
    df['Total Extra'] = df['Hora Extra 70% - Semana'] + df['Hora Extra 70% - Sabado']

    with st.sidebar:
        st.header("🔍 Filtros - Escritório")
        departamentos_selecionados = st.multiselect(
            "Departamentos:", 
            lista_departamentos, 
            default=lista_departamentos,
            key="escritorio_deptos"
        )
        tipo_selecionado = st.radio(
            "Tipo:", 
            ['Todos', 'DIRETO', 'INDIRETO'],
            horizontal=True,
            key="escritorio_tipo"
        )
        tipo_analise = st.radio(
            "Tipo de Análise da Tabela:", 
            ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'],
            key="escritorio_analise"
        )
        qtd_linhas = st.radio(
            "Qtd. de Funcionários na Tabela:", 
            ['5', '10', '20', 'Todos'], 
            horizontal=True,
            key="escritorio_qtd"
        )
        tipo_peso = st.radio(
            "Tipo de Peso:", 
            ['Peso sobre Produção', 'Peso sobre Hora Extra'],
            key="escritorio_peso"
        )
        
        st.divider()
        st.header("💰 Análise Financeira")
        analise_financeira = st.radio(
            "Análise:", 
            ['Geral', 'Ganhos', 'Descontos'],
            key="escritorio_financeira"
        )

    # Filtra dados por departamento e tipo
    df_filtrado = df[df['Departamento'].isin(departamentos_selecionados)]
    
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]

    # Novo filtro por funcionário (apenas para análise financeira)
    if analise_financeira in ['Geral', 'Ganhos', 'Descontos']:
        funcionario_selecionado = st.selectbox(
            "🔎 Filtrar por funcionário (opcional):",
            ["Todos"] + lista_funcionarios,
            key="filtro_funcionario"
        )
        
        if funcionario_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Nome do Funcionário'] == funcionario_selecionado]

    # Métricas (sem terceiros)
    direto_count = len(df_filtrado[df_filtrado['Tipo'] == 'DIRETO'])
    indireto_count = len(df_filtrado[df_filtrado['Tipo'] == 'INDIRETO'])
    total_geral = direto_count + indireto_count

    col1, col2, col3 = st.columns(3)
    col1.metric("👷 Direto", direto_count)
    col2.metric("👷‍♂️ Indireto", indireto_count)
    col3.metric("👥 Total", total_geral)

    st.divider()
  
    # Análise Financeira
    if not df_filtrado.empty:
        st.markdown("### 💰 Análise Financeira")
        
        if analise_financeira == 'Geral':
            fig_cascata, total_ganhos, total_descontos, remuneracao_liquida = criar_grafico_cascata(df_filtrado, ganhos, descontos)
            st.plotly_chart(fig_cascata, use_container_width=True)
            
            # Resumo dos valores financeiros
            col_fin1, col_fin2, col_fin3 = st.columns(3)
            col_fin1.metric("💚 Total Ganhos", 
                          f"R$ {total_ganhos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            col_fin2.metric("💸 Total Descontos", 
                          f"R$ {total_descontos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            col_fin3.metric("💰 Remuneração Líquida", 
                          f"R$ {remuneracao_liquida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
        elif analise_financeira == 'Ganhos':
            fig_ganhos = criar_grafico_detalhado(
                df_filtrado=df_filtrado,
                colunas=ganhos,
                titulo="Detalhamento dos Ganhos - Escritório",
                cor="green"
            )
            if fig_ganhos:
                st.plotly_chart(fig_ganhos, use_container_width=True)
            else:
                st.warning("Nenhum dado de ganhos encontrado para os filtros selecionados.")
                
        elif analise_financeira == 'Descontos':
            fig_descontos = criar_grafico_detalhado(
                df_filtrado=df_filtrado,
                colunas=descontos,
                titulo="Detalhamento dos Descontos - Escritório",
                cor="red"
            )
            if fig_descontos:
                st.plotly_chart(fig_descontos, use_container_width=True)
            else:
                st.warning("Nenhum dado de descontos encontrado para os filtros selecionados.")
        
        st.divider()

    # Gráfico de Pizza - Apenas diretos e indiretos
    pizza_base = df[df['Departamento'].isin(departamentos_selecionados)]
    pizza_diretos_indiretos = pizza_base['Tipo'].value_counts().reset_index()
    pizza_diretos_indiretos.columns = ['Tipo', 'count']
    
    fig_pizza = px.pie(
        pizza_diretos_indiretos,
        names='Tipo', 
        values='count', 
        title='Distribuição por Tipo de Efetivo (Escritório)',
        hole=0.3
    )
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pizza, use_container_width=True)

    # [...] (restante do código existente - ranking, gráfico por função, peso financeiro)

   
    # Ranking de Funcionários (ajustado para departamento)
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
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Departamento', 'Tipo', 'PRODUÇÃO', 'DSR']
        valor_coluna = 'PRODUÇÃO'
    else:
        cols_rank = ['Nome do Funcionário', nome_col_funcao, 'Departamento', 'Tipo', coluna_valor]
        valor_coluna = coluna_valor

    cols_rank = [c for c in cols_rank if c is not None and c in df_ranking.columns]
    df_ranking_limp = df_ranking[cols_rank].copy()
    df_ranking_limp = df_ranking_limp[pd.to_numeric(df_ranking_limp[valor_coluna], errors='coerce').notna()]
    df_ranking_limp = df_ranking_limp[df_ranking_limp[valor_coluna] > 0]
    ranking = df_ranking_limp.sort_values(by=valor_coluna, ascending=False)

    valor_total = df_ranking_limp[valor_coluna].sum()
    st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
    st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if qtd_linhas != 'Todos':
        ranking = ranking.head(int(qtd_linhas))

    def formatar_valor(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    ranking[valor_coluna] = ranking[valor_coluna].apply(formatar_valor)
    if 'DSR' in ranking.columns:
        ranking['DSR'] = ranking['DSR'].apply(formatar_valor)

    st.dataframe(ranking, use_container_width=True)
    st.divider()
    
    # Gráfico por Função (se existir a coluna)
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

    # Gráfico de Peso Financeiro (ajustado para departamento)
    todos_departamentos = sorted(df['Departamento'].astype(str).unique())
    peso_lista = []
    for depto in todos_departamentos:
        df_depto = df[df['Departamento'] == depto]
        df_direto = df_depto[df_depto['Tipo'] == 'DIRETO']
        prod_numerador = df_direto['PRODUÇÃO'].sum() + df_direto['REFLEXO S PRODUÇÃO'].sum()
        prod_denominador = df_direto['Remuneração Líquida Folha'].sum() + df_direto['Adiantamento'].sum()
        df_dir_ind = df_depto[df_depto['Tipo'].isin(['DIRETO', 'INDIRETO'])]
        total_extra = df_dir_ind['Total Extra'].sum()
        reposo_remunerado = df_dir_ind['Repouso Remunerado'].sum()
        hor_extra_denominador = df_dir_ind['Remuneração Líquida Folha'].sum() + df_dir_ind['Adiantamento'].sum()

        if tipo_peso == 'Peso sobre Produção':
            peso = (prod_numerador / prod_denominador) if prod_denominador > 0 else 0
        else:
            peso = ((total_extra + reposo_remunerado) / hor_extra_denominador) if hor_extra_denominador > 0 else 0

        peso_lista.append({'Departamento': depto, 'Peso Financeiro': peso})

    df_peso = pd.DataFrame(peso_lista)
    df_peso = df_peso.sort_values(by='Peso Financeiro', ascending=False)
    df_peso['Selecionada'] = df_peso['Departamento'].apply(lambda x: x in departamentos_selecionados)
    colors = df_peso['Selecionada'].map({True: 'darkblue', False: 'lightblue'})

        # Código anterior...
    
    fig_peso = px.bar(
        df_peso,
        x='Departamento',
        y='Peso Financeiro',
        title=f'Peso Financeiro por Departamento ({tipo_peso})',
        labels={'Peso Financeiro': 'Índice', 'Departamento': 'Departamento'},
        text=df_peso['Peso Financeiro'].apply(lambda x: f"{x:.2%}"),
    )

    fig_peso.update_traces(
        marker_color=colors,
        textposition='outside',
        marker_line_color='black',
        marker_line_width=0.5
    )
    
    fig_peso.update_layout(
        yaxis_tickformat='.0%',
        showlegend=False,
        xaxis={'categoryorder': 'array', 'categoryarray': df_peso['Departamento']}
    )
    
    st.plotly_chart(fig_peso, use_container_width=True) 
# ======================================
# FUNÇÕES COMPARTILHADAS (dos outros dashboards)
# ======================================

def criar_grafico_cascata(df_filtrado, ganhos, descontos):
    """Cria o gráfico de cascata (compartilhado)"""
    total_ganhos = sum(pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum() for col in ganhos if col in df_filtrado.columns)
    total_descontos = sum(pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum() for col in descontos if col in df_filtrado.columns)
    remuneracao_liquida = total_ganhos + total_descontos

    fig = go.Figure(go.Waterfall(
        name="Fluxo Financeiro",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=['Ganhos', 'Descontos', 'Remuneração Líquida'],
        text=[f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in [total_ganhos, total_descontos, remuneracao_liquida]],
        y=[total_ganhos, total_descontos, 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))

    fig.update_layout(
        title="Análise Financeira - Ganhos vs Descontos",
        showlegend=False,
        yaxis_title="Valor (R$)",
        xaxis_title="Categoria"
    )
    
    return fig, total_ganhos, total_descontos, remuneracao_liquida

def criar_grafico_detalhado(df_filtrado, colunas, titulo, cor):
    """Função corrigida - remove referência a df_peso"""
    dados_detalhados = []
    
    for col in colunas:
        if col in df_filtrado.columns:
            valor = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0).sum()
            if valor != 0:
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
# EXECUÇÃO PRINCIPAL (com a nova aba)
# ======================================


def main():
    st.set_page_config(page_title="Dashboards Inteligentes", layout="wide")
    
    # 1. Configuração do estado inicial
    if 'aba_atual' not in st.session_state:
        st.session_state.aba_atual = "📊 Efetivo Obra"
    
    # 2. Cabeçalho
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logotipo.png", width=400)
    with col2:
        st.markdown("<h1 style='margin-top: 30px;'>SISTEMA INTELIGENTE DE GESTÃO</h1>", unsafe_allow_html=True)
    
    # 3. Sidebar com navegação instantânea
    with st.sidebar:
        st.title("🎛️ Painel de Controle")
        
        # Cria botões estilo aba para melhor UX
        opcoes_abas = {
            "📊": "efetivo",
            "📈": "produtividade",
            "🏢": "escritorio"
        }
        
        # Exibe como botões horizontais
        cols = st.columns(len(opcoes_abas))
        for idx, (nome_aba, aba_key) in enumerate(opcoes_abas.items()):
            with cols[idx]:
                if st.button(nome_aba, key=f"btn_{aba_key}"):
                    st.session_state.aba_atual = nome_aba
    
    # 4. Renderização condicional
    try:
        if st.session_state.aba_atual == "📊":
            dashboard_efetivo()
        elif st.session_state.aba_atual == "🏢":
            dashboard_escritorio()
        elif st.session_state.aba_atual == "📈":
            dashboard_produtividade()

            
    except Exception as e:
        st.error(f"Erro ao carregar o dashboard: {str(e)}")
        st.session_state.aba_atual = "📊"  # Volta para aba segura

if __name__ == "__main__":
    main()

