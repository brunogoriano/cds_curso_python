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

st.set_page_config(page_title='Visão Entregadores', page_icon = '🚚', layout='wide')

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

#===============================================================
# Barra Lateral
#===============================================================
st.header('Marketplace - Visão Entregadores')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #Maior idade dos entregadores
            maior_idade = df3.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)

            
        with col2:
            #Menor idade dos entregadores
            menor_idade = df3.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade)
   

        with col3:
            #Melhor condição do veículos
            melhor_veiculos = df3.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_veiculos)
            
        with col4:
            #Pior condição do veículos
            pior_veiculos = df3.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_veiculos)
      
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            df_avg_ratings_per_delivery = (df3.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                               .groupby('Delivery_person_ID')
                                               .mean()
                                               .reset_index())
            st.dataframe(df_avg_ratings_per_delivery)
        
        with col2:
            st.markdown('##### Avaliação média por trâmsito')
            
            df_std = (df3.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                          .groupby('Road_traffic_density')
                          .mean()
                          .reset_index())
            df_std = (df3.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                          .groupby('Road_traffic_density')
                          .std()
                          .reset_index())
            
            #Unificando ambos cálculos em uma mesma tabela por meio do AGG
            df_aux = (df3.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                         .groupby('Road_traffic_density')
                         .agg({'Delivery_person_Ratings': ['mean','std' ]}))

            df_aux.columns = ['delivery_mean', 'delivery_std'] #mudança de nome das colunas
            df_aux = df_aux.reset_index()
            
            st.dataframe(df_aux)         
            
            
            st.markdown('##### Avaliação média por clima')
            
            df_avg_std_by_weather = (df3.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                                         .groupby('Weatherconditions')
                                         .agg({'Delivery_person_Ratings': ['mean','std' ]}))
            df_avg_std_by_weather.columns = ['Weatherconditionsy_mean', 'Weatherconditions_std'] #mudança de nome das colunas
            df_avg_std_by_weather = df_avg_std_by_weather.reset_index()
            st.dataframe(df_avg_std_by_weather)  
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
    
        col1, col2 = st.columns(2)        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            
            df_aux = (df3.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                          .groupby(['City', 'Delivery_person_ID'])
                          .min()
                          .sort_values(['City','Time_taken(min)'], ascending=True)
                          .reset_index())

            df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
            df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

            df4 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df4)
        
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            
            df_aux = (df3.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                          .groupby(['City', 'Delivery_person_ID'])
                          .max().sort_values(['City','Time_taken(min)'], ascending=False)
                          .reset_index())

            df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
            df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

            df4 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df4)
