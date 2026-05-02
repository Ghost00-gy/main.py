import streamlit as st
import os, json, sqlite3, base64
from datetime import datetime
from PIL import Image

# 1. CONFIGURAÇÕES DE ALTA DISPONIBILIDADE
st.set_page_config(
    page_title="HomeCare Connect | Elite Health", 
    layout="wide", 
    page_icon="🏥"
)

# Gerenciamento de Estado
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'fonte_grande' not in st.session_state: st.session_state.fonte_grande = False

# 2. MOTOR DE DADOS (SQLITE3)
def init_db():
    conn = sqlite3.connect('homecare_v4.db')
    cursor = conn.cursor()
    # Tabela de Profissionais com Documentação e Rating
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT,
                       conselho TEXT, bio TEXT, experiencia TEXT, 
                       doc_path TEXT, rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 0)''')
    
    # Registro de Inteligência de Mercado
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       termo TEXT, data TEXT, categoria_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. ACESSIBILIDADE E DESIGN SYSTEM
tamanho_fonte = "1.25rem" if st.session_state.fonte_grande else "1rem"

st.markdown(f"""
    <style>
    :root {{ --primary: #2E4A7D; --secondary: #4A90E2; --bg: #F8F9FA; }}
    html, body, [class*="css"] {{ font-size: {tamanho_fonte}; color: #1A3A5A; background-color: var(--bg); }}
    .stButton>button {{ border-radius: 12px; border: 2px solid var(--primary); font-weight: 600; }}
    .card-elite {{
        background: white; border-radius: 20px; padding: 30px;
        box-shadow: 0 15px 35px rgba(46, 74, 125, 0.08);
        border-left: 10px solid var(--primary); margin-bottom: 25px;
    }}
    .metric-card {{ background: white; padding: 20px; border-radius: 15px; border: 1px solid #eee; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# 4. COMPONENTES DE INTERFACE

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=380)
        st.title("Excelência em Cuidado Domiciliar")
        st.write("Conectando Tatuí aos melhores especialistas através de triagem inteligente e curadoria rigorosa.")
        
        if st.button("🚀 Iniciar Triagem de Saúde", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        
        st.divider()
        c_nav1, c_nav2 = st.columns(2)
        with c_nav1:
            if st.button("👨‍⚕️ Cadastro Especialista", use_container_width=True):
                st.session_state.pagina = "cadastro"; st.rerun()
        with c_nav2:
            if st.button("📊 Gestão & Métricas", use_container_width=True):
                st.session_state.pagina = "admin"; st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Cadastro de Especialista")
    st.write("Seja parte da elite de profissionais de Tatuí.")
    
    with st.form("form_cadastro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            whatsapp = st.text_input("WhatsApp (apenas números)")
            conselho = st.text_input("Nº Registro Profissional (CRM/COREN/CREFITO)")
        with c2:
            bio = st.text_area("Breve Currículo")
            exp = st.text_area("Experiências Principais")
            uploaded_file = st.file_uploader("Upload de Comprovante Profissional (PDF/JPG)", type=["pdf", "jpg", "png"])
        
        if st.form_submit_button("Submeter para Análise"):
            if nome and whatsapp and uploaded_file:
                # Salvar Arquivo Localmente para Verificação Admin
                file_path = f"docs/{whatsapp}_{uploaded_file.name}"
                os.makedirs("docs", exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                conn = sqlite3.connect('homecare_v4.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, contato, cidade, conselho, bio, experiencia, doc_path) VALUES (?,?,?,?,?,?,?,?)",
                             (nome, cat, whatsapp, "Tatuí", conselho, bio, exp, file_path))
                conn.commit(); conn.close()
                st.success("Cadastro enviado! Nossa equipe analisará seus documentos em breve.")
            else: st.error("Preencha todos os campos e anexe sua documentação.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    
    if not st.session_state.autenticado:
        st.title("🔑 Acesso Restrito")
        senha = st.text_input("Chave de Acesso Admin:", type="password")
        if st.button("Autenticar"):
            if senha == "tatuicare2026": #
                st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 Dashboard de Gestão & Inteligência")
    
    # MÉTRICAS DE BIG DATA LOCAL
    conn = sqlite3.connect('homecare_v4.db')
    m1, m2, m3 = st.columns(3)
    
    total_pros = conn.execute("SELECT COUNT(*) FROM profissionais").fetchone()[0]
    total_buscas = conn.execute("SELECT COUNT(*) FROM metricas_triagem").fetchone()[0]
    mais_buscado = conn.execute("SELECT termo, COUNT(termo) as c FROM metricas_triagem GROUP BY termo ORDER BY c DESC LIMIT 1").fetchone()
    
    m1.metric("Profissionais Cadastrados", total_pros)
    m2.metric("Total de Atendimentos IA", total_buscas)
    m3.metric("Maior Demanda em Tatuí", mais_buscado[0] if mais_buscado else "N/A")
    
    st.divider()
    
    # GESTÃO DE CURADORIA
    pendentes = conn.execute("SELECT id, nome, categoria, doc_path FROM profissionais WHERE verificado = 0").fetchall()
    st.subheader(f"Pendentes de Verificação ({len(pendentes)})")
    
    for p in pendentes:
        with st.expander(f"Analisar: {p[1]} ({p[2]})"):
            st.write(f"ID Interno: {p[0]}")
            if p[3] and os.path.exists(p[3]):
                st.download_button("Baixar Documento de Comprovação", open(p[3], "rb"), file_name=p[3])
            
            c_adm1, c_adm2 = st.columns(2)
            if c_adm1.button(f"✅ Aprovar {p[0]}", use_container_width=True):
                conn.execute("UPDATE profissionais SET verificado = 1 WHERE id = ?", (p[0],))
                conn.commit(); st.rerun()
            if c_adm2.button(f"🗑️ Rejeitar {p[0]}", use_container_width=True):
                conn.execute("DELETE FROM profissionais WHERE id = ?", (p[0],))
                conn.commit(); st.rerun()
    conn.close()

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Especializada")
    
    # BASE DE DADOS LOCAL EXPANDIDA (DOMÍNIO MÉDICO)
    BASE = {
        "coracao": "Enfermeiro", "cardiaco": "Enfermeiro",
        "femur": "Fisioterapeuta", "fratura": "Fisioterapeuta",
        "idoso": "Tecnico", "alzheimer": "Tecnico",
        "diabetes": "Enfermeiro", "insulina": "Enfermeiro",
        "avc": "Fisioterapeuta", "derrame": "Fisioterapeuta"
    }

    relato = st.text_area("Relate as necessidades do paciente:", placeholder="Ex: Idoso após cirurgia no fêmur...", height=150).lower()
    
    if st.button("Analisar e Localizar Elite", type="primary"):
        if relato:
            cat_sugerida = None
            for chave in BASE:
                if chave in relato:
                    cat_sugerida = BASE[chave]
                    # Salvar Métrica para Business Intelligence
                    c = sqlite3.connect('homecare_v4.db')
                    c.execute("INSERT INTO metricas_triagem (termo, data, categoria_id) VALUES (?,?,?)",
                                 (chave, datetime.now().strftime("%d/%m/%Y %H:%M"), cat_sugerida))
                    c.commit(); c.close()
                    break
            
            if cat_sugerida:
                st.success(f"**Recomendação HomeCare:** {cat_sugerida}")
                
                conn = sqlite3.connect('homecare_v4.db')
                pros = conn.execute("SELECT nome, contato, conselho, bio, rating FROM profissionais WHERE verificado=1 AND categoria=?", (cat_sugerida,)).fetchall()
                conn.close()

                if pros:
                    for p in pros:
                        url_wa = f"https://wa.me/{p[1]}?text=Olá%20{p[0]},%20vi%20seu%20perfil%20de%20elite%20no%20HomeCare%20Connect."
                        st.markdown(f"""
                        <div class="card-elite">
                            <span style="float:right; font-size: 1.5rem; color: #f1c40f;">{'★' * int(p[4])}</span>
                            <h2 style="margin:0; color:var(--primary);">{p[0]}</h2>
                            <p><b>{cat_sugerida}</b> | {p[2]}</p>
                            <p style="color: #666 italic;">"{p[3]}"</p>
                            <a href="{url_wa}" target="_blank" style="background:#25D366; color:white; padding:12px 30px; border-radius:10px; text-decoration:none; font-weight:bold; display:inline-block;">Contatar via WhatsApp</a>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.warning(f"No momento, não temos {cat_sugerida} verificados para esta demanda específica.")
            else: st.warning("Por favor, seja mais específico no relato para identificarmos a especialidade correta.")

# 5. MAESTRO DE NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
