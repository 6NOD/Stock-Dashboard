import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# API Config
API_BASE = "https://stock.indianapi.in"
API_KEY = st.secrets.get("INDIAN_STOCK_API_KEY", "")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Verified NSE stock symbols that return data
TOP_STOCKS = ["ITC", "INFY", "SBIN", "ICICIBANK", "HDFCBANK"]

# App Title
st.set_page_config(page_title="Top NSE Stocks Dashboard", layout="wide")
st.title("Top NSE Stocks - 3 Month Performance Tracker")

# Function to get 3-month historical data for a given stock
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

# Fetch and combine data for all stocks
all_data = pd.DataFrame()
for symbol in TOP_STOCKS:
    df = get_stock_data(symbol)
    if not df.empty:
        all_data = pd.concat([all_data, df])

# Display content
if not all_data.empty:
    selected_stock = st.selectbox("Select a Stock", TOP_STOCKS)
    df_selected = all_data[all_data.symbol == selected_stock]

    st.subheader(f"{selected_stock} - Candlestick Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=df_selected["date"],
        open=df_selected["open"],
        high=df_selected["high"],
        low=df_selected["low"],
        close=df_selected["close"],
        name=selected_stock
    )])
    fig.update_layout(title=f"{selected_stock} - NSE Candlestick Chart",
                      xaxis_title="Date", yaxis_title="Price",
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Price Data")
    st.dataframe(df_selected.tail(10))
else:
    st.warning("No data available. Please check your API key or try again later.")
    
