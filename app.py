import streamlit as st
import pandas as pd
import requests

# 1. Configurações da Página
st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# 2. Estilização CSS (Azul Escuro e Azul Claro)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Botão Principal */
    .stButton>button { 
        width: 100%; background-color: #002e5d; color: white; 
        font-weight: 700; border-radius: 8px; height: 3.5em; border: none;
        text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #004a94; color: white; }
    
    /* Card de Resultado */
    .main-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border-left: 10px solid #002e5d;
        margin-top: 20px;
        border-top: 1px solid #e1effe;
        border-right: 1px solid #e1effe;
        border-bottom: 1px solid #e1effe;
    }
    
    /* Título Resultado da Consulta */
    .titulo-resultado {
        color: #002e5d;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f7ff;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .badge-monofasico {
        background-color: #e1effe;
        color: #004a94;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
    }
    
    /* Labels e Textos */
    .label-blue { color: #6b7280; font-size: 11px; text-transform: uppercase; font-weight: 600; }
    .valor-dados { color: #111827; font-size: 15px; font-weight: 500; margin-bottom: 12px; }
    
    /* Caixa de Alíquotas */
    .tax-container {
        background-color: #f0f7ff; 
        padding: 15px;
        border-radius: 8px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        border: 1px solid #d0e7ff;
        margin: 15px 0;
    }
    
    .destaque-navy { color: #002e5d; font-weight: 700; }
    
    .base-legal-box {
        font-size: 13px;
        background: #fdfdfd;
        padding: 12px;
        border: 1px dashed #002e5d;
        border-radius: 6px;
        color: #4b5563;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho
st.markdown("<h2 style='text-align: center; color: #002e5d;'>Inteligência Tributária</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #004a94; margin-top: -15px;'>Irmãos Resende Consultoria</p>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Carrega a base.csv (deve estar no mesmo diretório no GitHub)
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        df['NCM_Match'] = df['NCM'].str.replace('.', '', regex=False).str.strip().str.split(' ').str[0]
        return df
    except:
        return None

df_base = load_data()

# 4. Input
ncm_query = st.text_input("Digite o NCM para análise:", placeholder="Somente números").replace('.', '').strip()

if st.button("Consultar"):
    if len(ncm_query) >= 4:
        with st.spinner('Buscando dados...'):
            # Descrição da API
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_query}")
            desc_oficial = res.json().get('descricao', 'NCM não localizado') if res.status_code == 200 else "NCM Inválido"

            # Busca na Planilha
            match = None
            if df_base is not None:
                for _, row in df_base.iterrows():
                    if ncm_query.startswith(str(row['NCM_Match'])):
                        match = row
                        break

            if match is not None:
                st.markdown(f"""
                <div class="main-card">
                    <div class="titulo-resultado">
                        <span>Resultado da Consulta</span>
                        <span class="badge-monofasico">Monofásico</span>
                    </div>
                    
                    <div class="label-blue">Descrição do Produto</div>
                    <div class="valor-dados">{desc_oficial}</div>
                    
                    <div class="label-blue">Grupo / Enquadramento</div>
                    <div class="valor-dados">{match.get('Descricao', match.get('Descrição', 'Geral'))}</div>

                    <div class="tax-container">
                        <div>
                            <div class="label-blue">CST Varejo</div>
                            <div class="valor-dados destaque-navy">04 - Alíquota Zero</div>
                        </div>
                        <div>
                            <div class="label-blue">CST Indústria</div>
                            <div class="valor-dados">02 - Diferenciada</div>
                        </div>
                        <div>
                            <div class="label-blue">PIS (Fabricante)</div>
                            <div class="valor-dados">{match.get('PIS', '2,10%')}</div>
                        </div>
                        <div>
                            <div class="label-blue">COFINS (Fabricante)</div>
                            <div class="valor-dados">{match.get('COFINS', '9,90%')}</div>
                        </div>
                    </div>

                    <div class="base-legal-box">
                        <b class="destaque-navy">FUNDAMENTAÇÃO:</b><br>
                        {match.get('Fundamentacao', match.get('Fundamentação', 'Conforme Tabela 4.3.10 do SPED.'))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠️ PRODUTO COM TRIBUTAÇÃO NORMAL (CST 01)")
                st.write(f"**NCM:** {ncm_query} - {desc_oficial}")
    else:
        st.warning("Informe pelo menos 4 dígitos do NCM.")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("© 2026 Irmãos Resende Consultoria | Tabela 4.3.10")
