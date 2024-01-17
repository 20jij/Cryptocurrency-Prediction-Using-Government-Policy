# This code preprocesses the crytpo and legality policy data, joins the two, and saves to a new csv file.

import pandas as pd
from dateutil import parser
import re
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
import os



# Date preprocessing
def read_csv_to_dataframe(file_path):
    try:
        dataframe = pd.read_csv(file_path)
        return dataframe
    except Exception as e:
        print(f"Error: {e}")
        return None


file_path = '/Users/jasonji/Desktop/Garg/data/SharedCryptoTax/Qing/Research_result_3.14.csv'  

policy = read_csv_to_dataframe(file_path)

columns_to_keep = ['Country', 'Legal Status', 'Citation Date']
policy = policy[columns_to_keep]
# Convert 'Citation Date' column to datetime format
policy['Citation Date'] = policy['Citation Date'].str.replace("[", "").str.replace("]", "").str.replace("'", "").str.split(", ")
policy = policy.explode('Citation Date').reset_index(drop=True)
policy['Citation Date'] = pd.to_datetime(policy['Citation Date'], format='%d %B %Y', errors='coerce')
# Remove duplicate entries from the policy DataFrame
policy.drop_duplicates(subset=['Country', 'Legal Status', 'Citation Date'], inplace=True)



# crypto price & volume data
crypto_data = pd.read_excel('/Users/jasonji/Desktop/Garg/data/price.xlsx')
crypto_data['Date'] = pd.to_datetime(crypto_data['Date'])
crypto_data.set_index('Date', inplace=True)
# Convert 'Vol' column to numeric format
def convert_vol(vol_str):
    multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9}  # Add more multipliers if needed
    num_part = re.findall(r'\d+\.\d+|\d+', vol_str)
    if num_part:
        num = float(num_part[0])
        for suffix, multiplier in multipliers.items():
            if suffix in vol_str:
                return num * multiplier
        return num
    else:
        return None  # Handle invalid entries

crypto_data['Vol.'] = crypto_data['Vol.'].apply(convert_vol)


# Define the time periods for analysis
time_periods = [-2,2] 

# Compute log price and log volume for each time period
log_prices = []
log_volumes = []

for citation_date in policy['Citation Date']:
    temp_price = []
    temp_volume = []
    for period in time_periods:
        target_date = citation_date + pd.DateOffset(days=period)
        if target_date in crypto_data.index:
            log_price = np.log(crypto_data.loc[target_date, 'Price'])
            log_volume = np.log(crypto_data.loc[target_date, 'Vol.'])
            
            temp_price.append(log_price)
            temp_volume.append(log_volume)
    if temp_price:
        log_prices.append(temp_price)
        log_volumes.append(temp_volume)
    else:
        log_prices.append(None)
        log_volumes.append(None)

# Add log price and log volume columns to the policy dataframe
policy['Log Price'] = log_prices
policy['Log Volume'] = log_volumes


policy.to_csv('policy_crypto_analysis.csv', index=False)
