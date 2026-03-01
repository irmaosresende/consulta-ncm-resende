import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# Estilização para um visual limpo e profissional
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #002e5d; color: white; font-weight: bold; border-radius: 5px; }
    .resultado-container { padding: 25px; border-radius: 10px; border: 1px solid #e0e0e0; background-color: #ffffff; color: #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .titulo-resultado { color: #002e5d; font-size: 24px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #002e5d; padding-bottom: 10px; }
    .label { font-weight: bold; color: #555; }
    .status-badge { padding: 5px 12px; border-radius: 15px; font-size: 14px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta Tributária Monofásica")
st.subheader("Irmãos Resende - Inteligência Fiscal")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        # Limpa o NCM: remove pontos, espaços e pega apenas a primeira parte antes de qualquer "Ex"
        df['NCM_Busca'] = df['NCM'].str.replace('.', '', regex=False).str.strip().str.split(' ').str[0]
        return df
    except:
        return None

df_base = carregar_dados()
EXCECOES = ['30039056', '30049046']

ncm_digitado = st.text_input("Digite o NCM:", placeholder="Ex: 87081000").replace('.', '').strip()

if st.button("Consultar"):
    if len(ncm_digitado) >= 4:
        with st.spinner('Analisando...'):
            # 1. Busca nome oficial na API
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_digitado}")
            desc_api = res.json().get('descricao', 'Descrição não encontrada') if res.status_code == 200 else "NCM não localizado"

            # 2. Lógica de busca na sua lista
            match = None
            if df_base is not None:
                for idx, row in df_base.iterrows():
                    if ncm_digitado.startswith(row['NCM_Busca']):
                        match = row
                        break

            st.markdown('<div class="titulo-resultado">Resultado da Consulta</div>', unsafe_allow_html=True)
            
            with st.container():
                if ncm_digitado in EXCECOES:
                    st.error("⚠️ **EXCEÇÃO IDENTIFICADA:** Este NCM não possui incidência monofásica conforme previsão legal.")
                elif match is not None:
                    st.markdown(f"""
                    <div class="resultado-container">
                        <span class="status-badge" style="background-color: #28a745;">MONOFÁSICO</span>
                        <p style="margin-top:15px;"><span class="label">Descrição:</span> {desc_api}</p>
                        <p><span class="label">NCM Identificado:</span> {match['NCM']}</p>
                        <p><span class="label">Grupo:</span> {match.get('Grupo/Subgrupo NCM', 'Autopeças/Geral')}</p>
                        <hr>
                        <p><span class="label">CST Sugerido (Venda):</span> 04 - Alíquota Zero</p>
                        <p><span class="label">Fundamentação:</span> Lei 10.485/2002 ou Lei 10.147/2000</p>
                        <p style="font-size: 12px; color: #777; margin-top:10px;"><i>*PJ Varejistas devem escriturar com Alíquota Zero conforme Art. 28 da Lei 13.097/2015.</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="resultado-container">
                        <span class="status-badge" style="background-color: #6c757d;">TRIBUTAÇÃO NORMAL</span>
                        <p style="margin-top:15px;"><span class="label">Descrição:</span> {desc_api}</p>
                        <p>Este NCM não foi localizado na lista de produtos monofásicos vigentes.</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("Por favor, digite um NCM válido.")

st.markdown("---")
st.caption("© 2026 Irmãos Resende | Tabela 4.3.10 SPED")
