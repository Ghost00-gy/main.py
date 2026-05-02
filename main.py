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

# Inicialização de Estado de Navegação (O Coração da Organização)
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# 2. MOTOR DE DADOS NACIONAL (v5)
def init_db():
    conn = sqlite3.connect('homecare_nacional.db')
    cursor = conn.cursor()
    # Tabela com suporte a Mapas (lat/lon) e Localização Nacional
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

# 3. GEOLOCALIZAÇÃO GRATUITA (OPEN SOURCE)
def obter_coordenadas(cidade, uf):
    try:
        geolocator = Nominatim(user_agent="homecare_connect_br")
        location = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        if location:
            return location.latitude, location.longitude
        return -23.5505, -46.6333  # Coordenada padrão (SP) caso falhe
    except:
        return -23.5505, -46.6333

# 4. PÁGINAS DO SISTEMA (ISOLADAS)

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=380)
        st.title("Excelência em Cuidado Domiciliar")
        st.write("A elite dos profissionais de saúde, agora em escala nacional com inteligência logística.")
        
        if st.button("🚀 Iniciar Triagem de Saúde", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        
        st.divider()
        c_nav1, c_nav2 = st.columns(2)
        if c_nav1.button("👨‍⚕️ Cadastro Especialista", use_container_width=True):
            st.session_state.pagina = "cadastro"; st.rerun()
        if c_nav2.button("📊 Gestão & Métricas", use_container_width=True):
            st.session_state.pagina = "admin"; st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar ao Início", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Cadastro Nacional de Especialistas")
    
    with st.form("form_cadastro_v5", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            uf = st.selectbox("Estado (UF)", ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "CE", "PE", "DF"])
        with c2:
            cidade = st.text_input("Cidade de Atuação")
            whatsapp = st.text_input("WhatsApp (com DDD)")
            conselho = st.text_input("Registro Profissional (Ex: CRM-SP 12345)")
            
        bio = st.text_area("Breve Resumo Profissional")
        st.markdown("---")
        concordo = st.checkbox("Li e concordo com o processamento de dados conforme a LGPD.")

        if st.form_submit_button("Finalizar Submissão"):
            if nome and cidade and whatsapp and concordo:
                lat, lon = obter_coordenadas(cidade, uf)
                conn = sqlite3.connect('homecare_nacional.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, uf, cidade, lat, lon, contato, conselho, bio) VALUES (?,?,?,?,?,?,?,?,?)",
                             (nome, cat, uf, cidade, lat, lon, whatsapp, conselho, bio))
                conn.commit(); conn.close()
                st.success(f"Cadastro de {nome} enviado para análise estratégica!")
            else:
                st.error("Preencha todos os campos obrigatórios.")

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Nacional e Mapa de Elite")
    
    c1, c2 = st.columns(2)
    uf_busca = c1.selectbox("Seu Estado (UF)", ["SP", "RJ", "MG", "RS", "PR", "BA", "CE"])
    cidade_busca = c2.text_input("Sua Cidade")
    relato = st.text_area("Relate a necessidade (ex: pós-operatório, idoso):").lower()
    
    if st.button("Mapear Profissionais Próximos", type="primary"):
        BASE = {"coracao": "Enfermeiro", "femur": "Fisioterapeuta", "idoso": "Tecnico", "curativo": "Enfermeiro"}
        cat_sugerida = next((BASE[k] for k in BASE if k in relato), "Enfermeiro")
        
        conn = sqlite3.connect('homecare_nacional.db')
        query = "SELECT nome, lat, lon, contato, rating, bio, conselho FROM profissionais WHERE verificado=1 AND categoria=? AND uf=? AND cidade LIKE ?"
        df = pd.read_sql_query(query, conn, params=(cat_sugerida, uf_busca, f"%{cidade_busca}%"))
        conn.close()

        if not df.empty:
            st.success(f"Encontramos {len(df)} especialistas de elite em {cidade_busca}!")
            
            # MAPA FOLIUM (Centralizado nos Profissionais)
            m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=12)
            for _, p in df.iterrows():
                folium.Marker(
                    [p['lat'], p['lon']],
                    popup=f"<b>{p['nome']}</b><br>Rating: {p['rating']}",
                    tooltip=p['nome'],
                    icon=folium.Icon(color='blue', icon='user-md', prefix='fa')
                ).add_to(m)
            st_folium(m, width=1200, height=450)

            # CARDS DE CONTATO
            for _, p in df.iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 25px; border-radius: 15px; border-left: 8px solid #2E4A7D; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <h3 style="margin:0;">{p['nome']} <span style="font-size:16px; color:gold;">{'★' * int(p['rating'])}</span></h3>
                    <p><b>{cat_sugerida}</b> | {p['conselho']}</p>
                    <p><i>"{p['bio']}"</i></p>
                    <a href="https://wa.me/{p['contato']}" target="_blank" style="background:#25D366; color:white; padding:10px 20px; border-radius:10px; text-decoration:none; font-weight:bold; display:inline-block;">Contatar via WhatsApp</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"Ainda não temos especialistas verificados nesta região. Nossa rede nacional está em expansão!")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    if not st.session_state.autenticado:
        senha = st.text_input("Chave Mestra Nacional:", type="password")
        if st.button("Acessar"):
            if senha == "tatuicare2026": st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 BI & Curadoria Nacional")
    # Lógica de aprovação e métricas conforme discutido...

# 5. MAESTRO DE NAVEGAÇÃO (GARANTE O ISOLAMENTO)
if st.session_state.pagina == "home":
    mostrar_home()
elif st.session_state.pagina == "cadastro":
    mostrar_cadastro()
elif st.session_state.pagina == "triagem":
    mostrar_triagem()
elif st.session_state.pagina == "admin":
    mostrar_admin()
