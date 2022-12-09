from configparser import ConfigParser
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
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
    df['priceUsd'] = round(df['priceUsd'].astype('str').astype('float'),2)

    return df

df = getCryptoData()


st.sidebar.header("Filter")

dateFilterStart, dateFilterEnd = st.sidebar.date_input('Filter by Date',value=[df['timestamp'].min(),df['timestamp'].max()])
symbolFilter = st.sidebar.selectbox('Select The Symbol',options=df['symbol'].head(100).unique())

dfSelection = df[ 
    ((df['timestamp'].dt.date >= dateFilterStart) & (df['timestamp'].dt.date <= dateFilterEnd)) 
    & (df['symbol'] == symbolFilter) 
]

## Create KPI header
cryptoName = dfSelection['name'].unique()[0]
cryptoPosition = dfSelection['rank'].unique()[0]
timesSeriesByPrice = dfSelection.pivot_table(index='timestamp',columns='symbol',values='priceUsd').reset_index()
currentPrice = round(float(str( dfSelection.sort_values("timestamp",ascending=False)["priceUsd"].values[0])),2)
currentSupply = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['supply'].values[0])),2)
maxSupply = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['maxSupply'].values[0])),2)
marketCapUsd = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['marketCapUsd'].values[0])),2)
volumeUsd24Hr = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['volumeUsd24Hr'].values[0])),2)

st.markdown('<h1 style="text-align:center">Market Info</h1>',unsafe_allow_html=True)

col01, col02, col03 ,Col04, Col05, col06,col07 = st.columns([5,10,10,10,10,10,10])

with col01:
    st.image(f'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/128/color/{symbolFilter.lower()}.png')
with col02:
    st.markdown(f'''# {cryptoName}''')
    st.markdown(f'#### Ranking Position {cryptoPosition}')
with col03:
    st.subheader(':dollar: Price USD')
    st.subheader(f'$ {currentPrice:,}')
with Col04:
    st.subheader(':heavy_minus_sign: Supply')
    st.subheader(f'$ {currentSupply:,}')
with Col05:
    st.subheader(':chart_with_upwards_trend: Max Supply')
    st.subheader(f'$ {maxSupply:,}')
with col06:
    st.subheader(':currency_exchange: Market Cap USD')
    st.subheader(f'$ {marketCapUsd:,}')
with col07:
    st.subheader(':convenience_store: Volume Usd 24hr')
    st.subheader(f'$ {volumeUsd24Hr:,}')
    
st.markdown("---")
st.subheader('Times Series Price Usd')


figLineChart = px.scatter(
 timesSeriesByPrice,
 y=timesSeriesByPrice.columns,
 x='timestamp'
).update_traces(mode='lines+markers')



st.plotly_chart(figLineChart,use_container_width=True)