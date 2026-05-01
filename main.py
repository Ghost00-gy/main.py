import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import sqlite3

# 1. CONFIGURAÇÕES TÉCNICAS E DE PÁGINA
st.set_page_config(page_title="HomeCare Connect", layout="wide", page_icon="🏥")

# Inicializa a variável de navegação (SPA)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. ESTILIZAÇÃO GLOBAL (CSS) - Identidade HomeCare Connect
st.markdown("""
    <style>
    .hero-text { font-size: 3.2rem; font-weight: 800; color: #1A3A5A; line-height: 1.1; margin-bottom: 1rem; }
    .subtitle-text { font-size: 1.4rem; color: #4A5568; margin-bottom: 2rem; }
    
    /* Estilo dos Botões Principais */
    .stButton>button {
        background-color: #1A3A5A;
        color: white;
        border-radius: 10px;
        padding: 0.7rem 2.5rem;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4A90E2;
        color: white;
    }

    /* Cards de Profissionais */
    .pro-card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-left: 8px solid #1A3A5A;
        margin-bottom: 20px;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNÇÕES DE CADA TELA

def mostrar_home():
    """Renderiza a Landing Page inicial"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        
        st.markdown('<p class="hero-text">Cuidado e conexão em casa.</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle-text">A plataforma inteligente que une famílias aos melhores profissionais de saúde através de IA.</p>', unsafe_allow_html=True)
        
        if st.button("🚀 Iniciar Triagem Agora"):
            st.session_state.pagina = "triagem"
            st.rerun()

    with col2:
        # Imagem profissional contextual
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800", use_column_width=True)

    st.markdown("---")
    # Seção de Diferenciais
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🛡️ Segurança")
        st.write("Profissionais verificados e dados protegidos com ética.")
    with c2:
        st.subheader("🧠 Inteligência")
        st.write("Triagem precisa baseada em sintomas e necessidades reais.")
    with c3:
        st.subheader("🤝 Conexão")
        st.write("Contato direto e agendamento via WhatsApp.")

def mostrar_triagem():
    """Renderiza a tela de Triagem com IA e busca de profissionais"""
    
    # Barra lateral interna para navegação
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=150)
        st.markdown("---")
        if st.button("⬅️ Voltar para o Início"):
            st.session_state.pagina = "home"
            st.rerun()
    
    st.title("🩺 Triagem Inteligente")
    st.write("Descreva o quadro do paciente para que nossa IA recomende o melhor cuidado.")

    relato = st.text_area("O que o paciente está sentindo?", 
                          placeholder="Ex: Minha mãe tem 80 anos, teve alta hospitalar e precisa de auxílio com curativos e banho.",
                          height=150)

    if st.button("Analisar Caso e Localizar Especialistas"):
        if relato:
            with st.spinner("Analisando necessidades com HomeCare IA..."):
                try:
                    # Configuração da IA
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-pro')
                    
                    prompt = f"""
                    Aja como um triador de home care. Analise: '{relato}'
                    Retorne APENAS um JSON:
                    {{
                        "categoria": "Medico" ou "Enfermeiro" ou "Tecnico" ou "Fisioterapeuta" ou "Psicologo",
                        "urgencia": "Baixa", "Media" ou "Alta",
                        "resumo": "Uma frase acolhedora de orientação."
                    }}
                    """
                    
                    response = model.generate_content(prompt)
                    # Limpeza de resposta para garantir o parse do JSON
                    raw_text = response.text.replace('```json', '').replace('```', '').strip()
                    res = json.loads(raw_text)
                    
                    # Feedback da IA
                    st.success(f"**Recomendação:** Especialista em {res['categoria']}")
                    st.info(f"📋 **Análise:** {res['resumo']} (Urgência: {res['urgencia']})")

                    # Busca no Banco de Dados (homecare_v2.db)
                    conn = sqlite3.connect('homecare_v2.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome, categoria, contato, cidade FROM profissionais WHERE categoria=?", (res['categoria'],))
                    profissionais = cursor.fetchall()
                    conn.close()

                    if profissionais:
                        st.write("### Especialistas Disponíveis")
                        for p in profissionais:
                            st.markdown(f"""
                            <div class="pro-card">
                                <h3 style="color:#1A3A5A; margin-bottom:5px;">{p[0]}</h3>
                                <p style="margin-bottom:10px;">📍 <b>{p[3]}</b> | Especialidade: {p[1]}</p>
                                <a href="https://wa.me/{p[2]}" target="_blank" class="whatsapp-btn">Chamar no WhatsApp</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"No momento, não temos especialistas em {res['categoria']} cadastrados nesta região.")
                
                except Exception as e:
                    st.error("Erro técnico na análise. Verifique sua chave API.")
        else:
            st.warning("Por favor, preencha o relato para análise.")

# 4. MAESTRO DE NAVEGAÇÃO
if st.session_state.pagina == "home":
    mostrar_home()
elif st.session_state.pagina == "triagem":
    mostrar_triagem()
