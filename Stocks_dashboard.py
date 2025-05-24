import requests
import streamlit as st
import pandas as pd

# API Configuration
API_BASE = "https://stock.indianapi.in"
API_KEY = st.secrets.get("INDIAN_STOCK_API_KEY", "")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# List of Top NSE Stocks
TOP_STOCKS = ["Reliance", "TCS", "HDFC Bank", "Infosys", "ICICI Bank"]

# Streamlit App Title
st.set_page_config(page_title="Top NSE Stocks Overview", layout="wide")
st.title("Top NSE Stocks - Financial Overview")

# Function to fetch company data by name
def get_company_data(name):
    endpoint = f"{API_BASE}/stock?name={name}"
    try:
        response = requests.get(endpoint, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data for {name}: {e}")
        return None

# Display data for each stock
for stock_name in TOP_STOCKS:
    data = get_company_data(stock_name)
    if data:
        st.subheader(f"{data.get('companyName', stock_name)}")
        current_price = data.get("currentPrice", {})
        percent_change = data.get("percentChange", "N/A")
        year_high = data.get("yearHigh", "N/A")
        year_low = data.get("yearLow", "N/A")
        industry = data.get("industry", "N/A")
        analyst_view = data.get("analystView", {})
        shareholding = data.get("shareholding", {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="NSE Price", value=current_price.get("NSE", "N/A"), delta=f"{percent_change}%")
        with col2:
            st.metric(label="52 Week High", value=year_high)
        with col3:
            st.metric(label="52 Week Low", value=year_low)

        st.markdown(f"**Industry:** {industry}")

        if analyst_view:
            st.markdown("**Analyst View:**")
            st.json(analyst_view)

        if shareholding:
            st.markdown("**Shareholding Pattern:**")
            st.json(shareholding)

        st.markdown("---")
    else:
        st.warning(f"No data available for {stock_name}.")

