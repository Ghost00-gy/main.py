import streamlit as st
import os, json, sqlite3
from PIL import Image

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="HomeCare Connect", layout="wide", page_icon="🏥")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# 2. BANCO DE DADOS - INICIALIZAÇÃO
def init_db():
    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, cidade TEXT,
                       conselho TEXT, bio TEXT, experiencia TEXT, 
                       verificado INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# 3. ESTILIZAÇÃO CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-admin {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 4px solid #1A3A5A;
        margin-bottom: 10px;
    }
    .card-resultado {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 10px solid #1A3A5A; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES DE TELA

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=250)
        st.markdown('# Cuidado e conexão em casa.')
        st.write("Conectamos famílias aos melhores profissionais com segurança e curadoria local.")
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
            conselho = st.text_input("Registro Profissional (Ex: COREN, CRM)")
            whatsapp = st.text_input("WhatsApp com DDD")
        with c2:
            cidade = st.text_input("Cidade/Estado")
            bio = st.text_area("Resumo Profissional")
            exp = st.text_area("Experiência de Atuação")
        if st.form_submit_button("Finalizar Cadastro"):
            if nome and whatsapp:
                conn = sqlite3.connect('homecare_v2.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO profissionais (nome, categoria, contato, cidade, conselho, bio, experiencia) VALUES (?,?,?,?,?,?,?)", 
                               (nome, cat, whatsapp, cidade, conselho, bio, exp))
                conn.commit(); conn.close()
                st.success("Cadastro realizado! Aguarde aprovação.")
            else: st.error("Preencha os campos obrigatórios.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📊 Painel Administrativo")

    # Sistema de Login Simples
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        senha = st.text_input("Digite a senha de administrador:", type="password")
        if st.button("Acessar Painel"):
            if senha == "tatuicare2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta. Acesso negado.")
        return # Para a execução aqui se não estiver autenticado

    # Conteúdo do Painel (Só aparece se autenticado)
    if st.sidebar.button("🔒 Sair do Painel"):
        st.session_state.autenticado = False
        st.rerun()

    conn = sqlite3.connect('homecare_v2.db')
    cursor = conn.cursor()
    
    # Métricas Rápidas
    total = cursor.execute("SELECT COUNT(*) FROM profissionais").fetchone()[0]
    pendentes = cursor.execute("SELECT COUNT(*) FROM profissionais WHERE verificado = 0").fetchone()[0]
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Total de Cadastros", total)
    col_m2.metric("Aguardando Aprovação", pendentes)
    
    st.markdown("---")
    
    pros = cursor.execute("SELECT id, nome, categoria, verificado, conselho FROM profissionais").fetchall()
    
    for p in pros:
        status = "✅ VERIFICADO" if p[3] == 1 else "⏳ PENDENTE"
        with st.container():
            st.markdown(f"""
            <div class="card-admin">
                <span style="float:right; font-weight:bold; color:{'#28a745' if p[3]==1 else '#ffc107'};">{status}</span>
                <b>{p[1]}</b><br>
                <small>{p[2]} | {p[4]}</small>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if p[3] == 0:
                    if st.button(f"Aprovar {p[1]}", key=f"ap_{p[0]}"):
                        cursor.execute("UPDATE profissionais SET verificado = 1 WHERE id = ?", (p[0],))
                        conn.commit(); st.rerun()
            with c2:
                if st.button(f"🗑️ Remover Cadastro", key=f"ex_{p[0]}"):
                    cursor.execute("DELETE FROM profissionais WHERE id = ?", (p[0],))
                    conn.commit(); st.rerun()
    conn.close()
    
def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Inteligente")
    
    # Base Local de Conhecimento
    BASE_CUIDADOS = {
        "coracao": {"cat": "Enfermeiro", "msg": "Cuidados pós-operatórios cardíacos exigem controle rigoroso de medicação e curativos."},
        "cardiaco": {"cat": "Enfermeiro", "msg": "Cuidados pós-operatórios cardíacos exigem controle rigoroso de medicação e curativos."},
        "femur": {"cat": "Fisioterapeuta", "msg": "Recuperação de cirurgia de fêmur foca em mobilidade e prevenção de atrofia."},
        "fratura": {"cat": "Fisioterapeuta", "msg": "Recuperação de cirurgia de fêmur foca em mobilidade e prevenção de atrofia."},
        "idoso": {"cat": "Tecnico", "msg": "Auxílio em atividades diárias, higiene e alimentação monitorada."},
        "ferida": {"cat": "Enfermeiro", "msg": "Tratamento e limpeza de feridas devem ser feitos com técnica estéril."},
        "curativo": {"cat": "Enfermeiro", "msg": "Tratamento e limpeza de feridas devem ser feitos com técnica estéril."},
        "reabilitacao": {"cat": "Fisioterapeuta", "msg": "Fisioterapia domiciliar para ganho de força e equilíbrio."},
        "medicamento": {"cat": "Tecnico", "msg": "Acompanhamento para administração correta de horários e dosagens."}
    }

    relato = st.text_area("Descreva a necessidade do paciente (ex: coração, idoso, curativo):", height=150).lower()
    
    if st.button("Localizar Especialistas"):
        if relato:
            encontrou_chave = False
            for chave, dados in BASE_CUIDADOS.items():
                if chave in relato:
                    st.success(f"📍 Recomendação para: {dados['cat']}")
                    st.info(f"💡 Dica Profissional: {dados['msg']}")
                    
                   # Dentro da função mostrar_triagem, no loop de profissionais encontrados:

if encontrados:
    st.write(f"### Profissionais Verificados em Tatuí:")
    for prof in encontrados:
        # Criamos a mensagem automática (codificada para URL)
        mensagem_venda = f"Olá {prof[0]}, vi seu perfil verificado no HomeCare Connect e gostaria de agendar uma consulta."
        mensagem_url = mensagem_venda.replace(" ", "%20")
        
        st.markdown(f"""
        <div class="card-resultado">
            <h3>{prof[0]}</h3>
            <p><b>{dados['cat']}</b> | {prof[2]}</p>
            <p style="font-size: 14px; color: #555;">{prof[3]}</p>
            <a href="https://wa.me/{prof[1]}?text={mensagem_url}" target="_blank" 
               style="background:#25D366; color:white; padding:12px 25px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block;">
               Chamar no WhatsApp
            </a>
        </div>
        """, unsafe_allow_html=True)
                    
                    if encontrados:
                        st.write(f"### Profissionais Verificados em Tatuí:")
                        for prof in encontrados:
                            st.markdown(f"""
                            <div class="card-resultado">
                                <h3>{prof[0]}</h3>
                                <p><b>{dados['cat']}</b> | {prof[2]}</p>
                                <p style="font-size: 14px; color: #555;">{prof[3]}</p>
                                <a href="https://wa.me/{prof[1]}" target="_blank" style="background:#25D366; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block;">Chamar no WhatsApp</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Ainda não temos {dados['cat']} verificados em nossa base.")
                    
                    encontrou_chave = True
                    break
            
            if not encontrou_chave:
                st.warning("Não identificamos uma categoria específica no seu relato. Tente usar termos como 'coração', 'idoso' ou 'curativo'.")
        else:
            st.warning("Por favor, descreva o caso.")

# 5. MAESTRO DE NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
