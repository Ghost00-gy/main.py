import streamlit as st
import os, json, sqlite3
from datetime import datetime

# 1. CONFIGURAÇÕES DE ELITE
st.set_page_config(
    page_title="HomeCare Connect | Saúde Domiciliar", 
    layout="wide", 
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# Inicialização de estados de sessão para acessibilidade e navegação
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'fonte_grande' not in st.session_state: st.session_state.fonte_grande = False

# 2. ARQUITETURA DE DADOS AVANÇADA
def init_db():
    conn = sqlite3.connect('homecare_v3.db')
    cursor = conn.cursor()
    # Tabela de Profissionais Expandida
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT,
                       conselho TEXT, bio TEXT, experiencia TEXT, 
                       rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 0)''')
    
    # Tabela de Métricas (Big Data Local)
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       termo_buscado TEXT, data_hora TEXT, categoria_sugerida TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. DESIGN SYSTEM E ACESSIBILIDADE
tamanho_fonte = "20px" if st.session_state.fonte_grande else "16px"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: {tamanho_fonte} !important; color: #1A3A5A; }}
    .stButton>button {{
        border-radius: 12px; padding: 0.6rem 1.2rem;
        transition: all 0.3s ease; border: 2px solid #2E4A7D;
    }}
    .stButton>button:hover {{ transform: scale(1.02); border-color: #4A90E2; }}
    .card-pro {{
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 25px rgba(46, 74, 125, 0.1);
        border-left: 8px solid #2E4A7D; margin-bottom: 25px;
    }}
    .acessibilidade-bar {{
        background: #f1f3f6; padding: 10px; border-radius: 10px;
        display: flex; gap: 10px; margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Barra de Acessibilidade (Sempre Visível no Topo)
with st.container():
    c_acc1, c_acc2 = st.columns([8, 2])
    with c_acc2:
        if st.checkbox("🔍 Fonte Grande", value=st.session_state.fonte_grande):
            st.session_state.fonte_grande = True
            st.rerun() if not st.session_state.fonte_grande else None
        else:
            st.session_state.fonte_grande = False

# 4. FUNCIONALIDADES DE TELA (LOGICA LOCAL)

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=350)
        st.markdown('# Onde a tecnologia encontra o cuidado.')
        st.write("Plataforma de intermediação de saúde com curadoria rigorosa e foco em Tatuí.")
        
        st.markdown("### Como podemos ajudar hoje?")
        if st.button("🚀 Iniciar Triagem Inteligente", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        
        st.divider()
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("👨‍⚕️ Cadastro Profissional", use_container_width=True):
                st.session_state.pagina = "cadastro"; st.rerun()
        with col_nav2:
            if st.button("🔑 Gestão Administrativa", use_container_width=True):
                st.session_state.pagina = "admin"; st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=800", caption="Saúde Conectada")

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar ao Início", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem de Especialidades")
    
    # Base de Conhecimento Local Expandida (2026)
    BASE_CUIDADOS = {
        "coracao": {"cat": "Enfermeiro", "msg": "Cuidados cardíacos pós-operatórios."},
        "femur": {"cat": "Fisioterapeuta", "msg": "Reabilitação motora e mobilidade."},
        "idoso": {"cat": "Tecnico", "msg": "Apoio em rotinas e higiene."},
        "diabetes": {"cat": "Enfermeiro", "msg": "Controle glicêmico e curativos."},
        "avc": {"cat": "Fisioterapeuta", "msg": "Reabilitação neurofuncional."},
        "pos-parto": {"cat": "Enfermeiro", "msg": "Apoio materno e neonatal."}
    }

    relato = st.text_area("Descreva detalhadamente a situação clínica:", height=150).lower()
    
    if st.button("Analisar e Recomendar", type="primary"):
        if relato:
            match = None
            for chave, dados in BASE_CUIDADOS.items():
                if chave in relato:
                    match = dados
                    # REGISTRO DE MÉTRICA (DATA DRIVEN)
                    conn = sqlite3.connect('homecare_v3.db')
                    conn.execute("INSERT INTO metricas_triagem (termo_buscado, data_hora, categoria_sugerida) VALUES (?,?,?)",
                                 (chave, datetime.now().strftime("%Y-%m-%d %H:%M"), dados['cat']))
                    conn.commit(); conn.close()
                    break
            
            if match:
                st.success(f"**Indicação Sugerida:** {match['cat']}")
                st.info(f"**Nota Clínica:** {match['msg']}")
                
                # BUSCA PROFISSIONAIS POR RATING (MAIOR QUALIDADE PRIMEIRO)
                conn = sqlite3.connect('homecare_v3.db')
                pros = conn.execute("SELECT nome, contato, conselho, bio, rating FROM profissionais WHERE verificado=1 AND categoria=? ORDER BY rating DESC", (match['cat'],)).fetchall()
                conn.close()

                if pros:
                    st.write("---")
                    for p in pros:
                        msg_wa = f"Olá {p[0]}, vi seu perfil verificado no HomeCare Connect. Preciso de suporte para um caso de {match['cat']}."
                        url_wa = f"https://wa.me/{p[1]}?text={msg_wa.replace(' ', '%20')}"
                        
                        with st.container():
                            st.markdown(f"""
                            <div class="card-pro">
                                <span style="float:right; font-size: 24px;">⭐ {p[4]}</span>
                                <h3 style="margin:0;">{p[0]}</h3>
                                <p><b>{match['cat']}</b> | {p[2]}</p>
                                <p>{p[3]}</p>
                                <a href="{url_wa}" target="_blank" style="background:#25D366; color:white; padding:12px 30px; border-radius:10px; text-decoration:none; font-weight:bold; display:inline-block;">Contatar via WhatsApp</a>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("Não há profissionais verificados disponíveis para esta categoria no momento.")
            else:
                st.warning("Não conseguimos identificar uma categoria automática. Tente usar palavras como 'coração', 'idoso' ou 'AVC'.")
        else:
            st.error("Por favor, relate o quadro clínico.")

# 5. EXECUÇÃO DO SISTEMA
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro":
    st.info("Interface de Cadastro Profissional em conformidade com LGPD.")
    # (Função de cadastro simplificada para este exemplo)
elif st.session_state.pagina == "admin":
    # (Interface de Admin com Senha 'tatuicare2026' já discutida)
    pass
