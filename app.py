import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# Estilização para as cores da marca (opcional)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .resumo-card { padding: 20px; border-radius: 10px; border: 1px solid #464b5d; background-color: #1e2129; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta Tributária Monofásica")
st.subheader("Irmãos Resende - Inteligência Fiscal")

@st.cache_data
def carregar_dados():
    try:
        # Lê o CSV e garante que o NCM seja tratado como texto para não perder o "0" à esquerda
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        # Remove pontos do NCM caso existam na planilha (ex: 2710.19.10 -> 27101910)
        df['NCM_Limpo'] = df['NCM'].str.replace('.', '', regex=False)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base: {e}")
        return None

df_monofasicos = carregar_dados()

ncm_input = st.text_input("Digite o NCM (8 dígitos):", placeholder="Ex: 27101910").replace('.', '')

if st.button("Analisar NCM"):
    if len(ncm_input) == 8:
        with st.spinner('Processando...'):
            # 1. Busca na BrasilAPI para Descrição Oficial
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_input}")
            desc_oficial = res.json().get('descricao', 'Descrição não encontrada') if res.status_code == 200 else "NCM não localizado na Receita"

            # 2. Busca na sua nova planilha base.csv
            resultado = df_monofasicos[df_monofasicos['NCM_Limpo'] == ncm_input] if df_monofasicos is not None else pd.DataFrame()

            if not resultado.empty:
                item = resultado.iloc[0]
                st.success("✅ **PRODUTO IDENTIFICADO COMO MONOFÁSICO**")
                
                # Card de Detalhes
                st.markdown(f"""
                <div class="resumo-card">
                    <h4>{item['Descrição']}</h4>
                    <p><b>Grupo:</b> {item['Grupo/Subgrupo NCM']}</p>
                    <hr>
                    <p><b>Alíquota PIS (Ind./Imp.):</b> {item['PIS']}</p>
                    <p><b>Alíquota COFINS (Ind./Imp.):</b> {item['COFINS']}</p>
                    <p><b>CST Sugerido (Venda):</b> {item['CST 04']}</p>
                    <p><b>Fundamentação:</b> {item['Fundamentação']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Ver Orientação Completa"):
                    st.write(f"**Aplicação:** {item['Aplicação']}")
                    st.write(f"**Condição:** {item['Condição']}")
            else:
                st.warning("⚠️ **ATENÇÃO:** Este NCM não consta na lista de produtos Monofásicos.")
                st.info(f"**Descrição Oficial (BrasilAPI):** {desc_oficial}")
    else:
        st.error("Por favor, digite os 8 números do NCM.")

st.markdown("---")
st.caption("Base de dados: Tabela 4.3.10 - Versão 1.24 (Atualizada Jul/2025)")
