# This code preprocesses the exchange rate and legality policy data, joins the two, and saves to a new csv file.

import pandas as pd
from dateutil import parser
import re
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
import os


# policy data
file_path = '../data/SharedCryptoTax/Qing/Research_result_3.14.csv'  
policy = pd.read_csv(file_path)
columns_to_keep = ['Country', 'Legal Status', 'Citation Date']
policy = policy[columns_to_keep]
# Convert 'Citation Date' column to datetime format
policy['Citation Date'] = policy['Citation Date'].str.replace("[", "").str.replace("]", "").str.replace("'", "").str.split(", ")
policy = policy.explode('Citation Date').reset_index(drop=True)
policy['Citation Date'] = pd.to_datetime(policy['Citation Date'], format='%d %B %Y', errors='coerce')



# Remove duplicate entries from the policy DataFrame
policy.drop_duplicates(subset=['Country', 'Legal Status', 'Citation Date'], inplace=True)

# print(policy)


# exchange rate data
exchange_rate_df = pd.read_csv('../data/exchange_rate.csv')
exchange_rate_df = exchange_rate_df[["Country", "TIME", "Value"]]
exchange_rate_df["Log_Value"] = np.log(exchange_rate_df["Value"])

# print(exchange_rate_df)

# exchange rate visualization 
# countries = df["Country"].unique()
# colors = plt.cm.jet(np.linspace(0, 1, len(countries)))
# plt.figure(figsize=(12, 8))
# for i, country in enumerate(countries):
#     country_df = df[df["Country"] == country]
#     plt.plot(country_df["TIME"], country_df["Log_Value"], label=country, color=colors[i])
# plt.title("Log of Exchange Rate Over Time for Different Countries")
# plt.xlabel("TIME")
# plt.ylabel("Log(Value)")
# plt.legend()
# plt.grid(True)
# plt.show()


# Define the time periods for analysis
time_periods = [-1,1] 

# Compute exchange rate before and after each new policy
exchange_rates = []

for index, row in policy.iterrows():
    citation_date = row['Citation Date']
    country = row['Country']
    rate = []
    
    for period in time_periods:
        if pd.isna(citation_date):
            break
        # print(citation_date)
        target_date = citation_date + pd.DateOffset(months=period)
        # print(target_date)
        target_date = target_date.strftime('%Y-%m')

        # find the row in exchange_rates that match the target data and country then get the exchange rate
        matching_row = exchange_rate_df.loc[(exchange_rate_df['Country'] == country) & (exchange_rate_df['TIME'] == target_date)]
        if not matching_row.empty:
            exchange_rate_value = matching_row['Value'].values[0]
            rate.append(exchange_rate_value)
        else:
            rate.append(np.nan)

    if rate:
        exchange_rates.append(rate)
    else:
        exchange_rates.append(None)

# print(exchange_rates)
# Add log price and log volume columns to the policy dataframe
policy['Exchange Rate'] = exchange_rates

print(policy.head)

policy.to_csv('policy_exchange_analysis.csv', index=False)
