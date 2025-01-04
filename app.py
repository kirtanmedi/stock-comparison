import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

# Set up Streamlit page configuration
st.set_page_config(layout="wide", page_title="Stock Data Viewer", initial_sidebar_state="collapsed")

# Manual toggle for testing mobile view
is_mobile = st.sidebar.checkbox("Switch to Mobile View", value=False)

# Load all tickers from a text file
all_tickers = []
with open("utils/tickers.txt", "r") as file:
    for ticker in file:
        all_tickers.append(ticker.strip())

# App title
st.title("Stock Data Viewer")

# Select tickers
tickers = st.multiselect(
    "Select Tickers to Compare",
    options=all_tickers,
    default=["MSFT", "AMZN", "AAPL", "META", "GOOGL"]
)

# Select time scale
# st.markdown("### Time Scale")
selected_time_scale = st.radio(
    "Time Scale",
    ["1D", "5D", "1M", "3M", "6M", "1Y", "5Y"],
    horizontal=True
)

# Adjust chart height (slightly shorter for mobile)
chart_height = 500 if is_mobile else 950

# Map the selected time scale to yfinance periods
time_scale_map = {
    "1D": "1d",
    "5D": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y"
}
selected_period = time_scale_map[selected_time_scale]

# Create tabs for Price and Percentage Change
tab1, tab2 = st.tabs(["Price", "Percentage Change"])

with tab1:
    # Create a Plotly figure for Price
    price_fig = go.Figure()

    for ticker in tickers:
        try:
            # Fetch stock data
            stock_data = yf.Ticker(ticker).history(period=selected_period)

            # Plot price data
            price_fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name=f"{ticker} (Price)",
                line=dict(width=2)
            ))

        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    # Customize the price chart layout
    price_fig.update_layout(
        autosize=True,
        height=chart_height,
        xaxis_title="Date",
        yaxis_title="Close Price (USD)",
        template="plotly_white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            y=1.15,
            x=0.5,
            xanchor="center"
        )
    )

    # Display the Price chart
    st.plotly_chart(price_fig, use_container_width=True)

with tab2:
    # Create a Plotly figure for Percentage Change
    pct_change_fig = go.Figure()

    for ticker in tickers:
        try:
            # Fetch stock data
            stock_data = yf.Ticker(ticker).history(period=selected_period)

            # Calculate percentage change since the start of the period
            stock_data['Percentage Change'] = (
                (stock_data['Close'] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]
            ) * 100

            # Plot percentage change data
            pct_change_fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Percentage Change'],
                mode='lines',
                name=f"{ticker} (% Change)",
                line=dict(width=2)
            ))

        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    # Customize the percentage change chart layout
    pct_change_fig.update_layout(
        autosize=True,
        height=chart_height,
        xaxis_title="Date",
        yaxis_title="Percentage Change (%)",
        template="plotly_white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            y=1.15,
            x=0.5,
            xanchor="center"
        )
    )

    # Display the Percentage Change chart
    st.plotly_chart(pct_change_fig, use_container_width=True)
