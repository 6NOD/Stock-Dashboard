import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Constants
API_KEY = "d910ad367b9345aab248fd7f4f8c038a"
BASE_URL = "https://api.twelvedata.com"

# Top 10 US Stocks, Index Funds, ETFs
TOP_US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta (Facebook)": "META",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK.B",
    "Johnson & Johnson": "JNJ",
    "Visa": "V"
}

TOP_INDEX_FUNDS = {
    "S&P 500 ETF (SPY)": "SPY",
    "Vanguard 500 Index Fund (VOO)": "VOO",
    "iShares Core S&P 500 (IVV)": "IVV",
    "Schwab S&P 500 Index (SWPPX)": "SWPPX",
    "Fidelity 500 Index Fund (FXAIX)": "FXAIX",
    "SPDR Dow Jones Industrial Average (DIA)": "DIA",
    "Vanguard Total Stock Market (VTI)": "VTI",
    "iShares Russell 2000 ETF (IWM)": "IWM",
    "Fidelity ZERO Large Cap Index (FNILX)": "FNILX",
    "iShares MSCI EAFE ETF (EFA)": "EFA"
}

TOP_ETFS = {
    "Invesco QQQ Trust (QQQ)": "QQQ",
    "ARK Innovation ETF (ARKK)": "ARKK",
    "SPDR S&P Biotech ETF (XBI)": "XBI",
    "iShares MSCI Emerging Markets ETF (EEM)": "EEM",
    "Vanguard Real Estate ETF (VNQ)": "VNQ",
    "iShares Silver Trust (SLV)": "SLV",
    "SPDR Gold Shares (GLD)": "GLD",
    "Vanguard Dividend Appreciation ETF (VIG)": "VIG",
    "iShares U.S. Technology ETF (IYW)": "IYW",
    "Vanguard Growth ETF (VUG)": "VUG"
}

CATEGORY_MAP = {
    "Top 10 US Stocks": TOP_US_STOCKS,
    "Top 10 Index Funds": TOP_INDEX_FUNDS,
    "Top 10 ETFs": TOP_ETFS
}

# Streamlit UI
st.set_page_config(page_title="US Market Dashboard", layout="wide")
st.title("US Stock Market Dashboard")

# Sidebar - Select Category and Ticker
category = st.sidebar.radio("Choose a category:", list(CATEGORY_MAP.keys()))
ticker_name = st.sidebar.selectbox("Select a security:", list(CATEGORY_MAP[category].keys()))
ticker = CATEGORY_MAP[category][ticker_name]

# Fetch current quote
def get_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return {"error": str(e)}

# Fetch intraday time series
def get_time_series(symbol):
    url = f"{BASE_URL}/time_series?symbol={symbol}&interval=5min&outputsize=30&apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "values" in data:
            df = pd.DataFrame(data["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["close"] = pd.to_numeric(df["close"], errors='coerce')
            df.sort_values("datetime", inplace=True)
            return df
        return None
    except Exception as e:
        return None

# Display stock info
quote = get_quote(ticker)

required_fields = ["price", "percent_change", "open", "volume", "datetime"]

if any(field not in quote for field in required_fields):
    st.error("Some data fields are missing in the API response. Here's the response:")
    st.json(quote)
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Price", f"$ {quote['price']}", f"{quote['percent_change']}%")
    col2.metric("Open", f"$ {quote['open']}")
    col3.metric("Volume", f"{quote['volume']}")
    col4.metric("Last Updated", quote['datetime'])

    # Display time series chart
    st.subheader(f"Intraday Price Chart - {ticker}")
    data = get_time_series(ticker)
    if data is not None and not data.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data["datetime"], y=data["close"], mode='lines', name=ticker))
        fig.update_layout(title=f"{ticker_name} - 5 min Interval", xaxis_title="Time", yaxis_title="Price (USD)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No chart data available.")

