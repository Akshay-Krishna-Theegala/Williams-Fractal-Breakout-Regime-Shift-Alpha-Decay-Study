# Williams Fractal Breakout: Regime Shift & Alpha Decay Study

A Python backtesting case study examining **market regime dependency**, **alpha decay**, and **transaction cost friction** on a Bill Williams Fractal breakout strategy across historical BTC/TUSD 5-minute intervals.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Backtest](https://img.shields.io/badge/Backtest-Compounded%20%26%20Fee--Adjusted-green)
![Focus](https://img.shields.io/badge/Research-Regime%20Analysis-lightgrey)

---

## Overview

Quantitative trading rules rarely fail all at once—more often, they perform well in one market environment and quietly degrade when underlying volatility or trend structure shifts. 

This repository documents a controlled experiment on a classic swing-pivot breakout system (`period = 20`) with a fixed stop-loss mechanism:
* **Favorable Regime (March 2023):** Strong directional price swings allowed breakout entries to capture sustained moves, growing a $1,000 starting balance to a peak of ~$1,142 and closing the window near ~$1,081 after fees.
* **Extended Multi-Regime Window (March – July 2023):** Once market conditions transitioned into prolonged consolidation and mean-reverting chop, the same ruleset suffered steady alpha decay, drawing the portfolio down toward ~$695.

Rather than optimizing parameters after the fact to force an upward curve, this project preserves both outcomes to illustrate how unconditioned breakout models behave across changing regimes.

---

## Equity Curve Comparison

### 1. Trending Regime (`2023-03-11` to `2023-04-01`)
Directional momentum outweighed stop-loss whipsaws and per-trade commissions, producing a net gain over the sample window.

<img width="1536" height="762" alt="image_01" src="https://github.com/user-attachments/assets/4f45743f-9497-4ce1-876f-7e2222c62db8" />


### 2. Full Multi-Regime Horizon (`2023-03-11` to `2023-07-24`)
Exposed to sideways price action without a macro regime filter, frequent false breakouts and round-trip transaction fees gradually eroded capital.

<img width="1536" height="762" alt="image_02" src="https://github.com/user-attachments/assets/529dcea2-ebb7-4882-9261-4e1e73c50ba3" />

---

## Methodology & Backtest Design

To keep the evaluation honest and free of common backtest distortions, the simulation enforces three constraints:

* **Confirmation-Aligned Signals:** Williams Fractals require $N$ subsequent bars to confirm a local swing high or low. All entry and exit triggers are shifted forward by `period` bars (`shift(period)`) so decisions only occur after a pivot is observable in real time.
* **Compounding Position Sizing:** Returns are computed multiplicatively on available equity rather than summing raw price differences, ensuring position sizes scale realistically with account balance.
* **Execution Friction & Stop-Loss Checks:** Each entry and exit incurs a `0.05%` fee (`fee_pct = 0.0005`), and open long positions evaluate intra-bar `Low` prices against the active stop-loss threshold. *(Note: Slippage during rapid volatility spikes and order-book depth constraints are approximated through the flat fee rate rather than tick-level execution modeling.)*

---

## Key Takeaways & Next Steps
* Don't Trust Short Windows Alone: A great short-term curve is rarely enough proof; longer multi-regime testing is where alpha decay shows up.

* Unfiltered Breakouts Struggle in Chop: Without a trend-strength or volatility filter (such as ADX, Bollinger Band width, or higher-timeframe moving average alignment), swing breakouts get whipsawed in sideways markets.

* Future Exploration: Testing higher timeframes (1h / 4h) and adding regime filters to reduce false signals when volatility contracts.

# Author: Akshay Krishna Theegala
## Repository Structure

```text
|
├── Binance_data.py               # Binance public REST API client for 5m OHLCV data
├── Williams_Fractals.py          # Fractal detection, stop-loss logic, and backtest loop
└── README.md                     # Study overview and findings
