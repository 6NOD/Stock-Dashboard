import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Top Indian stocks on NSE (with .NS suffix for Yahoo Finance)
TOP_STOCKS = ["ITC.NS", "INFY.NS", "SBIN.NS", "ICICIBANK.NS", "HDFCBANK.NS"]

st.title("Top NSE Stocks - 3 Month Performance Tracker (via Yahoo Finance)")

def fetch_stock_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        df.reset_index(inplace=True)
        df["symbol"] = symbol
        return df
    except Exception as e:
        st.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

# Combine data
all_data = pd.DataFrame()
for symbol in TOP_STOCKS:
    df = fetch_stock_data(symbol)
    if not df.empty:
        all_data = pd.concat([all_data, df])

if not all_data.empty:
    stock_choice = st.selectbox("Select Stock", TOP_STOCKS)
    df_selected = all_data[all_data.symbol == stock_choice]

    st.subheader(f"{stock_choice} - Candlestick Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=df_selected['Date'],
        open=df_selected['Open'],
        high=df_selected['High'],
        low=df_selected['Low'],
        close=df_selected['Close']
    )])
    fig.update_layout(xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    st.subheader("Latest Data")
    st.dataframe(df_selected.tail(10))
else:
    st.warning("No data available. Check internet or try again.")
