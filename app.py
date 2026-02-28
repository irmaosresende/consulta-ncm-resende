import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Consulta Monofásica - Irmãos Resende", page_icon="📊")

# Estilização personalizada para combinar com a marca
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta de NCM Monofásico")
st.subheader("Irmãos Resende - Inteligência Tributária")

# Carregar dados
@st.cache_data
def carregar_dados():
    # Certifique-se de que o CSV existe ou use um dicionário para teste
    try:
        df = pd.read_csv('dados.csv', dtype={'ncm': str})
        return df
    except:
        return pd.DataFrame(columns=['ncm', 'descricao', 'natureza_receita'])

df_monofasicos = carregar_dados()

# Input do usuário
ncm_input = st.text_input("Digite o código NCM (apenas números):", max_chars=8)

if st.button("Verificar Tributação"):
    if len(ncm_input) == 8:
        # Busca o NCM na base
        resultado = df_monofasicos[df_monofasicos['ncm'] == ncm_input]
        
        if not resultado.empty:
            st.success("✅ Este produto está no regime MONOFÁSICO!")
            
            # Exibir detalhes em cards
            col1, col2 = st.columns(2)
            with col1:
                st.metric("NCM", ncm_input)
            with col2:
                st.metric("Nat. Receita", resultado['natureza_receita'].values[0])
            
            st.info(f"**Descrição:** {resultado['descricao'].values[0]}")
            st.warning("⚠️ Lembre-se de segregar as receitas no PGDAS-D para não pagar PIS/COFINS em duplicidade.")
        else:
            st.error("❌ NCM não encontrado na lista de monofásicos.")
            st.write("Isso significa que o produto pode ser tributação normal (Alíquota Básica) ou não está na nossa base atualizada.")
    else:
        st.warning("Por favor, digite um NCM válido com 8 dígitos.")

st.markdown("---")
st.caption("© 2023 Irmãos Resende - Consultoria Tributária")