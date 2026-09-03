
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

DATA_FILE = "data/prices_full.csv" if os.path.exists("data/prices_full.csv") else "data/prices_seed.csv"


def load_data(path=DATA_FILE):
    df = pd.read_csv(path, parse_dates=["date"])
    return df.sort_values(["ticker", "date"])


def compute_returns(df):
    """Adds period-over-period % return and cumulative return per ticker."""
    df = df.copy()
    df["pct_return"] = df.groupby("ticker")["close_price"].pct_change() * 100
    df["cum_return"] = df.groupby("ticker")["close_price"].transform(
        lambda s: (s / s.iloc[0] - 1) * 100
    )
    return df


def summary_table(df):
    """One row per ticker: date range, total return, avg |period return|,
    and an approximate annualised volatility from the available (irregular)
    sample points."""
    rows = []
    for ticker, g in df.groupby("ticker"):
        g = g.sort_values("date")
        n_points = len(g)
        start_date, end_date = g["date"].iloc[0], g["date"].iloc[-1]
        total_return = (g["close_price"].iloc[-1] / g["close_price"].iloc[0] - 1) * 100
        days_span = (end_date - start_date).days
        avg_abs_return = g["pct_return"].abs().mean()
        # Approximate annualised volatility: std of period returns scaled by
        # sqrt(periods per year based on average spacing). Flagged as an
        # approximation given irregular, sparse sampling intervals.
        avg_gap_days = days_span / max(n_points - 1, 1)
        periods_per_year = 365 / avg_gap_days if avg_gap_days > 0 else np.nan
        approx_ann_vol = g["pct_return"].std() * np.sqrt(periods_per_year) if n_points > 2 else np.nan
        rows.append({
            "ticker": ticker,
            "n_points": n_points,
            "start_date": start_date.date(),
            "end_date": end_date.date(),
            "total_return_pct": round(total_return, 1),
            "avg_abs_period_return_pct": round(avg_abs_return, 1) if n_points > 1 else None,
            "approx_annualised_vol_pct": round(approx_ann_vol, 1) if not np.isnan(approx_ann_vol) else None,
        })
    return pd.DataFrame(rows)


def plot_normalized_comparison(df, outpath="charts/normalized_comparison.png"):
    """Indexes each ticker to 100 at its first available date so tickers
    with different start dates can be compared on relative performance."""
    fig, ax = plt.subplots(figsize=(9, 5))
    for ticker, g in df.groupby("ticker"):
        g = g.sort_values("date")
        indexed = g["close_price"] / g["close_price"].iloc[0] * 100
        ax.plot(g["date"], indexed, marker="o", label=ticker)
    ax.set_title("Relative Price Performance (Indexed to 100 at first data point)")
    ax.set_ylabel("Indexed price (start = 100)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    print(f"Saved chart to {outpath}")


if __name__ == "__main__":
    print(f"Using data source: {DATA_FILE}\n")
    df = load_data()
    df = compute_returns(df)

    print("\n=== Period returns ===")
    print(df[["ticker", "date", "close_price", "pct_return", "cum_return"]].to_string(index=False))

    print("\n=== Summary ===")
    summary = summary_table(df)
    print(summary.to_string(index=False))

    plot_normalized_comparison(df)
