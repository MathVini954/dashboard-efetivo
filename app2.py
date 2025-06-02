import pandas as pd
import streamlit as st

def listar_colunas_planilha():
    caminho_arquivo = "efetivo_abril.xlsx"
    aba = "EFETIVO"

    try:
        df = pd.read_excel(caminho_arquivo, sheet_name=aba, engine="openpyxl")
        colunas = df.columns.tolist()
        
        st.subheader("Colunas encontradas na planilha:")
        for i, col in enumerate(colunas, start=1):
            st.write(f"{i}. '{col}'")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

# Chamada no Streamlit
if __name__ == "__main__" or True:
    st.title("Verificar colunas da planilha de Efetivo")
    listar_colunas_planilha()
