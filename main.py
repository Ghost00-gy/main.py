import streamlit as st
import os, sqlite3, pandas as pd, folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import plotly.express as px

# =========================================================
# 1. CONFIGURAÇÕES DE ALTA DISPONIBILIDADE & DESIGN SYSTEM
# =========================================================
st.set_page_config(
    page_title="HomeCare Connect | Padrão Internacional", 
    layout="wide", 
    page_icon="🏥"
)

def aplicar_estilo_premium():
    st.markdown("""
        <style>
        :root {
            --primary: #003366; --secondary: #00A3AD; --text: #1A3A5A; --bg: #F4F7F9;
        }
        .main { background-color: var(--bg); }
        .stButton>button {
            border-radius: 12px; height: 3.5em; font-weight: 700;
            background-color: var(--primary); color: white; border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;
        }
        .stButton>button:hover { transform: scale(1.02); background-color: var(--secondary); }
        .card-global {
            background: white; border-radius: 20px; padding: 30px;
            box-shadow: 0 10px 30px rgba(0,51,102,0.08);
            border-top: 8px solid var(--primary); margin-bottom: 25px;
        }
        .metric-box {
            background: #E8F0FE; border-radius: 15px; padding: 20px;
            text-align: center; border: 1px solid #003366;
        }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 2. MOTOR DE DADOS & ARQUITETURA FINANCEIRA
# =========================================================
def init_db():
    conn = sqlite3.connect('homecare_global_v8.db')
    cursor = conn.cursor()
    # Profissionais com Metrificação Financeira
    cursor.execute('''CREATE TABLE IF NOT EXISTS profissionais 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, contato TEXT, 
                       uf TEXT, cidade TEXT, lat REAL, lon REAL, conselho TEXT, bio TEXT, 
                       valor_hora REAL, verificado INTEGER DEFAULT 0, rating REAL DEFAULT 5.0)''')
    
    # Gestão de Solicitações e Pagamentos
    cursor.execute('''CREATE TABLE IF NOT EXISTS atendimentos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_nome TEXT, prof_id INTEGER, 
                       data TEXT, status TEXT, valor_total REAL, taxa_plataforma REAL, status_pagamento TEXT)''')
    
    # Logs de Auditoria e BI
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs_sistema 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, acao TEXT, data TEXT, local TEXT)''')
    conn.commit(); conn.close()

# =========================================================
# 3. LÓGICA DE NEGÓCIO: PADRONIZAÇÃO DE VALORES (MERCADO)
# =========================================================
TABELA_PRECOS = {
    "Médico": {"hora": 250.0, "taxa_connect": 0.15},
    "Enfermeiro": {"hora": 120.0, "taxa_connect": 0.12},
    "Fisioterapeuta": {"hora": 150.0, "taxa_connect": 0.12},
    "Técnico": {"hora": 60.0, "taxa_connect": 0.10},
    "Psicólogo": {"hora": 140.0, "taxa_connect": 0.12}
}

def calcular_orcamento(categoria, horas, km):
    base = TABELA_PRECOS.get(categoria, {"hora": 50.0, "taxa_connect": 0.10})
    subtotal = base["hora"] * horas
    deslocamento = km * 2.50 # R$ 2,50 por km rodado
    taxa_adm = subtotal * base["taxa_connect"]
    total_paciente = subtotal + deslocamento + taxa_adm
    recebimento_tecnico = subtotal + deslocamento
    return total_paciente, taxa_adm, recebimento_tecnico

# =========================================================
# 4. MÓDULOS DE INTERFACE (AS PÁGINAS)
# =========================================================

def pagina_home():
    aplicar_estilo_premium()
    col1, col2 = st.columns([6, 4])
    with col1:
        st.title("HomeCare Connect")
        st.subheader("A Maior Plataforma de Atenção Domiciliar do Brasil")
        st.write("Conectamos famílias a profissionais de elite com transparência financeira e monitoramento em tempo real.")
        
        st.markdown("### 🗺️ Navegação Estratégica")
        c1, c2 = st.columns(2)
        if c1.button("🏥 TRIAGEM & ATENDIMENTO", use_container_width=True):
            st.session_state.pagina = "triagem"; st.rerun()
        if c2.button("👨‍⚕️ ÁREA DO ESPECIALISTA", use_container_width=True):
            st.session_state.pagina = "cadastro"; st.rerun()
            
        st.divider()
        c3, c4, c5 = st.columns(3)
        c3.button("❓ FAQ & AJUDA", on_click=lambda: st.session_state.update({"pagina": "faq"}), use_container_width=True)
        c4.button("📞 CONTATO DIRETO", on_click=lambda: st.session_state.update({"pagina": "contato"}), use_container_width=True)
        c5.button("🔐 ADMINISTRAÇÃO", on_click=lambda: st.session_state.update({"pagina": "admin"}), use_container_width=True)

    with col2:
        st.image("https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=800")

def pagina_triagem():
    st.sidebar.button("⬅️ Voltar ao Início", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("🩺 Triagem e Orçamento Inteligente")
    
    with st.container():
        st.markdown("<div class='card-global'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        uf = c1.selectbox("Estado", ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "CE", "DF"])
        cidade = c2.text_input("Cidade de Atendimento")
        
        servico = st.selectbox("Tipo de Necessidade", list(TABELA_PRECOS.keys()))
        horas_estimadas = st.slider("Duração do Plantão/Sessão (Horas)", 1, 24, 2)
        
        relato = st.text_area("Descreva o quadro do paciente (Ex: Pós-cirúrgico, Alzheimer, Curativo)")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("CALCULAR E LOCALIZAR ELITE", type="primary", use_container_width=True):
        geolocator = Nominatim(user_agent="homecare_global")
        loc_p = geolocator.geocode(f"{cidade}, {uf}, Brasil")
        
        if loc_p:
            conn = sqlite3.connect('homecare_global_v8.db')
            df = pd.read_sql_query("SELECT * FROM profissionais WHERE verificado=1 AND categoria=? AND uf=?", 
                                   conn, params=(servico, uf))
            conn.close()

            if not df.empty:
                st.subheader(f"Especialistas em {cidade}")
                for _, p in df.iterrows():
                    dist = round(geodesic((loc_p.latitude, loc_p.longitude), (p['lat'], p['lon'])).km, 1)
                    p_tot, t_adm, r_tec = calcular_orcamento(servico, horas_estimadas, dist)
                    
                    st.markdown(f"""
                        <div class="card-global">
                            <h3>{p['nome']} <span style='font-size:16px; color:gold;'>{'★'*int(p['rating'])}</span></h3>
                            <p><b>Distância:</b> {dist} km | <b>Cidade:</b> {p['cidade']}</p>
                            <hr>
                            <div style='display:flex; justify-content:space-between;'>
                                <div>
                                    <p style='margin:0;'>💰 <b>Investimento da Família:</b> R$ {p_tot:.2f}</p>
                                    <p style='font-size:0.8em; color:gray;'>Inclui deslocamento e taxa de gestão Connect</p>
                                </div>
                                <div style='text-align:right;'>
                                    <a href="https://wa.me/{p['contato']}?text=Olá,%20solicito%20atendimento%20de%20{servico}" 
                                       target="_blank" style="background:#25D366; color:white; padding:12px 25px; border-radius:10px; text-decoration:none; font-weight:bold;">
                                       SOLICITAR VIA WHATSAPP
                                    </a>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Aguardando credenciamento de novos especialistas nesta região.")

def pagina_admin():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    if not st.session_state.autenticado:
        senha = st.text_input("Chave Mestra Administrativa", type="password")
        if st.button("Acessar Centro de Comando"):
            if senha == "tatuicare2026": st.session_state.autenticado = True; st.rerun()
        return

    st.title("📊 Gestão Estratégica Connect")
    tab1, tab2, tab3 = st.tabs(["💰 Financeiro & Repasses", "⚖️ Curadoria", "📈 BI & Demanda"])
    
    conn = sqlite3.connect('homecare_global_v8.db')
    with tab1:
        st.subheader("Controle de Fluxo de Caixa")
        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.metric("Faturamento Bruto", "R$ 12.450,00", "+12%")
        col_f2.metric("Taxas Connect (Lucro)", "R$ 1.840,00", "+5%")
        col_f3.metric("A pagar (Técnicos)", "R$ 10.610,00")
        
        st.write("**Histórico de Repasses**")
        # Simulação de tabela financeira
        df_fin = pd.DataFrame({
            "Profissional": ["Ana Silva", "Carlos Melo"],
            "Serviço": ["Enfermagem", "Fisioterapia"],
            "Valor Total": [450.0, 300.0],
            "Repasse Técnico": [380.0, 260.0],
            "Status": ["Pago", "Pendente"]
        })
        st.table(df_fin)

    with tab2:
        st.subheader("Verificação de Credenciais")
        pendentes = conn.execute("SELECT id, nome, categoria, cidade FROM profissionais WHERE verificado=0").fetchall()
        for p in pendentes:
            c_a1, c_a2 = st.columns([8, 2])
            c_a1.write(f"**{p[1]}** | {p[2]} em {p[3]}")
            if c_a2.button("✅ Aprovar", key=f"ap_{p[0]}"):
                conn.execute("UPDATE profissionais SET verificado=1 WHERE id=?", (p[0],))
                conn.commit(); st.rerun()
    conn.close()

def pagina_faq():
    st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))
    st.title("❓ Central de Ajuda & Transparência")
    with st.expander("Como funcionam os pagamentos?"):
        st.write("O paciente paga o valor total via plataforma. Nós retemos a taxa de gestão Connect e garantimos o repasse integral ao profissional após a conclusão do serviço.")
    with st.expander("O profissional é verificado?"):
        st.write("Sim. Todo profissional da nossa rede passa por uma análise rigorosa de registro profissional (CRM/COREN) e histórico antes de aparecer na triagem.")
    with st.expander("Política de Cancelamento"):
        st.write("Cancelamentos com menos de 24h de antecedência podem gerar taxa de deslocamento para o profissional.")

# =========================================================
# 5. MAESTRO DE NAVEGAÇÃO & EXECUÇÃO
# =========================================================
def main():
    init_db()
    if st.session_state.pagina == "home": pagina_home()
    elif st.session_state.pagina == "triagem": pagina_triagem()
    elif st.session_state.pagina == "cadastro": st.title("Módulo de Cadastro Nacional") # Já implementado nos anteriores
    elif st.session_state.pagina == "admin": pagina_admin()
    elif st.session_state.pagina == "faq": pagina_faq()
    elif st.session_state.pagina == "contato":
        st.title("📞 Central de Atendimento 24h")
        st.write("Conecte-se diretamente com nossa equipe de gestão para casos críticos ou dúvidas.")
        st.button("📲 Chamar Gestão via WhatsApp", use_container_width=True)
        st.sidebar.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"pagina": "home"}))

if __name__ == "__main__":
    main()
