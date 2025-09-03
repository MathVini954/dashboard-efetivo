import streamlit as st
import pandas as pd
import numpy as np

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

# Função melhorada para converter valores
def parse_valor(val):
    if pd.isna(val) or val == '' or val is None:
        return ""
    
    # Se já for numérico
    if isinstance(val, (int, float)):
        return val
    
    # Converter para string
    val_str = str(val).strip()
    
    # Porcentagem
    if '%' in val_str:
        try:
            # Remove % e converte para float
            clean_val = val_str.replace('%', '').replace(',', '.').strip()
            return float(clean_val)
        except:
            return val_str
    
    # Moeda (R$)
    if 'R$' in val_str or 'r$' in val_str:
        try:
            # Remove R$, pontos e substitui vírgula por ponto
            clean_val = val_str.replace('R$', '').replace('r$', '').replace('.', '').replace(',', '.').strip()
            return float(clean_val)
        except:
            return val_str
    
    # Número com vírgula como decimal
    if ',' in val_str and '.' not in val_str:
        try:
            return float(val_str.replace(',', '.'))
        except:
            return val_str
    
    # Tentar converter para float diretamente
    try:
        return float(val_str)
    except:
        return val_str

# Formata valores monetários
def format_money(val):
    try:
        if val == "" or val is None:
            return "-"
        return f"R$ {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(val)

# Formata valores percentuais
def format_percent(val):
    try:
        if val == "" or val is None:
            return "-"
        return f"{float(val):.1f}%"
    except:
        return str(val)

# ===== DASHBOARD =====
if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        abas = xls.sheet_names
        
        for aba in abas:
            st.markdown(f"## 🏢 {aba}")
            
            # Ler a planilha de forma mais flexível
            df = pd.read_excel(uploaded_file, sheet_name=aba, header=None)
            
            # DEBUG: Mostrar estrutura da planilha
            st.write("📊 Estrutura da planilha (primeiras 10 linhas):")
            st.dataframe(df.head(10))
            
            indicadores = {}
            
            # Procurar por indicadores nas colunas A e B
            for i in range(len(df)):
                # Verificar se a célula A tem conteúdo
                if pd.notna(df.iloc[i, 0]) and str(df.iloc[i, 0]).strip() != '':
                    key = str(df.iloc[i, 0]).strip()
                    
                    # Verificar se há valor na coluna B
                    if len(df.columns) > 1 and pd.notna(df.iloc[i, 1]):
                        value = parse_valor(df.iloc[i, 1])
                        indicadores[key] = value
                        st.write(f"🔍 Encontrado: {key} = {value} (tipo: {type(value)})")
            
            # DEBUG: Mostrar todos os indicadores encontrados
            st.write("📋 Indicadores extraídos:", indicadores)
            
            if not indicadores:
                st.warning("⚠️ Nenhum indicador encontrado na estrutura atual da planilha.")
                continue
            
            # ===== CARDS PRINCIPAIS =====
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='card'><h4>AC (m²)</h4><p>{indicadores.get('AC(m²)', indicadores.get('AC (m²)', '-'))}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h4>AP (m²)</h4><p>{indicadores.get('AP(m²)', indicadores.get('AP (m²)', '-'))}</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card'><h4>Efetivo</h4><p>{format_percent(indicadores.get('Ef', indicadores.get('Efetivo', 0)))}</p></div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='card'><h4>Total Unidades</h4><p>{indicadores.get('Total Unidades', indicadores.get('Total unidades', '-'))}</p></div>", unsafe_allow_html=True)

            # ===== AVANÇO FÍSICO =====
            st.write("### 📈 Avanço Físico")
            planejado = indicadores.get("Avanço Físico Planejado", indicadores.get("Avanço físico planejado", 0))
            real = indicadores.get("Avanço Físico Real", indicadores.get("Avanço físico real", 0))
            aderencia = indicadores.get("Aderência Física", indicadores.get("Aderência física", 0))
            
            st.markdown(f"<p>Planejado: {format_percent(planejado)} | Real: {format_percent(real)} | Aderência: {format_percent(aderencia)}</p>", unsafe_allow_html=True)
            
            # Garantir que o valor seja numérico para a barra de progresso
            try:
                real_percent = float(real)
            except:
                real_percent = 0
                
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width:{real_percent}%; background-color:#4caf50;">{format_percent(real)}</div>
            </div>
            """, unsafe_allow_html=True)

            # ===== PRAZOS =====
            st.write("### ⏱️ Prazos")
            col1, col2 = st.columns(2)
            col1.markdown(f"<div class='card'><h4>Início</h4><p>{indicadores.get('Início', '-')}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h4>Tendência</h4><p>{indicadores.get('Tend', indicadores.get('Tendência', '-'))}</p></div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col1.markdown(f"<div class='card'><h4>Prazo Concl.</h4><p>{indicadores.get('Prazo Concl.', indicadores.get('Prazo concl.', '-'))}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h4>Prazo Cliente</h4><p>{indicadores.get('Prazo Cliente', indicadores.get('Prazo cliente', '-'))}</p></div>", unsafe_allow_html=True)

            # ===== FINANCEIRO =====
            st.write("### 💰 Indicadores Financeiros")
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='card'><h4>Orçamento Base</h4><p>{format_money(indicadores.get('Orçamento Base', indicadores.get('Orçamento base', 0)))}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h4>Orçamento Reajustado</h4><p>{format_money(indicadores.get('Orçamento Reajustado', indicadores.get('Orçamento reajustado', 0)))}</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card'><h4>Custo Final</h4><p>{format_money(indicadores.get('Custo Final', indicadores.get('Custo final', 0)))}</p></div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='card'><h4>Desvio</h4><p>{format_percent(indicadores.get('Desvio', 0))}</p></div>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='card'><h4>Desembolso</h4><p>{format_money(indicadores.get('Desembolso', 0))}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h4>Saldo</h4><p>{format_money(indicadores.get('Saldo', 0))}</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card'><h4>Custo Atual AC</h4><p>{format_money(indicadores.get('Custo Atual AC', indicadores.get('Custo atual AC', 0)))}</p></div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='card'><h4>Custo Atual AP</h4><p>{format_money(indicadores.get('Custo Atual AP', indicadores.get('Custo atual AP', 0)))}</p></div>", unsafe_allow_html=True)

            # ===== INDICADORES ECONÔMICOS =====
            st.write("### 📊 Indicadores Econômicos")
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"<div class='card'><h4>Índice Econômico</h4><p>{format_percent(indicadores.get('Índice Econômico', indicadores.get('Índice econômico', 0)))}</p></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='card'><h4>Rentab. Viabilidade</h4><p>{format_percent(indicadores.get('Rentab. Viabilidade', indicadores.get('Rentab. viabilidade', 0)))}</p></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='card'><h4>Rentab. Projetada</h4><p>{format_percent(indicadores.get('Rentab. Projetada', indicadores.get('Rentab. projetada', 0)))}</p></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        
else:
    st.warning("⛔ Por favor, faça upload da planilha Excel para visualizar o dashboard.")
