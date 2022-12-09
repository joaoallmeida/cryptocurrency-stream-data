from configparser import ConfigParser
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import pymongo
import time

## Config Web Page
st.set_page_config(
    page_title="Cryptocurrency Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

@st.experimental_memo
def getCryptoData():
    
    config = ConfigParser()
    config.read('env.ini')

    credentials = config['MONGODB']
    connStr = f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority"

    mongoClient = pymongo.MongoClient(connStr)
    dataBase = mongoClient['financial']
    collection = dataBase['crypto']
    data = collection.find()

    df = pd.DataFrame(data).drop(['_id'],axis=1)
    df['priceUsd'] = round(df['priceUsd'].astype('str').astype('float'),3)
    df['marketCapUsd'] = round(df['marketCapUsd'].astype('str').astype('float'),2)

    return df

df = getCryptoData()


## Filter
col01 , col02 = st.columns(2)

with col01:
    dateFilterStart, dateFilterEnd = st.date_input('Filter by Date',value=[df['timestamp'].min(),df['timestamp'].max()])
with col02:
    symbolFilter = st.selectbox('Select The Symbol',options=df['symbol'].head(100).unique())


dfSelection = df[ 
    ((df['timestamp'].dt.date >= dateFilterStart) & (df['timestamp'].dt.date <= dateFilterEnd)) 
    & (df['symbol'] == symbolFilter) 
]


placeholder = st.empty()

while True:

    ## Create KPI header
    cryptoName = dfSelection['name'].unique()[0]
    cryptoPosition = dfSelection['rank'].unique()[0]
    currentPrice = round(dfSelection.sort_values("timestamp",ascending=False)["priceUsd"].values[0],2)
    currentSupply = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['supply'].values[0])),2)
    maxSupply = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['maxSupply'].values[0])),2)
    marketCapUsd = dfSelection.sort_values("timestamp",ascending=False)['marketCapUsd'].values[0]
    volumeUsd24Hr = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['volumeUsd24Hr'].values[0])),2)


    with placeholder.container():

        st.markdown('<h1 style="text-align:center">Market Info</h1>',unsafe_allow_html=True)

        col01, col02, col03 ,col04, col05, col06,col07 = st.columns([5,10,10,10,10,12,12])

        with col01:
            st.image(f'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/128/color/{symbolFilter.lower()}.png',width=70)
        with col02:
            st.markdown(f'''## {cryptoName}''')
            st.markdown(f'###### Ranking Position {cryptoPosition}')
        with col03:
            st.markdown('#### :dollar: Price USD')
            st.markdown(f'##### $ {currentPrice:,}')
        with col04:
            st.markdown('#### :heavy_minus_sign: Supply')
            st.markdown(f'##### $ {currentSupply:,}')
        with col05:
            st.markdown('#### :chart_with_upwards_trend: Max Supply')
            st.markdown(f'##### $ {maxSupply:,}')
        with col06:
            st.markdown('#### :currency_exchange: Market Cap USD')
            st.markdown(f'##### $ {marketCapUsd:,}')
        with col07:
            st.markdown('#### :convenience_store: Volume Usd 24hr')
            st.markdown(f'##### $ {volumeUsd24Hr:,}')
            
        st.markdown("---")

        tab01, tab02 = st.tabs(['Price USD','Market Cap USD'])

        timesSeriesByPrice = dfSelection.pivot_table(index='timestamp',columns='symbol',values='priceUsd').reset_index()
        timesSeriesByMarketCap = dfSelection.pivot_table(index='timestamp', columns='symbol', values='marketCapUsd').reset_index()
        
        with tab01:
            st.subheader('Price USD')

            figLineChart = px.scatter(
                timesSeriesByPrice,
                y=timesSeriesByPrice.columns,
                x='timestamp',
                color_discrete_sequence=['#00FF8A']
            ).update_traces(mode='lines')

            st.plotly_chart(figLineChart,use_container_width=True)

        with tab02:
            st.subheader('Market Cap USD')

            figLineChart = px.scatter(
            timesSeriesByMarketCap,
            y=timesSeriesByMarketCap.columns,
            x='timestamp'
            ).update_traces(mode='lines')

            st.plotly_chart(figLineChart,use_container_width=True)

        time.sleep(1)

