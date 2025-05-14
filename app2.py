@st.cache
def carregar_dados(arquivo):
    df = pd.read_excel(arquivo, engine="openpyxl")
    ...
