import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from pathlib import Path

from utils.ui_utils import card_metric, plot_bg_transparent
from analytics.metrics import ShieldMetrics
from analytics.filters import ShieldFilters
from utils.paths import  SILVER_DIR, GOLD_DIR

from assistente.jarvis import AssistenteIA
from assistente.db_connect import DB

# =============================================================================
# 1. SETUP E ESTILO VISUAL 
# =============================================================================
st.set_page_config(
    page_title="SHIELD DASHBOARD",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role":  "model",
            "parts": [
                { "text": "Olá, Agente. Sou o J.A.R.V.I.S. e analiso dados do Banco Shield e Hidra. Como posso ajudar?" }
            ]
        }  
            ]

# Paleta de Cores
COLOR_SHIELD = "#00F0FF" # Cyan Neon
COLOR_HYDRA = "#FF2A2A"  # Red Neon
COLOR_BG = "#090C10"     # Ultra Dark Blue/Black
COLOR_CARD = "#161B22"   # Card Background


# Carregar CSS externo
css_path = Path(__file__).parent / "utils/styles.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()




st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_parquet(GOLD_DIR / "gold_fato_contratos_detalhada.parquet")
        df_qualidade = pd.read_parquet(SILVER_DIR / "quality_summary.parquet").to_dict(orient="records")[:1][0]
        return df, df_qualidade
    except Exception as e:
        st.error(f"Erro ao carregar os dados, tente rodar o pipeline")
        return pd.DataFrame, {}


@st.cache_resource
def criar_conexao_db():
    db = DB(GOLD_DIR)
    return db

df, df_qualidade = load_data()

# =============================================================================
# 1. INTERFACE PRINCIPAL
# =============================================================================

# Header
c1 = st.columns([0.1, 0.6, 0.1, 0.2])
with c1[1]:
    st.markdown("# S.H.I.E.L.D. Analytics System")



#======== CHATBOT J.A.R.V.I.S. ========
jarvis = AssistenteIA(
    id_conversa="conversa_shield_001",
    prompt="Você é o assistente J.A.R.V.I.S. especializado em dados do Banco Shield e Hidra Bank.",
    historico=st.session_state.messages
)




with c1[3]:
    # O Popover é o segredo do "popup"
    with st.popover("💬 J.A.R.V.I.S.", use_container_width=False):
        
        # Container para as mensagens (para dar scroll se ficar grande)
        messages_container = st.container(height=300)
        
        # Mostrar histórico
        with messages_container:
            for msg in st.session_state.messages:
                if msg["role"] == "function":
                    continue
                # Estilizando ícones baseado no tema
                avatar = "🛡️" if msg["role"] == "model" else "👤"
                st.chat_message(msg["role"], avatar=avatar).write(msg["parts"][0].get("text",""))
        
        # Input do chat
        if prompt := st.chat_input("Consultar base de dados...", key="chat_input"):
            # 1. Adicionar msg do usuário
            jarvis.guardar_historico("user", prompt)
            with messages_container:
                st.chat_message("user", avatar="👤").write(prompt)

            # 2. Resposta simples da IA (Aqui você conectaria seu LLM/Gemini depois)
            response = jarvis.consultar_llm(prompt)
            if "functionCall" in response:
                query = response["functionCall"]["args"]["query"]
                jarvis.guardar_historico("function_call",query)
                db = criar_conexao_db()
                try:
                    resultado_query = db.execute_query(query).to_string(index=False)
                except Exception as e:
                    resultado_query = f"Erro ao executar a query: {str(e)}"
                print( resultado_query,query)
                jarvis.guardar_historico("function", f"Resultado: {resultado_query}")
                response = jarvis.consultar_llm(prompt)

            
            jarvis.guardar_historico("model", response.get("text", response))
            with messages_container:
                st.chat_message("model", avatar="🛡️").write(response.get("text",""))
    


#======== CHATBOT J.A.R.V.I.S. ========





st.divider()

# Filtros (Topo, estilo barra de ferramentas)
with st.container():
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        banco_sel = st.multiselect("Banco", ShieldMetrics.options(df, "bank_name"))
    with f2:
        regiao_sel = st.multiselect("Localidade", ShieldMetrics.options(df, "location_name"))
    with f3:
        prod_sel = st.multiselect("Produto", ShieldMetrics.options(df, "product_name"))
    with f4:
        # Apenas visual para preencher
        st.markdown("<br>", unsafe_allow_html=True)

# Filtragem
df_filtered = ShieldFilters.apply_filters(
    df,
    bancos=banco_sel,
    produtos=prod_sel,
    regioes=regiao_sel
)

# Abas
tab1, tab2, tab3 = st.tabs(["Visão Geral", "Regiões", "Risco & Qualidade"])

# ---------------------------------------------------------------------
# ABA 1: VISÃO GERAL
# ---------------------------------------------------------------------
with tab1:
    # Métricas Topo
    col1, col2, col3, col4 = st.columns(4)
    vol_total = ShieldMetrics.volume_total(df_filtered)
    vol_shield = ShieldMetrics.volume_total(df_filtered[df_filtered['bank_name']=='Banco Shield'])
    share = (vol_shield / vol_total * 100) if vol_total > 0 else 0
    contratos = ShieldMetrics.contratos_ativos(df_filtered)
    risco_med = ShieldMetrics.risco_medio(df_filtered)

    with col1: card_metric("VOLUME TOTAL", f"R$ {vol_total/1e6:.1f} M")
    with col2: card_metric("SHIELD SHARE", f"{share:.1f}%", color="#FFD700") # Amarelo alerta
    with col3: card_metric("CONTRATOS ATIVOS", f"{contratos}")
    with col4: card_metric("NÍVEL DE RISCO", f"{risco_med:.2f}%",color=COLOR_HYDRA)

    # Gráficos Linha 1
    c_chart1, c_chart2 = st.columns([2, 1])
    
    with c_chart1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### DISPUTA DE TERRITÓRIO")
        df_time = ShieldMetrics.volume_tempo(df_filtered)
        fig_area = px.area(
            df_time, x='ano_mes', y='financed_amount', color='bank_name',
            labels={
                    'ano_mes': 'Ano / Mês',
                    'financed_amount': 'Valor Financiado (R$)',
                    'bank_name': 'Banco'
                },
            color_discrete_map={'Banco Shield': COLOR_SHIELD, 'Hidra Bank': COLOR_HYDRA}
        )
        st.plotly_chart(plot_bg_transparent(fig_area), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    

    with c_chart2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### SHARE POR PRODUTO")
        df_prod = ShieldMetrics.share_por_produto(df_filtered)
        fig_bar = px.bar(
            df_prod, y='product_name', x='financed_amount', color='bank_name', orientation='h',
            labels={
                    'product_name': 'Produto',
                    'financed_amount': 'Valor Financiado (R$)',
                    'bank_name': 'Banco'
                },
            color_discrete_map={'Banco Shield': COLOR_SHIELD, 'Hidra Bank': COLOR_HYDRA},
            barmode='stack'
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(plot_bg_transparent(fig_bar), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------
# ABA 2: REGIONAL
# ---------------------------------------------------------------------
with tab2:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### DOMÍNIO GEOGRÁFICO")
    
    df_reg = ShieldMetrics.group_region(df_filtered)
    
    # Gráfico de Barras Agrupadas Moderno
    fig_reg = px.bar(
        df_reg, x='location_name', y='financed_amount', color='bank_name', barmode='group',
        labels={
                    'location_name': 'Localidade',
                    'financed_amount': 'Valor Financiado (R$)',
                    'bank_name': 'Banco'
                },
        color_discrete_map={'Banco Shield': COLOR_SHIELD, 'Hidra Bank': COLOR_HYDRA},
    )
    st.plotly_chart(plot_bg_transparent(fig_reg), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1 = st.columns(1)[0]
    with c1:
        st.info(f"A região {ShieldMetrics.region_product(df_filtered).get('location_name', 'N/A')} apresenta alto volume da Hidra em {ShieldMetrics.region_product(df_filtered).get('product_name', 'N/A')}.")
    


# ---------------------------------------------------------------------
# ABA 3: RISCO
# ---------------------------------------------------------------------
with tab3:
    c_risk1, c_risk2 = st.columns([2, 1])
    
    with c_risk1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### RADAR DE RISCO E VOLUME")
        df_risk = ShieldMetrics.risco_volume_contratos(df_filtered)
        
        fig_scat = px.scatter(
            df_risk, x='financed_amount', y='risk_score', color='bank_name', size='contract_id',
                labels={
                    'risk_score': 'Score de Risco (%)',
                    'financed_amount': 'Valor Financiado (R$)',
                    'bank_name': 'Banco'
                },
            color_discrete_map={'Banco Shield': COLOR_SHIELD, 'Hidra Bank': COLOR_HYDRA},
            hover_data=['product_name']
        )
        # Linha de corte
        fig_scat.add_hline(y=0.10, line_dash="dot", line_color="#FF4B4B", annotation_text="DANGER ZONE")
        st.plotly_chart(plot_bg_transparent(fig_scat), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_risk2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### QUALIDADE DE DADOS")
        

        for col, val in df_qualidade.items():
            #st.markdown(f"**{col}**: {val}")
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding: 10px;'>
                <span style='color: #8B949E'>{col}</span>
                <span style='color: {COLOR_HYDRA}; font-weight: bold'>{val}</span>
            </div>

        """, unsafe_allow_html=True)


# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #444;'>SHIELD ANALYTICS SYSTEM</div>", unsafe_allow_html=True)