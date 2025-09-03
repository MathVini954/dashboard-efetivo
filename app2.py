import streamlit as st
import pandas as pd

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Dashboard de Obras",
    page_icon="🏗️",
    layout="wide"
)

# ===== ESTILO DARK MODE =====
st.markdown("""
<style>
body { background-color: #1e1e2f; color: #fff; }
.big-title { font-size:42px !important; font-weight: bold; text-align: center; margin-bottom:30px; color:#fff; }
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #2e2e3e;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    text-align: center;
    margin-bottom: 20px;
}
.card h4 { margin-bottom: 10px; color:#fff; }
.card p { font-size:16px; color:#fff; font-weight:bold; }
.progress-bar { background-color: #555; border-radius: 10px; overflow: hidden; height: 25px; margin-bottom:20px; }
.progress-bar-fill { height: 100%; background-color: #4caf50; text-align: center; color: white; font-weight: bold; line-height:25px;}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("<p class='big-title'>🏗️ Dashboard de Obras</p>", unsafe_allow_html=True)
st.write("Visualização profissional das obras com todos os indicadores principais.")

# ===== UPLOAD DO ARQUIVO =====
uploaded_file = st.file_uploader("📥 Faça upload da planilha Excel", type=["xlsx"])

# ===== FUNÇÕES AUXILIARES =====
def parse_valor(val):
    """Converte valores corretamente: percentual, moeda, número ou mantém texto/datas"""
    if pd.isna(val):
        return ""
    if isinstance(val, str):
        v = val.strip()
        if v.endswith("%"):
            try:
                return float(v.replace("%","").replace(",","."))
            except:
                return v
        if v.startswith("R$"):
            try:
                return float(v.replace("R$","").replace(".","").replace(",","."))
            except:
                return v
        try:
            return float(v.replace(",","."))
        except:
            return v
    return val

def format_money(val):
    try:
        return f"R$ {float(val):,.2f}"
    except:
        return str(val)

def format_percent(val):
    try:
        return f"{float(val):.1f}%"
    except:
        return str(val)

# ===== DASHBOARD =====
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    abas = xls.sheet_names
    
    for aba in abas:
        st.markdown(f"## 🏢 {aba}")
        df = pd.read_excel(uploaded_file, sheet_name=aba, header=None)
        
        indicadores = {}
        for i in range(len(df)):
            if pd.notna(df.iloc[i,0]):
                key = str(df.iloc[i,0]).strip()
                value = parse_valor(df.iloc[i,1])
                indicadores[key] = value
        
        # ===== CARDS PRINCIPAIS =====
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h4>AC (m²)</h4><p>{indicadores.get('AC(m²)','-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>AP (m²)</h4><p>{indicadores.get('AP(m²)','-')}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Efetivo</h4><p>{format_percent(indicadores.get('Ef',0))}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='card'><h4>Total Unidades</h4><p>{indicadores.get('Total Unidades','-')}</p></div>", unsafe_allow_html=True)

        # ===== AVANÇO FÍSICO =====
        st.write("### 📈 Avanço Físico")
        planejado = indicadores.get("Avanço Físico Planejado",0)
        real = indicadores.get("Avanço Físico Real",0)
        aderencia = indicadores.get("Aderência Física",0)
        st.markdown(f"<p>Planejado: {format_percent(planejado)} | Real: {format_percent(real)} | Aderência: {format_percent(aderencia)}</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width:{real}%; background-color:#4caf50;">{format_percent(real)}</div>
        </div>
        """, unsafe_allow_html=True)

        # ===== PRAZOS =====
        st.write("### ⏱️ Prazos")
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='card'><h4>Início</h4><p>{indicadores.get('Início','-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Tendência</h4><p>{indicadores.get('Tend','-')}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='card'><h4>Prazo Concl.</h4><p>{indicadores.get('Prazo Concl.','-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Prazo Cliente</h4><p>{indicadores.get('Prazo Cliente','-')}</p></div>", unsafe_allow_html=True)

        # ===== FINANCEIRO =====
        st.write("### 💰 Indicadores Financeiros")
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h4>Orçamento Base</h4><p>{format_money(indicadores.get('Orçamento Base',0))}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Orçamento Reajustado</h4><p>{format_money(indicadores.get('Orçamento Reajustado',0))}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Custo Final</h4><p>{format_money(indicadores.get('Custo Final',0))}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='card'><h4>Desvio</h4><p>{format_percent(indicadores.get('Desvio',0))}</p></div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h4>Desembolso</h4><p>{format_money(indicadores.get('Desembolso',0))}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Saldo</h4><p>{format_money(indicadores.get('Saldo',0))}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Custo Atual AC</h4><p>{format_money(indicadores.get('Custo Atual AC',0))}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='card'><h4>Custo Atual AP</h4><p>{format_money(indicadores.get('Custo Atual AP',0))}</p></div>", unsafe_allow_html=True)

        # ===== INDICADORES ECONÔMICOS =====
        st.write("### 📊 Indicadores Econômicos")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='card'><h4>Índice Econômico</h4><p>{format_percent(indicadores.get('Índice Econômico',0))}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Rentab. Viabilidade</h4><p>{format_percent(indicadores.get('Rentab. Viabilidade',0))}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Rentab. Projetada</h4><p>{format_percent(indicadores.get('Rentab. Projetada',0))}</p></div>", unsafe_allow_html=True)
        
        st.markdown("---")
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel para visualizar o dashboard.")
