import streamlit as st
import pandas as pd

@st.cache_data
def carregar_dados_efetivo():
    # Carrega o arquivo Excel
    df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
    
    # Mostrar as colunas no log para debug
    st.write("Colunas do DataFrame:", df.columns.tolist())
    
    # Verifica se as colunas existem antes de usar
    required_cols = ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Coluna obrigatória não encontrada: {col}")
            st.stop()  # Para a execução
    
    # Cria a coluna 'Total Extra'
    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
    
    return df

def dashboard_efetivo():
    df = carregar_dados_efetivo()
    st.dataframe(df.head())

def main():
    dashboard_efetivo()

if __name__ == "__main__":
    main()
