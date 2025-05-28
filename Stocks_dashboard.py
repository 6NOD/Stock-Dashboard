import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Set layout
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")

# API setup
API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://api.twelvedata.com"

# Predefined assets
assets = {
    "AAPL (Apple Inc)": "AAPL",
    "GOOGL (Alphabet Inc)": "GOOGL",
    "QQQ (Invesco ETF)": "QQQ",
    "VTIAX (Intl Mutual Fund)": "VTIAX",
    "FXAIX (Index Fund)": "FXAIX",
    "SPDR Gold Trust": "GLD"
}

st.title("Stock, ETF, Fund & Commodity Comparison")

selected = st.multiselect("Select assets to compare:", list(assets.keys()), default=["AAPL (Apple Inc)", "QQQ (Invesco ETF)"])

def fetch_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    r = requests.get(url)
    return r.json()

def display_asset(symbol):
    data = fetch_quote(symbol)

    if "code" in data:
        st.error(f"{symbol}: {data.get('message', 'API Error')}")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${data.get('price', 'N/A')}", f"{data.get('percent_change', '0')}%")
    col2.metric("1Y High", f"${data.get('fifty_two_week', {}).get('high', 'N/A')}")
    col3.metric("1Y Low", f"${data.get('fifty_two_week', {}).get('low', 'N/A')}")

    st.markdown(f"**Exchange:** {data.get('exchange', 'N/A')}")
    st.markdown(f"**Previous Close:** ${data.get('previous_close', 'N/A')}")
    st.markdown(f"**Open Price:** ${data.get('open', 'N/A')}")
    st.markdown("---")

def plot_history(symbol):
    url = f"{BASE_URL}/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={API_KEY}"
    r = requests.get(url).json()
    if "values" in r:
        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        df = df.sort_index()
        st.line_chart(df["close"].astype(float), use_container_width=True)
    else:
        st.warning(f"No chart data for {symbol}")

# Tabbed layout
tabs = st.tabs(["Overview", "Charts", "Fundamentals"])

with tabs[0]:
    for name in selected:
        st.subheader(name)
        display_asset(assets[name])

with tabs[1]:
    for name in selected:
        st.subheader(f"{name} Price Trend")
        plot_history(assets[name])

with tabs[2]:
    st.info("Fundamentals tab is under construction – coming soon!")
    
