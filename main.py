import streamlit as st
import os, sqlite3, pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import plotly.express as px
from datetime import datetime

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="HomeCare Connect | Brasil", layout="wide", page_icon="🏥")

# Inicialização de Estado de Navegação
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# 2. BANCO DE DADOS NACIONAL
def init_db():
    conn = sqlite3.connect('homecare_nacional.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, 
                       contato TEXT, uf TEXT, cidade TEXT, lat REAL, lon REAL,
                       conselho TEXT, bio TEXT, rating REAL DEFAULT 5.0, verificado INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS metricas_triagem 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, termo TEXT, uf TEXT, cidade TEXT, data TEXT, categoria_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. GEOLOCALIZAÇÃO GRATUITA
def obter_coordenadas(cidade, uf):
    try:
        geolocator = Nominatim(user_agent="homecare_connect_v5")
        location = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        return (location.latitude, location.longitude) if location else (-23.55, -46.63)
    except:
        return (-23.55, -46.63)

# 4. PÁGINAS DO SISTEMA

def mostrar_home():
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=380)
        st.title("Excelência em Cuidado Domiciliar")
        st.write("A elite dos profissionais de saúde, agora em escala nacional.")
        
        if st.button("🚀 Iniciar Triagem de Saúde", use_container_width=True):
            st.session_state.pagina = "triagem"
            st.rerun()
        
        st.divider()
        c_nav1, c_nav2 = st.columns(2)
        if c_nav1.button("👨‍⚕️ Cadastro Especialista", use_container_width=True):
            st.session_state.pagina = "cadastro"
            st.rerun()
        if c_nav2.button("📊 Gestão & Métricas", use_container_width=True):
            st.session_state.pagina = "admin"
            st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def mostrar_cadastro():
    st.sidebar.button("⬅️ Voltar ao Início", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("📝 Cadastro Nacional de Especialistas")
    
    with st.form("form_cadastro_nacional", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            cat = st.selectbox("Especialidade", ["Medico", "Enfermeiro", "Tecnico", "Fisioterapeuta", "Psicologo"])
            uf = st.selectbox("Estado (UF)", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        with c2:
            cidade = st.text_input("Cidade de Atuação")
            whatsapp = st.text_input("WhatsApp (com DDD)")
            conselho = st.text_input("Registro Profissional (CRM/COREN/etc)")
            
        st.markdown("---")
        concordo = st.checkbox("Li e concordo que meus dados sejam processados conforme a LGPD.")

        if st.form_submit_button("Finalizar Submissão"):
            if nome and cidade and whatsapp and concordo:
                lat, lon = obter_coordenadas(cidade, uf)
                conn = sqlite3.connect('homecare_nacional.db')
                conn.execute("INSERT INTO profissionais (nome, categoria, uf, cidade, lat, lon, contato, conselho) VALUES (?,?,?,?,?,?,?,?)",
                             (nome, cat, uf, cidade, lat, lon, whatsapp, conselho))
                conn.commit(); conn.close()
                st.success(f"Cadastro de {nome} enviado para análise!")
            else:
                st.error("Preencha todos os campos obrigatórios.")

def mostrar_triagem():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem Nacional Inteligente")
    
    # Lógica de triagem e mapa folium aqui (conforme conversamos antes)
    st.info("Área de triagem geográfica em desenvolvimento com Folium.")

def mostrar_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    # Lógica do painel de controle e BI nacional
    st.write("Painel Administrativo Nacional.")

# 5. MAESTRO DE NAVEGAÇÃO (O coração da organização)
if st.session_state.pagina == "home":
    mostrar_home()
elif st.session_state.pagina == "cadastro":
    mostrar_cadastro()
elif st.session_state.pagina == "triagem":
    mostrar_triagem()
elif st.session_state.pagina == "admin":
    mostrar_admin()
