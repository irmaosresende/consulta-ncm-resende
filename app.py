import streamlit as st
import pandas as pd
import requests

# 1. Configurações Iniciais da Página
st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

# 2. Estilização Visual Premium (Azul Escuro e Azul Claro)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Botão de Consulta - Azul Escuro */
    .stButton>button { 
        width: 100%; background-color: #002e5d; color: white; 
        font-weight: 700; border-radius: 8px; height: 3.8em; border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;
        text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #004a94; color: #ffffff; border: none; }
    
    /* Card Principal de Resultado */
    .main-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-left: 8px solid #002e5d;
        margin-top: 25px;
        border-right: 1px solid #e1effe;
        border-top: 1px solid #e1effe;
        border-bottom: 1px solid #e1effe;
    }
    
    /* Título do Resultado */
    .titulo-resultado {
        color: #002e5d;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e1effe;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Selo Monofásico - Azul Claro */
    .status-badge {
        background-color: #e1effe;
        color: #004a94;
        padding: 6px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Labels e Valores */
    .info-label { color: #6b7280; font-size: 11px; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
    .info-valor { color: #111827; font-size: 15px; font-weight: 500; margin-bottom: 15px; }
    
    /* Grelha de Impostos - Azul Suave */
    .tax-grid {
        background-color: #f0f7ff; 
        padding: 18px;
        border-radius: 10px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        border: 1px solid #d0e7ff;
    }
    
    /* Secção de Base Legal */
    .law-section {
        margin-top: 20px;
        padding: 15px;
        background-color: #ffffff;
        border: 1px dashed #002e5d;
        border-radius: 8px;
        font-size: 13px;
        color: #374151;
        line-height: 1.5;
    }
    
    .destaque-azul { color: #002e5d; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho de Identidade
st.title("🔍 Inteligência Tributária")
st.markdown("<h4 style='color: #004a94; margin-top: -20px;'>Irmãos Resende Consultoria</h4>", unsafe_allow_html=True)

# 4. Função para Carregar Dados do GitHub
@st.cache_data
def carregar_dados():
    try:
        # Tenta ler o arquivo base.csv
        df = pd.read_csv('base.csv', dtype={'NCM': str})
        # Limpa o NCM para busca (remove pontos e pega o prefixo)
        df['NCM_Busca'] = df['NCM'].astype(str).str.replace('.', '', regex=False).str.strip().str.split(' ').str[0]
        return df
    except:
        st.error("Erro: Certifique-se de que o arquivo 'base.csv' existe no repositório.")
        return None

df_base = carregar_dados()

# 5. Entrada do Usuário
ncm_digitado = st.text_input("Digite o código NCM:", placeholder="Ex: 33051000").replace('.', '').strip()

if st.button("ANALISAR AGORA"):
    if len(ncm_digitado) >= 4:
        with st.spinner('Cruzando dados com a Tabela 4.3.10...'):
            # Busca descrição oficial via BrasilAPI
            try:
                res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_digitado}")
                desc_api = res.json().get('descricao', 'Descrição não encontrada') if res.status_code == 200 else "NCM não localizado"
            except:
                desc_api = "Serviço de descrição temporariamente indisponível"

            # Busca na planilha local
            match = None
            if df_base is not None:
                for _, row in df_base.iterrows():
                    if ncm_digitado.startswith(str(row['NCM_Busca'])):
                        match = row
                        break

            # 6. Exibição do Resultado Estilizado
            if match is not None:
                st.markdown(f"""
                <div class="main-card">
                    <div class="titulo-resultado">
                        <span>Resultado da Consulta</span>
                        <span class="status-badge">Monofásico</span>
                    </div>
                    
                    <div class="info-group">
                        <div class="info-label">Descrição do Produto (BrasilAPI)</div>
                        <div class="info-valor">{desc_api}</div>
                    </div>

                    <div class="info-group">
                        <div class="info-label">Enquadramento Legal</div>
                        <div class="info-valor">{match.get('Descricao', match.get('Descrição', 'Item Monofásico Identificado'))}</div>
                    </div>
                    
                    <div class="tax-grid">
                        <div>
                            <div class="info-label">CST Varejo (Saída)</div>
                            <div class="info-valor destaque-azul">04 - Alíquota Zero</div>
                        </div>
                        <div>
                            <div class="info-label">CST Indústria (Entrada)</div>
                            <div class="info-valor">02 - Diferenciada</div>
                        </div>
                        <div>
                            <div class="info-label">PIS (Fabricante/Importador)</div>
                            <div class="info-valor">{match.get('PIS', 'Consultar Tabela')}</div>
                        </div>
                        <div>
                            <div class="info-label">COFINS (Fabricante/Importador)</div>
                            <div class="info-valor">{match.get('COFINS', 'Consultar Tabela')}</div>
                        </div>
                    </div>

                    <div class="law-section">
                        <span class="destaque-azul">FUNDAMENTAÇÃO JURÍDICA:</span><br>
                        {match.get('Fundamentacao', match.get('Fundamentação', 'Conforme Tabela 4.3.10 do SPED e legislação federal.'))}
                        <br><br>
                        <small><i>*Atenção: Revendedores varejistas devem utilizar Alíquota Zero conforme Art. 28 da Lei 13.097/2015.</i></small>
                    </div>
                    
                    <p style="text-align:center; font-size:10px; color:#9ca3af; margin-top:20px;">
                        Irmãos Resende Consultoria - © 2026 | Inteligência em Gestão Fiscal
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ PRODUTO COM TRIBUTAÇÃO NORMAL")
                st.info(f"O NCM {ncm_digitado} não consta na Tabela 4.3.10 de incidência monofásica.")
                st.markdown(f"**Descrição Oficial:** {desc_api}")
    else:
        st.error("Por favor, informe um NCM válido (mínimo 4 dígitos).")

st.markdown("---")
st.caption("Base: Tabela 4.3.10 do SPED (Versão 1.24) - Consultoria Irmãos Resende")
