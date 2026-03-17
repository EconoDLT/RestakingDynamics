# Core
library(readxl)
library(dplyr)

# Time series & econometrics
library(lmtest)       # Granger causality
library(car)          # VIF
library(vars)         # VAR + Granger

# ML
library(randomForest)

# Diagnostics
library(corrplot)

# Read Excel
df <- read_excel("restaking_processed_data.xlsx")

# Convert Date
df$Date <- as.Date(df$Date)

# Fix decimal commas and convert to numeric
num_vars <- c("Events",	"APY", "ezETH_Yield" , "FGI", "ETH", "Tx_Fee", "Premium", "Revenue", "TVL0", "TVL1", "TVL2", "ezETH_Share")

df <- df %>%
  mutate(across(all_of(num_vars),
                ~ as.numeric(gsub(",", ".", .))))

#Correlation Matrix
corr_data <- df <- dplyr::select(df, all_of(num_vars))

corr_matrix <- cor(corr_data, use = "complete.obs")

corrplot(corr_matrix, method = "color", type = "upper",
         tl.cex = 0.8, number.cex = 0.7)

#OLS time-series regression
ols_model <- lm(
  Revenue ~ TVL0 + TVL1 + TVL2 + ezETH_Yield + APY + Premium + ETH + FGI + Tx_Fee + ezETH_Share + Events,
  data = df
)

summary(ols_model)

#VIF Check
vif_values <- vif(ols_model)
print(vif_values)

#Granger Causality Test
var_data <- df

# Optimal lag selection
lag_selection <- VARselect(var_data, lag.max = 10, type = "const")
lag_selection$criteria

# Estimate VAR
var_model <- VAR(var_data, p = lag_selection$selection["AIC(n)"], type = "const")

# Granger causality: do Bs Granger-cause A1?
causality(var_model, cause = "TVL0")
causality(var_model, cause = "TVL1")
causality(var_model, cause = "TVL2")
causality(var_model, cause = "APY")
causality(var_model, cause = "ezETH_Yield")
causality(var_model, cause = "Premium")
causality(var_model, cause = "ETH")
causality(var_model, cause = "Tx_Fee")
causality(var_model, cause = "FGI")
causality(var_model, cause = "ezETH_Share")
causality(var_model, cause = "Events")

#Random Forest Test
set.seed(123)

rf_model <- randomForest(
  Revenue ~ TVL0 + TVL1 + TVL2 + ezETH_Yield + APY + Premium + ETH + FGI + Tx_Fee + ezETH_Share + Events,
  data = df,
  importance = TRUE,
  ntree = 1000
)

# Variable importance
importance(rf_model)
varImpPlot(rf_model, type = 1)


