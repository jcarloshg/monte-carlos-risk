# Quant Trading Pipeline — Phases Summary

Condensed overview of the seven phases that compose a production-grade quantitative trading pipeline, distilled from `logarithm/README.md`. Each phase below states its core objective, the key engineering problems to solve, and the deliverable it produces.

---

## Phase 1 — Data Engineering

**Core objective.** Transform raw, heterogeneous market data into a clean, normalized, point-in-time correct dataset. Every record must contain only information that was knowable at the time of its timestamp — a single survivorship error or timezone misalignment contaminates every downstream calculation.

**Key problems to solve.**

- **Survivorship bias**: the historical universe must include delisted, merged, and bankrupt securities.
- **Point-in-time correctness**: fundamental data (earnings, filings) must be tagged with the date they were *published*, not the reporting period end date.
- **Corporate actions**: price series require backward-adjusted splits, dividends, and spin-offs (back-adjusted vs. ratio-adjusted paradigms).
- **Market microstructure artifacts**: bid-ask bounce, stale quotes, crossed markets, and exchange outages must be filtered before any signal computation.
- **Tick data alignment**: consolidating multi-exchange feeds into a single NBBO requires sequence-number reconciliation and latency normalization.

**Deliverable.** A point-in-time correct, survivorship-bias-free research dataset: clean OHLCV bars at the target frequency, adjusted price series with corporate action factors, a valid security master with delisting reasons, and fundamental/alternative data panels with `as_of_date` tagging. Typically materialized as partitioned Parquet files or Arctic symbol stores.

---

## Phase 2 — Alpha Research

**Core objective.** Generate statistically robust predictive signals with positive expected return after transaction costs. The research process is a formal statistical hypothesis cycle: hypothesize an inefficiency → operationalize as a factor → measure IC and ICIR → validate out-of-sample. An alpha is a conditional expectation of forward returns: `E[rₜ₊ₕ | Xₜ]`.

**Key problems to solve.**

- **Multiple testing / data snooping**: testing many signals on the same data guarantees spurious discoveries — apply Bonferroni/BH correction and reserve a truly untouched hold-out set.
- **Signal decay**: measure IC at multiple forward horizons (1d, 5d, 21d) to determine the alpha's half-life and the appropriate holding period and turnover budget.
- **Factor orthogonalization**: decompose raw signals into systematic (beta) and idiosyncratic components before combining — raw momentum overlaps with size, value, and sector exposures that are not the intended bet.
- **Neutralization**: cross-sectional signals must be market-neutral, sector-neutral, and beta-neutral to isolate the intended anomaly.

**Deliverable.** A signal specification document and corresponding production-ready signal code: a function `compute_signal(universe, data) → pd.DataFrame` that outputs a cross-sectional z-score for each security at each date, with IC/ICIR statistics, a factor decay curve, and a documented out-of-sample validation period.

---

## Phase 3 — Backtesting & Simulation

**Core objective.** Estimate the realistic historical performance of a strategy under conditions that accurately simulate live trading. The primary engineering goal is *fidelity*, not favorable metrics — a backtest that overestimates performance by failing to model costs and market impact is worse than useless; it actively misallocates capital.

**Key problems to solve.**

- **Look-ahead bias**: using future data in signal computation — enforce strict `shift(1)` discipline and point-in-time data.
- **Survivorship bias**: testing only on currently-listed stocks — use a full universe including delistings.
- **Overfitting**: parameters tuned to in-sample noise — apply walk-forward CV and combinatorial purged CV (CPCV).
- **Transaction cost underestimation**: ignoring spread, market impact, and borrow cost — use empirical cost models such as Almgren-Chriss.
- **Fill assumption errors**: assuming fills at close/open without slippage — use realistic models (VWAP participation, partial fills).
- **Leverage / margin**: not modeling margin calls and forced liquidations — simulate margin accounts with realistic haircuts.

**Realistic cost components.** `Net P&L = Gross P&L − bid-ask spread cost − market impact (Almgren-Chriss: σ · √(ADV participation)) − commissions − short borrow cost − slippage on partial fills − financing cost on leveraged positions`.

**Deliverable.** A strategy performance report with annualized Sharpe (in-sample, out-of-sample, walk-forward average), maximum drawdown, Calmar ratio, turnover, capacity estimate (AUM at which impact degrades Sharpe by 50%), and a `pyfolio` tear sheet. Gate criteria: Sharpe ≥ 1.0 out-of-sample, max drawdown ≤ 20%, CPCV-estimated Sharpe variance < 30%.

---

## Phase 4 — Portfolio Construction

**Core objective.** Combine multiple alpha signals and asset positions into a single coherent portfolio that maximizes expected risk-adjusted return subject to real-world constraints. This is a formal mathematical optimization problem solved at each rebalancing event.

**The optimization problem.**

```
Maximize:   wᵀμ − (λ/2)wᵀΣw         (mean-variance objective)
Subject to: 1ᵀw = 1                  (fully invested)
            |w| ≤ w_max              (single-name concentration limit)
            wᵀβ_factor ≈ 0          (factor neutrality)
            Turnover(w, w_prev) ≤ T_budget  (transaction cost constraint)
```

Where `μ` is the alpha signal vector, `Σ` is the covariance matrix (typically from a risk model like Barra), and `λ` is the risk aversion parameter calibrated to the target portfolio volatility.

**Key design decisions.**

- **Risk model choice**: use a multi-factor risk model (Barra) rather than the sample covariance matrix for N > 100 assets — the sample covariance is poorly conditioned and leads to extreme concentrated allocations.
- **Rebalance frequency**: determined by signal half-life vs. transaction costs. A 21-day IC decay implies monthly rebalance; a 1-day IC decay implies daily or intraday.
- **Turnover penalty**: add `λ_tc · ||w − w_prev||₁` to the objective to regularize portfolio changes and model rebalancing costs explicitly.

**Deliverable.** A target weight vector `w*` for each rebalancing period, with factor exposure attribution, expected turnover, and estimated transaction cost of transitioning from the current portfolio to target. This feeds directly into the execution layer as a trade list `Δw = w* − w_current`.

---

## Phase 5 — Risk Management & Pre-Trade Controls

**Core objective.** Apply a layered set of quantitative and rule-based controls that gate every order before it reaches the market. Risk management is both a real-time enforcement system and a continuous portfolio-level monitoring process. The goal is asymmetric: catch dangerous positions before execution; do not slow down alpha-generating trades.

**Control layers.**

**Pre-trade (order-level, microsecond latency):**

- Maximum order size as % of ADV (e.g., single order ≤ 5% of 30-day ADV).
- Price reasonability check: reject orders > N% from last traded price.
- Fat-finger check: order value > threshold → manual approval queue.
- Symbol-level hard limits: restricted list, blacklisted securities.
- Margin / buying-power validation against real-time account state.

**Portfolio-level (per rebalance or intraday):**

- Gross and net exposure limits (e.g., gross ≤ 3× NAV).
- Single-name concentration (e.g., no position > 5% of NAV).
- Sector / factor exposure limits, enforced via risk model attribution.
- VaR and CVaR monitoring: alert at 80% of limit, halt at 100%.
- Maximum drawdown circuit breaker: halt strategy at −10% from HWM.
- Correlation monitoring: detect regime shifts via rolling correlation breaks.

**Stress testing:**

- Replay portfolio through historical stress scenarios (2008 crisis, COVID March 2020, 2022 rate shock).
- Hypothetical scenario shocks: equity −30%, credit spreads +200bps, VIX +40 points.
- Factor sensitivity reports: P&L change per 1σ move in each risk factor.

**Deliverable.** A cleared trade list — the subset of the target weight vector's trades that passed all pre-trade risk controls — plus a real-time risk dashboard showing current VaR, factor exposures, gross/net leverage, and drawdown status. Any rejected orders are logged with the specific violated limit for audit.

---

## Phase 6 — Execution & Order Management

**Core objective.** Convert the cleared trade list into market orders and execute them at the lowest possible realized cost — minimizing market impact, timing risk, and implementation shortfall. Execution quality directly erodes alpha: a strategy with a theoretical Sharpe of 2.0 can degrade to 0.8 in live trading purely through poor execution.

**Core execution algorithms.**

| Algorithm | Use case | Math |
| --- | --- | --- |
| **VWAP** | Blend into volume profile | Track daily VWAP; participate proportionally to historical volume curve |
| **TWAP** | Uniform time slicing | Equal notional over N time intervals |
| **Implementation Shortfall (IS)** | Minimize arrival price slippage | Almgren-Chriss: balance urgency vs. market impact |
| **POV (Percent of Volume)** | Passive execution, long alpha | Maintain fixed % participation in real-time observed volume |
| **Dark pool routing** | Minimize information leakage | Route block trades to ATS/dark pools (IEX, Liquidnet) before lit exchange |
| **SOR (Smart Order Router)** | Best execution across venues | Route to best BBO across NYSE, NASDAQ, BATS, EDGX, dark pools |

**Market microstructure considerations.**

- **Information leakage**: large orders reveal intent — use iceberg/reserve orders, randomize timing, fragment across venues.
- **Adverse selection**: limit orders fill when the market moves against you — model fill probability and adverse selection cost.
- **Latency**: co-location reduces round-trip to ~1–10μs; retail brokers sit at ~50ms. For HFT, this is existential.
- **FIX protocol**: the universal standard for order routing — every institutional connection uses FIX 4.2/4.4 or FIXT 1.1.

**Deliverable.** Filled trade confirmations (FIX `ExecutionReport` messages) with per-fill price, venue, and latency; updated position records in the OMS; and a real-time implementation shortfall report comparing actual fills vs. decision price (IS) and vs. VWAP/TWAP benchmarks. This feeds directly into TCA for Phase 7.

---

## Phase 7 — Live Monitoring & Post-Trade Analysis

**Core objective.** Continuously validate that the live strategy behaves as the backtest predicted. The core engineering problem is **distribution shift detection**: is today's live P&L consistent with the modeled return distribution, or is something broken (data feed error, regime change, model decay, execution bug)?

**Monitoring dimensions.**

**System health (ops-level):**

- Data feed heartbeats and latency (alert if market data > N ms stale).
- OMS connectivity and position reconciliation vs. prime broker.
- Memory, CPU, and network utilization of all trading processes.
- Order rejection rates — spikes indicate pre-trade risk misconfiguration or connectivity issues.

**Strategy health (quant-level):**

- Live IC: does the signal's daily rank correlation with realized returns match the backtest IC distribution?
- P&L attribution: break down P&L by signal, factor, sector, and execution cost daily.
- Turnover vs. plan: excessive turnover signals instability or an execution bug.
- Drawdown monitoring vs. circuit breaker thresholds.
- Factor exposure drift: has the portfolio drifted from the target risk profile?

**Regime monitoring:**

- Rolling realized volatility vs. GARCH forecast: detect vol regime shifts.
- Correlation matrix stability: a sudden correlation spike signals risk-off.
- Signal z-score distribution: divergence from backtest indicates possible model decay.

**The feedback loop.** Post-trade analysis is not terminal — it is the research input for the next cycle. Regime detection findings feed back into Phase 2 (re-research signal parameters). TCA findings feed back into Phase 6 (switch execution algorithms or brokers). Drawdown analysis feeds back into Phase 5 (tighten risk limits). This is why the pipeline diagram shows a continuous return arc from Phase 7 → Phase 1.

**Deliverable.** A daily strategy report containing live vs. backtest Sharpe ratio (rolling 63-day), factor attribution, IC realized vs. expected, execution TCA summary, current drawdown vs. HWM, and a formal model health status (green / yellow / red). Yellow/red status triggers a defined escalation: parameter review, position reduction, or strategy halt.

---

## Architecture Notes (cross-cutting)

A few cross-cutting engineering decisions that affect every phase:

- **Identifier management**: use a persistent, vendor-neutral security identifier (`FIGI` or `PermID`) as the primary key across all systems. Ticker symbols change on rebalance and corporate actions; relying on tickers causes silent data corruption.
- **Timezone discipline**: all timestamps stored in UTC nanoseconds. Market-local time conversions happen only at the display layer. Exchange timestamps vs. receipt timestamps must both be recorded for latency profiling.
- **Immutability**: never mutate historical data records. Corrections are appended as new records with a `corrected_at` timestamp — this preserves audit trails and allows point-in-time replay.
- **Separation of research and production code**: the research codebase (Jupyter, exploratory) and the production codebase (typed Python or C++, unit-tested, CI/CD deployed) must be strictly separated with a formal promotion process. Merging them is the single most common source of production bugs in quant shops.
