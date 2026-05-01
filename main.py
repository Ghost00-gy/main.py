import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import sqlite3

# 1. CONFIGURAÇÕES TÉCNICAS
st.set_page_config(page_title="HomeCare Connect", layout="wide", page_icon="🏥")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. BANCO DE DADOS (Persistência)
def init_db():
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, 
                       categoria TEXT, 
                       contato TEXT, 
                       cidade TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. ESTILIZAÇÃO GLOBAL
st.markdown("""
    <style>
    .hero-text { font-size: 3.2rem; font-weight: 800; color: #1A3A5A; line-height: 1.1; }
    .subtitle-text { font-size: 1.4rem; color: #4A5568; margin-bottom: 2rem; }
    .stButton>button {
        background-color: #1A3A5A;
        color: white;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: bold;
        border: none;
    }
    .pro-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 8px solid #1A3A5A;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. TELAS DO SISTEMA

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        st.markdown('<p class="hero-text">Cuidado e conexão em casa.</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle-text">A solução inteligente para famílias e profissionais de saúde.</p>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("🚀 Iniciar Triagem"):
            st.session_state.pagina = "triagem"
            st.rerun()
        if c2.button("👨‍⚕️ Sou Profissional"):
            st.session_state.pagina = "cadastro"
            st.rerun()

    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800", use_column_width=True)

def mostrar_triagem():
    with st.sidebar:
        if st.button("⬅️ Voltar ao Início"):
            st.session_state.pagina = "home"
            st.rerun()
    
    st.title("🩺 Triagem Inteligente")
    relato = st.text_area("O que o paciente está sentindo?", height=150)

    if st.button("Analisar e Buscar"):
        if relato:
            with st.spinner("IA Analisando..."):
                try:
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"Analise: '{relato}'. Retorne JSON com 'categoria' (Medico, Enfermeiro, Tecnico, Fisioterapeuta, Psicologo), 'urgencia' e 'resumo'."
                    response = model.generate_content(prompt)
                    res = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                    
                    st.success(f"Recomendação: {res['categoria']}")
                    
                    conn = sqlite3.connect('homecare_v2.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome, categoria, contato, cidade FROM profissionais WHERE categoria=?", (res['categoria'],))
                    pros = cursor.fetchall()
                    conn.close()

                    if pros:
                        for p in pros:
                            st.markdown(f"""<div class="pro-card"><h3>{p[0]}</h3><p>📍 {p[3]}</p><a href="https://wa.me/{p[2]}" style="color:#25D366; font-weight:bold;">Chamar no WhatsApp</a></div>""", unsafe_allow_html=True)
                    else:
                        st.warning("Nenhum profissional desta categoria cadastrado ainda.")
                except:
                    st.error("Erro na análise da IA.")

def mostrar_cadastro():
    with st.sidebar:
        if st.button("⬅️ Voltar ao Início"):
            st.session_state.pagina = "home"
            st.rerun()

    st.title("👨‍⚕️ Cadastro de Colaborador")
    st.write("Preencha seus dados para começar a receber chamados de pacientes.")
    
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo")
        cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
        whatsapp = st.text_input("WhatsApp (Ex: 5511999999999)")
        cidade = st.text_input("Cidade de Atuação")
        
        if st.form_submit_button("Finalizar Cadastro"):
            if nome and whatsapp:
                conn = sqlite3.connect('homecare_v2.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO profissionais (nome, categoria, contato, cidade) VALUES (?,?,?,?)", (nome, cat, whatsapp, cidade))
                conn.commit()
                conn.close()
                st.success("Cadastro realizado! Agora você aparecerá nas triagens.")
            else:
                st.error("Preencha os campos obrigatórios.")

# 5. NAVEGAÇÃO
if st.session_state.pagina == "home":
    mostrar_home()
elif st.session_state.pagina == "triagem":
    mostrar_triagem()
elif st.session_state.pagina == "cadastro":
    mostrar_cadastro()
