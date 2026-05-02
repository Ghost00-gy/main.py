import streamlit as st
import os, sqlite3, pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import plotly.express as px

# 1. SETUP DE ALTA DISPONIBILIDADE
st.set_page_config(page_title="HomeCare Connect | Elite Brasil", layout="wide", page_icon="🏥")

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# 2. MOTOR DE DADOS INTEGRADO
def init_db():
    conn = sqlite3.connect('homecare_nacional_v6.db')
    cursor = conn.cursor()
    # Profissionais
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, lat REAL, lon REAL, conselho TEXT, bio TEXT, 
                       rating REAL DEFAULT 5.0, total_votos INTEGER DEFAULT 0, verificado INTEGER DEFAULT 0)''')
    # Métricas e Heatmap
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, termo TEXT, uf TEXT, cidade TEXT, 
                       lat_busca REAL, lon_busca REAL, data TEXT)''')
    # Avaliações
    cursor.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, prof_id INTEGER, nota INTEGER, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. UTILITÁRIOS LOGÍSTICOS
@st.cache_data(ttl=3600)
def obter_coordenadas(cidade, uf):
    try:
        geolocator = Nominatim(user_agent="homecare_brazil_pro")
        location = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        return (location.latitude, location.longitude) if location else (None, None)
    except: return (None, None)

def calcular_distancia_km(ponto_a, ponto_b):
    if all(ponto_a) and all(ponto_b):
        return round(geodesic(ponto_a, ponto_b).km, 1)
    return "N/A"

# 4. COMPONENTES DE INTERFACE ISOLADOS

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("Conexão Saúde Elite Brasil")
        st.write("A maior rede de profissionais verificados com inteligência logística integrada.")
        if st.button("🚀 Iniciar Triagem Inteligente", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        st.divider()
        c_nav1, c_nav2 = st.columns(2)
        c_nav1.button("👨‍⚕️ Área do Profissional", on_click=lambda: st.session_state.update({"pagina": "cadastro"}), use_container_width=True)
        c_nav2.button("📊 Painel Estratégico", on_click=lambda: st.session_state.update({"pagina": "admin"}), use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Ingressar na Elite Nacional")
    with st.form("cadastro_elite"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        cat = c1.selectbox("Especialidade", ["Medico", "Enfermeiro", "Fisioterapeuta", "Psicologo"])
        uf = c2.selectbox("UF", ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "CE", "DF"])
        cidade = c2.text_input("Cidade")
        whatsapp = st.text_input("WhatsApp")
        bio = st.text_area("Bio Profissional")
        if st.form_submit_button("Enviar para Verificação"):
            lat, lon = obter_coordenadas(cidade, uf)
            conn = sqlite3.connect('homecare_nacional_v6.db')
            conn.execute("INSERT INTO profissionais (nome, categoria, contato, uf, cidade, lat, lon, bio) VALUES (?,?,?,?,?,?,?,?)",
                         (nome, cat, whatsapp, uf, cidade, lat, lon, bio))
            conn.commit(); conn.close()
            st.success("Dados enviados. Aguarde a verificação da curadoria.")

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Localização Real")
    
    col_loc1, col_loc2 = st.columns(2)
    uf_p = col_loc1.selectbox("Seu Estado", ["SP", "RJ", "MG", "PR", "SC", "RS"])
    cidade_p = col_loc2.text_input("Sua Cidade")
    relato = st.text_area("O que o paciente precisa?").lower()
    
    if st.button("Localizar Elite na Região", type="primary"):
        lat_p, lon_p = obter_coordenadas(cidade_p, uf_p)
        cat_sugerida = "Enfermeiro" # Simulação de IA simplificada
        
        conn = sqlite3.connect('homecare_nacional_v6.db')
        conn.execute("INSERT INTO metricas_triagem (termo, uf, cidade, lat_busca, lon_busca, data) VALUES (?,?,?,?,?,?)",
                     (relato, uf_p, cidade_p, lat_p, lon_p, datetime.now().strftime("%Y-%m-%d")))
        
        df = pd.read_sql_query("SELECT * FROM profissionais WHERE verificado=1 AND uf=? AND cidade LIKE ?", 
                               conn, params=(uf_p, f"%{cidade_p}%"))
        conn.close()

        if not df.empty:
            m = folium.Map(location=[lat_p, lon_p] if lat_p else [df['lat'].mean(), df['lon'].mean()], zoom_start=12)
            folium.Marker([lat_p, lon_p], icon=folium.Icon(color='red', icon='home')).add_to(m)
            
            for _, p in df.iterrows():
                dist = calcular_distancia_km((lat_p, lon_p), (p['lat'], p['lon']))
                folium.Marker([p['lat'], p['lon']], popup=f"{p['nome']} ({dist}km)", icon=folium.Icon(color='blue')).add_to(m)
                
                with st.container():
                    st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:15px; border-left:10px solid #2E4A7D; margin-bottom:10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <h3 style="margin:0;">{p['nome']} <span style="color:gold;">{'★' * int(p['rating'])}</span></h3>
                        <p>📍 <b>{dist} km</b> de distância de você em {p['cidade']}</p>
                        <p><i>{p['bio']}</i></p>
                        <a href="https://wa.me/{p['contato']}" style="background:#25D366; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">Chamar no WhatsApp</a>
                    </div>
                    """, unsafe_allow_html=True)
            st_folium(m, width=1200, height=400)
        else: st.warning("Buscando novos profissionais nesta região...")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    if not st.session_state.autenticado:
        if st.text_input("Chave Mestra", type="password") == "tatuicare2026": 
            st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 BI Nacional & Heatmap")
    conn = sqlite3.connect('homecare_nacional_v6.db')
    
    # Mapa de Calor de Demandas
    df_heat = pd.read_sql_query("SELECT lat_busca as lat, lon_busca as lon FROM metricas_triagem", conn)
    if not df_heat.empty:
        st.subheader("Concentração de Demandas (Onde investir em marketing)")
        fig = px.density_mapbox(df_heat, lat='lat', lon='lon', radius=20, center=dict(lat=-15, lon=-47), zoom=3, mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)

    # Curadoria Ágil
    pendentes = conn.execute("SELECT id, nome, cidade FROM profissionais WHERE verificado=0").fetchall()
    st.subheader(f"Curadoria Pendente ({len(pendentes)})")
    for p in pendentes:
        if st.button(f"✅ Aprovar {p[1]} ({p[2]})"):
            conn.execute("UPDATE profissionais SET verificado=1 WHERE id=?", (p[0],))
            conn.commit(); st.rerun()
    conn.close()

# 5. MAESTRO (Navegação Isolada)
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "admin": mostrar_admin()
