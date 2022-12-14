from configparser import ConfigParser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
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

autoRefresh = st_autorefresh(interval=60000,key="fizzbuzzcounter")

# @st.experimental_memo
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
    df['changePercent24Hr'] = round(df['changePercent24Hr'].astype('str').astype('float'),2)


    return df

df = getCryptoData()

## Filter
col01 , col02 = st.columns(2)

with col01:
    dateFilter = st.date_input('Filter by Date',value=df['timestamp'].max(), min_value=df['timestamp'].min())
with col02:
    symbolFilter = st.selectbox('Select The Symbol',options=df['symbol'].head(100).unique())

st.markdown('---')

dfSelection = df[ 
    ((df['timestamp'].dt.date == dateFilter)) #& (df['timestamp'].dt.date <= dateFilterEnd)) 
    & (df['symbol'] == symbolFilter) 
]



## Create KPI header
cryptoName = dfSelection['name'].unique()[0]
cryptoPosition = dfSelection['rank'].unique()[0]
currentPrice = round(dfSelection.sort_values("timestamp",ascending=False)["priceUsd"].values[0],2)
currentSupply = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['supply'].values[0])),2)
maxSupply = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['maxSupply'].values[0])),2)
marketCapUsd = dfSelection.sort_values("timestamp",ascending=False)['marketCapUsd'].values[0]
volumeUsd24Hr = round(float(str( dfSelection.sort_values("timestamp",ascending=False)['volumeUsd24Hr'].values[0])),2)
changePercent = dfSelection.sort_values("timestamp",ascending=False)['changePercent24Hr'].values[0]

st.markdown('<h1 style="text-align:center">Market Info</h1>',unsafe_allow_html=True)

col01, col02, col03 ,col04, col05, col06,col07 = st.columns([5,10,10,10,10,12,12])

with col01:
    st.image(f'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/128/color/{symbolFilter.lower()}.png')
with col02:
    st.markdown(f'''## {cryptoName}''')
    st.markdown(f'###### Ranking Position {cryptoPosition}')
with col03:
    st.metric(':dollar: Price USD', f'{currentPrice:,}', f'{changePercent:,.2%}')
with col04:
    st.metric(':heavy_minus_sign: Supply', f'{currentSupply:,}')
with col05:
    st.metric(':chart_with_upwards_trend: Max Supply', f'{maxSupply:,}')
with col06:
    st.metric(':currency_exchange: Market Cap USD', f'{marketCapUsd:,}')
with col07:
    st.metric(':convenience_store: Volume Usd 24hr',f'{volumeUsd24Hr:,}')
    
st.markdown("---")

tab01, tab02 = st.tabs([':heavy_dollar_sign: Price USD',':moneybag: Market Cap USD'])

timesSeriesByPrice = dfSelection.pivot_table(index='timestamp',columns='symbol',values='priceUsd').reset_index()
timesSeriesByMarketCap = dfSelection.pivot_table(index='timestamp', columns='symbol', values='marketCapUsd').reset_index()

with tab01:
    st.subheader(':heavy_dollar_sign: Price USD')

    figLineChart = px.scatter(
        timesSeriesByPrice,
        y=timesSeriesByPrice.columns,
        x='timestamp',
        color_discrete_sequence=['#00FF8A']
    )
    
    figLineChart.update_traces(mode='lines')#,fill="tonext")
    figLineChart.update_layout(showlegend=False,yaxis_title=None,xaxis_title=None)

    st.plotly_chart(figLineChart,use_container_width=True)

with tab02:
    st.subheader(':moneybag: Market Cap USD')

    figLineChart = px.scatter(
    timesSeriesByMarketCap,
    y=timesSeriesByMarketCap.columns,
    x='timestamp'
    )
    
    figLineChart.update_traces(mode='lines')#,fill="toself")
    figLineChart.update_layout(showlegend=False,yaxis_title=None,xaxis_title=None)
    
    st.plotly_chart(figLineChart,use_container_width=True)

## Ranking    
rankingDf = df[df['timestamp'].dt.date == datetime.now().date()].iloc[:,1:10].reset_index()
idx = rankingDf.groupby(['name'])['index'].transform(max) == rankingDf['index']
rankingDf = rankingDf[idx].drop('index',axis=1)

st.subheader('Cryptocurency Rankings')
st.table(rankingDf)
    