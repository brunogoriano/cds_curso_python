#Bibliotecas
import pandas as pd
import streamlit as st
from PIL import Image

#===============================================================
# Barra Lateral
#===============================================================
st.header('Marketplace - Visão Cliente')

image_path = 'analytics.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('##Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 1),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.header(date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Bruno Goriano')

#===============================================================
# Layout no Streamlit
#===============================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    
    st.markdown("# Teste 01")
with tab2:
    st.markdown("# Teste 02")
with tab3:
    st.markdown("# Teste 03")