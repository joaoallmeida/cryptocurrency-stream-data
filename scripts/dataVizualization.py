from configparser import ConfigParser
from datetime import datetime
import plotly.express as px
import pandas as pd
import streamlit as st
import pymongo

config = ConfigParser()
config.read('env.ini')

credentials = config['MONGODB']
connStr = f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority"

mongoClient = pymongo.MongoClient(connStr)
dataBase = mongoClient['financial']
collection = dataBase['crypto']
data = collection.find()

df = pd.DataFrame(data).drop(['_id'],axis=1)

## Config Web Page
st.set_page_config(
    page_title="crypto currency",
    page_icon="https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25fa5/svg/color/btc.svg",
    layout="wide",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.header(':bar_chart: Crypto Currency Dashboard')

st.sidebar.header("Filter")

dateFilter = st.sidebar.slider('Filter by Date',value=datetime.now().date())
# supplyFilter = st.sidebar.slider('Sypply Filter Range',step=1000,min_value=df['supply'].min().astype('int'), max_value=df['supply'].max().astype('int') )
# priceFilter = st.sidebar.slider('Filter price USD',max_value=df['priceUsd'].max())
symbolFilter = st.sidebar.multiselect('Select The Symbol',options=df['symbol'].unique(),default=df['symbol'].head(3).unique())
# nameFilter = st.sidebar.multiselect('Select The Name',options=df['name'].unique(),default=df['name'].head(3).unique())

dfSelection = df#[ 
#                  (df['timestamp'].dt.date == dateFilter) & 
                #   (df['symbol'].isin(symbolFilter)) 
#                   (df['name'].isin(nameFilter)) 
#                 #   (df['priceUsd'] == priceFilter)
#                 #   (df['supply'] == supplyFilter)
#]

st.dataframe(dfSelection)

timesSeriesByMarket = dfSelection.pivot_table(index='timestamp',columns='symbol',values='marketCapUsd').reset_index()

# figLineChart = st.line_chart(
#  timesSeriesBySupply,
#  y=symbolFilter,
#  x='timestamp'
# )

figLineChart = px.line(
 timesSeriesByMarket,
 y=timesSeriesByMarket.columns,
 x='timestamp',
 title='Times Series Market Cap Usd'
)
st.plotly_chart(figLineChart,use_container_width=True)