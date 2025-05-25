import requests
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="Stock Analysis MVP", layout="wide")

API_KEY = st.secrets["API_KEY"] if "API_KEY" in st.secrets else "d910ad367b9345aab248fd7f4f8c038a"
BASE_URL = "https://api.twelvedata.com"

st.title("Stock Analysis MVP")

st.sidebar.header("Stock Selector")
symbol = st.sidebar.text_input("Enter US Stock Symbol (e.g. AAPL, MSFT, TSLA):", value="AAPL").upper()

def fetch_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    return requests.get(url).json()

def fetch_intraday(symbol, interval="5min", outputsize=30):
    url = f"{BASE_URL}/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    return requests.get(url).json()

def fetch_financials(symbol):
    url = f"{BASE_URL}/income_statement?symbol={symbol}&apikey={API_KEY}"
    return requests.get(url).json()

# Tab Layout
tab1, tab2, tab3 = st.tabs(["Overview", "News", "Financials"])

with tab1:
    quote = fetch_quote(symbol)
    if "price" in quote:
        st.subheader(f"{symbol} - Real-Time Quote")
        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"${quote['price']}", f"{quote['percent_change']}%")
        col2.metric("Open", f"${quote['open']}")
        col3.metric("Volume", quote['volume'])

        st.subheader(f"{symbol} - Intraday Chart (5 min)")
        chart = fetch_intraday(symbol)
        if "values" in chart:
            df = pd.DataFrame(chart["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.sort_values("datetime")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["datetime"], y=df["close"], mode="lines", name="Price"))
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=20), height=400,
                              xaxis_title="Time", yaxis_title="Price")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not load intraday chart.")
    else:
        st.error("Invalid stock symbol.")

with tab2:
    st.subheader("Latest News")
    st.info("News API integration coming soon. Consider using Finhub, Alpha Vantage, or News API.")

with tab3:
    st.subheader("Financials Overview")
    data = fetch_financials(symbol)
    if "data" in data:
        df_fin = pd.DataFrame(data["data"])
        df_fin = df_fin.head(1).T
        df_fin.columns = ["Most Recent Statement"]
        st.dataframe(df_fin)
    else:
        st.warning("No financial data available for this symbol.")

