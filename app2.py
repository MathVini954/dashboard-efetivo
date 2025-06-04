import pandas as pd

# Troque aqui pelo caminho correto do seu arquivo Excel
arquivo = "efetivo_abril.xlsx"

# Lista de colunas de descontos que você quer somar — ajuste aqui conforme seu arquivo
colunas_descontos = [
    "Atrasos", "Faltas em Dias", "DESCONTO DE ALIMENTAÇÃO", "MENSALIDADE SINDICAL",
    "Vale Transporte", "Assistencia Medica", "Coparticipacao Dependente", "Coparticipacao Titular",
    "Desconto Empréstimo", "Diferenca Plano De Saude", "Desconto Ótica", "Plano Odontologico",
    "Plano Odontologico Dependente", "Pensão Alimentícia Salário Mínimo",
    "Assitência Médica Dependente", "Dsr sobre falta", "INSS Folha", "IRRF Folha", "Pensão Alimentícia"
]

try:
    df = pd.read_excel(arquivo)
    print("Arquivo carregado. Colunas disponíveis:")
    print(df.columns.tolist())
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
    exit()

# Filtra só as colunas de desconto que existem no DataFrame
colunas_encontradas = [c for c in colunas_descontos if c in df.columns]
print("\nColunas de desconto encontradas no arquivo:")
print(colunas_encontradas)

if not colunas_encontradas:
    print("Nenhuma coluna de desconto encontrada. Verifique os nomes das colunas.")
    exit()

# Tenta converter para numérico e soma, com debug
for col in colunas_encontradas:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

print("\nValores somados por coluna de desconto:")
for col in colunas_encontradas:
    total = df[col].sum()
    print(f"{col}: R$ {total:,.2f}")

print(f"\nTotal geral descontos: R$ {df[colunas_encontradas].sum().sum():,.2f}")
