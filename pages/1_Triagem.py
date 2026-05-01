import streamlit as st
st.set_page_config(page_title="HomeCare Connect | Triagem", page_icon="🩺")
import google.generativeai as genai
import sqlite3
import json

# Configuração da página
st.set_page_config(page_title="HomeCare Connect | Triagem", layout="wide")

# Configuração da IA (Usando os Secrets configurados anteriormente)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# CSS para Cards Premium
st.markdown("""
    <style>
    .pro-card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 8px solid #1A3A5A;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .pro-card:hover {
        transform: translateY(-5px);
    }
    .category-badge {
        background-color: #E2E8F0;
        color: #1A3A5A;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🩺 Triagem Inteligente")
st.write("Descreva detalhadamente a necessidade para que nossa IA conecte você ao especialista ideal.")

# Área de entrada do paciente
relato = st.text_area("Descrição do Caso", placeholder="Ex: Minha mãe tem 85 anos, dificuldade de locomoção e precisa de exercícios fisioterapêuticos.")

if st.button("Analisar e Localizar Profissionais"):
    if relato:
        with st.spinner("Analisando quadro clínico..."):
            # Lógica da IA
            prompt = f"Analise: '{relato}'. Retorne JSON: 'categoria' (Medico, Enfermeiro, Tecnico, Fisioterapeuta, Psicologo), 'urgencia' (Baixa, Media, Alta), 'resumo'."
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('
```', '').strip())
            
            st.subheader(f"Recomendação: {data['categoria']}")
            st.info(f"**Análise da IA:** {data['resumo']} (Urgência: {data['urgencia']})")
            
            # Busca no banco de dados
            conn = sqlite3.connect('homecare_v2.db')
            cursor = conn.cursor()
            cursor.execute("SELECT nome, categoria, contato, cidade FROM profissionais WHERE categoria=?", (data['categoria'],))
            profissionais = cursor.fetchall()
            conn.close()
            
            if profissionais:
                st.write("### Especialistas Disponíveis Próximos a Você")
                for p in profissionais:
                    # Renderização do Card Premium via HTML/CSS
                    st.markdown(f"""
                    <div class="pro-card">
                        <span class="category-badge">{p[1]}</span>
                        <h3 style="margin-top:10px;">{p[0]}</h3>
                        <p>📍 Atendimento em: <b>{p[3]}</b></p>
                        <a href="https://wa.me/{p[2]}" class="whatsapp-btn">Conectar via WhatsApp</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"A IA recomendou {data['categoria']}, mas ainda não temos profissionais nesta categoria cadastrados em sua região.")
    else:
        st.error("Por favor, descreva a situação para continuar.")
