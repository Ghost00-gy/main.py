import streamlit as st
import google.generativeai as genai
import os, json, sqlite3
from PIL import Image

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="HomeCare Connect", layout="wide", page_icon="🏥")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. BANCO DE DADOS
def init_db():
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT)''')
    cursor.execute("PRAGMA table_info(profissionais)")
    colunas_atuais = [coluna[1] for coluna in cursor.fetchall()]
    novas = [("conselho", "TEXT"), ("bio", "TEXT"), ("experiencia", "TEXT"), ("verificado", "INTEGER DEFAULT 0")]
    for nome_col, tipo_col in novas:
        if nome_col not in colunas_atuais:
            try:
                cursor.execute(f"ALTER TABLE profissionais ADD COLUMN {nome_col} {tipo_col}")
            except:
                pass 
    conn.commit()
    conn.close()

init_db()

# 3. ESTILIZAÇÃO
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-admin {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #1A3A5A;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES DE TELA
def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=250)
        st.markdown('# Cuidado e conexão em casa.')
        st.write("Conectamos famílias aos melhores profissionais com segurança e IA.")
        if st.button("🚀 Iniciar Triagem"):
            st.session_state.pagina = "triagem"; st.rerun()
        if st.button("👨‍⚕️ Sou Profissional (Cadastro)"):
            st.session_state.pagina = "cadastro"; st.rerun()
        if st.button("🔑 Acesso Administrativo"):
            st.session_state.pagina = "admin"; st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Cadastro Profissional")
    with st.form("registro"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            conselho = st.text_input("Registro Profissional")
            whatsapp = st.text_input("WhatsApp")
        with c2:
            cidade = st.text_input("Cidade/Estado")
            bio = st.text_area("Bio")
            exp = st.text_area("Experiência")
        if st.form_submit_button("Cadastrar"):
            if nome and whatsapp:
                conn = sqlite3.connect('homecare_v2.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO profissionais (nome, categoria, contato, cidade, conselho, bio, experiencia) VALUES (?,?,?,?,?,?,?)", (nome, cat, whatsapp, cidade, conselho, bio, exp))
                conn.commit(); conn.close()
                st.success("Sucesso!")
            else: st.error("Preencha tudo.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📊 Painel Admin")
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    pros = cursor.execute("SELECT id, nome, categoria, conselho, cidade, verificado FROM profissionais").fetchall()
    for p in pros:
        status = "✅ OK" if p[5] == 1 else "⏳ PENDENTE"
        with st.container():
            st.markdown(f'<div class="card-admin"><b>{p[1]}</b> | {p[2]} | {status}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if p[5] == 0:
                    if st.button(f"Aprovar {p[0]}", key=f"a_{p[0]}"):
                        cursor.execute("UPDATE profissionais SET verificado = 1 WHERE id = ?", (p[0],))
                        conn.commit(); st.rerun()
            with c2:
                if st.button(f"Excluir {p[0]}", key=f"e_{p[0]}"):
                    cursor.execute("DELETE FROM profissionais WHERE id = ?", (p[0],))
                    conn.commit(); st.rerun()
    conn.close()

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Inteligente")
    relato = st.text_area("Descreva o caso:")
    if st.button("Analisar"):
        if relato:
            with st.spinner("Conectando à rede de IA..."):
                try:
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    # REDUNDÂNCIA: Tenta o modelo flash, se falhar, usa o pro
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(f"Analise e retorne apenas JSON: {relato}")
                    except:
                        model = genai.GenerativeModel('gemini-pro')
                        response = model.generate_content(f"Analise e retorne apenas JSON: {relato}")
                    
                    texto = response.text.replace('```json', '').replace('```', '').strip()
                    res = json.loads(texto)
                    
                    st.success(f"Recomendação: {res.get('categoria', 'Enfermeiro')}")
                    
                    conn = sqlite3.connect('homecare_v2.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome, contato FROM profissionais WHERE verificado=1 AND categoria=?", (res.get('categoria'),))
                    encontrados = cursor.fetchall()
                    conn.close()
                    
                    for e in encontrados:
                        st.info(f"Profissional: {e[0]} - WhatsApp: {e[1]}")
                except Exception as ex:
                    st.error(f"Erro na conexão. Tente novamente em instantes.")
        else: st.warning("Descreva o caso.")

# NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
