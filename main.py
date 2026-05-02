import streamlit as st
import os, sqlite3, pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
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

# 2. MOTOR DE DADOS NACIONAL (v5)
def init_db():
    conn = sqlite3.connect('homecare_nacional.db')
    cursor = conn.cursor()
    # Tabela com suporte a Mapas (lat/lon) e Rating
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, lat REAL, lon REAL,
                       conselho TEXT, bio TEXT, rating REAL DEFAULT 5.0, 
                       verificado INTEGER DEFAULT 0)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       termo TEXT, uf TEXT, cidade TEXT, data TEXT, categoria_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. FUNÇÃO DE GEOLOCALIZAÇÃO (Custo Zero)
def obter_coordenadas(cidade, uf):
    try:
        # Nominatim é o serviço gratuito do OpenStreetMap
        geolocator = Nominatim(user_agent="homecare_connect_v5")
        location = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        if location:
            return location.latitude, location.longitude
        return -23.5505, -46.6333  # Padrão SP caso não encontre
    except:
        return -23.5505, -46.6333

# 4. COMPONENTES DE INTERFACE

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=380)
        st.title("Conexão Saúde em Todo o Brasil")
        st.write("A elite dos profissionais de saúde domiciliar com inteligência geográfica.")
        
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
            uf = st.selectbox("Estado (UF)", ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "CE", "PE", "DF"])
            cidade = st.text_input("Cidade")
        with c2:
            whatsapp = st.text_input("WhatsApp (com DDD)")
            conselho = st.text_input("Registro Profissional (Ex: CRM-SP 12345)")
            bio = st.text_area("Breve Bio")
            uploaded_file = st.file_uploader("Documento (PDF)", type=["pdf"])
        
        concordo = st.checkbox("Aceito os termos da LGPD.")

        if st.form_submit_button("Submeter"):
            if nome and cidade and uploaded_file and concordo:
                lat, lon = obter_coordenadas(cidade, uf)
                
                doc_path = f"docs/{whatsapp}_{uploaded_file.name}"
                os.makedirs("docs", exist_ok=True)
                with open(doc_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                conn = sqlite3.connect('homecare_nacional.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, uf, cidade, lat, lon, contato, conselho, bio, doc_path) VALUES (?,?,?,?,?,?,?,?,?,?)",
                             (nome, cat, uf, cidade, lat, lon, whatsapp, conselho, bio, doc_path))
                conn.commit(); conn.close()
                st.success(f"Cadastro para {cidade} registrado geograficamente!")
            else: st.error("Preencha todos os campos.")

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Mapa de Especialistas")
    
    c1, c2 = st.columns(2)
    uf_busca = c1.selectbox("Seu Estado", ["SP", "RJ", "MG", "RS", "PR"])
    cidade_busca = c2.text_input("Sua Cidade")
    
    relato = st.text_area("Descreva o caso clínico:").lower()
    
    if st.button("Mapear Profissionais Próximos", type="primary"):
        BASE = {"coracao": "Enfermeiro", "femur": "Fisioterapeuta", "idoso": "Tecnico"}
        cat_sugerida = next((BASE[k] for k in BASE if k in relato), "Enfermeiro")
        
        conn = sqlite3.connect('homecare_nacional.db')
        query = "SELECT nome, lat, lon, contato, rating, bio FROM profissionais WHERE verificado=1 AND categoria=? AND uf=? AND cidade LIKE ?"
        df = pd.read_sql_query(query, conn, params=(cat_sugerida, uf_busca, f"%{cidade_busca}%"))
        conn.close()

        if not df.empty:
            st.success(f"Encontramos {len(df)} especialistas em {cidade_busca}!")
            
            # CRIAÇÃO DO MAPA INTERATIVO (Folium)
            m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=12)
            for _, p in df.iterrows():
                folium.Marker(
                    [p['lat'], p['lon']],
                    popup=f"<b>{p['nome']}</b><br>Rating: {p['rating']}",
                    tooltip=p['nome'],
                    icon=folium.Icon(color='blue', icon='user-md', prefix='fa')
                ).add_to(m)
            
            st_folium(m, width=1200, height=450)

            # LISTA DE ELITE
            for _, p in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #2E4A7D; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
                        <h4>{p['nome']} <span style="font-size: 14px; color: gold;">{'★' * int(p['rating'])}</span></h4>
                        <p>{p['bio']}</p>
                        <a href="https://wa.me/{p['contato']}" target="_blank" style="color: green; font-weight: bold; text-decoration: none;">💬 Iniciar Atendimento</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum profissional verificado nesta região ainda.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    if not st.session_state.autenticado:
        senha = st.text_input("Senha Master:", type="password")
        if st.button("Entrar"):
            if senha == "tatuicare2026": st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 BI Nacional")
    conn = sqlite3.connect('homecare_nacional.db')
    pendentes = conn.execute("SELECT id, nome, cidade, uf FROM profissionais WHERE verificado=0").fetchall()
    
    st.subheader(f"Pendentes ({len(pendentes)})")
    for p in pendentes:
        if st.button(f"Aprovar {p[1]} ({p[2]})"):
            conn.execute("UPDATE profissionais SET verificado=1 WHERE id=?", (p[0],))
            conn.commit(); st.rerun()
    conn.close()

# MAESTRO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "admin": mostrar_admin()
