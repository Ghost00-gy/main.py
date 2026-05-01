import streamlit as st
import google.generativeai as genai
import os, json, sqlite3
from PIL import Image

# 1. CONFIGURAÇÕES
st.set_page_config(page_title="HomeCare Connect", layout="wide", page_icon="🏥")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. BANCO DE DADOS EVOLUÍDO
def init_db():
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    
    # Cria a tabela base se não existir
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT)''')
    
    # Lista de colunas que precisam existir para o app ser "Robusto"
    colunas_novas = [
        ("conselho", "TEXT"),
        ("bio", "TEXT"),
        ("experiencia", "TEXT"),
        ("verificado", "INTEGER DEFAULT 0")
    ]
    
    # Tenta adicionar cada coluna individualmente
    for nome_col, tipo_col in colunas_novas:
        try:
            cursor.execute(f"ALTER TABLE profissionais ADD COLUMN {nome_col} {tipo_col}")
        except sqlite3.OperationalError:
            # Se a coluna já existir, o SQLite avisará e nós apenas ignoramos
            pass
            
    conn.commit()
    conn.close()
    
# 3. ESTILIZAÇÃO E COMPONENTES VISUAIS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .card-admin {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 4px solid #1A3A5A;
        margin-bottom: 10px;
    }
    .badge-verificado {
        background-color: #28a745; color: white; padding: 2px 8px;
        border-radius: 10px; font-size: 10px;
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
    st.title("📝 Cadastro Profissional Robusto")
    
    with st.form("registro_completo"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            conselho = st.text_input("Registro Profissional (Ex: CRM/SP 12345)")
            whatsapp = st.text_input("WhatsApp (Ex: 5511999999999)")
        with col2:
            cidade = st.text_input("Cidade/Estado")
            bio = st.text_area("Resumo do Perfil (Bio)", placeholder="Conte um pouco sobre sua abordagem...")
            exp = st.text_area("Experiência Profissional", placeholder="Ex: 5 anos no Hospital X, especialista em UTI...")
            
        foto = st.file_uploader("Foto de Perfil (Opcional)", type=['png', 'jpg'])
        
        if st.form_submit_button("Enviar Cadastro para Aprovação"):
            if nome and whatsapp and conselho:
                conn = sqlite3.connect('homecare_v2.db')
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO profissionais (nome, categoria, contato, cidade, conselho, bio, experiencia) 
                                  VALUES (?,?,?,?,?,?,?)""", (nome, cat, whatsapp, cidade, conselho, bio, exp))
                conn.commit(); conn.close()
                st.success("Cadastro enviado! Nossa equipe revisará seus dados em breve.")
            else:
                st.error("Campos com * são obrigatórios.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📊 Centro de Comando HomeCare")
    
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    
    # Buscas para o Dashboard
    total = cursor.execute("SELECT COUNT(*) FROM profissionais").fetchone()[0]
    pendentes = cursor.execute("SELECT COUNT(*) FROM profissionais WHERE verificado = 0").fetchone()[0]
    
    # Exibição de Métricas no topo
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Parceiros", total)
    m2.metric("Aguardando Validação", pendentes, delta_color="inverse")
    m3.metric("Status do Sistema", "Online")
    
    st.markdown("---")
    
    # Listagem para Gestão
    cursor.execute("SELECT id, nome, categoria, conselho, cidade, verificado FROM profissionais")
    pros = cursor.fetchall()
    conn.close()
    
    if not pros:
        st.info("Nenhum profissional cadastrado.")
    else:
        st.subheader("Gerenciar Profissionais")
        for p in pros:
            status_cor = "orange" if p[5] == 0 else "green"
            status_txt = "PENDENTE" if p[5] == 0 else "VERIFICADO"
            
            with st.container():
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; border-left: 5px solid {status_cor}; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 18px;">{p[1]}</span>
                        <span style="background: {status_cor}; color: white; padding: 2px 10px; border-radius: 15px; font-size: 12px;">{status_txt}</span>
                    </div>
                    <p style="margin: 5px 0; color: #555;">{p[2]} | {p[3]} | 📍 {p[4]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão de ação rápida
                if p[5] == 0:
                    if st.button(f"Aprovar {p[1]}", key=f"btn_{p[0]}"):
                        c = sqlite3.connect('homecare_v2.db')
                        c.execute("UPDATE profissionais SET verificado = 1 WHERE id = ?", (p[0],))
                        c.commit()
                        c.close()
                        st.success(f"Profissional {p[1]} aprovado!")
                        st.rerun()

# Lógica da Triagem (mantida conforme anterior, mas agora mostrando dados robustos)
def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Conexão")
    relato = st.text_area("Relato do Caso")
    if st.button("Buscar Especialista"):
        # ... (Sua lógica de IA Gemini aqui) ...
        # Ao mostrar o card, agora você pode incluir o 'conselho' e a 'bio'
        st.info("Buscando no banco de dados robusto...")

# NAVEGAÇÃO FINAL
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
