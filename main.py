import streamlit as st
import google.generativeai as genai
import sqlite3
import json

# --- CONFIGURAÇÃO DA IA ---
# Aqui usamos st.secrets para proteger sua chave no GitHub público
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Erro: A chave API não foi encontrada nos 'Secrets' do Streamlit.")

model = genai.GenerativeModel('gemini-pro')

# --- FUNÇÕES DE BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('homecare.db')
    cursor = conn.cursor()
    # Criamos a tabela de profissionais se ela não existir
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, 
                       categoria TEXT, 
                       contato TEXT, 
                       cidade TEXT)''')
    conn.commit()
    conn.close()

# --- FUNÇÃO DE TRIAGEM COM IA ---
def realizar_triagem(texto):
    prompt = f"""
    Aja como um especialista em triagem hospitalar e home care especializado em idosos. 
    Analise o seguinte pedido de ajuda: "{texto}"
    Retorne APENAS um JSON com as chaves:
    "categoria": (Escolha uma: Medico, Enfermeiro, Tecnico, Fisioterapeuta ou Psicologo),
    "urgencia": (Baixa, Media ou Alta),
    "conselho": (Um conselho curto e humano para a família).
    """
    try:
        response = model.generate_content(prompt)
        # Limpamos a resposta para garantir que apenas o JSON seja lido
        json_clean = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_clean)
    except Exception as e:
        return {
            "categoria": "Tecnico", 
            "urgencia": "Media", 
            "conselho": "Houve um erro na análise, mas recomendamos buscar um profissional técnico para avaliação."
        }

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---
init_db()
st.set_page_config(page_title="HomeCare Inteligente", page_icon="🏠")

st.title("🏥 Sistema Home Care com IA")
st.sidebar.header("Menu de Navegação")

menu = ["Solicitar Atendimento", "Cadastro de Profissional", "Painel de Gestão"]
escolha = st.sidebar.selectbox("Ir para:", menu)

# --- ABA 1: SOLICITAR ATENDIMENTO ---
if escolha == "Solicitar Atendimento":
    st.header("🩺 Triagem e Encaminhamento")
    st.write("Descreva o que o paciente está sentindo ou qual a necessidade de cuidado.")
    
    relato = st.text_area("Ex: Meu avô tem 80 anos e precisa de ajuda para medicação e banho.")
    
    if st.button("Analisar Caso"):
        if relato:
            with st.spinner('A IA está analisando a melhor opção...'):
                res = realizar_triagem(relato)
                
                st.subheader(f"Prioridade: {res['urgencia']}")
                st.info(f"💡 **Dica da IA:** {res['conselho']}")
                
                # Busca profissionais no banco de dados local
                conn = sqlite3.connect('homecare.db')
                cursor = conn.cursor()
                cursor.execute("SELECT nome, contato, cidade FROM profissionais WHERE categoria=?", (res['categoria'],))
                vagas = cursor.fetchall()
                conn.close()
                
                if vagas:
                    st.success(f"Encontramos {len(vagas)} profissionais de {res['categoria']} disponíveis:")
                    for p in vagas:
                        # Link direto para o WhatsApp do profissional
                        link_whatsapp = f"https://wa.me/{p[1]}"
                        st.write(f"👤 **{p[0]}** ({p[2]}) - [Chamar no WhatsApp]({link_whatsapp})")
                else:
                    st.warning(f"No momento, não temos {res['categoria']} cadastrados no sistema.")
        else:
            st.error("Por favor, descreva a situação para a triagem.")

# --- ABA 2: CADASTRO DE PROFISSIONAL ---
elif escolha == "Cadastro de Profissional":
    st.header("📋 Cadastre-se como Colaborador")
    st.write("Junte-se à nossa rede para receber chamados de pacientes.")
    
    with st.form("cadastro_form"):
        nome_completo = st.text_input("Nome Completo")
        categoria_saude = st.selectbox("Sua Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
        whatsapp_contato = st.text_input("WhatsApp (Ex: 5511999999999)")
        cidade_atendimento = st.text_input("Cidade/Região")
        
        if st.form_submit_button("Finalizar Cadastro"):
            if nome_completo and whatsapp_contato:
                conn = sqlite3.connect('homecare.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO profissionais (nome, categoria, contato, cidade) VALUES (?,?,?,?)", 
                               (nome_completo, categoria_saude, whatsapp_contato, cidade_atendimento))
                conn.commit()
                conn.close()
                st.success("Cadastro realizado com sucesso! Você já está disponível para triagens.")
            else:
                st.error("Preencha todos os campos obrigatórios.")

# --- ABA 3: PAINEL DE GESTÃO (PARA VOCÊ) ---
elif escolha == "Painel de Gestão":
    st.header("📊 Administração da Rede")
    st.write("Aqui você visualiza todos os profissionais cadastrados no seu negócio.")
    
    conn = sqlite3.connect('homecare.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, categoria, cidade FROM profissionais")
    todos = cursor.fetchall()
    conn.close()
    
    if todos:
        st.table(todos)
    else:
        st.info("Ainda não existem profissionais cadastrados.")
