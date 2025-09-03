import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste Leitura Planilha", layout="wide")

uploaded_file = st.file_uploader("📥 Faça upload da planilha Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.write("Abas encontradas:", xls.sheet_names)

    for aba in xls.sheet_names:
        st.write(f"### Aba: {aba}")
        # Lê as duas primeiras colunas sem forçar tipo
        df = pd.read_excel(uploaded_file, sheet_name=aba, usecols="A:B", header=None)
        
        # Limpa espaços apenas da coluna de indicadores
        df[0] = df[0].astype(str).str.strip()
        
        # Exibe exatamente o que está sendo lido
        st.dataframe(df)
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel.")
