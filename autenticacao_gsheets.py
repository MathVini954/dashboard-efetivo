import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
import pandas as pd

# Conectar ao Google Sheets
def conectar_sheets():
    escopos = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = ServiceAccountCredentials.from_json_keyfile_name("streamlit-autenticacao-bae6036e18dc.json", escopos)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open("usuarios_streamlit")
    folha = planilha.sheet1
    return folha

# Carregar usuários
def carregar_usuarios():
    folha = conectar_sheets()
    dados = folha.get_all_records()
    return pd.DataFrame(dados)

# Salvar novo usuário
def salvar_usuario(usuario, senha_hash):
    folha = conectar_sheets()
    folha.append_row([usuario, senha_hash])

# Hash da senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Verificar senha
def verificar_senha(senha, senha_hash):
    return hash_senha(senha) == senha_hash
