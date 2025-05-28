import streamlit as st
import requests
import pandas as pd
import altair as alt

# Streamlit page config
st.set_page_config(page_title="Stock Comparison", layout="wide")

# Twelve Data API
API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://api.twelvedata.com"

# Assets
assets = {
    "AAPL (Apple Inc)": "AAPL",
    "GOOGL (Alphabet Inc)": "GOOGL",
    "QQQ (Invesco ETF)": "QQQ",
    "VTIAX (Intl Mutual Fund)": "VTIAX",
    "FXAIX (Index Fund)": "FXAIX",
    "SPDR Gold Trust": "GLD"
}

st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Stock & ETF Visual Dashboard</h1>", unsafe_allow_html=True)

selected = st.multiselect("Choose assets to compare:", list(assets.keys()), default=["AAPL (Apple Inc)", "QQQ (Invesco ETF)"])

# Fetch quote data
def fetch_quote(symbol):
    url = f"{BASE_URL}/quote?symbol={symbol}&apikey={API_KEY}"
    r = requests.get(url)
    return r.json()

# Chart history
def fetch_history(symbol):
    url = f"{BASE_URL}/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={API_KEY}"
    r = requests.get(url).json()
    return r.get("values", [])

# Display metric cards
def display_card(name, data):
    price = float(data.get("price", 0))
    pct_change = float(data.get("percent_change", 0))
    high = data.get("fifty_two_week", {}).get("high", "N/A")
    low = data.get("fifty_two_week", {}).get("low", "N/A")

    change_color = "#28a745" if pct_change >= 0 else "#dc3545"

    st.markdown(f"""
        <div style='padding: 20px; border-radius: 12px; background-color: #f9f9f9;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px;'>
            <h3 style='margin-bottom: 5px;'>{name}</h3>
            <p style='font-size: 20px;'>Price: <strong>${price:.2f}</strong> <span style='color: {change_color};'>({pct_change}%)</span></p>
            <p>52W High: ${high} | 52W Low: ${low}</p>
            <p>Exchange: {data.get("exchange", "N/A")} | Prev Close: ${data.get("previous_close", "N/A")}</p>
        </div>
    """, unsafe_allow_html=True)

# Area chart with Altair
def display_chart(name, values):
    if not values:
        st.warning(f"No chart data for {name}")
        return

    df = pd.DataFrame(values)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = df["close"].astype(float)

    chart = alt.Chart(df).mark_area(
        line={'color': '#4A90E2'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color="#4A90E2", offset=0), alt.GradientStop(color="#ffffff", offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x='datetime:T',
        y='close:Q',
        tooltip=["datetime:T", "close:Q"]
    ).properties(
        width='container',
        height=200,
        title=f"{name} Price Trend (Last 30 Days)"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

# Tabs
tabs = st.tabs(["Overview", "Charts", "Fundamentals"])

# --- Overview Tab ---
with tabs[0]:
    for name in selected:
        symbol = assets[name]
        quote = fetch_quote(symbol)
        if "code" in quote:
            st.error(f"{name}: {quote.get('message', 'API error')}")
        else:
            display_card(name, quote)

# --- Charts Tab ---
with tabs[1]:
    for name in selected:
        symbol = assets[name]
        values = fetch_history(symbol)
        display_chart(name, values)

# --- Fundamentals Tab ---
with tabs[2]:
    st.info("Coming soon: Compare financial ratios, revenue, P/E, EPS etc.")
    
