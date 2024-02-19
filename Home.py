import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="📈"
)

image_path = 'analytics.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("#Cury Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Méticas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização
    ###    
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    ###    
    - Visão Restaurantes:    
        - Indicadores semanais de crescimento dos restaurantes
    
    ### Aks for Help
    - Time de Data Science no Discord
        - @brunogoriano
""")