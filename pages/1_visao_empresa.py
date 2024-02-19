#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon = '☑️', layout='wide')

df_raw = pd.read_csv('dataset/train.csv')
df3 = df_raw.copy()

#Limpeza do DataFrame

# 1. Excluir as linhas vazias
linhas_vazias = (df3['Delivery_person_Age'] != 'NaN ')
df3 = df3.loc[linhas_vazias, :]

linhas_vazias = (df3['Road_traffic_density'] != 'NaN ')
df3 = df3.loc[linhas_vazias, :]

linhas_vazias = (df3['City'] != 'NaN ')
df3 = df3.loc[linhas_vazias, :]

linhas_vazias = (df3['Festival'] != 'NaN ')
df3 = df3.loc[linhas_vazias, :]

# 2. Conversão de texto/categoria/string para numeros inteiros
df3['Delivery_person_Age'] = df3['Delivery_person_Age'].astype(int)

# 3. Conversão de texto/categoria/string para numeros decimais
df3['Delivery_person_Ratings'] = df3['Delivery_person_Ratings'].astype(float)

# 4. Conversão de texto para data
df3['Order_Date'] = pd.to_datetime(df3['Order_Date'], format='%d-%m-%Y')

# 5. Remove as linhas da coluna multiple_deliveries com valor 'Nan '
linhas_vazias = (df3['multiple_deliveries'] != 'NaN ')
df3 = df3.loc[linhas_vazias, :]
df3['multiple_deliveries'] = df3['multiple_deliveries'].astype(int)

# 6. Remover spaços da string/texto/object
df3.loc[:, 'ID'] = df3.loc[:, 'ID'].str.strip()
df3.loc[:, 'Road_traffic_density'] = df3.loc[:, 'Road_traffic_density'].str.strip()
df3.loc[:, 'Type_of_order'] = df3.loc[:, 'Type_of_order'].str.strip()
df3.loc[:, 'Type_of_vehicle'] = df3.loc[:, 'Type_of_vehicle'].str.strip()
df3.loc[:, 'City'] = df3.loc[:, 'City'].str.strip()
df3.loc[:, 'Festival'] = df3.loc[:, 'Festival'].str.strip()

# 7. Limpar a coluna Time_taken
df3['Time_taken(min)'] = df3['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
df3['Time_taken(min)'] = df3['Time_taken(min)'].astype(int)

#print(df3.head())
#print(df3.dtypes)

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

#Filtros de Data
linhas_selecionadas = df3['Order_Date'] < date_slider
df3 = df3.loc[linhas_selecionadas, :]

#Filtros densidade de trânsito
linhas_selecionadas = df3['Road_traffic_density'].isin(traffic_options)
df3 = df3.loc[linhas_selecionadas, :]
#st.dataframe(df3)
                          

#===============================================================
# Layout no Streamlit
#===============================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        st.markdown("# Orders by Day")

        #Colunas
        cols = ['ID', 'Order_Date']

        #Selecao de linhas
        df_aux = df3.loc[:, cols].groupby('Order_Date').count().reset_index()
        #Necessário resetar o index para que a coluna Order_Date se torne uma coluna

        #Desenhar o gráfico de linhas
        #Bibliotecas: Matplotlib, Seabord, Plotly
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Traffic Order Share")
            df_aux = df3.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN ", :]
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum() #criando coluna de cálculo de porcentagem

            fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header("Traffic Order City") 
            #Gráfico de Bolhas
            df_aux = df3.loc[:, ['ID', 'City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN ", :]
            df_aux = df_aux.loc[df_aux['City'] != "NaN ", :]
            
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)
    
    
with tab2:
    with st.container():
        st.markdown("# Order by Week")

        #Criando cálculo da semana - criar coluna semana
        df3['week_of_year'] = df3['Order_Date'].dt.strftime('%U')  #Mascara %U tendo a segunda como primeiro dia da semana

        cols = ['ID', 'week_of_year']

        #Selecao de linhas
        df_aux = df3.loc[:, cols].groupby('week_of_year').count().reset_index()

        #Desenhar o gráfico de linhas
        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        st.markdown("# Order Share by Week")
        #Qtde de pedidos por semana/ Nº único de entregadorees por semana
        df_aux1 = df3.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = df3.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        #unindo dois dataframes com MERGE
        df_aux = pd.merge(df_aux1, df_aux2, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        #Plotando gráfico de linhas
        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container_width=True)
    
with tab3:
    st.markdown("# Country Maps")
    
    #Criação de um Mapa por meio da biblioteca FOLIUM
    df_aux = df3.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN ", :]
    df_aux = df_aux.loc[df_aux['City'] != "NaN ", :]
    
    map = folium.Map()

    #Plotando pontos no mapa por meio do MAKER
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                     popup=location_info[['City','Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024 , height=600)





