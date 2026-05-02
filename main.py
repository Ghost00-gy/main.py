import streamlit as st
import os, sqlite3, pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime

# =========================================================
# 1. DESIGN SYSTEM & ACESSIBILIDADE (Identidade Home Doctor)
# =========================================================
st.set_page_config(page_title="HomeCare Connect | Gestão de Elite", layout="wide", page_icon="🏥")

def aplicar_estilo():
    st.markdown("""
        <style>
        /* Paleta Institucional: Azul Marinho, Branco, Cinza */
        :root {
            --primary: #003366; /* Azul Home Doctor */
            --secondary: #00A3AD; /* Verde Água Hospitalar */
            --bg: #F4F7F9;
        }
        
        .main { background-color: var(--bg); }
        
        h1, h2, h3 { color: var(--primary); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        /* Card de Especialista Estilo Prontuário */
        .card-hospitalar {
            background: white; border-radius: 12px; padding: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 15px solid var(--primary);
            margin-bottom: 25px;
        }
        
        .stButton>button {
            border-radius: 8px; height: 3.5em; font-weight: 600;
            background-color: var(--primary); color: white;
            transition: all 0.3s ease; border: none;
        }
        
        .stButton>button:hover {
            background-color: var(--secondary); transform: translateY(-2px);
        }
        
        /* Acessibilidade para idosos: Inputs maiores */
        input, select, textarea { font-size: 1.2rem !important; }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 2. MOTOR DE DADOS & INTELIGÊNCIA
# =========================================================
def init_db():
    conn = sqlite3.connect('homecare_elite.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, lat REAL, lon REAL, conselho TEXT, bio TEXT, 
                       rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 1)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS conexoes 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, paciente_cidade TEXT, prof_id INTEGER)''')
    conn.commit(); conn.close()

@st.cache_data(ttl=3600)
def geolocalizar(cidade, uf):
    try:
        geolocator = Nominatim(user_agent="homecare_connect_br")
        location = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        return (location.latitude, location.longitude) if location else (None, None)
    except: return (None, None)

# =========================================================
# 3. MÓDULOS DE PÁGINA (ISOLADOS)
# =========================================================

def pagina_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100) # Ícone Saúde
        st.title("HomeCare Connect")
        st.subheader("Especialistas em Atenção Domiciliar: 30 Anos de Confiança")
        st.write("Conectamos pacientes a uma rede de elite monitorada e verificada em tempo real.")
        
        st.markdown("### O que você deseja hoje?")
        if st.button("🚀 INICIAR TRIAGEM INTERATIVA", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
            
        c1, c2 = st.columns(2)
        c1.button("👨‍⚕️ Cadastro de Profissional", on_click=lambda: st.session_state.update({"pagina": "cadastro"}), use_container_width=True)
        c2.button("📊 Painel de Gestão", on_click=lambda: st.session_state.update({"pagina": "admin"}), use_container_width=True)

    with col2:
        st.image("https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&q=80&w=800", caption="Cuidado Humano e Profissional")

def pagina_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Protocolo de Triagem Domiciliar")
    st.info("Siga os passos abaixo para localizarmos a melhor equipe para você.")
    
    # Passo 1: Localização do Paciente
    with st.expander("📍 PASSO 1: Localização do Atendimento", expanded=True):
        c1, c2 = st.columns(2)
        uf_p = c1.selectbox("UF", ["SP", "RJ", "MG", "PR", "SC", "RS", "BA"])
        cidade_p = c2.text_input("Cidade de Residência", placeholder="Ex: Tatuí")
        
    # Passo 2: Necessidade Clínica
    with st.expander("🩹 PASSO 2: Necessidade do Paciente", expanded=True):
        necessidade = st.radio("Selecione a complexidade:", 
                               ["Atenção Básica (Curativos/Medicação)", 
                                "Reabilitação (Fisioterapia/Fono)", 
                                "Monitoramento 24h (Técnico em Enfermagem)",
                                "Consulta Médica Domiciliar"])
        relato = st.text_area("Descreva brevemente o quadro clínico:")

    if st.button("BUSCAR ESPECIALISTAS DISPONÍVEIS", type="primary", use_container_width=True):
        if not cidade_p:
            st.error("Por favor, informe a cidade.")
            return

        lat_p, lon_p = geolocalizar(cidade_p, uf_p)
        
        if lat_p:
            conn = sqlite3.connect('homecare_elite.db')
            df = pd.read_sql_query("SELECT * FROM profissionais WHERE verificado=1 AND uf=? AND cidade LIKE ?", 
                                   conn, params=(uf_p, f"%{cidade_p}%"))
            conn.close()

            if not df.empty:
                st.success(f"Encontramos {len(df)} especialistas verificados em {cidade_p}")
                
                # Mapa Integrado
                m = folium.Map(location=[lat_p, lon_p], zoom_start=13)
                folium.Marker([lat_p, lon_p], icon=folium.Icon(color='red', icon='home'), tooltip="Sua Localização").add_to(m)
                
                for _, p in df.iterrows():
                    dist = round(geodesic((lat_p, lon_p), (p['lat'], p['lon'])).km, 1)
                    folium.Marker([p['lat'], p['lon']], icon=folium.Icon(color='blue', icon='user-md', prefix='fa'), tooltip=p['nome']).add_to(m)
                    
                    # CARD ESTILO HOSPITALAR
                    st.markdown(f"""
                        <div class="card-hospitalar">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h2 style="margin:0;">{p['nome']}</h2>
                                <span style="background: #E8F0FE; color: #003366; padding: 8px 15px; border-radius: 5px; font-weight: bold; border: 1px solid #003366;">PROFISSIONAL VERIFICADO</span>
                            </div>
                            <hr>
                            <p style="font-size: 1.2em;"><b>Especialidade:</b> {p['categoria']} | <b>Conselho:</b> {p['conselho']}</p>
                            <p>📍 Localizado a <b>{dist} km</b> da sua residência.</p>
                            <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 15px 0;">
                                <i>"{p['bio']}"</i>
                            </div>
                            <a href="https://wa.me/{p['contato']}" target="_blank" 
                               style="background:#25D366; color:white; padding:15px; border-radius:8px; text-decoration:none; font-weight:bold; display:block; text-align:center;">
                               SOLICITAR CONTATO VIA WHATSAPP
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                
                st_folium(m, width=1300, height=400)
            else:
                st.warning("Nossa rede está em expansão. Tente uma cidade próxima ou entre em contato com nossa central.")

def pagina_cadastro():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("👨‍⚕️ Credenciamento de Elite")
    st.write("Seja parte de uma rede com 30 anos de expertise em atenção domiciliar.")
    
    with st.form("cadastro_profissional"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        cat = c1.selectbox("Área de Atuação", ["Médico", "Enfermeiro", "Fisioterapeuta", "Técnico", "Psicólogo"])
        uf = c2.selectbox("UF de Atuação", ["SP", "RJ", "MG", "PR", "SC", "RS"])
        cidade = c2.text_input("Cidade Base")
        whats = st.text_input("WhatsApp para Conexão")
        conselho = st.text_input("Nº do Registro Profissional (Ex: CRM-SP 12345)")
        bio = st.text_area("Resumo da Experiência")
        
        if st.form_submit_button("SUBMETER PARA CURADORIA"):
            lat, lon = geolocalizar(cidade, uf)
            if lat and nome:
                conn = sqlite3.connect('homecare_elite.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, contato, uf, cidade, lat, lon, conselho, bio) VALUES (?,?,?,?,?,?,?,?,?)",
                             (nome, cat, whats, uf, cidade, lat, lon, conselho, bio))
                conn.commit(); conn.close()
                st.success("Seus dados foram enviados. Nossa equipe de curadoria entrará em contato em breve.")
            else:
                st.error("Erro ao validar localização ou nome. Tente novamente.")

# =========================================================
# 4. MAESTRO DE NAVEGAÇÃO (GARANTE QUE NADA SUMA)
# =========================================================

def main():
    aplicar_estilo()
    init_db()
    
    if 'pagina' not in st.session_state:
        st.session_state.pagina = "home"
    
    if st.session_state.pagina == "home":
        pagina_home()
    elif st.session_state.pagina == "triagem":
        pagina_triagem()
    elif st.session_state.pagina == "cadastro":
        pagina_cadastro()
    elif st.session_state.pagina == "admin":
        st.title("Painel de Gestão Nacional")
        st.write("Visualização de métricas e aprovações em desenvolvimento.")
        st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))

if __name__ == "__main__":
    main()
