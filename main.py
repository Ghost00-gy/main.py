import streamlit as st
from PIL import Image
import os

# 1. CONFIGURAÇÕES TÉCNICAS
st.set_page_config(page_title="HomeCare Connect", layout="wide")

# Inicializa a variável de navegação se ela não existir
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. ESTILIZAÇÃO GLOBAL (CSS)
st.markdown("""
    <style>
    .hero-text { font-size: 3rem; font-weight: 800; color: #1A3A5A; line-height: 1.2; }
    .subtitle-text { font-size: 1.5rem; color: #4A5568; margin-bottom: 2rem; }
    .stButton>button {
        background-color: #1A3A5A;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNÇÕES DE CADA PÁGINA
def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        
        st.markdown('<p class="hero-text">Cuidado e conexão em casa.</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle-text">A plataforma inteligente que une famílias aos melhores profissionais de saúde.</p>', unsafe_allow_html=True)
        
        if st.button("🚀 Iniciar Triagem Agora"):
            st.session_state.pagina = "triagem"
            st.rerun()

    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800", use_column_width=True)

    st.markdown("---")
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

def mostrar_triagem():
    # Botão para voltar (muito importante para UX)
    if st.sidebar.button("⬅️ Voltar para o Início"):
        st.session_state.pagina = "home"
        st.rerun()
    
    st.title("🩺 Triagem Inteligente")
    st.write("Aguardando o código da triagem...")
    # Aqui colaremos o conteúdo do seu arquivo '1_Triagem.py' no próximo passo.

# 4. LÓGICA DE NAVEGAÇÃO (O "MAESTRO")
if st.session_state.pagina == "home":
    mostrar_home()
elif st.session_state.pagina == "triagem":
    mostrar_triagem()
