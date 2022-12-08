from configparser import ConfigParser
from datetime import datetime
import plotly.express as px
import pandas as pd
import streamlit as st
import pymongo


## Config Web Page
st.set_page_config(
    page_title="Cryptocurrency Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

@st.cache
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
    
    return df

df = getCryptoData()

st.sidebar.header("Filter")

dateFilterStart, dateFilterEnd = st.sidebar.date_input('Filter by Date',value=[df['timestamp'].min(),df['timestamp'].max()])
symbolFilter = st.sidebar.selectbox('Select The Symbol',options=df['symbol'].unique())

dfSelection = df[ 
    ((df['timestamp'].dt.date >= dateFilterStart) & (df['timestamp'].dt.date <= dateFilterEnd)) 
    & (df['symbol'] == symbolFilter) 
]

cryptoName = dfSelection['name'] .unique()[0]
timesSeriesByPrice = dfSelection.pivot_table(index='timestamp',columns='symbol',values='priceUsd').reset_index()
currentPrice = dfSelection.sort_values("timestamp",ascending=False)["priceUsd"].values[0]
currentSupply = dfSelection.sort_values("timestamp",ascending=False)['supply'].values[0]
maxSupply = dfSelection.sort_values("timestamp",ascending=False)['maxSupply'].values[0]
marketCapUsd = dfSelection.sort_values("timestamp",ascending=False)['marketCapUsd'].values[0]
volumeUsd24Hr = dfSelection.sort_values("timestamp",ascending=False)['volumeUsd24Hr'].values[0]

leftCol01, leftCol02 ,middleCol01, middleCol02, rightCol01,rightCol02 = st.columns(6)

with leftCol01:
    st.markdown(f'<h2 style="text-align:left"> <img src="https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/128/color/{symbolFilter.lower()}.png">&nbsp;&nbsp;{cryptoName}</h2>',unsafe_allow_html=True)

with leftCol02:
    st.subheader(':dollar: Price USD')
    st.subheader(f'$ {currentPrice:,}')
with middleCol01:
    st.subheader(':heavy_minus_sign: Supply')
    st.subheader(f'$ {currentSupply:,}')
with middleCol02:
    st.subheader(':chart_with_upwards_trend: Max Supply')
    st.subheader(f'$ {maxSupply:,}')
with rightCol01:
    st.subheader(':currency_exchange: Market Cap USD')
    st.subheader(f'$ {marketCapUsd:,}')
with rightCol02:
    st.subheader(':convenience_store: Volume Usd 24hr')
    st.subheader(f'$ {volumeUsd24Hr:,}')
    
st.markdown("---")

st.subheader('Times Series Price Usd')
 
figLineChart = px.line(
 timesSeriesByPrice,
 y=timesSeriesByPrice.columns,
 x='timestamp'
)

st.plotly_chart(figLineChart,use_container_width=True)