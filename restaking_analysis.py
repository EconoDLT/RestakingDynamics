import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.tsa.api import VAR
from statsmodels.stats.diagnostic import linear_reset
from scipy import stats

from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance

import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 0. CONFIGURATION
# ============================================================
FILE_PATH = "restaking_processed_data.xlsx"
OUTPUT_DIR = "outputs"
RANDOM_SEED = 42

DEP_VAR = "Revenue"
EVENT_COL = "Events"

BASE_VARS = ["TVL0", "TVL1", "TVL2", "ezETH_Yield", "APY", "Premium",
             "ETH", "FGI", "Tx_Fee", "ezETH_Share", "Events"]

CONTINUOUS_BASE = [v for v in BASE_VARS if v != "Events"]

LAG_SUFFIXES = {"Model 1 (t)": "", "Model 2 (t-1)": "_{t-1}", "Model 3 (t-2)": "_{t-2}"}

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. LOAD & VALIDATE DATA
# ============================================================
def load_data(path):
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns from '{path}'")
    return df


def check_data(df, cols):
    issues = []
    missing = df[cols].isnull().sum()
    if missing.any():
        issues.append(f"Missing values:\n{missing[missing > 0]}")
    for c in cols:
        if df[c].std(skipna=True) == 0:
            issues.append(f"Column '{c}' has zero variance.")
        if np.isinf(df[c].replace([np.inf, -np.inf], np.nan).dropna()).any():
            issues.append(f"Column '{c}' contains infinite values.")
    if issues:
        print("DATA ISSUES FOUND:")
        for i in issues:
            print(" -", i)
    else:
        print("Data passed all checks.")
    return issues


# ============================================================
# 2. CORRELATION MATRIX
# ============================================================
def correlation_matrix(df, cols, out_png):
    corr = df[cols].corr()
    print("\nCorrelation matrix:\n", corr.round(3))
    high = [(a, b, corr.loc[a, b]) for i, a in enumerate(cols)
            for b in cols[i + 1:] if abs(corr.loc[a, b]) > 0.8]
    if high:
        print("High correlations (|r| > 0.8):")
        for a, b, v in high:
            print(f"  {a} <-> {b}: {v:.3f}")
    else:
        print("No |r| > 0.8 correlations found.")

    plt.figure(figsize=(9, 7))
    im = plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(im, shrink=0.8)
    plt.xticks(range(len(cols)), cols, rotation=45, ha="right")
    plt.yticks(range(len(cols)), cols)
    for i in range(len(cols)):
        for j in range(len(cols)):
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()
    return corr


# ============================================================
# 3. OLS + VIF
# ============================================================
def run_ols(df, y_col, x_cols, label):
    data = df.dropna(subset=x_cols + [y_col])
    X = add_constant(data[x_cols])
    y = data[y_col]
    model = sm.OLS(y, X).fit()
    print(f"\n{'=' * 70}\nOLS -- {label}  (n={int(model.nobs)})\n{'=' * 70}")
    print(model.summary())
    return model, data


def run_vif(data, x_cols, label):
    X = add_constant(data[x_cols])
    vif = pd.DataFrame({
        "Variable": X.columns,
        "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    })
    vif = vif[vif["Variable"] != "const"].sort_values("VIF", ascending=False)
    print(f"\nVIF -- {label}\n{vif.to_string(index=False)}")
    return vif


# ============================================================
# 4. ROBUSTNESS: WINSORIZED + HC3
# ============================================================
def winsorize(s, cutoff=0.05):
    lo, hi = s.quantile(cutoff), s.quantile(1 - cutoff)
    return s.clip(lower=lo, upper=hi)


def run_robust(df, y_col, x_cols, event_col, label):
    data = df.dropna(subset=x_cols + [y_col]).copy()
    cont_cols = [c for c in x_cols if c != event_col]
    for c in cont_cols:
        data[c] = winsorize(data[c])
    X = add_constant(data[x_cols])
    y = data[y_col]
    model = sm.OLS(y, X).fit(cov_type="HC3")
    print(f"\n{'=' * 70}\nRobust (winsorized + HC3) -- {label}  (n={int(model.nobs)})\n{'=' * 70}")
    print(model.summary())
    return model


# ============================================================
# 5a. BIVARIATE GRANGER CAUSALITY
# ============================================================
def granger_bivariate(df, y_col, predictors, maxlag=5):
    print(f"\n{'=' * 70}\nGranger causality (bivariate, X -> {y_col})\n{'=' * 70}")
    results = []
    for x in predictors:
        data = df[[y_col, x]].dropna()
        if len(data) < 20:
            print(f"{x}: skipped (n={len(data)} too small)")
            continue
        try:
            test = grangercausalitytests(data, maxlag=maxlag, verbose=False)
            pvals = [test[l][0]["ssr_chi2test"][1] for l in range(1, maxlag + 1)]
            best_lag = int(np.argmin(pvals)) + 1
            best_p = pvals[best_lag - 1]
            results.append({"Variable": x, "Best_Lag": best_lag, "Best_P": best_p,
                             "Significant": best_p < 0.05})
            print(f"{x:<15} lag {best_lag}  p={best_p:.4f}  "
                  f"{'*** significant' if best_p < 0.05 else ''}")
        except Exception as e:
            print(f"{x}: test failed ({e})")
    return pd.DataFrame(results)

# ============================================================
# 5b. MULTIVARIATE VAR GRANGER TEST (supplementary)
# ============================================================
def granger_var_system(df, all_vars, maxlag=10):
    print(f"\n{'=' * 70}")
    print("Multivariate VAR Granger test (SUPPLEMENTARY)")
    print(f"{'=' * 70}")
    data = df[all_vars].dropna()
    try:
        sel = VAR(data).select_order(maxlags=maxlag)
        p = sel.aic
        var_model = VAR(data).fit(p)
        rows = []
        for x in all_vars:
            try:
                res = var_model.test_causality(caused=[v for v in all_vars if v != x],
                                                causing=[x], kind="f")
                rows.append({"Variable": x, "F_stat": res.test_statistic,
                             "P_value": res.pvalue})
                print(f"{x:<15} F={res.test_statistic:.3f}  p={res.pvalue:.4g}")
            except Exception as e:
                print(f"{x}: causality test failed ({e})")
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"VAR system test failed entirely: {e}")
        return pd.DataFrame()

# ============================================================
# 6. RANDOM FOREST FEATURE IMPORTANCE
# ============================================================
def random_forest_importance(df, y_col, x_cols, label, n_estimators=1000, seed=RANDOM_SEED):
    data = df.dropna(subset=x_cols + [y_col])
    X, y = data[x_cols], data[y_col]
    rf = RandomForestRegressor(n_estimators=n_estimators, random_state=seed)
    rf.fit(X, y)
    gini = pd.Series(rf.feature_importances_, index=x_cols)
    perm = permutation_importance(rf, X, y, n_repeats=10, random_state=seed)
    perm_s = pd.Series(perm.importances_mean, index=x_cols)
    out = pd.DataFrame({"Gini": gini, "Permutation": perm_s}).sort_values("Permutation", ascending=False)
    print(f"\n{'=' * 70}\nRandom Forest feature importance -- {label} (seed={seed}, ntree={n_estimators})\n{'=' * 70}")
    print(out.round(4))
    return out


# ============================================================
# 7. CHOW TEST AT EACH EVENT DATE
# ============================================================
def chow_test(y, X_full, break_pos):
    k = X_full.shape[1]
    model_full = sm.OLS(y, X_full).fit()
    rss_full = model_full.ssr

    X1, y1 = X_full[:break_pos], y[:break_pos]
    X2, y2 = X_full[break_pos:], y[break_pos:]
    if len(y1) < k + 5 or len(y2) < k + 5:
        return None, None, "Insufficient observations in one sub-sample"

    m1, m2 = sm.OLS(y1, X1).fit(), sm.OLS(y2, X2).fit()
    rss_pooled = m1.ssr + m2.ssr
    df_pooled = m1.df_resid + m2.df_resid
    f_stat = ((rss_full - rss_pooled) / k) / (rss_pooled / df_pooled)
    p_val = stats.f.sf(f_stat, k, df_pooled)
    return f_stat, p_val, "OK"


def run_chow_per_event(df, y_col, regressors, event_col):
    data = df.dropna(subset=regressors + [y_col, event_col]).reset_index(drop=True)
    X = add_constant(data[regressors]).values
    y = data[y_col].values
    dates = data["Date"] if "Date" in data.columns else pd.Series(range(len(data)))

    event_positions = data.index[data[event_col] == 1].tolist()
    print(f"\n{'=' * 70}\nChow test at each Events date (n={len(data)})\n{'=' * 70}")
    print(f"{'Date':<14}{'Position':<10}{'F-stat':<12}{'p-value':<12}{'Structural break?'}")
    rows = []
    for pos in event_positions:
        f_stat, p_val, status = chow_test(y, X, pos)
        if status != "OK":
            print(f"{str(dates.iloc[pos]):<14}{pos:<10}{'--':<12}{'--':<12}{status}")
            continue
        sig = "YES" if p_val < 0.05 else "No"
        print(f"{str(dates.iloc[pos])[:10]:<14}{pos:<10}{f_stat:<12.4f}{p_val:<12.4f}{sig}")
        rows.append({"Date": dates.iloc[pos], "Position": pos, "F_stat": f_stat,
                     "P_value": p_val, "Structural_Break": p_val < 0.05})
    return pd.DataFrame(rows)

# ============================================================
# MAIN
# ============================================================
def main():
    df = load_data(FILE_PATH)

    results = {}

    for label, suffix in LAG_SUFFIXES.items():
        x_cols = [v + suffix for v in BASE_VARS]
        print(f"\n\n{'#' * 70}\n# {label}\n{'#' * 70}")

        check_data(df, x_cols + [DEP_VAR])

        model, data = run_ols(df, DEP_VAR, x_cols, label)
        vif = run_vif(data, x_cols, label)
        robust_model = run_robust(df, DEP_VAR, x_cols, EVENT_COL if suffix == "" else EVENT_COL + suffix, label)
        reset_test(model, label)

        results[label] = {"ols": model, "vif": vif, "robust": robust_model}

    # Correlation matrix on base (t) variables
    correlation_matrix(df, [v for v in BASE_VARS], os.path.join(OUTPUT_DIR, "correlation_matrix.png"))

    # Granger causality (base/t variables only, as in the paper's Table VI)
    granger_df = granger_bivariate(df, DEP_VAR, CONTINUOUS_BASE + ["Events"])
    granger_df.to_csv(os.path.join(OUTPUT_DIR, "granger_bivariate.csv"), index=False)

    granger_var_df = granger_var_system(df, [DEP_VAR] + BASE_VARS)
    if not granger_var_df.empty:
        granger_var_df.to_csv(os.path.join(OUTPUT_DIR, "granger_var_system_SUPPLEMENTARY.csv"), index=False)

    # Random forest (base/t variables, matching Table VII)
    rf_df = random_forest_importance(df, DEP_VAR, BASE_VARS, "Model 1 (t)")
    rf_df.to_csv(os.path.join(OUTPUT_DIR, "random_forest_importance.csv"))

    # Chow test per event (base/t regressors, excluding Events itself as a regressor,
    # consistent with the corrected script that produced the Oct-1 break finding)
    chow_regressors = [v for v in BASE_VARS if v != "Events"]
    chow_df = run_chow_per_event(df, DEP_VAR, chow_regressors, EVENT_COL)
    chow_df.to_csv(os.path.join(OUTPUT_DIR, "chow_test_per_event.csv"), index=False)

    print(f"\n\nAll output tables and the correlation plot were saved to '{OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()
