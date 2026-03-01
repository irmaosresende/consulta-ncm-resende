import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# Estilização
st.markdown("""
    <style>
    .card-resultado { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background-color: #ffffff; box-shadow: 2px 2px 12px rgba(0,0,0,0.1); }
    .label-titulo { color: #002e5d; font-weight: bold; font-size: 18px; border-bottom: 2px solid #002e5d; margin-bottom: 15px; }
    .dado-corpo { margin-bottom: 8px; font-size: 15px; }
    .bold { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta Tributária Monofásica")
st.subheader("Irmãos Resende - Inteligência Fiscal")

@st.cache_data
def carregar_dados():
    try:
        # Carrega o CSV com os dados do DOC
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        return df
    except:
        return None

df_base = carregar_dados()

ncm_input = st.text_input("Digite o NCM (apenas números):", placeholder="Ex: 33030010").strip()

if st.button("Consultar Resultado"):
    if len(ncm_input) >= 4:
        with st.spinner('Cruzando dados com Tabela 4.3.10...'):
            # 1. API para Nome Oficial
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_input}")
            desc_oficial = res.json().get('descricao', 'Descrição não encontrada') if res.status_code == 200 else "NCM não localizado"

            # 2. Busca Inteligente na Planilha (Verifica se o NCM digitado começa com o NCM da Tabela)
            match = None
            if df_base is not None:
                for _, row in df_base.iterrows():
                    if ncm_input.startswith(str(row['NCM'])):
                        match = row
                        break

            st.markdown('<div class="label-titulo">Resultado da Consulta</div>', unsafe_allow_html=True)

            if match is not None:
                st.markdown(f"""
                <div class="card-resultado">
                    <div class="dado-corpo"><span class="bold">Descrição do Produto:</span> {desc_oficial}</div>
                    <div class="dado-corpo"><span class="bold">Enquadramento:</span> <span style="color:green;">MONOFÁSICO</span></div>
                    <div class="dado-corpo"><span class="bold">Código EFD (Tabela 4.3.10):</span> {match['Codigo']}</div>
                    <hr>
                    <div class="dado-corpo"><span class="bold">CST Saída (Varejo):</span> 04 - Alíquota Zero</div>
                    <div class="dado-corpo"><span class="bold">PIS (Fabricante/Imp):</span> {match['PIS']}%</div>
                    <div class="dado-corpo"><span class="bold">COFINS (Fabricante/Imp):</span> {match['COFINS']}%</div>
                    <hr>
                    <div class="dado-corpo"><span class="bold">Base Legal:</span> {match['Fundamentacao']}</div>
                    <p style="font-size:11px; color:gray; margin-top:10px;">*Dados extraídos da Versão 1.24 da Tabela 4.3.10 do SPED.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Este NCM não foi identificado como Monofásico nos grupos da Tabela 4.3.10.")
                st.info(f"**Descrição Oficial:** {desc_oficial}")
    else:
        st.error("Digite pelo menos 4 números do NCM.")

st.markdown("---")
st.caption("© 2026 Irmãos Resende | Consultoria Tributária")
