@st.cache_data
def carregar_usuarios():
    try:
        return pd.read_excel("usuarios.xlsx")
    except FileNotFoundError:
        st.error("Arquivo 'usuarios.xlsx' não encontrado.")
        st.stop()

@st.cache_data
def carregar_dados_efetivo():
    try:
        return pd.read_excel("efetivo.xlsx")
    except FileNotFoundError:
        st.error("Arquivo 'efetivo.xlsx' não encontrado.")
        st.stop()

@st.cache_data
def carregar_dados_produtividade():
    try:
        return pd.read_excel("produtividade.xlsx")
    except FileNotFoundError:
        st.error("Arquivo 'produtividade.xlsx' não encontrado.")
        st.stop()
