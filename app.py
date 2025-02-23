import streamlit as st
import pandas as pd
import yahoo_fin.stock_info as si

def fetch_data(tickers):
    """Fetches adjusted closing prices for given tickers from Yahoo Finance."""
    data = {}
    for ticker in tickers:
        try:
            df = si.get_data(ticker, interval="1d")  # Daily data
            data[ticker] = df['adjclose']
        except Exception as e:
            st.error(f"Could not fetch data for {ticker}. Error: {e}")
            return None  # Return None if any ticker fails
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
    reference_index = st.sidebar.selectbox("Reference Index", ["SPY", "DJI", "QQQ", "IXIC"], index=0) # Added more common indices
    default_comparison_assets = ["HSI", "GLD", "BTC-USD"] # BTC-USD is Yahoo Finance ticker for Bitcoin
    comparison_assets = st.sidebar.multiselect(
        "Comparison Assets",
        ["HSI", "GLD", "BTC-USD", "AAPL", "MSFT", "TSLA", "EURUSD=X", "GBPUSD=X", "JPY=X"], # Added more asset options and currencies
        default=default_comparison_assets
    )

    tickers_to_fetch = [reference_index] + comparison_assets

    st.info(f"Fetching data for: {', '.join(tickers_to_fetch)}...")
    raw_data = fetch_data(tickers_to_fetch)

    if raw_data is not None:
        st.success("Data fetched successfully!")

        st.subheader("Raw Adjusted Closing Prices")
        st.dataframe(raw_data.tail()) # Display last few rows of raw data

        relative_performance_df = calculate_relative_performance(raw_data, reference_index)

        if relative_performance_df is not None:
            st.subheader(f"Relative Performance (Normalized to {reference_index} = 100)")
            st.markdown(f"This chart shows how each asset performs *relative* to the **{reference_index}**.  When the line for an asset is above 100, it means it has outperformed the {reference_index} since the beginning of the data period. Below 100 means it has underperformed.")
            st.line_chart(relative_performance_df)
        else:
            st.error("Error calculating relative performance.")
    else:
        st.error("Failed to fetch data. Please check tickers and internet connection.")

if __name__ == "__main__":
    main()
