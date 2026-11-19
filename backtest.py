import pandas as pd
import numpy as np
import vectorbt as vbt
from Binance_data import btc_ohlcv
import matplotlib.pyplot as plt


def preprocess_data(df):
    """Ensures numeric data types for OHLCV columns."""
    df = df.copy()
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def calculate_williams_fractals(df, period=20, stop_loss_pct=0.02):
    """
    Identifies Williams Fractals (swing highs/lows) and calculates dynamic stop-losses.
    """
    high = df['High']
    low = df['Low']

    bear_fractals = pd.Series(np.nan, index=df.index)
    bull_fractals = pd.Series(np.nan, index=df.index)
    stop_loss = pd.Series(np.nan, index=df.index)

    # Note: Williams Fractals require 'period' lookahead to confirm a pivot.
    for i in range(period, len(df) - period):
        window = df.iloc[i - period: i + period + 1]

        if window['High'].iloc[period] == window['High'].max():
            bear_fractals.iloc[i] = high.iloc[i]
        if window['Low'].iloc[period] == window['Low'].min():
            bull_fractals.iloc[i] = low.iloc[i]

        if not np.isnan(bear_fractals.iloc[i]):
            stop_loss.iloc[i] = bear_fractals.iloc[i] * (1 - stop_loss_pct)
        elif not np.isnan(bull_fractals.iloc[i]):
            stop_loss.iloc[i] = bull_fractals.iloc[i] * (1 + stop_loss_pct)

    return bear_fractals, bull_fractals, stop_loss


def run_backtest(df, entries, exits, stop_loss, initial_capital=1000.0, fee_pct=0.0005):
    """
    Stateful backtest engine with percentage-based compounding returns,
    stop-loss tracking, and transaction fees.
    """
    close = df['Close']
    low = df['Low']

    portfolio_value = np.zeros(len(df))
    cash = initial_capital
    position_size = 0.0
    entry_price = 0.0
    current_stop = 0.0

    portfolio_value[0] = initial_capital

    for i in range(1, len(df)):
        current_close = close.iloc[i]
        current_low = low.iloc[i]

        # Check Stop-Loss breach if in a long position
        if position_size > 0 and current_low <= current_stop:
            # Exit via stop loss
            cash = position_size * current_stop * (1 - fee_pct)
            position_size = 0.0
            current_stop = 0.0

        # Regular Entry Logic
        elif position_size == 0 and entries.iloc[i]:
            entry_price = current_close
            capital_to_deploy = cash * (1 - fee_pct)  # Apply entry fee
            position_size = capital_to_deploy / entry_price
            cash = 0.0
            if not np.isnan(stop_loss.iloc[i]):
                current_stop = stop_loss.iloc[i]

        # Regular Exit Logic
        elif position_size > 0 and exits.iloc[i]:
            cash = position_size * current_close * (1 - fee_pct)  # Apply exit fee
            position_size = 0.0
            current_stop = 0.0

        # Mark-to-market portfolio valuation
        if position_size > 0:
            portfolio_value[i] = position_size * current_close
        else:
            portfolio_value[i] = cash

    return pd.Series(portfolio_value, index=df.index)


# --- Execution Pipeline ---
if __name__ == "__main__":
    # 1. Load and Clean Data
    data = preprocess_data(btc_ohlcv)

    # 2. Parameters
    period = 20
    stop_loss_pct = 0.02
    initial_capital = 1000.0
    fee_pct = 0.0005  # 0.05% fee per transaction (realistic for exchanges)

    # 3. Compute Indicators & Signals
    bear_fractals, bull_fractals, stop_loss = calculate_williams_fractals(data, period, stop_loss_pct)

    # Align signals with historical confirmation shift
    exits = bear_fractals.notna().shift(period).fillna(False)
    entries = bull_fractals.notna().shift(period).fillna(False)

    # 4. Run Backtest
    portfolio_curve = run_backtest(data, entries, exits, stop_loss, initial_capital, fee_pct)

    # 5. Performance Metrics Summary
    final_val = portfolio_curve.iloc[-1]
    total_return_pct = ((final_val - initial_capital) / initial_capital) * 100
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Portfolio Value: ${final_val:,.2f}")
    print(f"Net Strategy Return: {total_return_pct:.2f}%")

    # 6. Plotting Results
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_curve, label='Portfolio Value (Compound & Fee-Adjusted)', color='blue')
    plt.title('Compounded Portfolio Equity Curve with Stop-Loss & Fees')
    plt.xlabel('Date')
    plt.ylabel('Value ($)')
    plt.legend()
    plt.grid(True)
    plt.show()
