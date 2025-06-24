import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="CryptoTrack", layout="wide")

st.title("📈 CryptoTrack – Live Cryptocurrency Dashboard")

# --- Get coin list from CoinGecko API ---
@st.cache_data
def get_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    res = requests.get(url)
    return res.json()

coins = get_coin_list()
coin_names = [coin['name'] for coin in coins]
coin_id_map = {coin['name']: coin['id'] for coin in coins}

selected_coin = st.selectbox("Choose a cryptocurrency", coin_names, index=coin_names.index("Bitcoin"))
coin_id = coin_id_map[selected_coin]

# --- Get live market data ---
@st.cache_data(ttl=60)
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    res = requests.get(url)
    return res.json()

coin_data = get_coin_data(coin_id)

# --- Display data ---
st.subheader(f"💰 {selected_coin} Price Info")
price = coin_data['market_data']['current_price']['usd']
change_24h = coin_data['market_data']['price_change_percentage_24h']
market_cap = coin_data['market_data']['market_cap']['usd']
st.metric(label="Current Price (USD)", value=f"${price:,.2f}", delta=f"{change_24h:.2f}%")
st.metric(label="Market Cap (USD)", value=f"${market_cap:,.2f}")

# --- Historical price chart ---
@st.cache_data
def get_price_history(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    res = requests.get(url, params=params)
    data = res.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

history_df = get_price_history(coin_id)
fig = px.line(history_df, x="timestamp", y="price", title=f"{selected_coin} - Last 30 Days Price")
st.plotly_chart(fig, use_container_width=True)
