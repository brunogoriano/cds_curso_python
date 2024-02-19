#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas
import pandas as pd
import numpy as np
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes', page_icon = '🍽️', layout='wide')

#Limpeza do DataFrame
df_raw = pd.read_csv('dataset/train.csv')
df3 = df_raw.copy()

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
st.header('Marketplace - Visão Restaurantes')

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
        st.title("Overal Metrics | Entrega")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df3.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Qtde Entregadores', delivery_unique) 
            
        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df3['distance'] = (df3.loc[:, cols].apply(lambda x:
                                haversine(
                                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 ))
            avg_distance = np.round(df3['distance'].mean(), 2)
            
            col2.metric('Distância (AVG)', avg_distance) 
            
        with col3:            
            cols = ['Time_taken(min)', 'Festival']
            df_aux = (df3.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time' ], 2)

            col3.metric('TME | Festival', df_aux)
            
        with col4:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = (df3.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time' ], 2)

            col4.metric('DP | Festival', df_aux)
            
        with col5:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = (df3.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time' ], 2)

            col5.metric('TME | NO Festival', df_aux)
            
        with col6: 
            cols = ['Time_taken(min)', 'Festival']
            df_aux = (df3.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time' ], 2)

            col6.metric('DP | NO Festival', df_aux)
                        
    
    with st.container():
        st.markdown("""---""")
        st.markdown('### Tempo Médio de entrega por cidade')
        df_aux = (df3.loc[:, ['City', 'Time_taken(min)']]
                          .groupby('City')
                          .agg({'Time_taken(min)': ['mean', 'std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        fig = go.Figure()
        fig.add_trace( go.Bar( name='Control',
                                      x=df_aux['City'],
                                      y=df_aux['avg_time'], 
                                      error_y = dict( type='data', array=df_aux['std_time'])))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
                
    with st.container():
        st.markdown("""---""")
        st.title("Distribuição do Tempo")
               
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Tempo Medio de entrega por cidade')
            cols = ['Delivery_location_latitude',
                    'Delivery_location_longitude',
                    'Restaurant_latitude',
                    'Restaurant_longitude']
            df3['distance'] = (df3.loc[:, cols].apply(lambda x:
                                    haversine(
                                                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude']))
                                                      ,axis=1 ))
            avg_distance = df3.loc[: , ['City', 'distance']].groupby('City').mean().reset_index()

            fig = (go.Figure(data=[go.Pie(labels=avg_distance['City']
                                         , values=avg_distance['distance']
                                         , pull=[0, 0.1, 0])]))
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown('###### Desvio Padrão por Cidade e Tráfego')
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = (df3.loc[:, cols]
                          .groupby(['City', 'Road_traffic_density'])
                          .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.title("Distribuição da Distancia")
        
        df_aux = (df3.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                      .groupby(['City', 'Type_of_order'])
                      .agg({'Time_taken(min)': ['mean', 'std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)