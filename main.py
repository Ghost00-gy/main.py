import streamlit as st
from PIL import Image
import os

# Configuração da página inicial
st.set_page_config(page_title="HomeCare Connect | Home", layout="wide")

# Estilização extra para a Home
st.markdown("""
    <style>
    .hero-text { font-size: 3rem; font-weight: 800; color: #1A3A5A; line-height: 1.2; }
    .subtitle-text { font-size: 1.5rem; color: #4A5568; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# Layout da Home
col1, col2 = st.columns([1, 1])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=250)
    
    st.markdown('<p class="hero-text">Cuidado e conexão em casa.</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">A plataforma inteligente que une famílias aos melhores profissionais de saúde.</p>', unsafe_allow_html=True)
    
    if st.button("🚀 Iniciar Triagem Agora"):
        # Comando para trocar de página programaticamente
        st.switch_page("pages/1_🩺_Triagem.py")

with col2:
    # Imagem profissional de saúde (Placeholder de alta qualidade)
    st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800", use_column_width=True)

st.markdown("---")

# Seção de métricas/Diferenciais
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("🛡️ Segurança")
    st.write("Profissionais verificados e dados protegidos.")
with c2:
    st.subheader("🧠 Inteligência")
    st.write("Triagem precisa baseada em sintomas reais.")
with c3:
    st.subheader("🤝 Conexão")
    st.write("Agendamento direto via WhatsApp.")
