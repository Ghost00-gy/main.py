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
    with st.sidebar:
        if st.button("⬅️ Voltar ao Início"):
            st.session_state.pagina = "home"
            st.rerun()
    
    st.title("🩺 Triagem Inteligente")
    st.write("Nossa IA analisará o caso para conectar você ao profissional verificado mais adequado.")

    relato = st.text_area("Descreva o quadro do paciente:", height=150, 
                          placeholder="Ex: Idoso com dificuldade de locomoção após cirurgia no fêmur...")

    if st.button("Analisar e Localizar Especialistas"):
        if relato:
            with st.spinner("IA avaliando necessidades clínicas..."):
                try:
                    # 1. Configuração da IA Gemini
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-pro')
                    
                    # Prompt ultra-específico para evitar lixo no JSON
                    prompt = f"""
                    Analise este relato de saúde: '{relato}'
                    Responda RIGOROSAMENTE apenas um objeto JSON (sem markdown, sem texto antes ou depois):
                    {{
                        "categoria": "Medico" ou "Enfermeiro" ou "Tecnico" ou "Fisioterapeuta" ou "Psicologo",
                        "urgencia": "Baixa" ou "Media" ou "Alta",
                        "resumo": "Uma orientação curta."
                    }}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # 2. Limpeza Avançada de JSON
                    # Remove possíveis marcações de markdown ```json que a IA costuma colocar
                    raw_res = response.text.strip()
                    if raw_res.startswith("```"):
                        raw_res = raw_res.split("```")[1]
                        if raw_res.startswith("json"):
                            raw_res = raw_res[4:]
                    
                    res = json.loads(raw_res.strip())
                    
                    st.divider()
                    st.subheader(f"📍 Recomendação: {res['categoria']}")
                    st.info(f"**Análise da IA:** {res['resumo']}")

                    # 3. Busca no Banco de Dados - APENAS VERIFICADOS
                    conn = sqlite3.connect('homecare_v2.db')
                    cursor = conn.cursor()
                    
                    # Importante: Categoria deve bater exatamente com o que a IA mandou
                    cursor.execute("""SELECT nome, categoria, contato, cidade, conselho, bio, experiencia 
                                      FROM profissionais 
                                      WHERE categoria=? AND verificado=1""", (res['categoria'],))
                    pros = cursor.fetchall()
                    conn.close()

                    if pros:
                        st.write(f"### Encontramos {len(pros)} especialista(s) verificado(s):")
                        for p in pros:
                            with st.container():
                                st.markdown(f"""
                                <div style="background: white; padding: 25px; border-radius: 15px; border-left: 10px solid #1A3A5A; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
                                    <span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">✅ PROFISSIONAL VERIFICADO</span>
                                    <h2 style="margin: 10px 0 5px 0; color: #1A3A5A;">{p[0]}</h2>
                                    <p style="color: #666; font-weight: bold; margin-bottom: 15px;">{p[1]} | {p[4]} | 📍 {p[3]}</p>
                                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                        <p style="font-size: 14px; color: #444;"><b>Sobre:</b> {p[5]}</p>
                                        <p style="font-size: 14px; color: #444; margin-top: 5px;"><b>Experiência:</b> {p[6]}</p>
                                    </div>
                                    <a href="[https://wa.me/](https://wa.me/){p[2]}" target="_blank" 
                                       style="background: #25D366; color: white !important; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">
                                       Agendar via WhatsApp
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning(f"A IA recomendou um especialista em **{res['categoria']}**, mas você ainda não aprovou nenhum profissional desta categoria no Painel de Controle.")
                
                except Exception as e:
                    # AGORA O ERRO VAI APARECER AQUI PARA SABERMOS O QUE É
                    st.error(f"Erro técnico: {str(e)}")
                    st.write("Dica: Verifique se o formato do seu banco de dados está correto e se os profissionais estão marcados como 'Aprovado'.")
        else:
            st.warning("Por favor, descreva o caso.")

# NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
