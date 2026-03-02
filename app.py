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
    
    /* Botão Principal em Azul Escuro */
    .stButton>button { 
        width: 100%; background-color: #002e5d; color: white; 
        font-weight: 700; border-radius: 8px; height: 3.5em; border: none;
        text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #004a94; color: white; border: none; }
    
    /* Card de Resultado Profissional */
    .main-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border-left: 10px solid #002e5d;
        margin-top: 25px;
        border-top: 1px solid #e1effe;
        border-right: 1px solid #e1effe;
        border-bottom: 1px solid #e1effe;
    }
    
    /* Cabeçalho do Card */
    .titulo-resultado {
        color: #002e5d;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #f0f7ff;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .status-badge {
        background-color: #e1effe;
        color: #004a94;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    /* Organização de Informações */
    .info-label { color: #6b7280; font-size: 11px; text-transform: uppercase; font-weight: 600; margin-bottom: 2px; }
    .info-valor { color: #111827; font-size: 15px; font-weight: 500; margin-bottom: 15px; }
    
    /* Grid de Impostos em Azul Claro */
    .tax-container {
        background-color: #f0f7ff; 
        padding: 20px;
        border-radius: 10px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        border: 1px solid #d0e7ff;
        margin: 15px 0;
    }
    
    .destaque-navy { color: #002e5d; font-weight: 700; }
    
    /* Box de Base Legal */
    .base-legal-box {
        font-size: 13px;
        background: #ffffff;
        padding: 15px;
        border: 1px dashed #002e5d;
        border-radius: 8px;
        color: #374151;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Logo e Título Superior
st.markdown("<h2 style='text-align: center; color: #002e5d; margin-bottom: 0;'>Inteligência Tributária</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #004a94; font-weight: 500;'>Irmãos Resende Consultoria</p>", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    try:
        # Lê a base do GitHub (ajuste o nome se necessário)
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        # Limpa o NCM para busca (remove pontos e espaços)
        df['NCM_Match'] = df['NCM'].astype(str).str.replace('.', '', regex=False).str.strip()
        return df
    except:
        return None

df_base = carregar_dados()

# 4. Campo de Busca
ncm_query = st.text_input("Digite o NCM (8 dígitos):", placeholder="Ex: 33051000").replace('.', '').strip()

if st.button("Analisar Tributação"):
    if len(ncm_query) >= 4:
        with st.spinner('Consultando base legal...'):
            # Consulta Descrição via BrasilAPI
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_query}")
            desc_oficial = res.json().get('descricao', 'Descrição não disponível') if res.status_code == 200 else "NCM Inválido"

            # Busca na Planilha base.csv
            match = None
            if df_base is not None:
                for _, row in df_base.iterrows():
                    # Permite busca por prefixo (ex: digitar 33051000 e achar 3305 na tabela)
                    if ncm_query.startswith(str(row['NCM_Match'])):
                        match = row
                        break

            # 5. RESULTADO FINAL
            if match is not None:
                st.markdown(f"""
                <div class="main-card">
                    <div class="titulo-resultado">
                        <span>Resultado da Consulta</span>
                        <span class="status-badge">Monofásico</span>
                    </div>
                    
                    <div class="info-label">Descrição do Produto</div>
                    <div class="info-valor">{desc_oficial}</div>
                    
                    <div class="info-label">Grupo / Enquadramento</div>
                    <div class="info-valor">{match.get('Descrição', match.get('Descricao', 'Item Monofásico'))}</div>

                    <div class="tax-container">
                        <div>
                            <div class="info-label">CST Varejo (Saída)</div>
                            <div class="info-valor destaque-navy">04 - Alíquota Zero</div>
                        </div>
                        <div>
                            <div class="info-label">CST Indústria (Entrada)</div>
                            <div class="info-valor">02 - Diferenciada</div>
                        </div>
                        <div>
                            <div class="info-label">PIS (Fabricante)</div>
                            <div class="info-valor">{match.get('PIS', '---')}</div>
                        </div>
                        <div>
                            <div class="info-label">COFINS (Fabricante)</div>
                            <div class="info-valor">{match.get('COFINS', '---')}</div>
                        </div>
                    </div>

                    <div class="base-legal-box">
                        <span class="destaque-navy">FUNDAMENTAÇÃO LEGAL:</span><br>
                        {match.get('Fundamentação', match.get('Fundamentacao', 'Conforme Tabela 4.3.10 do SPED.'))}
                    </div>
                    
                    <p style="text-align:center; font-size:10px; color:#9ca3af; margin-top:20px;">
                        Relatório Gerado por Irmãos Resende Consultoria - © 2026
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="padding:20px; border-radius:10px; background-color:#fff5f5; border:1px solid #feb2b2; margin-top:20px;">
                    <h4 style="color:#c53030; margin:0;">Tributação Normal</h4>
                    <p style="color:#742a2a; margin-top:10px;">O NCM <b>{ncm_query}</b> não foi identificado como monofásico nesta base.</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Informe pelo menos 4 dígitos para a busca.")

st.markdown("---")
st.caption("Irmãos Resende | Base: Tabela 4.3.10 do SPED (Versão 1.24)")
