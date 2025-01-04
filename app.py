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

# Initialize portfolio in session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

# Select tickers
tickers = st.multiselect(
    "Select Tickers to Compare",
    options=all_tickers,
    default=["MSFT", "AMZN", "AAPL", "META", "GOOGL"]
)

# Select time scale
selected_time_scale = st.radio(
    "Time Scale",
    ["1D", "5D", "1M", "3M", "6M", "1Y", "5Y"],
    horizontal=True
)

# Adjust chart height
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

# Create tabs for Price, Percentage Change, and Portfolio
tab1, tab2, tab3 = st.tabs(["Price", "Percentage Change", "Portfolio"])

# Price Tab
with tab1:
    price_fig = go.Figure()

    for ticker in tickers:
        try:
            stock_data = yf.Ticker(ticker).history(period=selected_period)
            price_fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name=f"{ticker} (Price)",
                line=dict(width=2)
            ))
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

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
        legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center")
    )
    st.plotly_chart(price_fig, use_container_width=True)

# Percentage Change Tab
with tab2:
    pct_change_fig = go.Figure()

    for ticker in tickers:
        try:
            stock_data = yf.Ticker(ticker).history(period=selected_period)
            stock_data['Percentage Change'] = (
                (stock_data['Close'] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]
            ) * 100
            pct_change_fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Percentage Change'],
                mode='lines',
                name=f"{ticker} (% Change)",
                line=dict(width=2)
            ))
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

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
        legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center")
    )
    st.plotly_chart(pct_change_fig, use_container_width=True)

# Portfolio Tab
with tab3:
    st.subheader("Manage Your Portfolio")

    # Add to portfolio form
    with st.form("portfolio_form"):
        # Horizontal alignment using columns
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            ticker = st.selectbox("Select Ticker", all_tickers)
        with col2:
            shares = st.number_input("Number of Shares", min_value=0.0, step=0.01)
        with col3:
            avg_cost = st.number_input("Average Cost per Share (USD)", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add to Portfolio")
        if submitted:
            st.session_state.portfolio.append({"Ticker": ticker, "Shares": shares, "Avg Cost": avg_cost})
            # st.success(f"Added {shares} shares of {ticker} at ${avg_cost:.2f} each.")

    st.markdown("### Current Portfolio")

    # Edit/Delete Portfolio Entries
    if st.session_state.portfolio:
        for idx, stock in enumerate(st.session_state.portfolio):
            col1, col2, col3 = st.columns([10, 1, 1])
            with col1:
                col4, col5, col6 = st.columns([1, 1, 1])
                with col4:
                    st.write(stock["Ticker"])
                with col5: 
                    st.write(str(stock["Shares"]))
                with col6:
                    st.write(str(stock["Avg Cost"]))
            if col2.button("Edit", key=f"edit-{idx}"):
                with st.form(f"edit_form_{idx}"):
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        new_shares = st.number_input(
                            "Edit Number of Shares", min_value=0.0, step=0.01, value=stock["Shares"]
                        )
                    with col2:
                        new_avg_cost = st.number_input(
                            "Edit Average Cost per Share", min_value=0.0, step=0.01, value=stock["Avg Cost"]
                        )
                    submit_edit = st.form_submit_button("Save Changes")
                    if submit_edit:
                        st.session_state.portfolio[idx]["Shares"] = new_shares
                        st.session_state.portfolio[idx]["Avg Cost"] = new_avg_cost
                        # st.success(f"Updated {stock['Ticker']}!")
                        st.rerun()
            if col3.button("Delete", key=f"delete-{idx}"):
                st.session_state.portfolio.pop(idx)
                # st.success(f"Deleted {stock['Ticker']}!")
                st.rerun()

    # Calculate and plot portfolio percentage change over the selected time frame
    if st.session_state.portfolio:
        st.markdown("### Portfolio Percentage Change Over Time")
        portfolio_fig = go.Figure()

        total_initial_value = 0
        weighted_pct_changes = None

        for stock in st.session_state.portfolio:
            try:
                # Fetch stock data
                stock_data = yf.Ticker(stock["Ticker"]).history(period=selected_period)

                # Calculate the initial value of this stock
                initial_value = stock["Shares"] * stock_data["Close"].iloc[0]
                total_initial_value += initial_value

                # Calculate percentage change for the stock
                stock_data["Percentage Change"] = (
                    (stock_data["Close"] - stock_data["Close"].iloc[0]) / stock_data["Close"].iloc[0]
                ) * 100

                # Weighted percentage change for this stock
                stock_weighted_pct = stock_data["Percentage Change"] * initial_value

                # Aggregate weighted percentage changes
                if weighted_pct_changes is None:
                    weighted_pct_changes = stock_weighted_pct
                else:
                    weighted_pct_changes += stock_weighted_pct

            except Exception as e:
                st.error(f"Error fetching data for {stock['Ticker']}: {e}")

        if weighted_pct_changes is not None:
            # Normalize by total initial value to get the portfolio's percentage change
            portfolio_percentage_change = weighted_pct_changes / total_initial_value

            # Plot the portfolio percentage change
            portfolio_fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=portfolio_percentage_change,
                mode='lines',
                name="Portfolio (% Change)",
                line=dict(width=2, color='blue')
            ))

        # Customize the plot
        portfolio_fig.update_layout(
            autosize=True,
            height=chart_height,
            xaxis_title="Date",
            yaxis_title="Portfolio Percentage Change (%)",
            template="plotly_white",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center")
        )
        st.plotly_chart(portfolio_fig, use_container_width=True)
