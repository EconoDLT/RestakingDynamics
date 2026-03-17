# Financial Dynamics of Liquid Restaking
**DeFi, Restaking Protocols, and Layered Risks across Interconnected Protocols and Blockchains**

This repository contains the collected data, the R code used, further explanations and clarifications for the research paper that analyzes the dynamics of the liquid restaking market.

**Related Skills/Knowledge:** Distributed Systems, Econometrics, Financial Modelling, Crypto-Economic Security (Part of Network Security for Blockchains), Risk Analysis, Attack Simulation.

---

## Repository Structure

```
RestakingDynamics/
│
├── README.md
│
├── analysis_code/
│   └── restaking_analysis.R
│
└── data/
    └── processed_data/             # This file is required to run the script
    │   └── restaking_processed_data.xlsx
    └── raw_data/                   # This folder includes multiple raw data files
                                    # Free to use as long as the data source is stated
```

---

## 1 — Code

### `restaking_analysis.R`

The script is written in R. Fundamental functions are:
- `lm()` for OLS regression.
- `VAR()` and `causality()` for Granger-causality test.
- `randomForest()`, `importance()` and `varImpPlot()` for random forest feature importance test.
- `anova()` for Chow‑type structural break test
- `residuals()` to see the regression residuals.
- `vif()` to see the variance inflation factor, to avoid multicollinearity.

---

## 2 — Data

### Data Overview

The dataset covers:
- 53 bridge protocols,
- 15 on-chain lending protocols,
- 9 blockchains (three groups: Ethereum (L1), L2, AltL1).
Protocol availability across blockchains is shown in `protocol_availability.png`.
Data has a daily frequency and covers the period: 17 October 2022 to 01 January 2025. The start date is when the bridge volume data was available on DeFiLlama for the first time.

### Raw Data

Separate raw data files are uploaded to the `data/raw_data` folder. The source of each data file is written in the folder names.
E.g.: `MultiChainLending/Data/RawData/Bridge_Volume_From_DeFiLlama/bridge_volumes_arbitrum_one.csv`

### Processed Data

The analyzed dataset is composed of four files:
- `ethereum_lending.csv`
- `L2_lending.csv`
- `altL1_lending.csv`
- `aggregated_lending.csv`

The following variables are included in the data files:
- Core Financial Metrics: `TVL`, `Revenue`, `BridgeVolume`, `Liquidation`, `Withdraw`, `Deposit`, `ActiveUsers`.
- Yield Data: `ETH_APY`, `Stablecoin_APY`.
- Dummy Variables For Events: `BridgeIntegrations`, `BridgeHack`, `Mainnet`.
- Market Sentiment: `FGI` (Fear and Greed Index).
- Network Control Variables: `volETH` (ETH Volatility), `GasPrice`.
- Credit Risk Parameter: `CER` (Credit Expansion Ratio).

``
CER = dailyBorrowUSD / dailyDepositUSD
``

---
