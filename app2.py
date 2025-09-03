import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Obras", page_icon="🏗️", layout="wide")

# ===== Estilo Dark Mode =====
st.markdown("""
<style>
body { background-color: #1e1e2f; color: #fff; }
.big-title { font-size:42px !important; font-weight: bold; text-align: center; margin-bottom:30px; color:#fff; }
.card { padding:20px; border-radius:15px; background-color:#2e2e3e; box-shadow:0px 4px 15px rgba(0,0,0,0.5); text-align:center; margin-bottom:20px; }
.card h4 { margin-bottom:10px; color:#fff; }
.card p { font-size:16px; color:#fff; font-weight:bold; }
.progress-bar { background-color:#555; border-radius:10px; overflow:hidden; height:25px; margin-bottom:20px; }
.progress-bar-fill { height:100%; background-color:#4caf50; text-align:center; color:white; font-weight:bold; line-height:25px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<p class='big-title'>🏗️ Dashboard de Obras</p>", unsafe_allow_html=True)
st.write("Visualização profissional das obras com todos os indicadores principais.")

uploaded_file = st.file_uploader("📥 Faça upload da planilha Excel", type=["xlsx"])

def format_money(val):
    try:
        return f"R$ {float(val):,.2f}"
    except:
        return str(val)

def format_percent(val):
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return str(val)

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    for aba in xls.sheet_names:
        st.markdown(f"## 🏢 {aba}")
        df = pd.read_excel(uploaded_file, sheet_name=aba, usecols="A:B", header=None, dtype=str)
        df[0] = df[0].str.strip()
        df[1] = df[1].str.strip()
        
        indicadores = {}
        for i in range(len(df)):
            key = df.iloc[i,0]
            value = df.iloc[i,1]
            # Converte para float ou datetime quando possível
            try:
                value = float(value)
            except:
                try:
                    value = pd.to_datetime(value)
                except:
                    pass
            indicadores[key] = value
        
        # ===== Cards principais =====
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='card'><h4>AC (m²)</h4><p>{indicadores.get('AC(m²)','-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>AP (m²)</h4><p>{indicadores.get('AP(m²)','-')}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Efetivo</h4><p>{format_percent(indicadores.get('Ef',0))}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='card'><h4>Total Unidades</h4><p>{indicadores.get('Total Unidades','-')}</p></div>", unsafe_allow_html=True)
        
        # ===== Avanço físico =====
        st.write("### 📈 Avanço Físico")
        planejado = indicadores.get("Avanço Físico Planejado",0)
        real = indicadores.get("Avanço Físico Real",0)
        aderencia = indicadores.get("Aderência Física",0)
        st.markdown(f"<p>Planejado: {format_percent(planejado)} | Real: {format_percent(real)} | Aderência: {format_percent(aderencia)}</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width:{real*100}%;">{format_percent(real)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== Prazos =====
        st.write("### ⏱️ Prazos")
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='card'><h4>Início</h4><p>{indicadores.get('Início','-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Tendência</h4><p>{indicadores.get('Tend','-')}</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='card'><h4>Prazo Concl.</h4><p>{indicadores.get('Prazo Concl.','-')}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Prazo Cliente</h4><p>{indicadores.get('Prazo Cliente','-')}</p></div>", unsafe_allow_html=True)
        
        # ===== Financeiro =====
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
        
        # ===== Indicadores Econômicos =====
        st.write("### 📊 Indicadores Econômicos")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='card'><h4>Índice Econômico</h4><p>{format_percent(indicadores.get('Índice Econômico',0))}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>Rentab. Viabilidade</h4><p>{format_percent(indicadores.get('Rentab. Viabilidade',0))}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>Rentab. Projetada</h4><p>{format_percent(indicadores.get('Rentab. Projetada',0))}</p></div>", unsafe_allow_html=True)
        
        st.markdown("---")
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel.")
