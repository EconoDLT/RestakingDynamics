# Financial Dynamics and Interconnected Risk of Liquid Restaking
**DeFi, Restaking Protocols, and Layered Risks across Interconnected Protocols and Blockchains**

This repository contains the collected data, the R code used, further explanations and clarifications for the following research paper that analyzes the dynamics of the liquid restaking market:

H. O. Sevim, “Financial Dynamics and Interconnected Risk of Liquid Restaking,” arXiv:2604.03274, 2026. https://arxiv.org/abs/2604.03274

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
├── restaking_analysis.R                    # Code to analyze the data
│
└── data/
    └── raw_data/                           # This folder includes multiple raw data files
    └── processed_data/                     # This file is required to run the script
        └── restaking_processed_data.xlsx
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

**Input:** `restaking_processed_data.xlsx`

---

## 2 — Data

### Data Overview

The dataset covers:
- Eigenlayer data on the Ethereum network,
- Renzo Protocol data across Ethereum, Arbitrum, Base, Linea, Blast, and Mode networks.
Data has a daily frequency and covers the period: 22 January 2022 to 17 April 2025. The start date is the first day when Renzo Protocol's LRT (ezETH) is deployed on a layer-2 network.

### Raw Data

Separate raw data files are uploaded to the `data/raw_data` folder. The source of each data file is written in the folder names.
E.g.: `/raw_data/restaking_protocool_data_from_the_graph/renzo_arbitrum.json`

### Processed Data

The analyzed dataset is `restaking_processed_data.xlsx`.

The following variables are included in the data files:
- Core Financial Metrics: `Revenue` (Total revenue of Renzo Protocol), `TVL0`, (EigenLayer TVL), `TVL1` (Renzo TVL on Ethereum), `TVL2` (Renzo TVL on L2s),   `Share` (ezETH share in the liquid restaking market), `Premium` (ezETH premium variable), `ETH` (ETH price).
- Yield Data: `Yield` (ezETH yield rate), `APY` (stETH APY as the benchmark DeFi yield).
- Market Sentiment: `FGI` (Fear and Greed Index).
- Network Control Variables: `GasPrice`.
- Dummy Variable For Tokenization Events: `Events`.

`Events` variable covers:
- 04/26/2024: Renzo Protocol tokenization announcement,
- 04/29/2024: EigenLayer tokenization details are announced,
- 04/30/2024: REZ token was generated,
- 10/01/2024: EIGEN token was generated.

---

Contact for more details and clarifications: hasretozan.sevim@unicatt.it
