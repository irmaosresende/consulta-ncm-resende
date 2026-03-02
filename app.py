import streamlit as st
import pandas as pd
import requests

# 1. Configuração de Layout da Página
st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# 2. Estilização CSS para Visual de Página da Internet
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Container Principal */
    .report-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border-top: 8px solid #002e5d;
        margin-top: 30px;
    }

    /* Título do Resultado */
    .title-result {
        color: #002e5d;
        font-size: 26px;
        font-weight: 700;
        border-bottom: 2px solid #eef2f6;
        padding-bottom: 15px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .badge-status {
        background-color: #e1effe;
        color: #004a94;
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 14px;
        font-weight: 600;
    }

    /* Seções de Informação */
    .info-box { margin-bottom: 20px; }
    .info-tag { color: #8a94a6; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
    .info-text { color: #1a202c; font-size: 18px; font-weight: 500; margin-top: 5px; }

    /* Grid de Tributação (Azul Claro) */
    .tax-card {
        background-color: #f8fbff;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        padding: 25px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin: 25px 0;
    }

    .tax-item { display: flex; flex-direction: column; }
    .tax-label { color: #4a5568; font-size: 12px; font-weight: 600; }
    .tax-value { color: #002e5d; font-size: 20px; font-weight: 700; }

    /* Rodapé / Base Legal */
    .legal-footer {
        background-color: #f1f5f9;
        padding: 20px;
        border-radius: 8px;
        font-size: 14px;
        color: #475569;
        line-height: 1.6;
        border-left: 4px solid #002e5d;
    }
    
    .stButton>button {
        background-color: #002e5d;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Interface de Busca
st.markdown("<h2 style='text-align: center; color: #002e5d;'>Consulta Tributária</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-top: -15px;'>Irmãos Resende Consultoria Especializada</p>", unsafe_allow_html=True)

@st.cache_data
def get_database():
    try:
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        df['NCM_Clean'] = df['NCM'].str.replace('.', '', regex=False).str.strip()
        return df
    except: return None

db = get_database()
ncm_input = st.text_input("Insira o NCM do Produto:", placeholder="Ex: 33051000").replace('.', '').strip()

if st.button("GERAR RELATÓRIO"):
    if len(ncm_input) >= 4:
        # Busca API BrasilAPI
        res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_input}")
        oficial_desc = res.json().get('descricao', 'NCM não catalogado') if res.status_code == 200 else "NCM Inválido"

        # Busca Base Local
        match = None
        if db is not None:
            for _, row in db.iterrows():
                if ncm_input.startswith(str(row['NCM_Clean'])):
                    match = row
                    break

        if match is not None:
            # RENDERIZAÇÃO DO MODO PÁGINA WEB
            st.markdown(f"""
                <div class="report-container">
                    <div class="title-result">
                        <span>Resultado da Consulta</span>
                        <span class="badge-status">INCIDÊNCIA MONOFÁSICA</span>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-tag">NCM Analisado</div>
                        <div class="info-text">{ncm_input}</div>
                    </div>

                    <div class="info-box">
                        <div class="info-tag">Descrição do Produto</div>
                        <div class="info-text">{oficial_desc}</div>
                    </div>

                    <div class="info-box">
                        <div class="info-tag">Classificação Tabela 4.3.10</div>
                        <div class="info-text">{match.get('Descrição', match.get('Descricao', 'Geral'))}</div>
                    </div>

                    <div class="tax-card">
                        <div class="tax-item">
                            <span class="tax-label">CST Saída (Varejo)</span>
                            <span class="tax-value">04 - Alíq. Zero</span>
                        </div>
                        <div class="tax-item">
                            <span class="tax-label">CST Entrada</span>
                            <span class="tax-value">02 / 70</span>
                        </div>
                        <div class="tax-item">
                            <span class="tax-label">Alíquota PIS</span>
                            <span class="tax-value">{match.get('PIS', '2,10%')}</span>
                        </div>
                        <div class="tax-item">
                            <span class="tax-label">Alíquota COFINS</span>
                            <span class="tax-value">{match.get('COFINS', '10,30%')}</span>
                        </div>
                    </div>

                    <div class="legal-footer">
                        <strong>FUNDAMENTAÇÃO LEGAL:</strong><br>
                        {match.get('Fundamentação', match.get('Fundamentacao', 'Conforme diretrizes da Lei 10.147/00 e Tabela 4.3.10 do SPED.'))}
                    </div>
                    
                    <p style="text-align:center; font-size:11px; color:#94a3b8; margin-top:30px;">
                        Relatório oficial gerado em 2026 para Irmãos Resende Consultoria.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Este produto não foi identificado como Monofásico nos grupos da Tabela 4.3.10.")
    else:
        st.error("Por favor, digite um NCM válido.")

st.markdown("<br><br>", unsafe_allow_html=True)
