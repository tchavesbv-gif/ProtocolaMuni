import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Sistema de Protocolos - CISMIV",
    page_icon="📋",
    layout="wide"
)

# Configuração da Conexão com o Supabase
# Dica: Você pode colocar essas chaves nos secrets do Streamlit ou variáveis de ambiente
SUPABASE_URL = "SUA_URL_DO_SUPABASE"
SUPABASE_KEY = "SUA_CHAVE_ANON_DO_SUPABASE"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Título principal
st.title("📋 Gestão de Protocolos Intermunicipais - CISMIV")
st.markdown("Controle e rastreabilidade de documentos entre os municípios consorciados.")

# Menu lateral de navegação
menu = st.sidebar.selectbox("Navegação", ["Consultar Protocolos", "Novo Protocolo", "Dashboard / KPIs"])

# ==========================================
# 1. CONSULTAR PROTOCOLOS
# ==========================================
if menu == "Consultar Protocolos":
    st.subheader("🔍 Protocolos Registrados")
    
    try:
        # Buscando dados da tabela 'protocolos' no Supabase
        response = supabase.table("protocolos").select("*").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            
            # Filtro rápido por status
            status_filtro = st.selectbox("Filtrar por Status", ["Todos"] + list(df["status"].unique()))
            if status_filtro != "Todos":
                df = df[df["status"] == status_filtro]
                
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum protocolo cadastrado no momento.")
            
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")

# ==========================================
# 2. NOVO PROTOCOLO
# ==========================================
elif menu == "Novo Protocolo":
    st.subheader("➕ Abertura de Novo Protocolo")
    
    with st.form("form_protocolo"):
        col1, col2 = st.columns(2)
        
        with col1:
            municipio_origem = st.text_input("Município de Origem / Secretaria")
            tipo_documento = st.selectbox("Tipo de Documento", ["Ofício", "Requisição de Insumo", "Prestação de Contas", "Outros"])
            
        with col2:
            prioridade = st.selectbox("Prioridade", ["Normal", "Urgente", "Urgentíssimo"])
            assunto = st.text_input("Assunto Resumido")
            
        descricao = st.text_area("Descrição Detalhada da Solicitação")
        
        submitted = st.form_submit_button("Cadastrar Protocolo")
        
        if submitted:
            if municipio_origem and assunto and descricao:
                try:
                    # Gerando um número de protocolo simples baseado na data/hora
                    numero_gerado = f"PRT-{datetime.now().strftime('%Y%m%d-%H%M')}"
                    
                    novo_registro = {
                        "numero_protocolo": numero_gerado,
                        "municipio_origem_id": municipio_origem, # Pode ser ajustado para UUID se usar relacao
                        "tipo_documento": tipo_documento,
                        "assunto": assunto,
                        "descricao": descricao,
                        "status": "Aberto",
                        "prioridade": prioridade
                    }
                    
                    supabase.table("protocolos").insert(novo_registro).execute()
                    st.success(f"Protocolo **{numero_gerado}** cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")
            else:
                st.warning("Por favor, preencha todos os campos obrigatórios.")

# ==========================================
# 3. DASHBOARD / KPIS
# ==========================================
elif menu == "Dashboard / KPIs":
    st.subheader("📊 Painel Gerencial")
    
    try:
        response = supabase.table("protocolos").select("*").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Protocolos", len(df))
            col2.metric("Em Aberto", len(df[df["status"] == "Aberto"]))
            col3.metric("Urgentes", len(df[df["prioridade"].isin(["Urgente", "Urgentíssimo"])]))
            
            st.bar_chart(df["status"].value_counts())
        else:
            st.info("Sem dados suficientes para gerar métricas.")
    except Exception as e:
        st.error(f"Erro ao carregar o dashboard: {e}")