import pandas as pd

# Caminho para seu arquivo Excel
CAMINHO_ARQUIVO = "efetivo_abril.xlsx"  # Altere se necessário

# Colunas que representam descontos
colunas_descontos = [
   'Atrasos', 'Faltas em Dias', 'DESCONTO DE ALIMENTAÇÃO', 'MENSALIDADE SINDICAL',
        'Vale Transporte', 'Assistencia Medica', 'Coparticipacao Dependente', 'Coparticipacao Titular', 'Desconto Empréstimo',
        'Diferenca Plano De Saude', 'Desconto Ótica', 'Plano Odontologico',
        'Plano Odontologico Dependente', 'Pensão Alimentícia Salário Mínimo',
        'Assitência Médica Dependente', 'Dsr sobre falta', 'INSS Folha', 'IRRF Folha', 'Pensão Alimentícia'
]

# Tenta carregar o DataFrame
try:
    df = pd.read_excel(CAMINHO_ARQUIVO)
    print("✅ Arquivo carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar o arquivo: {e}")
    exit()

# Mostra as colunas carregadas para debug
print("\n🔍 Colunas encontradas no DataFrame:")
print(df.columns.tolist())

# Filtra as colunas de desconto que realmente existem no arquivo
colunas_existentes = [col for col in colunas_descontos if col in df.columns]

if not colunas_existentes:
    print("\n⚠️ Nenhuma coluna de desconto foi encontrada no arquivo.")
    exit()

print("\n✅ Colunas de desconto encontradas:")
print(colunas_existentes)

# Normaliza os valores para float (remove R$, vírgulas, etc.)
for col in colunas_existentes:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace("R\$", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Soma por coluna e total geral
somas = df[colunas_existentes].sum()
total_geral = somas.sum()

# Exibe os resultados
print("\n📊 Soma por coluna de descontos:")
for col, valor in somas.items():
    print(f"{col}: R$ {valor:,.2f}")

print(f"\n💰 Total geral de descontos: R$ {total_geral:,.2f}")
