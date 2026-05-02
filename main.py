import streamlit as st
import os, json, sqlite3, base64
import pandas as pd
import plotly.express as px
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

# 2. MOTOR DE DADOS COM AUDITORIA (SQLITE3)
def init_db():
    conn = sqlite3.connect('homecare_v4.db')
    cursor = conn.cursor()
    # Tabela de Profissionais
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT,
                       conselho TEXT, bio TEXT, experiencia TEXT, 
                       doc_path TEXT, rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 0)''')
    
    # Registro de Inteligência de Mercado
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       termo TEXT, data TEXT, categoria_id TEXT)''')
    
    # Registro de Auditoria
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs_auditoria 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, acao TEXT, 
                       alvo TEXT, data_hora TEXT, responsavel TEXT)''')
    conn.commit()
    conn.close()

def registrar_log(acao, alvo):
    conn = sqlite3.connect('homecare_v4.db')
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    conn.execute("INSERT INTO logs_auditoria (acao, alvo, data_hora, responsavel) VALUES (?,?,?,?)",
                 (acao, alvo, agora, "Admin-Master"))
    conn.commit(); conn.close()

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
    st.title("📝 Cadastro de Elite")
    
with st.form("form_cadastro_nacional"):
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        nome = st.text_input("Nome Completo")
        cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
        # Escala Nacional
        estado = st.selectbox("Estado (UF)", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    with col_n2:
        cidade = st.text_input("Cidade de Atuação")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        conselho = st.text_input("Registro Profissional (CRM/COREN/etc)")
        st.markdown("---")
        concordo = st.checkbox("Li e concordo que meus dados sejam processados conforme a LGPD.")

        if st.form_submit_button("Finalizar Submissão"):
            if nome and whatsapp and concordo and uploaded_file:
                # Salvar arquivo
                doc_path = f"docs/{whatsapp}_{uploaded_file.name}"
                os.makedirs("docs", exist_ok=True)
                with open(doc_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                conn = sqlite3.connect('homecare_v4.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, contato, cidade, conselho, bio, doc_path) VALUES (?,?,?,?,?,?,?)",
                             (nome, cat, whatsapp, "Tatuí", conselho, bio, doc_path))
                conn.commit(); conn.close()
                st.success("Candidatura enviada com sucesso!")
            else:
                st.error("Preencha todos os campos e aceite os termos.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    
    if not st.session_state.autenticado:
        st.title("🔑 Acesso Administrativo")
        senha = st.text_input("Chave Mestra:", type="password")
        if st.button("Acessar"):
            if senha == "tatuicare2026":
                st.session_state.autenticado = True; st.rerun()
        return

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard BI", "⚖️ Curadoria", "📜 Auditoria"])
    
    conn = sqlite3.connect('homecare_v4.db')
    
    with tab1:
        st.subheader("Centro de Inteligência Tatuí")
        df_metricas = pd.read_sql_query("SELECT termo, COUNT(*) as volume FROM metricas_triagem GROUP BY termo", conn)
        
        col_g1, col_g2 = st.columns([6, 4])
        with col_g1:
            if not df_metricas.empty:
                fig = px.bar(df_metricas, x='termo', y='volume', title="Demandas por Patologia", color_discrete_sequence=['#2E4A7D'])
                st.plotly_chart(fig, use_container_width=True)
        with col_g2:
            df_cat = pd.read_sql_query("SELECT categoria_id, COUNT(*) as total FROM metricas_triagem GROUP BY categoria_id", conn)
            if not df_cat.empty:
                fig_pizza = px.pie(df_cat, values='total', names='categoria_id', hole=.3, title="Por Especialidade")
                st.plotly_chart(fig_pizza, use_container_width=True)

    with tab2:
        pendentes = conn.execute("SELECT id, nome, categoria, doc_path FROM profissionais WHERE verificado = 0").fetchall()
        for p in pendentes:
            with st.expander(f"Analisar: {p[1]}"):
                if p[3] and os.path.exists(p[3]):
                    st.download_button("Baixar PDF", open(p[3], "rb"), file_name=p[3], key=f"dl_{p[0]}")
                if st.button(f"Aprovar {p[1]}", key=f"ap_{p[0]}"):
                    conn.execute("UPDATE profissionais SET verificado = 1 WHERE id = ?", (p[0],))
                    conn.commit()
                    registrar_log("APROVAÇÃO", p[1])
                    st.rerun()

    with tab3:
        df_logs = pd.read_sql_query("SELECT data_hora, acao, alvo FROM logs_auditoria ORDER BY id DESC", conn)
        st.table(df_logs)
    
    conn.close()

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Especializada")
    
    BASE = {"coracao": "Enfermeiro", "cardiaco": "Enfermeiro", "femur": "Fisioterapeuta", "idoso": "Tecnico"}
    relato = st.text_area("Descreva a necessidade:").lower()
    
    if st.button("Localizar Especialistas"):
        cat_sugerida = next((BASE[k] for k in BASE if k in relato), None)
        if cat_sugerida:
            # Salvar métrica
            conn = sqlite3.connect('homecare_v4.db')
            conn.execute("INSERT INTO metricas_triagem (termo, data, categoria_id) VALUES (?,?,?)",
                         (cat_sugerida, datetime.now().strftime("%d/%m/%Y"), cat_sugerida))
            conn.commit(); conn.close()
            
            st.success(f"Recomendação: {cat_sugerida}")
            # Busca profissionais... (lógica de exibição que já temos)
        else:
            st.warning("Seja mais específico no relato.")

# MAESTRO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
