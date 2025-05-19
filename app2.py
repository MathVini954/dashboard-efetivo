import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import os
 import streamlit as st

# Inicializa o estado do botão
if "sidebar_fixed" not in st.session_state:
    st.session_state.sidebar_fixed = False

# CSS customizado para animar a sidebar
st.markdown(
    """
    <style>
    /* Oculta o cabeçalho padrão do Streamlit */
    header, footer {visibility: hidden;}

    /* Estiliza a sidebar nativa */
    section[data-testid="stSidebar"] {
        transition: all 0.3s ease;
        background-color: #111;
        color: white;
        padding: 1rem;
        width: 260px !important;
    }

    /* Esconde a sidebar se não estiver fixada */
    body:not(:hover) section[data-testid="stSidebar"]:not(.fixed-sidebar) {
        margin-left: -260px;
    }

    /* Quando fixada, a classe impede esconder */
    .fixed-sidebar {
        margin-left: 0 !important;
    }

    /* Botão flutuante para fixar/desafixar */
    #fixar-btn {
        position: fixed;
        top: 20px;
        left: 10px;
        z-index: 10000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Botão de fixar/desafixar
fixar = st.button(
    "📌 Fixar" if not st.session_state.sidebar_fixed else "❌ Desafixar",
    key="fixar-btn"
)
if fixar:
    st.session_state.sidebar_fixed = not st.session_state.sidebar_fixed

# Aplica a classe se a sidebar estiver fixada
if st.session_state.sidebar_fixed:
    st.markdown(
        """<script>
        document.querySelector('section[data-testid="stSidebar"]').classList.add('fixed-sidebar');
        </script>""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """<script>
        document.querySelector('section[data-testid="stSidebar"]').classList.remove('fixed-sidebar');
        </script>""",
        unsafe_allow_html=True,
    )

# CONTEÚDO REAL NA SIDEBAR
with st.sidebar:
    st.header("🔍 Filtros")
    st.selectbox("Categoria", ["Todos", "A", "B", "C"])
    st.slider("Valor mínimo", 0, 100, 50)

# CONTEÚDO PRINCIPAL
st.title("📊 Meu Dashboard")
st.write("Este é o conteúdo principal que permanece visível.")

# ---------- Funções de autenticação ----------

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha, hash_s):
    return hash_senha(senha) == hash_s

def carregar_usuarios():
    if os.path.exists("usuarios.csv"):
        return pd.read_csv("usuarios.csv")
    else:
        return pd.DataFrame(columns=["usuario", "senha_hash"])

def salvar_usuario(usuario, senha_hash):
    df = carregar_usuarios()
    novo_usuario = pd.DataFrame([[usuario, senha_hash]], columns=["usuario", "senha_hash"])
    df = pd.concat([df, novo_usuario], ignore_index=True)
    df.to_csv("usuarios.csv", index=False)

# ---------- Tela de login/cadastro ----------

def tela_login():
    st.title("🔐 Login")

    menu = st.radio("Escolha uma opção:", ["Login", "Cadastrar"])

    if menu == "Login":
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            df_usuarios = carregar_usuarios()
            if usuario in df_usuarios['usuario'].values:
                senha_hash = df_usuarios[df_usuarios['usuario'] == usuario]['senha_hash'].values[0]
                if verificar_senha(senha, senha_hash):
                    st.session_state['logado'] = True
                    st.session_state['usuario'] = usuario
                    st.success("✅ Login realizado com sucesso!")
                    st.stop()
                else:
                    st.error("❌ Senha incorreta.")
            else:
                st.error("❌ Usuário não encontrado.")

    else:
        st.subheader("📋 Cadastro de Novo Usuário")
        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirme a senha", type="password")

        if st.button("Cadastrar"):
            if nova_senha != confirmar_senha:
                st.warning("⚠️ As senhas não coincidem.")
            elif novo_usuario.strip() == "":
                st.warning("⚠️ O nome de usuário não pode estar vazio.")
            else:
                df = carregar_usuarios()
                if novo_usuario in df['usuario'].values:
                    st.warning("⚠️ Usuário já existe.")
                else:
                    salvar_usuario(novo_usuario, hash_senha(nova_senha))
                    st.success("✅ Usuário cadastrado com sucesso! Faça login.")

# ---------- Função para adicionar a sidebar flutuante com fixação ----------

def sidebar_flutuante():
    # HTML, CSS e JS para o comportamento da sidebar
    html_code = """
    <style>
    /* Sidebar estilos */
    #sidebar {
        position: fixed;
        top: 0;
        left: -220px;
        height: 100%;
        width: 220px;
        background-color: #262730;
        color: white;
        transition: left 0.3s ease;
        padding: 20px;
        z-index: 100;
    }

    #sidebar:hover {
        left: 0px;
    }

    #sidebar.fixed {
        left: 0px !important;
    }

    /* Botão fixar sidebar */
    #fixar-btn {
        position: fixed;
        top: 20px;
        left: 220px;
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        z-index: 101;
    }

    #fixar-btn:hover {
        background-color: #0056b3;
    }
    </style>

    <div id="sidebar">
        <h3>Menu Lateral</h3>
        <ul>
            <li><a href="#">Efetivo</a></li>
            <li><a href="#">Produtividade</a></li>
            <li><a href="#">Planejamento</a></li>
        </ul>
    </div>

    <div id="fixar-btn" onclick="fixarSidebar()">Fixar Sidebar</div>

    <script>
    let sidebar = document.getElementById('sidebar');
    let fixarBtn = document.getElementById('fixar-btn');

    function fixarSidebar() {
        sidebar.classList.toggle('fixed');
    }
    
    // Adiciona a funcionalidade de "hover"
    sidebar.addEventListener('mouseover', function() {
        sidebar.style.left = '0';
    });

    sidebar.addEventListener('mouseout', function() {
        if (!sidebar.classList.contains('fixed')) {
            sidebar.style.left = '-220px';
        }
    });
    </script>
    """
    components.html(html_code, height=800, width=220)

# ---------- Dashboard de Efetivo ----------

@st.cache_data
def carregar_dados_efetivo():
    df = pd.read_excel("efetivo_abril.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.fillna(0)
    for col in ['Hora Extra 70% - Sabado', 'Hora Extra 70% - Semana', 'PRODUÇÃO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    if 'DIRETO / INDIRETO' in df.columns:
        df['Tipo'] = df['DIRETO / INDIRETO'].astype(str).str.upper().str.strip()
    else:
        df['Tipo'] = 'INDEFINIDO'
    df['Total Extra'] = df['Hora Extra 70% - Sabado'] + df['Hora Extra 70% - Semana']
    return df

# ---------- Execução Principal ----------
def main():
    st.set_page_config(page_title="Dashboards de Obra", layout="wide")

    # Sidebar visual interativa
    sidebar_interativa()

    col1, col2 = st.columns([1, 4])

    with col1:
        st.image("logotipo.png", width=400)

    with col2:
        st.markdown(
            "<h1 style='margin-top: 30px; vertical-align: middle;'>SISTEMA DE CUSTO E PLANEJAMENTO</h1>",
            unsafe_allow_html=True,
        )

    if "logado" not in st.session_state:
        st.session_state['logado'] = False
    if "usuario" not in st.session_state:
        st.session_state['usuario'] = ""

    if not st.session_state['logado']:
        tela_login()
    else:
        with st.sidebar:
            st.title(f"\ud83d\udc4b Bem-vindo, {st.session_state['usuario']}")

        aba1, aba2, aba3 = st.tabs(["\ud83d\udcca Efetivo", "\ud83d\udcc8 Produtividade", "\ud83c\udfd7\ufe0f An\u00e1lise Custo e Planejamento"])

        with aba1:
            dashboard_efetivo()

        with aba2:
            dashboard_produtividade()

        with aba3:
            st.title("\ud83c\udfd7\ufe0f AN\u00c1LISE CUSTO E PLANEJAMENTO")
            st.markdown(
                """
                <div style="text-align: center; margin-top: 100px;">
                    <h2>ESTAMOS EM DESENVOLVIMENTO</h2>
                    <div style="font-size: 50px; color: grey;">\ud83d\udc77\u200d\u2642\ufe0f\ud83d\udea7</div>
                </div>
                """, unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()
