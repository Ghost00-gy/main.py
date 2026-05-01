import streamlit as st
import google.generativeai as genai
import sqlite3
import json
from PIL import Image
import os

# --- 1. CONFIGURAÇÃO E ESTILO (UI/UX) ---
st.set_page_config(page_title="HomeCare Connect", page_icon="🏥", layout="wide")

# Injeção de CSS para usar as cores da sua marca
st.markdown("""
    <style>
    /* Cor de fundo e fontes */
    .main { background-color: #F0F2F6; }
    
    /* Estilização dos Botões */
    .stButton>button {
        background-color: #1A3A5A; /* Azul Marinho da sua logo */
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4A90E2; /* Azul Celeste ao passar o mouse */
        color: white;
    }

    /* Estilo dos Cards de Resultado */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 6px solid #1A3A5A;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURAÇÃO DA IA ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# --- 3. BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    # Tabela de Profissionais
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, contato TEXT, cidade TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 4. BARRA LATERAL (IDENTIDADE E ACESSO) ---
with st.sidebar:
    # Tenta carregar a logo que você subiu
    if os.path.exists("logo.png"):
        image = Image.open("logo.png")
        st.image(image)
    else:
        st.title("HomeCare Connect")
        st.caption("Cuidado e Conexão em Casa")
    
    st.markdown("---")
    
    # Sistema de Navegação Simples (Simulando Login)
    st.subheader("Área de Acesso")
    perfil = st.radio("Selecione seu perfil:", ["Sou Paciente", "Sou Profissional", "Administração"])

# --- 5. LÓGICA DAS PÁGINAS ---

if perfil == "Sou Paciente":
    st.header("🩺 Triagem Inteligente")
    st.write("Explique o que o paciente está sentindo para conectarmos o profissional certo.")
    
    relato = st.text_area("Descrição do caso:", placeholder="Ex: Idoso com dificuldade de locomoção...")
    
    if st.button("Analisar Necessidade"):
        if relato:
            with st.spinner("Analisando com HomeCare IA..."):
                # (Simulação da chamada da IA para exemplo visual)
                st.markdown("""
                <div class="card">
                    <h3 style='color: #1A3A5A;'>Resultado da Avaliação</h3>
                    <p><b>Profissional Recomendado:</b> Fisioterapeuta</p>
                    <p><b>Prioridade:</b> Média</p>
                    <p><i>Aguarde, estamos localizando os melhores profissionais próximos a você...</i></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Por favor, descreva a situação.")

elif perfil == "Sou Profissional":
    st.header("👨‍⚕️ Cadastro de Especialista")
    with st.form("cadastro"):
        nome = st.text_input("Nome Completo")
        cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
        tel = st.text_input("WhatsApp (com DDD)")
        cid = st.text_input("Cidade de Atuação")
        
        if st.form_submit_button("Finalizar Cadastro"):
            conn = sqlite3.connect('homecare_v2.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO profissionais (nome, categoria, contato, cidade) VALUES (?,?,?,?)", (nome, cat, tel, cid))
            conn.commit()
            conn.close()
            st.success("Cadastro realizado com sucesso na rede HomeCare Connect!")

else:
    st.header("📊 Painel de Gestão")
    # Visualização dos dados em formato de tabela profissional
    conn = sqlite3.connect('homecare_v2.db')
    df_prof = cursor = conn.execute("SELECT nome, categoria, cidade FROM profissionais").fetchall()
    conn.close()
    st.table(df_prof)
