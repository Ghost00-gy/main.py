import streamlit as st
import google.generativeai as genai
import os, json, sqlite3
from PIL import Image

# 1. CONFIGURAÇÕES
st.set_page_config(page_title="HomeCare Connect", layout="wide", page_icon="🏥")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. BANCO DE DADOS - MIGRACAO BLINDADA
def init_db():
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    
    # Garante a tabela base
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT)''')
    
    # Verifica quais colunas já existem de fato
    cursor.execute("PRAGMA table_info(profissionais)")
    colunas_atuais = [coluna[1] for coluna in cursor.fetchall()]
    
    # Colunas necessárias para a versão robusta
    novas = [
        ("conselho", "TEXT"),
        ("bio", "TEXT"),
        ("experiencia", "TEXT"),
        ("verificado", "INTEGER DEFAULT 0")
    ]
    
    for nome_col, tipo_col in novas:
        if nome_col not in colunas_atuais:
            try:
                cursor.execute(f"ALTER TABLE profissionais ADD COLUMN {nome_col} {tipo_col}")
            except:
                pass 
                
    conn.commit()
    conn.close()

# Inicializa o banco com a nova estrutura
init_db()

# 3. ESTILIZAÇÃO
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-admin {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 4px solid #1A3A5A;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. TELAS

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
    
    with st.form("registro_completo"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            conselho = st.text_input("Registro Profissional (CRM, COREN, etc)")
            whatsapp = st.text_input("WhatsApp (com DDD)")
        with c2:
            cidade = st.text_input("Cidade/Estado")
            bio = st.text_area("Resumo Profissional")
            exp = st.text_area("Histórico de Atuação")
            
        if st.form_submit_button("Finalizar Cadastro"):
            if nome and whatsapp and conselho:
                conn = sqlite3.connect('homecare_v2.db')
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO profissionais (nome, categoria, contato, cidade, conselho, bio, experiencia) 
                                  VALUES (?,?,?,?,?,?,?)""", (nome, cat, whatsapp, cidade, conselho, bio, exp))
                conn.commit(); conn.close()
                st.success("Cadastro realizado com sucesso!")
            else:
                st.error("Preencha os campos obrigatórios.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📊 Painel de Controle")
    
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    
    # Proteção contra erro de leitura caso o banco demore a atualizar
    try:
        total = cursor.execute("SELECT COUNT(*) FROM profissionais").fetchone()[0]
        pendentes = cursor.execute("SELECT COUNT(*) FROM profissionais WHERE verificado = 0").fetchone()[0]
        
        m1, m2 = st.columns(2)
        m1.metric("Total de Inscritos", total)
        m2.metric("Aguardando Validação", pendentes)
        
        st.markdown("---")
        
        cursor.execute("SELECT id, nome, categoria, conselho, cidade, verificado FROM profissionais")
        pros = cursor.fetchall()
        
        for p in pros:
            status = "✅ OK" if p[5] == 1 else "⏳ PENDENTE"
            with st.container():
                st.markdown(f"""
                <div class="card-admin">
                    <b>{p[1]}</b> | {p[2]} | {status}<br>
                    <small>{p[3]} - {p[4]}</small>
                </div>
                """, unsafe_allow_html=True)
                if p[5] == 0:
                    if st.button(f"Aprovar {p[1]}", key=f"v_{p[0]}"):
                        cursor.execute("UPDATE profissionais SET verificado = 1 WHERE id = ?", (p[0],))
                        conn.commit()
                        st.rerun()
    except:
        st.warning("Estruturando banco de dados... Por favor, clique no botão novamente.")
    finally:
        conn.close()

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Inteligente")
    st.info("Sistema pronto para análise de casos.")

# NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
