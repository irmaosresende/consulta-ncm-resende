import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #002e5d; color: white; font-weight: bold; }
    .resumo-card { padding: 20px; border-radius: 10px; border: 1px solid #d1d1d1; background-color: #f8f9fa; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta Tributária Monofásica")
st.subheader("Irmãos Resende - Inteligência Fiscal")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        # Limpa o NCM da planilha: remove pontos e espaços
        df['NCM_Busca'] = df['NCM'].str.replace('.', '', regex=False).str.strip().str.split(' ').str[0]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base.csv: {e}")
        return None

df_base = carregar_dados()
EXCECOES = ['30039056', '30049046']

ncm_digitado = st.text_input("Digite o NCM (8 dígitos):", placeholder="Ex: 87081000").replace('.', '').strip()

if st.button("Analisar Tributação"):
    if len(ncm_digitado) >= 4:
        with st.spinner('Verificando...'):
            # 1. Busca nome oficial na API
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_digitado}")
            desc_api = res.json().get('descricao', 'NCM não encontrado na Receita') if res.status_code == 200 else "NCM Inválido"

            # 2. Lógica de busca na sua nova lista
            # Verifica se o NCM digitado começa com algum NCM da sua lista (ex: 30031010 começa com 3003)
            match = None
            if df_base is not None:
                for idx, row in df_base.iterrows():
                    if ncm_digitado.startswith(row['NCM_Busca']):
                        match = row
                        break

            if ncm_digitado in EXCECOES:
                st.error(f"⚠️ **EXCEÇÃO:** O NCM {ncm_digitado} é uma exceção à regra monofásica.")
            elif match is not None:
                st.success("✅ **PRODUTO MONOFÁSICO IDENTIFICADO**")
                st.markdown(f"""
                <div class="resumo-card">
                    <h4>{desc_api}</h4>
                    <p><b>Referência na Tabela:</b> {match['NCM']}</p>
                    <p><b>Descrição na Lista:</b> {match['Descricao']}</p>
                    <hr>
                    <p><b>CST de Saída (Varejo):</b> 04 (Alíquota Zero)</p>
                    <p><b>Fundamentação:</b> Lei 10.485/2002 ou Lei 10.147/2000</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("ℹ️ **TRIBUTAÇÃO NORMAL:** Este NCM não foi localizado na lista de Monofásicos.")
                st.write(f"**Descrição Oficial:** {desc_api}")
    else:
        st.error("Digite pelo menos 4 dígitos do NCM.")

st.markdown("---")
st.caption("© 2026 Irmãos Resende | Dados baseados na Tabela 4.3.10 e Leis 10.485/10.147.")
