from configparser import ConfigParser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import pymongo
import time
import json
import requests

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

@st.experimental_singleton
def connMongo():
    config = ConfigParser()
    config.read('env.ini')

    credentials = config['MONGODB']
    connStr = f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority"
    mongoClient = pymongo.MongoClient(connStr)
    
    return mongoClient

 
@st.experimental_memo(ttl=30) 
def getCryptoData():
    
    mongoClient = connMongo()
    dataBase = mongoClient['financial']
    collection = dataBase['crypto']
    data = collection.find()

    df = pd.DataFrame(data).drop(['_id'],axis=1)
    df['priceUsd'] = df['priceUsd'].astype('str').astype('float')
    df['marketCapUsd'] = df['marketCapUsd'].astype('str').astype('float')
    df['changePercent24Hr'] = (df['changePercent24Hr'].astype('str').astype('float') / 100)

    return df

df = getCryptoData()

## Filter
with st.sidebar:
#     dateFilterStart , dateFilterEnd = st.date_input('Filter by Date',value=[df['timestamp'].min(),df['timestamp'].max()])
    symbolFilter = st.selectbox('Select The Symbol',options=df['symbol'].unique())

    st.markdown('---')


dfSelection = df[ 
    #    ((df['timestamp'].dt.date == dateFilterStart) & (df['timestamp'].dt.date <= dateFilterEnd)) 
     (df['symbol'] == symbolFilter) 
]


## Create KPI header
cryptoName = dfSelection['name'].unique()[0]
cryptoPosition = dfSelection['rank'].unique()[0]
currentPrice = dfSelection.sort_values("timestamp",ascending=False)["priceUsd"].values[0] 
currentSupply = float(str( dfSelection.sort_values("timestamp",ascending=False)['supply'].values[0]))
maxSupply = float(str( dfSelection.sort_values("timestamp",ascending=False)['maxSupply'].values[0]))
marketCapUsd = dfSelection.sort_values("timestamp",ascending=False)['marketCapUsd'].values[0]
volumeUsd24Hr = float(str( dfSelection.sort_values("timestamp",ascending=False)['volumeUsd24Hr'].values[0]))
changePercent = dfSelection.sort_values("timestamp",ascending=False)['changePercent24Hr'].values[0]


with st.sidebar:
    
    st.title(f'{symbolFilter} to USD Converter')
    
    numberConvert = st.number_input(f'{symbolFilter}',format='%f',key='convertNumber')
    calculated = (numberConvert * currentPrice)
    convertResult = st.number_input('USD',value=calculated,key='result')
    
    
st.markdown('<h1 style="text-align:center">Market Info</h1>',unsafe_allow_html=True)

col01, col02, col03 ,col04, col05, col06,col07 = st.columns([5,10,7,10,10,12,12])

with col01:
    st.image(f'https://cryptoicons.org/api/color/{symbolFilter.lower()}/128')
with col02:
    st.markdown(f'''## {cryptoName}''')
    st.markdown(f'###### Ranking Position #{cryptoPosition}')
with col03:
    price = f'{currentPrice:,.2f}' if currentPrice > 1 else f'{currentPrice:,.5f}'
    st.metric(':dollar: Price USD', f'{price}', f'{changePercent:,.2%}')
with col04:
    st.metric(':heavy_minus_sign: Supply', f'{currentSupply:,.2f}')
with col05:
    st.metric(':chart_with_upwards_trend: Max Supply', f'{maxSupply:,.2f}')
with col06:
    st.metric(':currency_exchange: Market Cap USD', f'{marketCapUsd:,.2f}')
with col07:
    st.metric(':convenience_store: Volume Usd 24hr',f'{volumeUsd24Hr:,.2f}')
    
st.markdown("---")

## Charts

config = dict({"displayModeBar":'hover',"scrollZoom":False,"displaylogo":False})

with st.container():
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
        

        figLineChart.update_traces(mode='lines')
        figLineChart.update_layout(
            showlegend=False
            ,yaxis_title=None
            ,xaxis_title=None
            ,xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=12,
                                label="12H",
                                step="hour",
                                stepmode="backward"),
                            dict(count=1,
                                label="1D",
                                step="day",
                                stepmode="backward"),
                            dict(count=7,
                                label="7D",
                                step="day",
                                stepmode="backward"),
                            dict(count=1,
                                label="1M",
                                step="month",
                                stepmode="backward"),
                            dict(count=3,
                                label="3M",
                                step="month",
                                stepmode="backward"),
                            dict(count=1,
                                label="YTD",
                                step="year",
                                stepmode="todate"),
                            dict(label='ALL',
                                 step="all")
                        ])
                    ),
                    rangeslider=dict(
                        visible=True
                    ),
                    type="date"
                )
        )

        st.plotly_chart(figLineChart,theme='streamlit',use_container_width=True,config=config)

    with tab02:
        st.subheader(':moneybag: Market Cap USD')

        figLineChart = px.scatter(
        timesSeriesByMarketCap,
        y=timesSeriesByMarketCap.columns,
        x='timestamp'
        )
        
        figLineChart.update_traces(mode='lines')
        figLineChart.update_layout(
            showlegend=False
            ,yaxis_title=None
            ,xaxis_title=None
            ,xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=12,
                                label="12H",
                                step="hour",
                                stepmode="backward"),
                            dict(count=1,
                                label="1D",
                                step="day",
                                stepmode="backward"),
                            dict(count=7,
                                label="7D",
                                step="day",
                                stepmode="backward"),
                            dict(count=1,
                                label="1M",
                                step="month",
                                stepmode="backward"),
                            dict(count=3,
                                label="3M",
                                step="month",
                                stepmode="backward"),
                            dict(count=1,
                                label="YTD",
                                step="year",
                                stepmode="todate"),
                            dict(label='ALL',
                                 step="all")
                        ])
                    ),
                    rangeslider=dict(
                        visible=True
                    ),
                    type="date"
                )
        )
        
        st.plotly_chart(figLineChart,theme='streamlit',use_container_width=True,config=config)


## Ranking    
# rankingDf = df[df['timestamp'].dt.date == datetime.now().date()].iloc[:,1:10].reset_index()
# idx = rankingDf.groupby(['name'])['index'].transform(max) == rankingDf['index']
# rankingDf = rankingDf[idx].drop('index',axis=1)

# st.subheader('Cryptocurency Ranking')
# st.table(rankingDf)