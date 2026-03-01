import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

st.title("🔍 Consulta de NCM Monofásico")
st.subheader("Irmãos Resende - Inteligência Tributária")

# Tentativa de carregar a sua base local de monofásicos
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        return df
    except:
        return None

df_monofasicos = carregar_dados()

ncm_input = st.text_input("Digite o código NCM (apenas 8 números):", max_chars=8)

if st.button("Verificar Tributação"):
    if len(ncm_input) == 8:
        # 1. Consulta na BrasilAPI para pegar a descrição oficial
        with st.spinner('Consultando BrasilAPI...'):
            url = f"https://brasilapi.com.br/api/ncm/v1/{ncm_input}"
            response = requests.get(url)
            
            if response.status_code == 200:
                dados_api = response.json()
                st.info(f"**Descrição Oficial:** {dados_api['descricao']}")
                
                # 2. Verifica se está na sua lista de monofásicos
                if df_monofasicos is not None and ncm_input in df_monofasicos['NCM'].values:
                    st.success("✅ Este NCM consta como **MONOFÁSICO** em nossa base!")
                else:
                    st.warning("⚠️ Este NCM não foi encontrado na lista de monofásicos ou é tributação normal.")
            else:
                st.error("❌ NCM não encontrado na base da Receita Federal (BrasilAPI).")
    else:
        st.warning("Por favor, digite um NCM válido com 8 dígitos.")

st.markdown("---")
st.caption("© 2026 Irmãos Resende - Consultoria Tributária")
