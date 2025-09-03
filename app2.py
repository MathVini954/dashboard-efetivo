import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste Leitura Planilha", layout="wide")

uploaded_file = st.file_uploader("📥 Faça upload da planilha Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    abas = xls.sheet_names
    st.write("Abas encontradas:", abas)
    
    for aba in abas:
        st.write(f"### Aba: {aba}")
        # Lê apenas as duas primeiras colunas como string
        df = pd.read_excel(uploaded_file, sheet_name=aba, usecols="A:B", dtype=str)
        # Limpa espaços
        df[0] = df[0].str.strip()
        df[1] = df[1].str.strip()
        # Exibe exatamente o que foi lido
        st.dataframe(df)
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel.")

