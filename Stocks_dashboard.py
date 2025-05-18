import streamlit as st
import os
import requests
import pandas as pd
import plotly.graph_objects as go

# Load API key from Streamlit secrets
api_key = st.secrets["INDIAN_STOCK_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}"}
api_base = "https://stock.indianapi.in"

# App Title
st.title("ITC Stock Dashboard - 3 Months View")

def get_itc_data():
    endpoint = f"{api_base}/stock/NSE:ITC/history?interval=1d&range=3mo"
    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        st.error(f"API Error: {response.status_code}")
        st.text(response.text)
        return pd.DataFrame()
    try:
        data = response.json().get("prices", [])
        df = pd.DataFrame(data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"JSON Parsing Error: {e}")
        return pd.DataFrame()

df = get_itc_data()
if not df.empty:
    st.subheader("ITC Price Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(title="ITC - NSE Candlestick", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)
    st.subheader("Recent Data")
    st.dataframe(df.tail(10))
else:
    st.warning("No data available.")
