import streamlit as st
import pandas as pd

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", sheet_name="EFETIVO", engine="openpyxl")
    df.columns = df.columns.str.strip()
    # Garantir que colunas numéricas estejam no formato correto
    cols_num = [
        'Hora Extra 70% - Semana', 'Hora Extra 70% - Sabado', 'Remuneração Líquida Folha',
        'Adiantamento', 'PRODUÇÃO', 'REFLEXO S PRODUÇÃO', 'Repouso Remunerado'
    ]
    for c in cols_num:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        else:
            st.warning(f"Coluna '{c}' não encontrada no arquivo.")
            df[c] = 0
    return df

def main():
    st.title("Teste de Cálculo Peso Financeiro")

    df = carregar_dados_efetivo()

    # Filtrar apenas tipo DIRETO para peso da produção
    df_direto = df[df['Tipo'] == 'DIRETO']

    # Somar os valores para cada coluna usada no peso financeiro (para DIRETO)
    soma_producao = df_direto['PRODUÇÃO'].sum()
    soma_reflexo = df_direto['REFLEXO S PRODUÇÃO'].sum()
    soma_remuneracao = df_direto['Remuneração Líquida Folha'].sum()
    soma_adiantamento = df_direto['Adiantamento'].sum()
    soma_total_extra = df_direto['Hora Extra 70% - Semana'].sum() + df_direto['Hora Extra 70% - Sabado'].sum()
    soma_repouso = df_direto['Repouso Remunerado'].sum()

    st.markdown("### Totais usados para cálculo do Peso sobre Produção (somente DIRETO):")
    st.write(f"**Soma PRODUÇÃO:** {soma_producao:,.2f}")
    st.write(f"**Soma REFLEXO S PRODUÇÃO:** {soma_reflexo:,.2f}")
    st.write(f"**Soma Remuneração Líquida Folha:** {soma_remuneracao:,.2f}")
    st.write(f"**Soma Adiantamento:** {soma_adiantamento:,.2f}")

    st.markdown("### Totais usados para cálculo do Peso sobre Hora Extra (somente DIRETO):")
    st.write(f"**Soma Total Extra (Hora Extra Semana + Sábado):** {soma_total_extra:,.2f}")
    st.write(f"**Soma Repouso Remunerado:** {soma_repouso:,.2f}")
    st.write(f"**Soma Remuneração Líquida Folha:** {soma_remuneracao:,.2f}")
    st.write(f"**Soma Adiantamento:** {soma_adiantamento:,.2f}")

    # Agora calcula os índices totais (soma dos numeradores / soma dos denominadores)
    peso_producao = (soma_producao + soma_reflexo) / (soma_remuneracao + soma_adiantamento) if (soma_remuneracao + soma_adiantamento) > 0 else 0
    peso_hora_extra = (soma_total_extra + soma_repouso) / (soma_remuneracao + soma_adiantamento) if (soma_remuneracao + soma_adiantamento) > 0 else 0

    st.markdown("### Resultado do cálculo do Peso Financeiro geral (somando tudo):")
    st.write(f"**Peso sobre Produção:** {peso_producao:.4f} ({peso_producao*100:.2f}%)")
    st.write(f"**Peso sobre Hora Extra:** {peso_hora_extra:.4f} ({peso_hora_extra*100:.2f}%)")

if __name__ == "__main__":
    main()
