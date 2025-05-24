import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from datetime import datetime

# Setup
API_BASE = "https://stock.indianapi.in"
API_KEY = st.secrets.get("INDIAN_STOCK_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
TOP_NSE_SYMBOLS = ["ITC", "INFY", "SBIN", "ICICIBANK", "HDFCBANK"]
st.title("Top NSE Stocks - 3 Month Performance (with Fallback)")

# Main fetch function with fallback
def get_stock_data(symbol):
    endpoint = f"{API_BASE}/stock/NSE:{symbol}/history?interval=1d&range=3mo"
    try:
        response = requests.get(endpoint, headers=HEADERS)
        st.write(f"API Status for {symbol}: {response.status_code}")  # Debug
        st.write(response.text[:200])  # Show part of the response

        response.raise_for_status()
        data = response.json().get("prices", [])
        df = pd.DataFrame(data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["symbol"] = symbol
            return df
        else:
            raise ValueError("Empty data from IndianAPI")
    except Exception as e:
        st.warning(f"IndianAPI failed for {symbol}, falling back to Yahoo Finance. Error: {e}")
        return get_stock_data_yfinance(symbol)

# Fallback function using Yahoo Finance
def get_stock_data_yfinance(symbol):
    try:
        df = yf.download(f"{symbol}.NS", period="3mo", interval="1d")
        if df.empty:
            st.error(f"No fallback data found for {symbol}")
            return pd.DataFrame()
        df.reset_index(inplace=True)
        df.rename(columns={
            "Open": "open", "High": "high", "Low": "low", "Close": "close", "Date": "date"
        }, inplace=True)
        df["symbol"] = symbol
        return df[["date", "open", "high", "low", "close", "symbol"]]
    except Exception as e:
        st.error(f"Yahoo Finance failed for {symbol}: {e}")
        return pd.DataFrame()

# Collect all stock data
all_data = pd.DataFrame()
for symbol in TOP_NSE_SYMBOLS:
    df = get_stock_data(symbol)
    if not df.empty:
        all_data = pd.concat([all_data, df], ignore_index=True)

# Show if we have any data
if not all_data.empty:
    st.subheader("Candlestick Chart")
    selected = st.selectbox("Select a stock", TOP_NSE_SYMBOLS)
    df_filtered = all_data[all_data.symbol == selected]

    fig = go.Figure(data=[go.Candlestick(
        x=df_filtered["date"],
        open=df_filtered["open"],
        high=df_filtered["high"],
        low=df_filtered["low"],
        close=df_filtered["close"],
        name=selected
    )])
    fig.update_layout(title=f"{selected} - 3 Month Candlestick", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    st.subheader("Recent Data Snapshot")
    st.dataframe(df_filtered.tail(10))
else:
    st.error("No valid stock data retrieved. Please check your API key or try again later.")

