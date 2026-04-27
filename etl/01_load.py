import pandas as pd

analysis = pd.read_excel("data/raw/analysis.xlsx")
balance = pd.read_excel("data/raw/balancesheet.xlsx")
cashflow = pd.read_excel("data/raw/cashflow.xlsx")

print("Analysis:", analysis.shape)
print("Balance:", balance.shape)
print("Cashflow:", cashflow.shape)