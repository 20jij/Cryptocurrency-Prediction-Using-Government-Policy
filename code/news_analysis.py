# Analyze relationship between number of CBDC news each month and the price of crypto

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import numpy as np
	

# CBDC data
cbdc = pd.read_csv('/Users/jasonji/Desktop/Garg/data/CBDC.csv')
# data cleaning
cbdc.rename(columns = {'Unnamed: 0':'Country'}, inplace = True)
cbdc = cbdc[['Country', 'Central Banks', 'Month &', 'Year', 'Status']]
# Clean 'Month &' column: remove leading/trailing spaces and fix misspelling
cbdc['Month &'] = cbdc['Month &'].str.strip().str.replace('Decemeber', 'December', case=False)
# Convert 'Month &' and 'Year' to datetime format
cbdc['Date'] = pd.to_datetime(cbdc['Month &'] + ' ' + cbdc['Year'].astype(str), format='%B %Y')

# Group by 'Date' and calculate the count for each group
entry_counts = cbdc.groupby('Date').size()
entry_counts.name = 'Entry_Count'

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

# compute monthly mean for price, volume, percentage change
monthly_data = crypto_data.resample('M').agg({'Price': 'mean', 'Vol.': 'mean', 'Change %': 'mean'})
# Convert 'Date' index to the first day of each month
monthly_data.index = monthly_data.index.to_period('M').to_timestamp()

# Join entry_counts with monthly_data based on 'Date' index
result = monthly_data.merge(entry_counts, left_index=True, right_index=True, how='left')
result.rename(columns={'Entry_Count': 'News_Count'}, inplace=True)
# drop months without news_count
result = result.dropna(subset=['News_Count'])
# Convert 'Price' and 'Vol.' columns to log scale
result['Log_Price'] = np.log(result['Price'])
result['Log_Vol'] = np.log(result['Vol.'])



# Scatter plot: News_Count vs. Price
plt.figure(figsize=(10, 6))
plt.scatter(result['News_Count'], result['Log_Price'])
plt.xlabel('News_Count')
plt.ylabel('Log_Price')
plt.title('News_Count vs. Log_Price')
plt.grid(True)
plt.show()

# Scatter plot: News_Count vs. Vol.
plt.figure(figsize=(10, 6))
plt.scatter(result['News_Count'], result['Log_Vol'])
plt.xlabel('News_Count')
plt.ylabel('Log_Vol')
plt.title('News_Count vs. Log_Vol')
plt.grid(True)
plt.show()

# Scatter plot: News_Count vs. Change %
plt.figure(figsize=(10, 6))
plt.scatter(result['News_Count'], result['Change %'])
plt.xlabel('News_Count')
plt.ylabel('Change %')
plt.title('News_Count vs. Change %')
plt.grid(True)
plt.show()







