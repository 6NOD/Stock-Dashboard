import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Constants
API_KEY = "d910ad367b9345aab248fd7f4f8c038a"
BASE_URL = "https://api.twelvedata.com"

# Stock symbols
STOCKS = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC": "HDFC.NS",
    "Hindustan Unilever": "HINDUNILVR.NS"
}

# Streamlit UI
st.set_page_config(page_title="Indian Stock Dashboard", layout="wide")
st.title("Indian Stock Market Dashboard")

# Sidebar - Select Stock
ticker_name = st.sidebar.selectbox("Select a stock:", list(STOCKS.keys()))
ticker = STOCKS[ticker_name]

# Fetch current quote
def get_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url).json()
    return response

# Fetch intraday time series
def get_time_series(symbol):
    url = f"{BASE_URL}/time_series?symbol={symbol}&interval=5min&outputsize=30&apikey={API_KEY}"
    response = requests.get(url).json()
    if "values" in response:
        df = pd.DataFrame(response["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["close"] = pd.to_numeric(df["close"], errors='coerce')
        df.sort_values("datetime", inplace=True)
        return df
    return None

# Display stock info
quote = get_quote(ticker)

if "code" in quote:
    st.error(f"Error fetching data: {quote.get('message', 'Unknown error')}")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Price", f"Rs. {quote['price']}", f"{quote['percent_change']}%")
    col2.metric("Open", f"Rs. {quote['open']}")
    col3.metric("Volume", f"{quote['volume']}")
    col4.metric("Last Updated", quote['datetime'])

    # Display time series chart
    st.subheader(f"Intraday Price Chart - {ticker}")
    data = get_time_series(ticker)
    if data is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data["datetime"], y=data["close"], mode='lines', name=ticker))
        fig.update_layout(title=f"{ticker_name} - 5 min Interval", xaxis_title="Time", yaxis_title="Price (INR)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No chart data available.")
        
