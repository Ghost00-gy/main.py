import streamlit as st
import os, sqlite3, pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURAÇÕES DE ALTA DISPONIBILIDADE
st.set_page_config(
    page_title="HomeCare Connect | Brasil",
    layout="wide", 
    page_icon="🏥"
)

# Gerenciamento de Estado
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'fonte_grande' not in st.session_state: st.session_state.fonte_grande = False

# 2. MOTOR DE DADOS NACIONAL (v5)
def init_db():
    conn = sqlite3.connect('homecare_nacional.db')
    cursor = conn.cursor()
    # Tabela com campos de UF e Cidade para Escala Nacional
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, conselho TEXT, bio TEXT, 
                       doc_path TEXT, rating REAL DEFAULT 5.0, 
                       total_avaliacoes INTEGER DEFAULT 0,
                       verificado INTEGER DEFAULT 0)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       termo TEXT, uf TEXT, cidade TEXT, data TEXT, categoria_id TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs_auditoria 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, acao TEXT, 
                       alvo TEXT, data_hora TEXT, responsavel TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. DESIGN SYSTEM NACIONAL
tamanho_fonte = "1.25rem" if st.session_state.fonte_grande else "1rem"
st.markdown(f"""
    <style>
    :root {{ --primary: #2E4A7D; --bg: #F8F9FA; }}
    html, body, [class*="css"] {{ font-size: {tamanho_fonte}; color: #1A3A5A; background-color: var(--bg); }}
    .card-elite {{
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 30px rgba(46, 74, 125, 0.1);
        border-left: 10px solid var(--primary); margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. COMPONENTES DE INTERFACE

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=380)
        st.title("Conexão Saúde em Todo o Brasil")
        st.write("A elite dos profissionais de saúde domiciliar, agora com cobertura nacional e inteligência logística.")
        
        if st.button("🚀 Iniciar Triagem Nacional", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        
        st.divider()
        c_nav1, c_nav2 = st.columns(2)
        c_nav1.button("👨‍⚕️ Cadastro Profissional", on_click=lambda: st.session_state.update({"pagina": "cadastro"}), use_container_width=True)
        c_nav2.button("📊 Centro de Inteligência", on_click=lambda: st.session_state.update({"pagina": "admin"}), use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Cadastro Nacional de Especialistas")
    
    with st.form("form_cadastro_nacional"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            uf = st.selectbox("Estado (UF)", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
            cidade = st.text_input("Cidade")
        with c2:
            whatsapp = st.text_input("WhatsApp (com DDD)")
            conselho = st.text_input("Registro Profissional (Ex: CRM-SP 12345)")
            uploaded_file = st.file_uploader("Documento de Comprovação (PDF)", type=["pdf"])
        
        st.markdown("---")
        concordo = st.checkbox("Declaro que as informações são verídicas e aceito os termos da LGPD.")

        if st.form_submit_button("Submeter Candidatura Nacional"):
            if nome and uf and cidade and uploaded_file and concordo:
                doc_path = f"docs/{whatsapp}_{uploaded_file.name}"
                os.makedirs("docs", exist_ok=True)
                with open(doc_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                conn = sqlite3.connect('homecare_nacional.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, uf, cidade, contato, conselho, doc_path) VALUES (?,?,?,?,?,?,?)",
                             (nome, cat, uf, cidade, whatsapp, conselho, doc_path))
                conn.commit(); conn.close()
                st.success(f"Cadastro para {cidade}-{uf} enviado para análise!")
            else: st.error("Por favor, preencha todos os campos obrigatórios.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    if not st.session_state.autenticado:
        senha = st.text_input("Chave Mestra Nacional:", type="password")
        if st.button("Acessar"):
            if senha == "tatuicare2026": st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 Painel de Controle Nacional")
    tab1, tab2 = st.tabs(["📈 Business Intelligence", "⚖️ Curadoria de Documentos"])
    
    conn = sqlite3.connect('homecare_nacional.db')
    with tab1:
        # Gráfico por Estado
        df_uf = pd.read_sql_query("SELECT uf, COUNT(*) as volume FROM metricas_triagem GROUP BY uf", conn)
        if not df_uf.empty:
            fig = px.choropleth(df_uf, locations='uf', locationmode="USA-states", color='volume', scope="south america", title="Mapa de Calor de Demandas (Brasil)")
            st.plotly_chart(fig, use_container_width=True)
        
        m1, m2 = st.columns(2)
        total_nacional = conn.execute("SELECT COUNT(*) FROM profissionais WHERE verificado=1").fetchone()[0]
        m1.metric("Especialistas Ativos no Brasil", total_nacional)
        
    with tab2:
        pendentes = conn.execute("SELECT id, nome, uf, cidade, doc_path FROM profissionais WHERE verificado=0").fetchall()
        for p in pendentes:
            with st.expander(f"Analisar: {p[1]} ({p[3]}-{p[2]})"):
                st.write(f"Localidade: {p[3]} / {p[2]}")
                if st.button(f"Aprovar {p[1]}", key=f"ap_{p[0]}"):
                    conn.execute("UPDATE profissionais SET verificado=1 WHERE id=?", (p[0],))
                    conn.commit(); st.rerun()
    conn.close()

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Localização de Elite")
    
    c1, c2 = st.columns(2)
    uf_busca = c1.selectbox("Onde você está? (UF)", ["SP", "RJ", "MG", "RS", "PR", "Outros..."])
    cidade_busca = c2.text_input("Sua Cidade")
    
    relato = st.text_area("Descreva a necessidade clínica (ex: pós-operatório, idoso, curativo):").lower()
    
    if st.button("Localizar Especialista Próximo", type="primary"):
        BASE = {"coracao": "Enfermeiro", "femur": "Fisioterapeuta", "idoso": "Tecnico"}
        cat_sugerida = next((BASE[k] for k in BASE if k in relato), None)
        
        if cat_sugerida and cidade_busca:
            # Salvar Métrica Geográfica
            conn = sqlite3.connect('homecare_nacional.db')
            conn.execute("INSERT INTO metricas_triagem (termo, uf, cidade, data, categoria_id) VALUES (?,?,?,?,?)",
                         (cat_sugerida, uf_busca, cidade_busca, datetime.now().strftime("%d/%m/%Y"), cat_sugerida))
            
            # Buscar apenas na região do paciente
            pros = conn.execute("SELECT nome, contato, conselho, rating, bio FROM profissionais WHERE verificado=1 AND categoria=? AND uf=? AND cidade LIKE ?", 
                                (cat_sugerida, uf_busca, f"%{cidade_busca}%")).fetchall()
            conn.close()
            
            if pros:
                st.success(f"Encontramos {len(pros)} especialistas de elite em {cidade_busca}!")
                for p in pros:
                    # Cálculo de Rota (Simulado até a inserção da API Key)
                    st.markdown(f"""
                    <div class="card-elite">
                        <span style="float:right;">⭐ {p[3]}</span>
                        <h3>{p[0]}</h3>
                        <p><b>{cat_sugerida}</b> | {p[2]}</p>
                        <p><i>"{p[4]}"</i></p>
                        <p style="color: #2E4A7D; font-weight: bold;">📍 Disponível para atendimento em {cidade_busca}</p>
                        <a href="https://wa.me/{p[1]}" target="_blank" style="background:#25D366; color:white; padding:10px 25px; border-radius:10px; text-decoration:none; font-weight:bold; display:inline-block;">Chamar no WhatsApp</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"Ainda não temos especialistas verificados em {cidade_busca}. Nossa rede está expandindo!")
        else:
            st.error("Preencha a cidade e descreva o caso.")

# MAESTRO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
