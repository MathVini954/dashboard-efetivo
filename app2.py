import pandas as pd
import plotly.express as px
import hashlib
import os
import streamlit as st

# ---------- Funções de autenticação ----------
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha, hash_s):
    return hash_senha(senha) == hash_s

def carregar_usuarios():
    if os.path.exists("usuarios.csv"):
        return pd.read_csv("usuarios.csv")
    else:
        return pd.DataFrame(columns=["usuario", "senha_hash"])

def salvar_usuario(usuario, senha_hash):
    df = carregar_usuarios()
    novo_usuario = pd.DataFrame([[usuario, senha_hash]], columns=["usuario", "senha_hash"])
    df = pd.concat([df, novo_usuario], ignore_index=True)
    df.to_csv("usuarios.csv", index=False)

# ---------- Tela de login/cadastro ----------
def tela_login():
    st.title("🔐 Login")

    menu = st.radio("Escolha uma opção:", ["Login", "Cadastrar"])

    if menu == "Login":
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            df_usuarios = carregar_usuarios()
            if usuario in df_usuarios['usuario'].values:
                senha_hash = df_usuarios[df_usuarios['usuario'] == usuario]['senha_hash'].values[0]
                if verificar_senha(senha, senha_hash):
                    st.session_state['logado'] = True
                    st.session_state['usuario'] = usuario
                    st.success("✅ Login realizado com sucesso!")
                    st.stop()
                else:
                    st.error("❌ Senha incorreta.")
            else:
                st.error("❌ Usuário não encontrado.")

    else:
        st.subheader("📋 Cadastro de Novo Usuário")
        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirme a senha", type="password")

        if st.button("Cadastrar"):
            if nova_senha != confirmar_senha:
                st.warning("⚠️ As senhas não coincidem.")
            elif novo_usuario.strip() == "":
                st.warning("⚠️ O nome de usuário não pode estar vazio.")
            else:
                df = carregar_usuarios()
                if novo_usuario in df['usuario'].values:
                    st.warning("⚠️ Usuário já existe.")
                else:
                    salvar_usuario(novo_usuario, hash_senha(nova_senha))
                    st.success("✅ Usuário cadastrado com sucesso! Faça login.")

# ---------- Dashboard de Efetivo ----------
@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", sheet_name="Efetivo", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    # Corrige colunas de hora extra
    for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Coluna Tipo: Direto ou Indireto
    df['Tipo'] = df['DIRETO / INDIRETO'].astype(str).str.upper().str.strip()
    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']

    # Lê a aba dos terceiros corretamente
    try:
        df_terceiros = pd.read_excel("efetivo_abril.xlsx", sheet_name="TERCEIROS", engine="openpyxl")
        df_terceiros.columns = df_terceiros.columns.str.strip()

        # Assume estrutura: Obra | Empresa | Qtd
        df_terceiros = df_terceiros.rename(columns={
            df_terceiros.columns[0]: 'Obra',
            df_terceiros.columns[1]: 'Empresa',
            df_terceiros.columns[2]: 'Qtd'
        })

        df_terceiros['Qtd'] = pd.to_numeric(df_terceiros['Qtd'], errors='coerce').fillna(0)
        df_terceiros['Obra'] = df_terceiros['Obra'].astype(str).str.strip()

    except Exception as e:
        df_terceiros = pd.DataFrame(columns=['Obra', 'Empresa', 'Qtd'])

    return df, df_terceiros


def dashboard_efetivo():
    st.header("📊 Efetivo da Obra")

    df, df_terceiros = carregar_dados_efetivo()

    obras = df['Obra'].dropna().unique()
    obras_selecionadas = st.multiselect("Selecione a(s) obra(s):", obras, default=obras)

    # Filtra dados principais e terceiros
    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
    df_terceiros_filtrado = df_terceiros[df_terceiros['Obra'].isin(obras_selecionadas)]
    total_terceiros = df_terceiros_filtrado['Qtd'].sum()

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("👷‍♂️ Direto", df_filtrado[df_filtrado['Tipo'] == 'DIRETO'].shape[0])
    col2.metric("🧑‍💼 Indireto", df_filtrado[df_filtrado['Tipo'] == 'INDIRETO'].shape[0])
    col3.metric("🏗️ Terceiros", int(total_terceiros))

    # Gráfico de Pizza
    pizza = df_filtrado['Tipo'].value_counts().reset_index()
    pizza.columns = ['Tipo', 'count']
    pizza = pd.concat([pizza, pd.DataFrame([{'Tipo': 'TERCEIROS', 'count': total_terceiros}])], ignore_index=True)

    fig_pizza = px.pie(pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo')
    st.plotly_chart(fig_pizza, use_container_width=True)

    # Gráfico de barras (Exemplo adicional, se quiser manter outro)
    fig_barra = px.bar(
        df_filtrado.groupby('Função').size().reset_index(name='Qtd'),
        x='Função', y='Qtd',
        title='Quantidade por Função'
    )
    st.plotly_chart(fig_barra, use_container_width=True)

    # Mostrar tabela de terceiros
    with st.expander("🔎 Ver empresas terceirizadas"):
        st.dataframe(df_terceiros_filtrado[['Obra', 'Empresa', 'Qtd']], hide_index=True)


# ---------- Dashboard de Produtividade ----------
def dashboard_produtividade():
    def carregar_dados():
        df = pd.read_excel("produtividade.xlsx")
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')
        return df

    def filtrar_dados(df, tipo_obra, servico, datas_selecionadas):
        if tipo_obra != "Todos":
            df = df[df['TIPO_OBRA'] == tipo_obra]
        if servico:
            df = df[df['SERVIÇO'] == servico]
        if datas_selecionadas:
            df = df[df['DATA_FORMATADA'].isin(datas_selecionadas)]
        return df

    def criar_grafico_produtividade(df):
        df_mensal = df.groupby('DATA_FORMATADA').agg({
            'PRODUTIVIDADE_PROF_DIAM2': 'mean',
            'PRODUTIVIDADE_ORCADA_DIAM2': 'mean'
        }).reset_index()
        fig = px.line(df_mensal, x='DATA_FORMATADA', y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                      labels={'value': 'Produtividade', 'DATA_FORMATADA': 'Mês/Ano'},
                      title="Produtividade Profissional por M² (Real x Orçado)",
                      line_shape='linear', markers=True)
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
        mes_ano_opcoes = df['DATA_FORMATADA'].unique().tolist()
        datas_selecionadas = st.multiselect('Selecione o(s) Mês/Ano', mes_ano_opcoes, default=mes_ano_opcoes)

    df_filtrado = filtrar_dados(df, tipo_obra, servico, datas_selecionadas)
    fig_produtividade = criar_grafico_produtividade(df_filtrado)
    fig_barras = criar_grafico_barras(df_filtrado)

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

    if "logado" not in st.session_state:
        st.session_state['logado'] = False
    if "usuario" not in st.session_state:
        st.session_state['usuario'] = ""

    if not st.session_state['logado']:
        tela_login()
    else:
        st.sidebar.title(f"👋 Bem-vindo, {st.session_state['usuario']}")

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
