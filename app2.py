import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import os

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

# ---------- Dashboard de Efetivo ----------
@st.cache_data
def carregar_dados_efetivo():
    with st.spinner("🔄 Carregando dados de efetivo..."):
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

def dashboard_efetivo():
    st.title("📊 Análise de Efetivo - Abril 2025")
    df = carregar_dados_efetivo()

    with st.sidebar:
        st.header("🔍 Filtros - Efetivo")
        lista_obras = sorted(df['Obra'].astype(str).unique())
        obras_selecionadas = st.multiselect("Obras:", lista_obras, default=lista_obras)
        tipo_selecionado = st.radio("Tipo:", ['Todos', 'DIRETO', 'INDIRETO', 'TERCEIRO'], horizontal=True)
        tipo_analise = st.radio("Tipo de Análise da Tabela:", ['Produção', 'Hora Extra Semana', 'Hora Extra Sábado'])
        qtd_linhas = st.radio("Qtd. de Funcionários na Tabela:", ['5', '10', '20', 'Todos'], horizontal=True)

    df_filtrado = df[df['Obra'].isin(obras_selecionadas)]
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_selecionado]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👷 Direto", len(df_filtrado[df_filtrado['Tipo'] == 'DIRETO']))
    col2.metric("👷‍♂️ Indireto", len(df_filtrado[df_filtrado['Tipo'] == 'INDIRETO']))
    col3.metric("🏗️ Terceiro", len(df_filtrado[df_filtrado['Tipo'] == 'TERCEIRO']))
    col4.metric("👥 Total", len(df_filtrado))
    st.divider()

    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        df_pizza = df[df['Obra'].isin(obras_selecionadas)]
        pizza = df_pizza['Tipo'].value_counts().reset_index()
        pizza.columns = ['Tipo', 'count']
        fig_pizza = px.pie(pizza, names='Tipo', values='count', title='Distribuição por Tipo de Efetivo')
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_g2:
        coluna_valor = {
            'Produção': 'PRODUÇÃO',
            'Hora Extra Semana': 'Hora Extra 70% - Semana',
            'Hora Extra Sábado': 'Hora Extra 70% - Sabado'
        }[tipo_analise]

        if tipo_analise == 'Produção' and 'REFLEXO S PRODUÇÃO' in df.columns:
            df_filtrado['DSR'] = df_filtrado['REFLEXO S PRODUÇÃO']
            ranking = df_filtrado[['Funcionário', 'Função', 'Obra', 'Tipo', 'PRODUÇÃO', 'DSR']].sort_values(by='PRODUÇÃO', ascending=False)
        else:
            ranking = df_filtrado[['Funcionário', 'Função', 'Obra', 'Tipo', coluna_valor]].sort_values(by=coluna_valor, ascending=False)

        valor_total = df_filtrado[coluna_valor].sum()
        st.markdown(f"### 📋 Top Funcionários por **{tipo_analise}**")
        st.markdown(f"**Total em {tipo_analise}:** R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        if qtd_linhas != 'Todos':
            ranking = ranking.head(int(qtd_linhas))

        ranking[coluna_valor] = ranking[coluna_valor].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if 'DSR' in ranking.columns:
            ranking['DSR'] = ranking['DSR'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(ranking, use_container_width=True)

    st.divider()
    graf_funcao = df_filtrado['Função'].value_counts().reset_index()
    graf_funcao.columns = ['Função', 'Qtd']

    fig_bar = px.bar(
        graf_funcao,
        x='Função',
        y='Qtd',
        color='Qtd',
        color_continuous_scale='Blues',
        title='Efetivo por Função',
        text='Qtd'
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.markdown("### 🎯 Quadrantes de Eficiência (Produção vs Hora Extra)")
    fig_quadrantes = px.scatter(
        df_filtrado, x='Total Extra', y='PRODUÇÃO', color='Tipo',
        hover_data=['Funcionário', 'Função', 'Obra'],
        title="Quadrantes de Eficiência - Produção vs Hora Extra"
    )
    st.plotly_chart(fig_quadrantes, use_container_width=True)

# ---------- Dashboard de Produtividade ----------
def dashboard_produtividade():
    with st.spinner("🔄 Carregando dados de produtividade..."):
        df = pd.read_excel("produtividade.xlsx")
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        df['DATA_FORMATADA'] = df['DATA'].dt.strftime('%b/%y')

    with st.sidebar:
        st.header("🔍 Filtros - Produtividade")
        tipo_obra_opcoes = ["Todos"] + df['TIPO_OBRA'].unique().tolist()
        tipo_obra = st.selectbox('Selecione o Tipo de Obra', tipo_obra_opcoes)
        servico = st.selectbox('Selecione o Serviço', [""] + df['SERVIÇO'].unique().tolist())
        datas_selecionadas = st.multiselect("Selecione os meses:", df['DATA_FORMATADA'].unique())

    df_filtrado = df.copy()
    if tipo_obra != "Todos":
        df_filtrado = df_filtrado[df_filtrado['TIPO_OBRA'] == tipo_obra]
    if servico:
        df_filtrado = df_filtrado[df_filtrado['SERVIÇO'] == servico]
    if datas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['DATA_FORMATADA'].isin(datas_selecionadas)]

    st.title("📈 Análise de Produtividade")
    fig1 = px.line(df_filtrado, x='DATA_FORMATADA', y=['PRODUTIVIDADE_PROF_DIAM2', 'PRODUTIVIDADE_ORCADA_DIAM2'],
                   title="Produtividade Profissional por M² (Real x Orçado)",
                   markers=True, labels={"value": "Produtividade", "DATA_FORMATADA": "Mês"})
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df_filtrado.groupby('TIPO_OBRA')['PRODUTIVIDADE_PROF_DIAM2'].mean().reset_index(),
                  x='TIPO_OBRA', y='PRODUTIVIDADE_PROF_DIAM2',
                  title="Produtividade Média por Tipo de Obra")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- App Principal ----------
def main():
    if 'logado' not in st.session_state or not st.session_state['logado']:
        tela_login()
    else:
        aba = st.sidebar.selectbox("Menu", ["Efetivo", "Produtividade"])
        if aba == "Efetivo":
            dashboard_efetivo()
        elif aba == "Produtividade":
            dashboard_produtividade()

if __name__ == "__main__":
    main()
