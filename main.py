import streamlit as st
import os, sqlite3, pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from datetime import datetime

# 1. CONFIGURAÇÕES DE ALTA DISPONIBILIDADE
st.set_page_config(page_title="HomeCare Connect | Brasil", layout="wide", page_icon="🏥")

# Inicialização de Estado de Navegação
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# 2. MOTOR DE DADOS NACIONAL
def init_db():
    conn = sqlite3.connect('homecare_nacional.db')
    cursor = conn.cursor()
    # Tabela com suporte a geolocalização
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, 
                       contato TEXT, uf TEXT, cidade TEXT, lat REAL, lon REAL,
                       conselho TEXT, bio TEXT, rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, termo TEXT, uf TEXT, cidade TEXT, 
                       lat_busca REAL, lon_busca REAL, data TEXT, categoria_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. GEOLOCALIZAÇÃO OPEN SOURCE
def obter_coordenadas(cidade, uf):
    try:
        geolocator = Nominatim(user_agent="homecare_connect_br")
        location = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        return (location.latitude, location.longitude) if location else (None, None)
    except:
        return (None, None)

# 4. PÁGINAS ISOLADAS

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=380)
        st.title("Conexão Saúde em Todo o Brasil")
        st.write("A elite dos profissionais de saúde com inteligência logística e geocodificação.")
        
        if st.button("🚀 Iniciar Triagem de Saúde", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        
        st.divider()
        c_nav1, c_nav2 = st.columns(2)
        c_nav1.button("👨‍⚕️ Cadastro Especialista", on_click=lambda: st.session_state.update({"pagina": "cadastro"}), use_container_width=True)
        c_nav2.button("📊 Gestão & Métricas", on_click=lambda: st.session_state.update({"pagina": "admin"}), use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Cadastro Nacional de Especialistas")
    with st.form("form_cadastro_v6", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            uf = st.selectbox("Estado (UF)", ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "CE", "PE", "DF"])
        with c2:
            cidade = st.text_input("Cidade de Atuação")
            whatsapp = st.text_input("WhatsApp (com DDD)")
            conselho = st.text_input("Registro Profissional (CRM/COREN/etc)")
        if st.form_submit_button("Finalizar Submissão"):
            if nome and cidade and whatsapp:
                lat, lon = obter_coordenadas(cidade, uf)
                conn = sqlite3.connect('homecare_nacional.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, uf, cidade, lat, lon, contato, conselho) VALUES (?,?,?,?,?,?,?,?)",
                             (nome, cat, uf, cidade, lat, lon, whatsapp, conselho))
                conn.commit(); conn.close()
                st.success(f"Cadastro de {nome} em {cidade} realizado com sucesso!")

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Localização de Paciente")
    
    with st.container():
        st.markdown("### 📍 Sua Localização")
        c1, c2 = st.columns(2)
        uf_paci = c1.selectbox("Seu Estado", ["SP", "RJ", "MG", "RS", "PR", "BA", "CE"])
        cidade_paci = c2.text_input("Sua Cidade")
        
    relato = st.text_area("Descreva a necessidade clínica:").lower()
    
    if st.button("Mapear Profissionais Próximos", type="primary"):
        if cidade_paci and relato:
            lat_p, lon_p = obter_coordenadas(cidade_paci, uf_paci)
            BASE = {"coracao": "Enfermeiro", "femur": "Fisioterapeuta", "idoso": "Tecnico"}
            cat_sugerida = next((BASE[k] for k in BASE if k in relato), "Enfermeiro")
            
            conn = sqlite3.connect('homecare_nacional.db')
            # Registra busca com localização do paciente para BI
            conn.execute("INSERT INTO metricas_triagem (termo, uf, cidade, lat_busca, lon_busca, data, categoria_id) VALUES (?,?,?,?,?,?,?)",
                         (cat_sugerida, uf_paci, cidade_paci, lat_p, lon_p, datetime.now().strftime("%d/%m/%Y"), cat_sugerida))
            
            # Busca profissionais verificados na mesma região
            query = "SELECT nome, lat, lon, contato, rating FROM profissionais WHERE verificado=1 AND categoria=? AND uf=? AND cidade LIKE ?"
            df = pd.read_sql_query(query, conn, params=(cat_sugerida, uf_paci, f"%{cidade_paci}%"))
            conn.close()

            if not df.empty:
                st.success(f"Encontramos especialistas em {cidade_paci}!")
                # Mapa centralizado no paciente
                m = folium.Map(location=[lat_p, lon_p] if lat_p else [df['lat'].mean(), df['lon'].mean()], zoom_start=12)
                folium.Marker([lat_p, lon_p], popup="Você está aqui", icon=folium.Icon(color='red', icon='home')).add_to(m)
                for _, p in df.iterrows():
                    folium.Marker([p['lat'], p['lon']], popup=p['nome'], icon=folium.Icon(color='blue', icon='user-md', prefix='fa')).add_to(m)
                st_folium(m, width=1200, height=450)
            else:
                st.warning("Nenhum especialista de elite verificado nesta região ainda.")
        else:
            st.error("Informe sua cidade e o relato clínico.")

# 5. MAESTRO DE NAVEGAÇÃO
if st.session_state.pagina == "home": mostrar_home()
elif st.session_state.pagina == "cadastro": mostrar_cadastro()
elif st.session_state.pagina == "triagem": mostrar_triagem()
elif st.session_state.pagina == "admin": st.write("Painel Administrativo em desenvolvimento.")
