import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# Estilização para replicar o padrão de relatório técnico
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #002e5d; color: white; font-weight: bold; }
    .card-resultado { padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #fff; margin-bottom: 20px; }
    .secao-titulo { font-weight: bold; color: #002e5d; border-bottom: 1px solid #eee; margin-bottom: 10px; padding-bottom: 5px; }
    .dado-linha { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; }
    .label { color: #666; font-weight: 500; }
    .valor { color: #333; font-weight: bold; }
    .status-sim { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta Tributária Monofásica")
st.subheader("Irmãos Resende - Inteligência Fiscal")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        df['NCM_Busca'] = df['NCM'].str.replace('.', '', regex=False).str.strip().str.split(' ').str[0]
        return df
    except:
        return None

df_base = carregar_dados()

ncm_input = st.text_input("Digite o NCM para consulta:", placeholder="Ex: 33051000").replace('.', '').strip()

if st.button("Consultar"):
    if len(ncm_input) >= 4:
        with st.spinner('Acessando Tabela 4.3.10...'):
            # Busca na API para descrição oficial
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_input}")
            desc_api = res.json().get('descricao', 'NCM não localizado') if res.status_code == 200 else "NCM Inválido"

            # Busca na base local
            match = None
            if df_base is not None:
                for idx, row in df_base.iterrows():
                    if ncm_input.startswith(row['NCM_Busca']):
                        match = row
                        break

            st.markdown("### Resultado da Consulta")
            
            if match is not None:
                # Simulando a estrutura do JSON enviado
                st.markdown(f"""
                <div class="card-resultado">
                    <div class="secao-titulo">DADOS GERAIS</div>
                    <div class="dado-linha"><span class="label">NCM:</span> <span class="valor">{ncm_input}</span></div>
                    <div class="dado-linha"><span class="label">Descrição:</span> <span class="valor">{desc_api}</span></div>
                    <div class="dado-linha"><span class="label">Grupo:</span> <span class="valor">{match.get('Grupo/Subgrupo NCM', 'N/A')}</span></div>
                    <div class="dado-linha"><span class="label">Monofásico:</span> <span class="status-sim">SIM (Incidência Monofásica)</span></div>
                    
                    <div class="secao-titulo" style="margin-top:20px;">ENQUADRAMENTO (CST)</div>
                    <div class="dado-linha"><span class="label">CST Fabricante/Importador:</span> <span class="valor">02</span></div>
                    <div class="dado-linha"><span class="label">CST Atacado:</span> <span class="valor">04</span></div>
                    <div class="dado-linha"><span class="label">CST Varejo:</span> <span class="valor">04</span></div>
                    
                    <div class="secao-titulo" style="margin-top:20px;">ALÍQUOTAS</div>
                    <div class="dado-linha"><span class="label">PIS Fabricante:</span> <span class="valor">{match.get('PIS', '2.20%')}</span></div>
                    <div class="dado-linha"><span class="label">COFINS Fabricante:</span> <span class="valor">{match.get('COFINS', '10.30%')}</span></div>
                    <div class="dado-linha"><span class="label">PIS/COFINS (Atacado/Varejo):</span> <span class="valor">0.00% (Alíquota Zero)</span></div>
                    
                    <div class="secao-titulo" style="margin-top:20px;">FUNDAMENTAÇÃO LEGAL</div>
                    <div style="font-size: 13px; color: #555;">{match.get('Fundamentação', 'Baseado na Lei 10.147/00 e Tabela 4.3.10 do SPED.')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Este produto segue a tributação normal (CST 01) ou não consta na lista de monofásicos.")
    else:
        st.error("Por favor, digite um NCM válido.")
