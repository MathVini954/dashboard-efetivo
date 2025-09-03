import streamlit as st
import pandas as pd

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Dashboard de Obras",
    page_icon="🏗️",
    layout="wide"
)

# ===== ESTILO CSS =====
st.markdown("""
<style>
.big-title { font-size:42px !important; font-weight: bold; text-align: center; margin-bottom:30px; }
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #f0f2f6;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 20px;
}
.card h4 { margin-bottom: 10px; }
.progress-bar {
    background-color: #d9d9d9;
    border-radius: 10px;
    overflow: hidden;
    height: 20px;
}
.progress-bar-fill {
    height: 100%;
    background-color: #4caf50;
    text-align: center;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("<p class='big-title'>🏗️ Dashboard de Obras</p>", unsafe_allow_html=True)
st.write("Acompanhamento visual das obras - produção, efetivo, financeiro e indicadores estratégicos.")

# ===== UPLOAD DA PLANILHA =====
uploaded_file = st.file_uploader("📥 Faça upload da planilha Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    abas = xls.sheet_names
    
    for aba in abas:
        st.markdown(f"## 🏢 {aba}")  # Nome da obra
        
        # Lê a aba
        df = pd.read_excel(uploaded_file, sheet_name=aba, header=None)
        indicadores = {str(df.iloc[i,0]).strip(): df.iloc[i,1] for i in range(len(df)) if pd.notna(df.iloc[i,0])}
        
        # ===== CARDS PRINCIPAIS =====
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h4>AC (m²)</h4><p>{indicadores.get('AC (m²)', '-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Efetivo</h4><p>{indicadores.get('Ef', '-')}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Total Unidades</h4><p>{indicadores.get('Total Unidades', '-')}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='card'><h4>Desembolso</h4><p>R$ {indicadores.get('Desembolso', '-')}</p></div>", unsafe_allow_html=True)
        
        # ===== AVANÇO FÍSICO COM BARRA DE PROGRESSO =====
        st.write("### 📈 Avanço Físico")
        planejado = indicadores.get("Avanço Físico Planejado", 0)
        real = indicadores.get("Avanço Físico Real", 0)
        aderencia = indicadores.get("Aderência Física", 0)
        
        st.markdown(f"<p>Planejado: {planejado}% | Real: {real}% | Aderência: {aderencia}%</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width:{real}%; background-color:#4caf50;">{real}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== INDICADORES FINANCEIROS =====
        st.write("### 💰 Indicadores Financeiros")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='card'><h4>Orçamento Base</h4><p>R$ {indicadores.get('Orçamento Base', '-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Orçamento Reajustado</h4><p>R$ {indicadores.get('Orçamento Reajustado', '-')}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Custo Final</h4><p>R$ {indicadores.get('Custo Final', '-')}</p></div>", unsafe_allow_html=True)
        
        # ===== ÍNDICES E RENTABILIDADE =====
        st.write("### 📊 Indicadores Econômicos")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='card'><h4>Índice Econômico</h4><p>{indicadores.get('Índice Econômico', '-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Rentab. Viabilidade</h4><p>{indicadores.get('Rentab. Viabilidade', '-')}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Rentab. Projetada</h4><p>{indicadores.get('Rentab. Projetada', '-')}</p></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel para visualizar o dashboard.")
