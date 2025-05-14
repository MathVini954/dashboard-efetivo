import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib

st.set_page_config(layout="wide")

# ========== FUNÇÕES ==========

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_usuario(nome, senha, df_usuarios):
    senha_hash = hash_senha(senha)
    df_usuarios['senha_hash'] = df_usuarios['senha'].apply(lambda x: hash_senha(str(x)))
    return nome in df_usuarios['nome'].values and senha_hash in df_usuarios[df_usuarios['nome'] == nome]['senha_hash'].values

@st.cache_data
def carregar_usuarios():
    return pd.read_excel("usuarios.xlsx")

@st.cache_data
def carregar_dados_efetivo():
    return pd.read_excel("efetivo.xlsx")

@st.cache_data
def carregar_dados_produtividade():
    return pd.read_excel("produtividade.xlsx")

# ========== AUTENTICAÇÃO ==========

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = ""

usuarios_df = carregar_usuarios()

if not st.session_state["autenticado"]:
    st.title("🔐 Login")
    nome_login = st.text_input("Usuário")
    senha_login = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if verificar_usuario(nome_login, senha_login, usuarios_df):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = nome_login
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")
    st.stop()

# ========== NAVEGAÇÃO ==========
st.sidebar.success(f"Bem-vindo, {st.session_state['usuario']}!")

st.title("📊 Dashboard Central")
opcao = st.selectbox("Selecione uma opção:", ["Dashboard de Efetivo", "Dashboard de Produtividade", "Custos e Planejamento"])

# ========== DASHBOARD DE EFETIVO ==========
if opcao == "Dashboard de Efetivo":
    st.header("📊 Dashboard de Efetivo")
    df = carregar_dados_efetivo()
    
    col1, col2, col3 = st.columns(3)
    obras = sorted(df['OBRA'].unique())
    selected_obra = col1.selectbox('Selecione a Obra:', obras)
    filtro_por_data = col2.checkbox('Filtrar por Data')
    datas_disponiveis = sorted(df['DATA'].unique())
    data_inicio = data_fim = None
    if filtro_por_data:
        data_inicio = col1.date_input('Data de início', value=pd.to_datetime(min(datas_disponiveis)))
        data_fim = col2.date_input('Data de fim', value=pd.to_datetime(max(datas_disponiveis)))

    df_filtered = df[df['OBRA'] == selected_obra]
    if filtro_por_data and data_inicio and data_fim:
        df_filtered = df_filtered[
            (df_filtered['DATA'] >= pd.to_datetime(data_inicio)) &
            (df_filtered['DATA'] <= pd.to_datetime(data_fim))
        ]

    col1, col2 = st.columns(2)
    col1.metric("Total de Profissionais", df_filtered['PROFISSIONAL'].sum())
    col2.metric("Total de Ajudantes", df_filtered['AJUDANTE'].sum())

    st.dataframe(df_filtered, use_container_width=True)

    fig = px.bar(df_filtered, x='DATA', y=['PROFISSIONAL', 'AJUDANTE'], barmode='group', title='Evolução de Profissionais e Ajudantes por Data')
    st.plotly_chart(fig, use_container_width=True)

# ========== DASHBOARD DE PRODUTIVIDADE ==========
elif opcao == "Dashboard de Produtividade":
    st.header("🚧 Dashboard de Produtividade")

    df_prod = carregar_dados_produtividade()

    obras_prod = sorted(df_prod['OBRA'].astype(str).unique())
    obras_selec = st.multiselect("Filtrar por Obra:", obras_prod, default=obras_prod)

    df_prod_filtrado = df_prod[df_prod['OBRA'].isin(obras_selec)]
    st.dataframe(df_prod_filtrado, use_container_width=True)

    if not df_prod_filtrado.empty:
        fig_prod = px.bar(
            df_prod_filtrado,
            x='SERVIÇO',
            y='PRODUTIVIDADE PROF. DIA/M²',
            color='OBRA',
            barmode='group',
            title='Produtividade por Serviço'
        )
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")

# ========== CUSTOS E PLANEJAMENTO ==========
elif opcao == "Custos e Planejamento":
    st.header("💰 Custos e Planejamento")
    st.info("Esta funcionalidade está em desenvolvimento.")
