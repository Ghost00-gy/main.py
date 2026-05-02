import streamlit as st
import os, sqlite3, pandas as pd, folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import plotly.express as px

# =========================================================
# 1. INICIALIZAÇÃO DE ESTADO (CORREÇÃO DO ERRO)
# =========================================================
# Deve ser a primeira coisa no script para evitar AttributeError
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'tema' not in st.session_state: st.session_state.tema = "Claro"

# =========================================================
# 2. CONFIGURAÇÕES INTERNACIONAIS & DESIGN SYSTEM
# =========================================================
st.set_page_config(
    page_title="HomeCare Connect | Global HealthTech", 
    layout="wide", 
    page_icon="🏥"
)

def aplicar_estilo_elite():
    # Cores inspiradas no padrão Home Doctor (Azul Marinho e Branco)
    primaria = "#003366" 
    segundaria = "#00A3AD"
    st.markdown(f"""
        <style>
        .main {{ background-color: #F0F2F6; }}
        .stButton>button {{
            border-radius: 10px; height: 3.5em; width: 100%;
            font-weight: bold; background-color: {primaria}; color: white;
        }}
        .card-global {{
            background: white; border-radius: 15px; padding: 25px;
            box-shadow: 0 8px 20px rgba(0,51,102,0.1);
            border-left: 10px solid {primaria}; margin-bottom: 20px;
        }}
        .sidebar .sidebar-content {{ background-image: linear-gradient(#003366, #00A3AD); color: white; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. MOTOR DE DADOS & LOGÍSTICA FINANCEIRA (BACK-END)
# =========================================================
def init_db():
    conn = sqlite3.connect('homecare_v9_master.db')
    cursor = conn.cursor()
    # Cadastro de Elite
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, lat REAL, lon REAL, conselho TEXT, bio TEXT, 
                       valor_hora REAL, verificado INTEGER DEFAULT 0, rating REAL DEFAULT 5.0)''')
    # Transações Financeiras e Atendimentos
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacoes 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente TEXT, prof_id INTEGER, 
                       valor_total REAL, taxa_plataforma REAL, status TEXT, data TEXT)''')
    # Inteligência de Busca (BI)
    cursor.execute('''CREATE TABLE IF NOT EXISTS buscas 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, termo TEXT, cidade TEXT, uf TEXT, data TEXT)''')
    conn.commit(); conn.close()

# Padronização de Mercado (Conforme solicitado)
TABELA_VALORES = {
    "Médico": {"hora": 300.0, "comissao": 0.15}, # 15% para a plataforma
    "Enfermeiro": {"hora": 130.0, "comissao": 0.12},
    "Fisioterapeuta": {"hora": 160.0, "comissao": 0.12},
    "Técnico": {"hora": 75.0, "comissao": 0.10},
    "Psicólogo": {"hora": 150.0, "comissao": 0.12}
}

# =========================================================
# 4. MÓDULOS DE INTERFACE (FRONT-END MODULAR)
# =========================================================

def pagina_home():
    aplicar_estilo_elite()
    col_h1, col_h2 = st.columns([1, 1])
    with col_h1:
        st.title("Excelência em Home Office Health")
        st.write("Conectando o cuidado hospitalar ao conforto do lar com 30 anos de inspiração em segurança.")
        
        st.info("💡 **Acesso Rápido para Famílias e Profissionais**")
        if st.button("🔍 LOCALIZAR ESPECIALISTA (TRIAGEM)", type="primary"):
            st.session_state.pagina = "triagem"; st.rerun()
        
        c1, c2 = st.columns(2)
        c1.button("👨‍⚕️ Cadastro Profissional", on_click=lambda: st.session_state.update({"pagina": "cadastro"}))
        c2.button("📈 Painel Administrativo", on_click=lambda: st.session_state.update({"pagina": "admin"}))
        
        st.divider()
        st.button("❓ Central de Ajuda & FAQ", on_click=lambda: st.session_state.update({"pagina": "faq"}))

    with col_h2:
        st.image("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=800")

def pagina_triagem():
    st.sidebar.button("⬅️ MENU PRINCIPAL", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Mediação Connect")
    
    with st.container():
        st.markdown("<div class='card-global'>", unsafe_allow_html=True)
        col_t1, col_t2 = st.columns(2)
        uf_b = col_t1.selectbox("Estado", ["SP", "RJ", "MG", "PR", "RS", "BA", "SC"])
        cidade_b = col_t2.text_input("Sua Cidade")
        cat_b = st.selectbox("Especialidade Necessária", list(TABELA_VALORES.keys()))
        relato = st.text_area("Descreva a necessidade (Para nossa mediação):")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("GERAR ORÇAMENTO E MAPEAR", type="primary"):
        # Lógica de Geolocalização (Open Source)
        geolocator = Nominatim(user_agent="homecare_v9")
        loc = geolocator.geocode(f"{cidade_b}, {uf_b}, Brasil")
        
        if loc:
            conn = sqlite3.connect('homecare_v9_master.db')
            # Busca profissionais verificados e na mesma UF/Cidade
            query = "SELECT * FROM profissionais WHERE verificado=1 AND categoria=? AND uf=?"
            df = pd.read_sql_query(query, conn, params=(cat_b, uf_b))
            conn.close()

            if not df.empty:
                st.subheader(f"Especialistas em {cidade_b}")
                m = folium.Map(location=[loc.latitude, loc.longitude], zoom_start=13)
                
                for _, p in df.iterrows():
                    dist = round(geodesic((loc.latitude, loc.longitude), (p['lat'], p['lon'])).km, 1)
                    
                    # Cálculo Financeiro (Regra de Negócio)
                    valor_base = TABELA_VALORES[cat_b]["hora"]
                    taxa_plataforma = valor_base * TABELA_VALORES[cat_b]["comissao"]
                    total_paciente = valor_base + (dist * 2.5) + taxa_plataforma
                    
                    # Exibição do Card Hospitalar
                    st.markdown(f"""
                        <div class="card-global">
                            <h3>{p['nome']} <span style='color:gold;'>{'★' * int(p['rating'])}</span></h3>
                            <p><b>Registro:</b> {p['conselho']} | <b>Distância:</b> {dist} km</p>
                            <p><i>"{p['bio']}"</i></p>
                            <div style='background:#f0f2f6; padding:15px; border-radius:10px; display:flex; justify-content:space-between;'>
                                <span><b>Investimento Total:</b> R$ {total_paciente:.2f}</span>
                                <span><b>Mediação Connect:</b> Inclusa</span>
                            </div>
                            <br>
                            <a href="https://wa.me/{p['contato']}?text=Olá,%20vi%20seu%20perfil%20no%20HomeCare%20Connect" 
                               target="_blank" style="background:#25D366; color:white; padding:12px 30px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block; width:100%; text-align:center;">
                               INICIAR CHAT DE ATENDIMENTO
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                    folium.Marker([p['lat'], p['lon']], popup=p['nome']).add_to(m)
                st_folium(m, width=1300, height=400)
            else:
                st.warning("Nenhum profissional verificado nesta região. Estamos em expansão!")

def pagina_admin():
    st.sidebar.button("⬅️ MENU PRINCIPAL", on_click=lambda: st.session_state.update({"pagina": "home"}))
    if not st.session_state.autenticado:
        if st.text_input("Chave Administrativa", type="password") == "tatuicare2026":
            st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 Centro de Inteligência & Financeiro")
    tab1, tab2, tab3 = st.tabs(["💰 Fluxo Financeiro", "⚖️ Curadoria", "🌍 Mapa de Demanda"])
    
    with tab1:
        st.subheader("Gestão de Recebíveis e Repasses")
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Faturamento (Mediação)", "R$ 4.580,00", "+15%")
        c_f2.metric("Repasses Pendentes", "R$ 12.300,00")
        
        # Tabela Financeira Exemplo
        df_f = pd.DataFrame({
            "Data": ["01/05", "02/05"], "Paciente": ["Família Silva", "Família Melo"],
            "Profissional": ["Dr. João", "Enf. Ana"], "Status": ["Pago", "Aguardando"]
        })
        st.table(df_f)

    with tab2:
        st.subheader("Aprovação de Novos Integrantes")
        conn = sqlite3.connect('homecare_v9_master.db')
        pendentes = conn.execute("SELECT id, nome, categoria, cidade FROM profissionais WHERE verificado=0").fetchall()
        for p in pendentes:
            col_a1, col_a2 = st.columns([7, 3])
            col_a1.write(f"**{p[1]}** | {p[2]} em {p[3]}")
            if col_a2.button("✅ Aprovar Registro", key=f"ap_{p[0]}"):
                conn.execute("UPDATE profissionais SET verificado=1 WHERE id=?", (p[0],))
                conn.commit(); st.rerun()
        conn.close()

def pagina_faq():
    st.sidebar.button("⬅️ MENU PRINCIPAL", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("❓ Central de Ajuda e FAQ")
    with st.expander("Como funciona o pagamento?"):
        st.write("O paciente paga o valor total à plataforma. Nós garantimos o repasse ao técnico em até 48h após o serviço.")
    with st.expander("Segurança e Verificação"):
        st.write("Todos os profissionais são verificados manualmente por nossa equipe através do CRM/COREN.")

# =========================================================
# 5. O MAESTRO (CONTROLE DE FLUXO)
# =========================================================
def main():
    init_db()
    # Navegação robusta para evitar AttributeError
    paginas = {
        "home": pagina_home,
        "triagem": pagina_triagem,
        "admin": pagina_admin,
        "faq": pagina_faq,
        "cadastro": lambda: st.write("Módulo de Cadastro Nacional em Manutenção...")
    }
    
    servico = paginas.get(st.session_state.pagina, pagina_home)
    servico()

if __name__ == "__main__":
    main()
