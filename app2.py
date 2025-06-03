import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================
# CONFIGURAÇÃO DA SIDEBAR HOVER/FIXA
# ======================================

def setup_hover_sidebar():
    """Configura o CSS e JavaScript para a sidebar hover/fixa"""
    
    # Estado para controlar se a sidebar está fixa
    if 'sidebar_fixed' not in st.session_state:
        st.session_state.sidebar_fixed = False
    
    # CSS customizado com JavaScript para controlar hover
    css = f"""
    <style>
        /* Container principal para controlar hover */
        .sidebar-hover-container {{
            position: fixed;
            left: 0;
            top: 0;
            width: {'350px' if st.session_state.sidebar_fixed else '20px'};
            height: 100vh;
            z-index: 999;
            transition: width 0.3s ease;
        }}
        
        /* Esconder/mostrar sidebar baseado no estado */
        .css-1d391kg {{
            transition: transform 0.3s ease-in-out !important;
            transform: translateX({'0px' if st.session_state.sidebar_fixed else '-100%'}) !important;
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%) !important;
            border-right: 2px solid #dee2e6 !important;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1) !important;
        }}
        
        /* Indicador visual na borda esquerda quando não está fixa */
        .sidebar-trigger {{
            position: fixed;
            left: 0;
            top: 0;
            width: 8px;
            height: 100vh;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
            z-index: 1000;
            opacity: {'0' if st.session_state.sidebar_fixed else '0.7'};
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .sidebar-trigger:hover {{
            width: 12px;
            opacity: 1;
        }}
        
        /* Botão de fixar/desafixar */
        .pin-button {{
            position: fixed;
            left: {'320px' if st.session_state.sidebar_fixed else '10px'};
            top: 10px;
            background: {'#ff4757' if st.session_state.sidebar_fixed else '#2ed573'};
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            z-index: 1001;
            font-size: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        
        .pin-button:hover {{
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        
        /* Ajustar o conteúdo principal */
        .main .block-container {{
            padding-left: {'20px' if not st.session_state.sidebar_fixed else '0px'};
            transition: padding-left 0.3s ease;
        }}
        
        /* Classe para mostrar sidebar */
        .sidebar-visible .css-1d391kg {{
            transform: translateX(0px) !important;
        }}
        
        /* Tooltip para o botão */
        .pin-button::after {{
            content: '{'Desafixar sidebar' if st.session_state.sidebar_fixed else 'Fixar sidebar'}';
            position: absolute;
            left: 50px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}
        
        .pin-button:hover::after {{
            opacity: 1;
        }}
    </style>
    
    <script>
        // Função para mostrar sidebar
        function showSidebar() {{
            if (!{str(st.session_state.sidebar_fixed).lower()}) {{
                document.body.classList.add('sidebar-visible');
            }}
        }}
        
        // Função para esconder sidebar
        function hideSidebar() {{
            if (!{str(st.session_state.sidebar_fixed).lower()}) {{
                document.body.classList.remove('sidebar-visible');
            }}
        }}
        
        // Função para alternar fixação
        function toggleSidebar() {{
            // Simula clique no botão do Streamlit
            const event = new Event('click');
            const button = document.querySelector('[data-testid="baseButton-secondary"]');
            if (button) {{
                button.click();
            }}
        }}
        
        // Adiciona eventos quando o DOM carregar
        document.addEventListener('DOMContentLoaded', function() {{
            const trigger = document.querySelector('.sidebar-trigger');
            const sidebar = document.querySelector('.css-1d391kg');
            
            if (trigger) {{
                trigger.addEventListener('mouseenter', showSidebar);
            }}
            
            if (sidebar) {{
                sidebar.addEventListener('mouseenter', showSidebar);
                sidebar.addEventListener('mouseleave', hideSidebar);
            }}
            
            // Observer para detectar mudanças no DOM
            const observer = new MutationObserver(function(mutations) {{
                const trigger = document.querySelector('.sidebar-trigger');
                const sidebar = document.querySelector('.css-1d391kg');
                
                if (trigger && !trigger.hasEventListener) {{
                    trigger.addEventListener('mouseenter', showSidebar);
                    trigger.hasEventListener = true;
                }}
                
                if (sidebar && !sidebar.hasEventListener) {{
                    sidebar.addEventListener('mouseenter', showSidebar);
                    sidebar.addEventListener('mouseleave', hideSidebar);
                    sidebar.hasEventListener = true;
                }}
            }});
            
            observer.observe(document.body, {{
                childList: true,
                subtree: true
            }});
        }});
        
        // Adiciona eventos imediatamente também
        setTimeout(function() {{
            const trigger = document.querySelector('.sidebar-trigger');
            const sidebar = document.querySelector('.css-1d391kg');
            
            if (trigger) {{
                trigger.addEventListener('mouseenter', showSidebar);
            }}
            
            if (sidebar) {{
                sidebar.addEventListener('mouseenter', showSidebar);
                sidebar.addEventListener('mouseleave', hideSidebar);
            }}
        }}, 100);
    </script>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    # Indicador visual na borda esquerda
    if not st.session_state.sidebar_fixed:
        st.markdown('<div class="sidebar-trigger" onmouseenter="showSidebar()"></div>', unsafe_allow_html=True)
    
    # Botão de fixar/desafixar
    st.markdown(f'''
    <button class="pin-button" onclick="toggleSidebar()" title="{'Desafixar sidebar' if st.session_state.sidebar_fixed else 'Fixar sidebar'}">
        {'📌' if st.session_state.sidebar_fixed else '📍'}
    </button>
    ''', unsafe_allow_html=True)

# ======================================
# FUNÇÕES DE CARREGAMENTO DE DADOS (sem alteração)
# ======================================

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

# ======================================
# DASHBOARD DE EFETIVO
# ======================================

def dashboard_efetivo():
    st.title("📊 Análise de Efetivo - Abril 2025")

    df = carregar_dados_efetivo()
    df_terceiros = carregar_terceiros()

    df['Total Extra'] = df['Hora Extra 70% - Semana'] + df['Hora Extra 70% - Sabado']

    with st.sidebar:
        st.header("🔍 Filtros - Efetivo")
        
        # Botão para alternar fixação da sidebar
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📌" if not st.session_state.sidebar_fixed else "📍", 
                        help="Fixar/Desafixar sidebar",
                        key="toggle_sidebar_efetivo"):
                st.session_state.sidebar_fixed = not st.session_state.sidebar_fixed
                st.rerun()
        
        lista_obras = sorted(df['Obra'].astype(str).unique())
        obras_selecionadas = st.multiselect("Obras:", lista_obras, default=lista_obras)
        tipo_selecionado = st.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
        tipo_analise = st.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
        qtd_linhas = st.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)
        tipo_peso = st.radio("Tipo de Peso (Gráficos Novos):", ['Peso sobre Produção', 'Peso sobre Hora Extra'])

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
   todas_obras = sorted(df['Obra'].astype(str).unique())
    peso_lista = []
    
    for obra in todas_obras:
        df_obra = df[df['Obra'] == obra]
        
        # Produção: só DIRETO
        df_direto = df_obra[df_obra['Tipo'] == 'DIRETO']
        prod_numerador = df_direto['PRODUÇÃO'].sum() + df_direto['REFLEXO S PRODUÇÃO'].sum()
        prod_denominador = df_direto['Remuneração Líquida Folha'].sum() + df_direto['Adiantamento'].sum()
        
        # Hora Extra: DIRETO + INDIRETO
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
    
    # CORREÇÃO: Usar coluna categórica ao invés de série de cores
    df_peso['Status'] = df_peso['Obra'].apply(
        lambda x: 'Selecionada' if x in obras_selecionadas else 'Não Selecionada'
    )
    
    fig_peso = px.bar(
        df_peso,
        x='Obra',
        y='Peso Financeiro',
        color='Status',  # Usar coluna categórica
        title=f'Peso Financeiro por Obra ({tipo_peso})',
        labels={'Peso Financeiro': 'Índice', 'Obra': 'Obra'},
        text=df_peso['Peso Financeiro'].apply(lambda x: f"{x:.2%}"),
        color_discrete_map={
            'Selecionada': 'darkblue',
            'Não Selecionada': 'lightblue'
        }
    )
    
    fig_peso.update_traces(textposition='outside')
    fig_peso.update_layout(yaxis_tickformat='.0%')
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
        
        # Botão para alternar fixação da sidebar
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📌" if not st.session_state.sidebar_fixed else "📍", 
                        help="Fixar/Desafixar sidebar",
                        key="toggle_sidebar_produtividade"):
                st.session_state.sidebar_fixed = not st.session_state.sidebar_fixed
                st.rerun()
        
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
    
    # Configura a sidebar hover/fixa
    setup_hover_sidebar()

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
