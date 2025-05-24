import streamlit as st
import os
import requests
import pandas as pd
import plotly.graph_objects as go

# Load API key from secrets
api_key = st.secrets.get("INDIAN_STOCK_API_KEY")

# Debug to verify API key presence
st.sidebar.markdown("### Debug Info")
st.sidebar.write("API Key Loaded:", bool(api_key))

# Validate API key
if not api_key:
    st.error("API key not found. Please add it to `.streamlit/secrets.toml`")
    st.stop()

headers = {"Authorization": f"Bearer {api_key}"}
api_base = "https://stock.indianapi.in"

# App Title
st.title("ITC Stock Dashboard - 3 Months View")

# Function to fetch ITC stock history
def get_itc_data():
    endpoint = f"{api_base}/stock/NSE:ITC/history?interval=1d&range=3mo"
    response = requests.get(endpoint, headers=headers)

    if response.status_code != 200:
        st.error(f"API Error {response.status_code}")
        st.code(response.text)
        return pd.DataFrame()

    try:
        data = response.json().get("prices", [])
        df = pd.DataFrame(data)
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Error parsing response: {e}")
        return pd.DataFrame()

# Load and display data
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

    st.subheader("Recent Data Snapshot")
    st.dataframe(df.tail(10))
else:
    st.warning("No stock data available.")

