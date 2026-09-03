"""
Needs internet 

"""
import pandas as pd
import yfinance as yf

TICKERS = ["COHR", "TSLA", "LITE", "GLW"]
PERIOD = "2y"

def main():
    frames = []
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        hist = yf.Ticker(ticker).history(period=PERIOD)
        df = hist.reset_index()[["Date", "Close"]].rename(columns={"Date": "date", "Close": "close_price"})
        df["ticker"] = ticker
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["source"] = "yfinance"
        frames.append(df[["ticker", "date", "close_price", "source"]])

    full = pd.concat(frames, ignore_index=True)
    full.to_csv("data/prices_full.csv", index=False)
    print(f"Saved {len(full)} rows to data/prices_full.csv")

if __name__ == "__main__":
    main()
