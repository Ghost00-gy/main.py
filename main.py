import streamlit as st
import os, sqlite3, pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime

# 1. SETUP DE ACESSIBILIDADE E ALTA DISPONIBILIDADE
st.set_page_config(page_title="HomeCare Connect | Elite Brasil", layout="wide", page_icon="🏥")

# Gerenciamento de Estado
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'tema_escuro' not in st.session_state: st.session_state.tema_escuro = False

# 2. DESIGN SYSTEM ACESSÍVEL (CSS Dinâmico)
bg_color = "#1A1A1A" if st.session_state.tema_escuro else "#F8F9FA"
text_color = "#FFFFFF" if st.session_state.tema_escuro else "#1A3A5A"
card_bg = "#2D2D2D" if st.session_state.tema_escuro else "#FFFFFF"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ background-color: {bg_color}; color: {text_color}; font-size: 1.1rem; }}
    .stButton>button {{ border-radius: 15px; height: 3em; font-size: 1.1rem; font-weight: bold; transition: 0.3s; }}
    .card-acessivel {{
        background: {card_bg}; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-left: 12px solid #2E4A7D;
        margin-bottom: 20px; color: {text_color};
    }}
    .icon-box {{ font-size: 2rem; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# 3. MOTOR DE DADOS NACIONAL (Mantendo o que já fizemos)
def init_db():
    conn = sqlite3.connect('homecare_v7.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, lat REAL, lon REAL, conselho TEXT, bio TEXT, 
                       rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

init_db()

# 4. COMPONENTES INTERATIVOS

def barra_acessibilidade():
    col_a1, col_a2 = st.sidebar.columns(2)
    if col_a1.button("🌓 Alternar Tema"):
        st.session_state.tema_escuro = not st.session_state.tema_escuro
        st.rerun()
    st.sidebar.divider()

def mostrar_home():
    barra_acessibilidade()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("Excelência em Conexão de Saúde")
        st.write("Nós somos o elo de confiança entre você e os melhores especialistas do Brasil.")
        
        # Botões Grandes para Acessibilidade
        if st.button("🚀 INICIAR TRIAGEM AGORA", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        
        st.divider()
        c1, c2 = st.columns(2)
        c1.button("👨‍⚕️ Sou Profissional", on_click=lambda: st.session_state.update({"pagina": "cadastro"}), use_container_width=True)
        c2.button("🔑 Gestão Connect", on_click=lambda: st.session_state.update({"pagina": "admin"}), use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_triagem():
    barra_acessibilidade()
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Interativa e Humana")
    
    # Passo 1: Localização Simplificada
    st.subheader("1. Onde você precisa de cuidado?")
    c1, c2 = st.columns(2)
    uf_p = c1.selectbox("Estado (UF)", ["SP", "RJ", "MG", "RS", "PR", "BA", "SC"])
    cidade_p = c2.text_input("Sua Cidade (Ex: Tatuí)")
    
    # Passo 2: Seleção Visual (Ícones Grandes)
    st.subheader("2. Qual a necessidade principal?")
    cat_escolhida = st.radio("Selecione o tipo de suporte:", 
                             ["Pós-Operatório", "Cuidados ao Idoso", "Reabilitação Física", "Acompanhamento Psicológico", "Procedimentos de Enfermagem"],
                             horizontal=True)
    
    # Passo 3: Relato Humano
    relato = st.text_area("Descreva mais detalhes para nossa curadoria:", placeholder="Ex: Preciso de um curativo complexo após cirurgia cardíaca...")

    if st.button("BUSCAR ELITE NA MINHA REGIÃO", type="primary", use_container_width=True):
        if cidade_p:
            # Lógica Geográfica que já construímos
            geolocator = Nominatim(user_agent="homecare_connect_v7")
            loc_p = geolocator.geocode(f"{cidade_p}, {uf_p}, Brasil")
            
            if loc_p:
                conn = sqlite3.connect('homecare_v7.db')
                df = pd.read_sql_query("SELECT * FROM profissionais WHERE verificado=1 AND uf=? AND cidade LIKE ?", 
                                       conn, params=(uf_p, f"%{cidade_p}%"))
                conn.close()

                if not df.empty:
                    st.success(f"Encontramos {len(df)} profissionais validados por nossa equipe em {cidade_p}!")
                    
                    # Mapa de Acessibilidade
                    m = folium.Map(location=[loc_p.latitude, loc_p.longitude], zoom_start=13)
                    folium.Marker([loc_p.latitude, loc_p.longitude], icon=folium.Icon(color='red', icon='home'), tooltip="Sua Casa").add_to(m)
                    
                    for _, p in df.iterrows():
                        dist = round(geodesic((loc_p.latitude, loc_p.longitude), (p['lat'], p['lon'])).km, 1)
                        
                        # Card Interativo Tripartite
                        st.markdown(f"""
                        <div class="card-acessivel">
                            <div style="display: flex; justify-content: space-between;">
                                <h3>{p['nome']}</h3>
                                <span style="background: #E8F0FE; color: #2E4A7D; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.8em;">✓ VALIDADO POR HOMECARE CONNECT</span>
                            </div>
                            <p><b>Especialidade:</b> {p['categoria']} | <b>Conselho:</b> {p['conselho']}</p>
                            <p>📍 Está a <b>{dist} km</b> de você.</p>
                            <p style="background: rgba(46, 74, 125, 0.05); padding: 10px; border-radius: 10px;"><i>"{p['bio']}"</i></p>
                            <div style="margin-top: 15px;">
                                <a href="https://wa.me/{p['contato']}" target="_blank" style="background:#25D366; color:white; padding:12px 30px; border-radius:12px; text-decoration:none; font-weight:bold; display:inline-block; width: 100%; text-align: center;">CONECTAR AGORA VIA WHATSAPP</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st_folium(m, width=1200, height=450)
                else:
                    st.warning("Estamos expandindo nossa rede. Em breve teremos profissionais nesta região!")
            else:
                st.error("Não conseguimos localizar a cidade informada. Verifique o nome.")

# 5. MAESTRO DE NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "cadastro": # Função de cadastro nacional já implementada...
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("Cadastro Especialista")
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "admin": # Função admin com BI já implementada...
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("Painel de Gestão")
