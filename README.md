# Financial Dynamics and Interconnected Risk of Liquid Restaking

This repository contains the collected data, the R code used, further explanations and clarifications for the following research paper that analyzes the dynamics of the liquid restaking market:

H. O. Sevim, C. F. Torres, “Financial Dynamics and Interconnected Risk of Liquid Restaking,” arXiv:2604.03274, 2026. https://arxiv.org/abs/2604.03274

***Abstract: Decentralized finance introduces new business models and use cases as part of digital finance. Restaking has recently emerged as a transformative mechanism in DeFi, promising extra yields but introducing complex and interconnected risks. The paper monitors the current restaking landscape, empirically analyzes the revenue drivers of a liquid restaking protocol, and conducts a technical investigation on the emitted risk arising from the interconnection between liquid restaking and other protocols. The revenue dynamics of Renzo Protocol are analyzed by employing an OLS regression model, Granger-causality and random forest feature importance tests. Our results identify that revenue is primarily predicted by the value locked in the underlying EigenLayer ecosystem, the yield of Renzo protocol's liquid restaking token and the multi-blockchain expansion of that token. The multi-blockchain expansion of the liquid restaking token presents a double-edged sword: bridging to other networks is crucial for user adoption, but it adds the bridge risks to the existing risks of restaking. We investigate the cross-contamination risk between different DeFi services and the liquid restaking protocol. By mapping the asset flow across the decentralized finance ecosystem, it is detected that the bridge risk of the current size of Renzo's liquid-restaking assets does not impose a systemic risk on the current restaking and staking ecosystem. To address the potential consequences of the emphasized interconnection risks, we introduce two hypothetical scenarios and a stress test, assuming a large number of compromised liquid restaking tokens and a smart contract logic failure in a DeFi protocol. Considering the overall liquid-restaking protocols and the growing interconnection, this analysis requires further work to explore the growing complexities.***

**Keywords:** Blockchain, Decentralized Finance, Restaking, Econometric Analysis, Data Analytics

**Related Skills/Knowledge:** Distributed Systems, Econometrics, Financial Modelling, Crypto-Economic Security (Part of Network Security for Blockchains), Risk Analysis, Attack Simulation.

---

## Repository Structure
```
RestakingDynamics/
│
├── README.md
│
├── restaking_analysis.py                   # Code to analyze the data
│
└── data/
    └── processed_data/                     # This file is required to run the script
        └── restaking_processed_data.xlsx
```
---
## 1 — Code
### `restaking_analysis.py`
The script is written in Python. Fundamental functions are:
- `statsmodels.api.OLS()` for OLS regression.
- Winsorization + `.fit(cov_type="HC3")` for the robustness check with heteroskedasticity-robust standard errors.
- `variance_inflation_factor()` for VIF, to avoid multicollinearity.
- `statsmodels.tsa.stattools.grangercausalitytests()` for the Granger-causality test.
- `sklearn.ensemble.RandomForestRegressor` and `sklearn.inspection.permutation_importance` for random forest feature importance.
- A per-event Chow test (via `scipy.stats.f`) for structural breaks at each `Events` date.
- `statsmodels.stats.diagnostic.linear_reset()` for the RESET functional-form test.

**Input:** `restaking_processed_data.xlsx`

**Requirements:** `pip install pandas numpy statsmodels scikit-learn scipy openpyxl matplotlib`

---
## 2 — Data
### Data Overview
The dataset covers:
- Eigenlayer data on the Ethereum network,
- Renzo Protocol data across Ethereum, Arbitrum, Base, Linea, Blast, and Mode networks.

Data has a daily frequency and covers the period: 22 January 2024 to 17 April 2025. The start date is the first day when Renzo Protocol's LRT (ezETH) is deployed on a layer-2 network.

### Processed Data
The analyzed dataset is `restaking_processed_data.xlsx`.
The following variables are included in the data files:
- Core Financial Metrics: `Revenue` (Total revenue of Renzo Protocol), `TVL0`, (EigenLayer TVL), `TVL1` (Renzo TVL on Ethereum), `TVL2` (Renzo TVL on L2s),   `Share` (ezETH share in the liquid restaking market), `Premium` (ezETH premium variable), `ETH` (ETH price).
- Yield Data: `Yield` (ezETH yield rate), `APY` (stETH APY as the benchmark DeFi yield).
- Market Sentiment: `FGI` (Fear and Greed Index).
- Network Control Variables: `TxFee`.
- Dummy Variable For Tokenization Events: `Events`.

`Events` variable covers:
- 04/26/2024: Renzo Protocol tokenization announcement,
- 04/29/2024: EigenLayer tokenization details are announced,
- 04/30/2024: REZ token was generated,
- 10/01/2024: EIGEN token was generated.

### Data Transformation
The analyzed dataset `restaking_processed_data.xlsx` is constructed through several basic steps:
- We used Python's `dtype` and `isna` functions from the `pandas` package to check data types and identify missing values before transformation.
- The variables `Revenue`, `TVL0`, `TVL1`, and `TVL2` were log-transformed using the log1p function.
- Non stationary variables were differenced using the `diff` function. `TVL1` and `ETH` were the initially non-stationary variables that required differencing.
- The ezETH `Yield` rates queried with `dune_query_ezeth_yield_rate.txt` converted from decimal to percentage points (×100) so that a 1-unit change represents a 1 percentage point change, matching the scale of other variables and making regression coefficients easier to interpret.

### Raw Data Request
Data can be shared upon request as long as sharing is compliant with the terms and conditions of the data sources.

---
## 3 — Limitations
- The relationships identified in the analysis are exploratory and do not imply causation. Co-integration and additional unit root tests might be required to understand the relationships better.
- If the variables are cointegrated, ECM (Error Correction Model) or VECM (Vector Error Correction Model) tests might be required.
- The analysis relies on available subgraph data, which may include inconsistent values. Additionally, restaking service is considerably new, which means historical data on protocols is limited, potentially constraining the analysis of long-term trends in stability and growth.
  
---
