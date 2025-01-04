import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Load all tickers (replace this with an actual list or data source)
all_tickers = []

with open("util/tickers.txt", "r") as file:
    for ticker in file:
        all_tickers.append(ticker.strip())

# Set up Streamlit layout
st.title("Stock Data: Toggle Between Price and Percentage Change")

# Time scale options and mapping
time_scales = ["1D", "5D", "1M", "3M", "6M", "1Y", "5Y"]
time_scale_map = {
    "1D": "1d",
    "5D": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y"
}

# Sidebar for ticker selection
tickers = st.multiselect(
    "Select Tickers to Compare",
    options=all_tickers,
    default=["MSFT", "AMZN", "AAPL", "GOOGL", "META"]
)

# Toggle between price and percentage change
chart_type = st.radio(
    "Select Chart Type",
    options=["Price", "Percentage Change"],
    horizontal=True
)

# Create a container for the chart
with st.container():
    if not tickers:
        st.warning("Please select at least one ticker to display.")
    else:
        # Time Scale Selector
        selected_time_scale = st.radio(
            "Select Time Scale", time_scales, horizontal=True
        )

        # Map the selected time scale to yfinance period
        selected_period = time_scale_map[selected_time_scale]

        # Create Plotly figure
        chart_fig = go.Figure()

        # Fetch and plot data for each selected ticker
        for ticker in tickers:
            try:
                # Fetch stock data
                stock_data = yf.Ticker(ticker).history(period=selected_period)

                if chart_type == "Price":
                    # Plot price data
                    chart_fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name=f"{ticker} (Price)",
                        line=dict(width=2)
                    ))
                elif chart_type == "Percentage Change":
                    # Calculate percentage change since the start of the period
                    stock_data['Percentage Change'] = (
                        (stock_data['Close'] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]
                    ) * 100

                    # Plot percentage change data
                    chart_fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Percentage Change'],
                        mode='lines',
                        name=f"{ticker} (% Change)",
                        line=dict(width=2)
                    ))

            except Exception as e:
                st.error(f"Error fetching data for {ticker}: {e}")

        # Customize the chart layout
        yaxis_title = "Close Price (USD)" if chart_type == "Price" else "Percentage Change (%)"
        chart_fig.update_layout(
            autosize=True,  # Enables responsive sizing
            height=900,     # Set a taller default height
            title=f"{chart_type} Comparison - {', '.join(tickers)}",
            xaxis_title="Date",
            yaxis_title=yaxis_title,
            template="plotly_white",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20)
        )

        # Display the chart
        st.plotly_chart(chart_fig, use_container_width=True)
