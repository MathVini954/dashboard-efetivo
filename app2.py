import streamlit as st
import pandas as pd

# ======= CONFIGURAÇÃO DA PÁGINA =======
st.set_page_config(
    page_title="Dashboard de Obras",
    page_icon="🏗️",
    layout="wide"
)

# ======= ESTILO CSS =======
st.markdown("""
<style>
.big-title { font-size:40px !important; font-weight: bold; text-align: center; }
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #f9f9f9;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ======= HEADER =======
st.markdown("<p class='big-title'>📊 Dashboard de Obras</p>", unsafe_allow_html=True)
st.write("Acompanhamento consolidado das obras - produção, efetivo e indicadores principais.")

# ======= UPLOAD DO ARQUIVO EXCEL =======
uploaded_file = st.file_uploader("Escolha a planilha Excel", type=["xlsx"])

if uploaded_file:
    # Lê todas as abas da planilha
    xls = pd.ExcelFile(uploaded_file)
    abas = xls.sheet_names
    
    for aba in abas:
        st.markdown(f"## 🏗️ {aba}")
        
        # Lê a aba como DataFrame
        df = pd.read_excel(uploaded_file, sheet_name=aba, header=None)
        
        # Cria um dicionário com os indicadores da obra
        indicadores = {}
        for i in range(len(df)):
            if pd.notna(df.iloc[i,0]):
                key = str(df.iloc[i,0]).strip()
                value = df.iloc[i,1] if len(df.columns) > 1 else None
                indicadores[key] = value
        
        # ======= CARDS DE RESUMO =======
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h4>AC (m²)</h4><p>{indicadores.get('AC (m²)', '-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Efetivo</h4><p>{indicadores.get('Ef', '-')}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Total Unidades</h4><p>{indicadores.get('Total Unidades', '-')}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='card'><h4>Avanço Real</h4><p>{indicadores.get('Avanço Físico Real', '-')}</p></div>", unsafe_allow_html=True)
        
        # ======= TABELA COMPLETA =======
        st.write("### 📋 Detalhes da Obra")
        df_indicadores = pd.DataFrame(list(indicadores.items()), columns=["Indicador", "Valor"])
        st.dataframe(df_indicadores, use_container_width=True)
        
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel para visualizar o dashboard.")
