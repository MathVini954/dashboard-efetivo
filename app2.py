import pandas as pd

arquivo = "efetivo_abril.xlsx"

print("Passo 1: tentando carregar o arquivo...")

try:
    df = pd.read_excel(arquivo)
    print("Arquivo carregado com sucesso!")
except Exception as e:
    print("Erro ao carregar arquivo:", e)
    exit()

print("\nPasso 2: colunas encontradas:")
print(df.columns.tolist())

# Defina as colunas que quer somar, veja abaixo um exemplo genérico
colunas_descontos = [
    "Atrasos", "Faltas em Dias", "DESCONTO DE ALIMENTAÇÃO", "MENSALIDADE SINDICAL",
    "Vale Transporte", "Assistencia Medica", "Coparticipacao Dependente", "Coparticipacao Titular",
    "Desconto Empréstimo", "Diferenca Plano De Saude", "Desconto Ótica", "Plano Odontologico",
    "Plano Odontologico Dependente", "Pensão Alimentícia Salário Mínimo",
    "Assitência Médica Dependente", "Dsr sobre falta", "INSS Folha", "IRRF Folha", "Pensão Alimentícia"
]

print("\nPasso 3: filtrando colunas existentes no DataFrame...")

colunas_validas = [col for col in colunas_descontos if col in df.columns]

print(f"Colunas válidas encontradas para desconto: {colunas_validas}")

if len(colunas_validas) == 0:
    print("Nenhuma coluna de desconto válida encontrada, verifique os nomes.")
    exit()

print("\nPasso 4: convertendo colunas para numérico e somando:")

for col in colunas_validas:
    try:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        soma = df[col].sum()
        print(f"Soma da coluna '{col}': R$ {soma:,.2f}")
    except Exception as e:
        print(f"Erro ao processar a coluna '{col}': {e}")

print(f"\nPasso 5: soma total dos descontos: R$ {df[colunas_validas].sum().sum():,.2f}")
