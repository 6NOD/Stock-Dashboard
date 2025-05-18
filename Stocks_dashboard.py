import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import os

# API Config
API_BASE = "https://stock.indianapi.in"
HEADERS = {"Authorization": f"Bearer {os.getenv('INDIAN_STOCK_API_KEY')}"}

# App Title
st.title("ITC Stock Dashboard - 3 Months View")

# Function to get 3-month historical data
def get_itc_data():
    endpoint = f"{API_BASE}/stock/NSE:ITC/history?interval=1d&range=3mo"
    response = requests.get(endpoint, headers=HEADERS)
    data = response.json().get("prices", [])
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

# Get and show data
df = get_itc_data()
if not df.empty:
    st.subheader("ITC Price Chart (Daily Candlestick)")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="ITC"
    )])
    fig.update_layout(title="ITC - NSE Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    st.subheader("Recent Data Snapshot")
    st.dataframe(df.tail(10))
else:
    st.error("Failed to fetch ITC data. Please check your API key or network.")
