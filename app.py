import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="centered", page_title="Stock Data Viewer")

# Load all tickers
all_tickers = []

with open("utils/tickers.txt", "r") as file:
    for ticker in file:
        all_tickers.append(ticker.strip())

# Title
st.title("Stock Data: Toggle Between Price and Percentage Change")

# Split layout into columns for better mobile readability
col1, col2 = st.columns([3, 1])

with col1:
    tickers = st.multiselect(
        "Select Tickers to Compare",
        options=all_tickers,
        default=["MSFT", "AMZN", "AAPL", "GOOGL", "META"]
    )

with col2:
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
            "Select Time Scale",
            ["1D", "5D", "1M", "3M", "6M", "1Y", "5Y"],
            horizontal=True
        )

        # Map the selected time scale to yfinance period
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

        # Create Plotly figure
        chart_fig = go.Figure()

        # Fetch and plot data for each selected ticker
        for ticker in tickers:
            try:
                stock_data = yf.Ticker(ticker).history(period=selected_period)

                if chart_type == "Price":
                    chart_fig.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name=f"{ticker} (Price)",
                        line=dict(width=2)
                    ))
                elif chart_type == "Percentage Change":
                    stock_data['Percentage Change'] = (
                        (stock_data['Close'] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]
                    ) * 100
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
        chart_fig.update_layout(
            autosize=True,  # Enables responsive sizing
            height=600,     # Shorter default height for mobile
            title=f"{chart_type} Comparison - {', '.join(tickers)}",
            xaxis_title="Date",
            yaxis_title="Close Price (USD)" if chart_type == "Price" else "Percentage Change (%)",
            template="plotly_white",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20)
        )

        # Display the chart
        st.plotly_chart(chart_fig, use_container_width=True)
