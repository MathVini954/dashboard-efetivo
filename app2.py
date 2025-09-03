import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Obras",
    page_icon="🏗️",
    layout="wide"
)

# ======= ESTILO CSS =======
st.markdown("""
<style>
    .big-title { font-size:40px !important; font-weight: bold; text-align: center; }
    .section { padding: 30px 0; }
    .card {
        padding: 20px;
        border-radius: 15px;
        background-color: #f9f9f9;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ======= HEADER =======
st.markdown("<p class='big-title'>📊 Dashboard de Obras</p>", unsafe_allow_html=True)
st.write("Acompanhamento consolidado das obras - produção, efetivo e indicadores principais.")

# ======= LEITURA DA PLANILHA =======
file_path = "ONE_PAGE.xlsx"  # substitua pelo caminho certo
df = pd.read_excel(file_path)

# Identificar nomes das obras (linhas que contêm o nome da obra)
obras = df[df.iloc[:,0].notna()].iloc[:,0].unique()

# ======= LOOP DAS OBRAS =======
for obra in obras:
    with st.expander(f"🏗️ {obra}", expanded=False):
        # Filtra dados da obra
        obra_df = df[df.iloc[:,0] == obra]

        # ======= CARDS DE RESUMO =======
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='card'><h4>Produção</h4><p>📈 1200 m²</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='card'><h4>Efetivo</h4><p>👷 85 pessoas</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='card'><h4>Financeiro</h4><p>💰 R$ 1,2M</p></div>", unsafe_allow_html=True)

        st.write("### 📋 Detalhes")
        st.dataframe(obra_df)

        st.write("### 📊 Visualizações")
        st.bar_chart(obra_df.set_index(obra_df.columns[1]).iloc[:,1:])  # Exemplo de gráfico

