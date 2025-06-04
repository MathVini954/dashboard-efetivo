import pandas as pd

# Simula leitura do seu DataFrame
df = pd.read_excel("efetivo_abril.xlsx")  # substitua pelo seu arquivo, se necessário

# Lista de colunas que são consideradas "descontos"
descontos = [
    'Atrasos', 'Faltas em Dias', 'DESCONTO DE ALIMENTAÇÃO', 'MENSALIDADE SINDICAL',
        'Vale Transporte', 'Assistencia Medica', 'Coparticipacao Dependente', 'Coparticipacao Titular', 'Desconto Empréstimo',
        'Diferenca Plano De Saude', 'Desconto Ótica', 'Plano Odontologico',
        'Plano Odontologico Dependente', 'Pensão Alimentícia Salário Mínimo',
        'Assitência Médica Dependente', 'Dsr sobre falta', 'INSS Folha', 'IRRF Folha', 'Pensão Alimentícia'

]

# Filtra as colunas que existem no DataFrame
colunas_existentes = [col for col in descontos if col in df.columns]

# Função para limpar e converter colunas para float
def normalizar_colunas(df, colunas):
    for col in colunas:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("R\$", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

# Aplica normalização
df = normalizar_colunas(df, colunas_existentes)

# Soma por coluna
soma_colunas = df[colunas_existentes].sum()

# Soma total
soma_total = soma_colunas.sum()

# Mostra resultados
print("Soma por coluna de descontos:")
print(soma_colunas)

print("\nTotal geral de descontos:")
print(f"R$ {soma_total:,.2f}")
