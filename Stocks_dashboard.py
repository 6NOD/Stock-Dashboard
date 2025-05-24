import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# API Config
API_BASE = "https://stock.indianapi.in"
API_KEY = st.secrets.get("INDIAN_STOCK_API_KEY", "")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Top 10 Stocks by Market Cap (adjust as needed)
TOP_10_STOCKS = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "KOTAKBANK", "LT", "SBIN"]

# App Title
st.title("Top 10 NSE Stocks - 3 Month Performance Tracker")

# Function to get historical data for a given stock
def get_stock_data(symbol):
    endpoint = f"{API_BASE}/stock/NSE:{symbol}/history?interval=1d&range=3mo"
    try:
        response = requests.get(endpoint, headers=HEADERS)
        response.raise_for_status()
        data = response.json().get("prices", [])
        df = pd.DataFrame(data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["symbol"] = symbol
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# Aggregate and display data
all_data = pd.DataFrame()

for symbol in TOP_10_STOCKS:
    df = get_stock_data(symbol)
    if not df.empty:
        all_data = pd.concat([all_data, df])

if not all_data.empty:
    st.subheader("Candlestick Charts (Last 3 Months)")
    selected_stock = st.selectbox("Select a Stock to View", TOP_10_STOCKS)
    df_selected = all_data[all_data.symbol == selected_stock]

    fig = go.Figure(data=[go.Candlestick(
        x=df_selected["date"],
        open=df_selected["open"],
        high=df_selected["high"],
        low=df_selected["low"],
        close=df_selected["close"],
        name=selected_stock
    )])
    fig.update_layout(title=f"{selected_stock} - NSE Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    st.subheader("Recent Data Snapshot")
    st.dataframe(df_selected.tail(10))
else:
    st.warning("No data available for the selected stocks. Please check your API key or try again later.")
