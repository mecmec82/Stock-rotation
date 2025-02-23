import streamlit as st
import pandas as pd
import yfinance as yf  # Import yfinance

def fetch_data(tickers):
    """Fetches adjusted closing prices for given tickers from Yahoo Finance using yfinance."""
    data = {}
    for ticker in tickers:
        try:
            # Use yf.download to get data directly into a DataFrame
            df = yf.download(ticker, period="max", interval="1d") # period="max" gets max available history
            if df.empty:
                st.error(f"No data found for {ticker} from yfinance.")
                return None
            data[ticker] = df['Adj Close'] # 'Adj Close' column in yfinance
        except Exception as e:
            st.error(f"Could not fetch data for {ticker} using yfinance. Error: {e}")
            return None
    return pd.DataFrame(data)

def calculate_relative_performance(df, reference_ticker):
    """Calculates relative performance compared to a reference ticker."""
    if reference_ticker not in df.columns:
        st.error(f"Reference ticker '{reference_ticker}' not found in data.")
        return None

    reference_series = df[reference_ticker]
    relative_df = df.copy()

    for col in df.columns:
        relative_df[col] = (df[col] / reference_series) * 100  # Normalize to reference index

    return relative_df

def main():
    st.title("Relative Market Performance Dashboard")
    st.markdown("Compare market performance relative to a reference index.")

    # Sidebar controls
    st.sidebar.header("Settings")
    reference_index = st.sidebar.selectbox("Reference Index", ["SPY", "DJI", "QQQ", "^IXIC"], index=0) # ^IXIC for Nasdaq Composite in yfinance
    default_comparison_assets = ["HSI", "GLD", "BTC-USD"]
    comparison_assets = st.sidebar.multiselect(
        "Comparison Assets",
        ["HSI", "GLD", "BTC-USD", "AAPL", "MSFT", "TSLA", "EURUSD=X", "GBPUSD=X", "JPY=X"],
        default=default_comparison_assets
    )

    tickers_to_fetch = [reference_index] + comparison_assets

    st.info(f"Fetching data for: {', '.join(tickers_to_fetch)}...")
    raw_data = fetch_data(tickers_to_fetch)

    if raw_data is not None:
        st.success("Data fetched successfully using yfinance!")

        st.subheader("Raw Adjusted Closing Prices")
        st.dataframe(raw_data.tail())

        relative_performance_df = calculate_relative_performance(raw_data, reference_index)

        if relative_performance_df is not None:
            st.subheader(f"Relative Performance (Normalized to {reference_index} = 100)")
            st.markdown(f"This chart shows how each asset performs *relative* to the **{reference_index}**.  When the line for an asset is above 100, it means it has outperformed the {reference_index} since the beginning of the data period. Below 100 means it has underperformed.")
            st.line_chart(relative_performance_df)
        else:
            st.error("Error calculating relative performance.")
    else:
        st.error("Failed to fetch data using yfinance. Please check tickers and internet connection.")

if __name__ == "__main__":
    main()
