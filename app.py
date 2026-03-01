import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Consulta NCM - Irmãos Resende", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #002e5d; color: white; font-weight: bold; }
    .card-resultado { padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #fff; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .secao-titulo { font-weight: bold; color: #002e5d; border-bottom: 1px solid #eee; margin-bottom: 10px; padding-bottom: 5px; }
    .dado-linha { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; }
    .label { color: #666; font-weight: 500; }
    .valor { color: #333; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Consulta Tributária Monofásica")
st.subheader("Irmãos Resende - Inteligência Fiscal")

@st.cache_data
def carregar_dados():
    try:
        # Tenta ler o CSV. Se falhar, avisa o usuário.
        df = pd.read_csv('base.csv', dtype={'NCM': str}, sep=None, engine='python')
        # Limpa a coluna NCM para comparação
        df['NCM_Busca'] = df['NCM'].str.replace('.', '', regex=False).str.strip().str.split(' ').str[0]
        return df
    except Exception as e:
        st.error(f"Erro ao ler base.csv no GitHub: {e}")
        return None

df_base = carregar_dados()

ncm_input = st.text_input("Digite o NCM (8 dígitos):", placeholder="Ex: 33051000").replace('.', '').strip()

if st.button("Consultar Agora"):
    if len(ncm_input) >= 4:
        with st.spinner('Buscando dados...'):
            # 1. API BrasilAPI para descrição oficial
            res = requests.get(f"https://brasilapi.com.br/api/ncm/v1/{ncm_input}")
            desc_api = res.json().get('descricao', 'NCM não localizado na base da Receita') if res.status_code == 200 else "NCM Inválido"

            # 2. Busca na base do GitHub
            match = None
            if df_base is not None:
                # Procura se o NCM digitado começa com algum NCM da planilha
                for _, row in df_base.iterrows():
                    if ncm_input.startswith(str(row['NCM_Busca'])):
                        match = row
                        break

            st.markdown("### Resultado da Consulta")
            
            if match is not None:
                # Pegando os dados de forma segura (se a coluna não existir, mostra 'N/A')
                # O .get() evita erros se o nome da coluna no CSV mudar
                desc_planilha = match.get('Descricao', match.get('Descrição', desc_api))
                grupo = match.get('Grupo', match.get('Grupo/Subgrupo NCM', 'Geral'))
                pis = match.get('PIS', '2,10%')
                cofins = match.get('COFINS', '9,90%')
                lei = match.get('Fundamentacao', match.get('Fundamentação', 'Lei 10.147/00'))

                st.markdown(f"""
                <div class="card-resultado">
                    <div class="secao-titulo">DADOS DO PRODUTO</div>
                    <div class="dado-linha"><span class="label">NCM Consultado:</span> <span class="valor">{ncm_input}</span></div>
                    <div class="dado-linha"><span class="label">Descrição Oficial:</span> <span class="valor">{desc_api}</span></div>
                    <div class="dado-linha"><span class="label">Enquadramento:</span> <span class="valor" style="color:green;">MONOFÁSICO</span></div>
                    
                    <div class="secao-titulo" style="margin-top:20px;">REGRAS DE CST (SAÍDA)</div>
                    <div class="dado-linha"><span class="label">Atacado / Varejo:</span> <span class="valor">CST 04 (Alíquota Zero)</span></div>
                    <div class="dado-linha"><span class="label">Indústria / Importação:</span> <span class="valor">CST 02 (Alíq. Diferenciada)</span></div>
                    
                    <div class="secao-titulo" style="margin-top:20px;">ALÍQUOTAS (FABRICANTE)</div>
                    <div class="dado-linha"><span class="label">PIS:</span> <span class="valor">{pis}</span></div>
                    <div class="dado-linha"><span class="label">COFINS:</span> <span class="valor">{cofins}</span></div>
                    
                    <div class="secao-titulo" style="margin-top:20px;">BASE LEGAL</div>
                    <div style="font-size: 13px; color: #555;">{lei}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Este NCM não foi localizado na lista de produtos monofásicos.")
                st.info(f"**Descrição Oficial:** {desc_api}")
    else:
        st.error("Digite pelo menos 4 dígitos do NCM.")

st.markdown("---")
st.caption("Irmãos Resende - Inteligência Tributária")
