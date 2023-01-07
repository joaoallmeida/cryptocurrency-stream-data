from configparser import ConfigParser
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import streamlit as st
import pymongo
import pytz, os

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

    credentials = {"username" :os.getenv('MONGODB_USER'), "password": os.getenv('MONGODB_PASS')}
    connStr = f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority"
    mongoClient = pymongo.MongoClient(connStr)
    
    return mongoClient
 
@st.experimental_memo(show_spinner=False,ttl=60)
def getCryptoData() -> pd.DataFrame:
    
    mongoClient = connMongo()
    dataBase = mongoClient['financial']
    collection = dataBase['crypto']
    data = collection.find()

    floatColumns = ['priceUsd','marketCapUsd','volumeUsd24Hr','vwap24Hr']
    
    df = pd.DataFrame(data).drop(['_id'],axis=1)
    
    for col in floatColumns:
        df[col] = df[col].astype('str').astype('float')
   
    df['changePercent24Hr'] = (df['changePercent24Hr'].astype('str').astype('float') / 100 )

    return df

def rankCrypto(df: pd.DataFrame) -> pd.DataFrame:
    
    rankDf = df[df['timestamp'] == df['timestamp'].max()][['rank','name','priceUsd','changePercent24Hr','volumeUsd24Hr','vwap24Hr']].head(100).sort_values(['rank'],ascending=True)

    floatColumns  = ['priceUsd','volumeUsd24Hr','vwap24Hr']
    dictRename = {
            "rank":"#",
            "name":"Name",
            "priceUsd":"Price USD",
            "changePercent24Hr":"Change Percent 24Hr",
            "volumeUsd24Hr":"Volume USD 24Hr",
            "vwap24Hr":"VWAP 24Hr"
        }

    for col in floatColumns:
        rankDf[col] = rankDf[col].apply(lambda x: (f"{x:,.2f}" if x > 1 else f"{x:,.5f}").format(x))

    rankDf = rankDf.rename(dictRename,axis=1).reset_index(drop=True)

    return rankDf

def getLatestData(df: pd.DataFrame) -> pd.DataFrame:
    dfLatestData = df[df['timestamp'].dt.date == datetime.now(pytz.timezone('UTC')).date()]
    return dfLatestData

@st.cache
def convertCurrency(valueConvert,currentPrice):
    result= (valueConvert * currentPrice)
    return result


def tableStyle(df):
    
  def color_negative_red(value):
   
    if value < 0:
      color = 'red'
    elif value > 0:
      color = 'green'
    else:
      color = 'black'
    return 'color: %s' % color

  return df.style.applymap(color_negative_red, subset=['Change Percent 24Hr']).format({'Change Percent 24Hr': "{:.2%}"})

    
#######################-#######################   
    
## Reading data ##
df = getCryptoData()

placeholder = st.empty()

## Filter ## 
with st.sidebar:
    st.markdown('<h1 style="text-align:center">Filter</h1>',unsafe_allow_html=True)
    
    dateFilterStart , dateFilterEnd = st.date_input('Date Filter',value=[(df['timestamp'].max() - timedelta(days=1)),df['timestamp'].max()],disabled=False)
    symbolFilter = st.selectbox('Select the Symbol',options=df['symbol'].unique())

    st.markdown('---')


## Filter Data ##
dfSelection = df[
    ((df['timestamp'].dt.date >= dateFilterStart) & (df['timestamp'].dt.date <= dateFilterEnd)) &
    (df['symbol'] == symbolFilter) 
]    

## Create KPI header ##
cryptoName = dfSelection['name'].unique()[0]
cryptoPosition = dfSelection['rank'].unique()[0]
currentPrice = dfSelection.sort_values("timestamp",ascending=False)["priceUsd"].values[0] 
currentSupply = float(str( dfSelection.sort_values("timestamp",ascending=False)['supply'].values[0]))
maxSupply = float(str( dfSelection.sort_values("timestamp",ascending=False)['maxSupply'].values[0]))
marketCapUsd = dfSelection.sort_values("timestamp",ascending=False)['marketCapUsd'].values[0]
volumeUsd24Hr = float(str( dfSelection.sort_values("timestamp",ascending=False)['volumeUsd24Hr'].values[0]))
changePercent = dfSelection.sort_values("timestamp",ascending=False)['changePercent24Hr'].values[0]

with st.sidebar:
    
    st.markdown(f'<h1 style="text-align:center">{symbolFilter} to USD Converter</h1>',unsafe_allow_html=True)
    
    col01 , col02 = st.columns([0.2,1])
    
    with col01:
        st.markdown(f'<img src="https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/svg/color/{symbolFilter.lower()}.svg" width="35" height="105">',unsafe_allow_html=True)
        st.markdown(f'<img src="https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/svg/color/usd.svg" width="35" height="75">',unsafe_allow_html=True)
    
    with col02:    
        numberConvert = st.number_input(f'{symbolFilter}',format='%f',label_visibility='hidden')
        convertPrice = st.number_input('USD',value=convertCurrency(numberConvert,currentPrice),label_visibility='hidden')
    

with placeholder.container():

    st.markdown('<h1 style="text-align:center">Market Info</h1>',unsafe_allow_html=True)

    col01, col02, col03 ,col04, col05, col06,col07 = st.columns([5,10,7,12,12,12,12])

    with col01:
        st.image(f'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/128/color/{symbolFilter.lower()}.png')
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
        
    st.markdown("<br>",unsafe_allow_html=True)

    ### Charts ###

    config = dict({"displayModeBar":'hover',"scrollZoom":False,"displaylogo":False,"responsive":False,"autosizable":True})
        
    tab01, tab02 = st.tabs([':heavy_dollar_sign: Price USD',':moneybag: Market Cap USD'])

    timesSeriesByPrice = dfSelection.pivot_table(index='timestamp',columns='symbol',values='priceUsd').reset_index()
    timesSeriesByMarketCap = dfSelection.pivot_table(index='timestamp', columns='symbol', values='marketCapUsd').reset_index()

    with tab01:
        st.subheader(':heavy_dollar_sign: Price USD')
        

        figLineChart = px.scatter(
            timesSeriesByPrice,
            y=timesSeriesByPrice.columns,
            x='timestamp',
            color_discrete_sequence=['#16c784']
        )
        
        figLineChart.update_traces(mode='lines',fill='tozerox')
        figLineChart.update_layout(
            showlegend=False
            ,yaxis_title=None
            ,xaxis_title=None
            ,xaxis=dict(
                    rangeslider=dict(
                        thickness=0.20,
                        visible=True,
                    ),
                    type="date",
                    showspikes=True,
                    spikedash='dot',
                    spikemode='across',
                    spikecolor='#A4A3A1'
                )
        )

        st.plotly_chart(figLineChart,theme='streamlit',use_container_width=True,config=config)

    with tab02:
        st.subheader(':moneybag: Market Cap USD')

        figLineChart = px.scatter(
            timesSeriesByMarketCap,
            y=timesSeriesByMarketCap.columns,
            x='timestamp',
            color_discrete_sequence=['#5A52FF']
        )
        
        figLineChart.update_traces(mode='lines',fill='tozerox')
        figLineChart.update_layout(
            showlegend=False
            ,yaxis_title=None
            ,xaxis_title=None
            ,xaxis=dict(
                    rangeslider=dict(
                        thickness=0.20,
                        visible=True
                    ),
                    type="date",
                    showspikes=True,
                    spikedash='dot',
                    spikemode='across',
                    spikecolor='#A4A3A1'
                )
        )
        
        st.plotly_chart(figLineChart,theme='streamlit',use_container_width=True,config=config)

    st.markdown('---')
    ## Ranking   
    st.header(":globe_with_meridians: Today's Cryptocurrency Rank")
    
    rankDf = rankCrypto(df)
    rankDf = tableStyle(rankDf)
    st.table(rankDf)
