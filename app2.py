import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Obras",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3B82F6;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #374151;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        height: 100%;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
    }
    .metric-title {
        font-size: 1rem;
        color: #93C5FD;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #FFFFFF;
        font-weight: 800;
    }
    .stSelectbox > div > div {
        background-color: #1E293B;
        color: white;
    }
    .stSelectbox label {
        color: #93C5FD !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-header">🏗️ Dashboard de Obras</p>', unsafe_allow_html=True)

# Upload da planilha
st.markdown('<p class="sub-header">📁 Upload da Planilha</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Escolha o arquivo Excel com os dados das obras:", type=['xlsx', 'xls'], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        # Carregar todas as abas
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        # Escolher aba
        selected_sheet = st.selectbox("Escolha a obra (aba da planilha):", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        if df.shape[1] < 2:
            st.error("A planilha precisa ter pelo menos 2 colunas (Métrica, Valor)")
            st.stop()
        
        df_clean = df.iloc[:, [0,1]].dropna()
        df_clean.columns = ['Metrica','Valor']
        
        # Criar dicionário de dados
        dados = {str(row['Metrica']).strip(): row['Valor'] for _, row in df_clean.iterrows()}
        st.success(f"✅ Dados carregados da aba: **{selected_sheet}**")
        
        # Funções utilitárias
        def get_value(key, default="N/A"):
            return dados.get(key, default)
        
        def format_money(value):
            if isinstance(value, (int,float)):
                return f"R$ {value:,.0f}".replace(",",".")
            elif isinstance(value,str) and 'R$' in value:
                return value
            return str(value)
        
        def format_percent(value):
            if isinstance(value, (int,float)) and value <= 1:
                return f"{value*100:.1f}%"
            elif isinstance(value,(int,float)) and value > 1:
                return f"{value:.1f}%"
            elif isinstance(value,str) and '%' in value:
                return value
            return str(value)
        
        # -------------------- Métricas Principais --------------------
        st.markdown('<p class="sub-header">📊 Métricas Principais</p>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Total Unidades</p><p class="metric-value">{get_value("Total Unidades")}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><p class="metric-title">AC(m²)</p><p class="metric-value">{get_value("AC(m²)")}</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><p class="metric-title">AP(m²)</p><p class="metric-value">{get_value("AP(m²)")}</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Rentab. Viabilidade</p><p class="metric-value">{format_percent(get_value("Rentab. Viabilidade"))}</p></div>', unsafe_allow_html=True)
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Rentab. Projetada</p><p class="metric-value">{format_percent(get_value("Rentab. Projetada"))}</p></div>', unsafe_allow_html=True)
        with col6:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Custo AC</p><p class="metric-value">{format_money(get_value("Custo Atual AC"))}</p></div>', unsafe_allow_html=True)
        with col7:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Custo AP</p><p class="metric-value">{format_money(get_value("Custo Atual AP"))}</p></div>', unsafe_allow_html=True)
        
        # -------------------- Análise Financeira --------------------
        st.markdown('<p class="sub-header">💰 Análise Financeira</p>', unsafe_allow_html=True)
        orc_base = get_value("Orçamento Base",0)
        orc_reaj = get_value("Orçamento Reajustado",0)
        custo_final = get_value("Custo Final",0)
        
        def to_float(val):
            if isinstance(val,str):
                try:
                    return float(val.replace('R$','').replace('.','').replace(',','.'))
                except:
                    return 0
            return val
        orc_base = to_float(orc_base)
        orc_reaj = to_float(orc_reaj)
        custo_final = to_float(custo_final)
        
        fig_orc = go.Figure()
        fig_orc.add_trace(go.Bar(
            x=['Orçamento Base','Orçamento Reajustado','Custo Final'],
            y=[orc_base,orc_reaj,custo_final],
            marker_color=['#3B82F6','#60A5FA','#10B981'],
            text=[format_money(orc_base),format_money(orc_reaj),format_money(custo_final)],
            textposition='auto'
        ))
        fig_orc.update_layout(
            title='Comparativo de Orçamento',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_orc,use_container_width=True)
        
        # -------------------- 4 Caixas Financeiras --------------------
        col_fin1,col_fin2,col_fin3,col_fin4 = st.columns(4)
        with col_fin1:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Desvio</p><p class="metric-value">{get_value("Desvio")}</p></div>',unsafe_allow_html=True)
        with col_fin2:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Desembolso</p><p class="metric-value">{format_money(get_value("Desembolso"))}</p></div>',unsafe_allow_html=True)
        with col_fin3:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Saldo</p><p class="metric-value">{format_money(get_value("Saldo"))}</p></div>',unsafe_allow_html=True)
        with col_fin4:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Índice Econômico</p><p class="metric-value">{get_value("Índice Econômico")}</p></div>',unsafe_allow_html=True)
        
        # -------------------- Velocímetro Avanço Físico --------------------
        st.markdown('<p class="sub-header">📅 Prazos e Avanço Físico</p>', unsafe_allow_html=True)
        av_real = get_value("Avanço Físico Real",0)
        av_plan = get_value("Avanço Físico Planejado",1)
        
        # Converter valores
        def parse_percent(val):
            if isinstance(val,str):
                try:
                    val = float(val.replace('%','').replace(',','.'))
                except:
                    val = 0
            if val <= 1: val *= 100
            return val
        av_real_num = parse_percent(av_real)
        av_plan_num = parse_percent(av_plan)
        
        fig_velo = go.Figure(go.Indicator(
            mode="gauge+number",
            value=av_real_num,
            domain={'x':[0,1],'y':[0,1]},
            title={'text':"Avanço Físico Real",'font':{'size':16,'color':'white'}},
            number={'font':{'size':40,'color':'white'},'suffix':'%'},
            gauge={
                'axis':{'range':[0,100],'tickwidth':1,'tickcolor':'white','tickfont':{'size':12,'color':'white'}},
                'bar':{'color':'#3B82F6','thickness':0.25},
                'bgcolor':'rgba(0,0,0,0)',
                'borderwidth':2,'bordercolor':'gray',
                'threshold':{
                    'line':{'color':'#EF4444','width':4},
                    'thickness':0.75,
                    'value':av_plan_num
                }
            }
        ))
        fig_velo.update_layout(
            height=400,
            font={'color':'white','family':'Arial'},
            margin=dict(l=30,r=30,t=80,b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_velo,use_container_width=True)
        
        # -------------------- Linha do tempo --------------------
        st.markdown('<p class="sub-header">⏰ Linha do Tempo</p>', unsafe_allow_html=True)
        inicio = get_value("Início","N/A")
        tend = get_value("Tend","N/A")
        prazo_concl = get_value("Prazo Concl.","N/A")
        prazo_cliente = get_value("Prazo Cliente","N/A")
        
        dates = [inicio,tend,prazo_concl,prazo_cliente]
        labels = ["Início","Tendência","Prazo Conclusão","Prazo Cliente"]
        colors = ["#3B82F6","#F59E0B","#10B981","#EF4444"]
        date_values=[]
        for d in dates:
            if isinstance(d,(datetime,pd.Timestamp)):
                date_values.append(d)
            elif isinstance(d,str) and d!="N/A":
                try: date_values.append(pd.to_datetime(d))
                except: date_values.append(None)
            else: date_values.append(None)
        
        valid_dates = [d for d in date_values if d is not None]
        if len(valid_dates)>=2:
            min_date=min(valid_dates)
            max_date=max(valid_dates)
            fig_tl=go.Figure()
            fig_tl.add_trace(go.Scatter(x=[min_date,max_date],y=[0,0],mode='lines',line=dict(color='white',width=3),showlegend=False))
            for i,(date,label,color) in enumerate(zip(date_values,labels,colors)):
                if date is not None:
                    fig_tl.add_trace(go.Scatter(
                        x=[date],y=[0],mode='markers+text',
                        marker=dict(size=15,color=color),
                        text=[label],textposition="top center",
                        name=label,textfont=dict(color='white',size=12)
                    ))
            fig_tl.update_layout(
                title='Cronograma da Obra',
                showlegend=True,
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False,zeroline=False),
                yaxis=dict(showgrid=False,zeroline=False,showticklabels=False)
            )
            st.plotly_chart(fig_tl,use_container_width=True)
        else:
            st.info("Não há datas suficientes para criar a linha do tempo.")
        
        # -------------------- Dados Carregados --------------------
        with st.expander("🔍 Visualizar dados carregados"):
            st.dataframe(df_clean,use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {str(e)}")
        st.info("Certifique-se de que a planilha tem o formato correto: Coluna A (Métrica), Coluna B (Valor)")
else:
    st.warning("⚠️ Por favor, faça upload da planilha Excel para visualizar os dados das obras.")
    st.info("**Formato esperado:** Coluna A com nomes das métricas, Coluna B com os valores correspondentes")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #6B7280;'>Dashboard atualizado em tempo real | Dados da obra selecionada</div>", unsafe_allow_html=True)
