# 1. preprocess policy data
# 2. visualize policy bars, crypto volumne and price, and gold price on the same graph

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt


file_path = '/Users/jasonji/Desktop/Garg/code/policy_analysis1.csv'

policy = pd.read_csv(file_path)

# Define a function to compute log price percent change for a given row
def compute_percent_change(row, column_name):
    log_list = eval(row[column_name])
    if len(log_list) < 2:
        return None
    else:
        # take the first value and the last value and compute the difference
        first_value = log_list[0]
        last_value = log_list[-1]
        percent_change = ((last_value - first_value) / first_value) * 100
        return percent_change



# Convert legal status to binary
# remove rows with 'Unknown' legal status
policy = policy[policy['Legal Status'] != 'Unknown']
policy.reset_index(drop=True, inplace=True)

legal_status_mapping = {
    'Illegal': 'Illegal',
    'Legal': 'Legal',
    'Legal /  Banking ban': 'Legal',
    'Legal to trade and hold': 'Legal',
    'Not considered currency': 'Legal',
    'Legal to trade and hold /  Illegal as a payment tool, banking ban': 'Legal',
    'Legal to trade and hold /  Illegal as payment tool': 'Legal',
    'Not regulated by central bank': 'Legal',
    'Ban on mining[155]': 'Illegal',
    'Not regulated as of 2014': 'Legal',
    'Legal to mine  Banking ban': 'Legal',
    'Legal / Use discouraged by central bank': 'Legal',
    'Legal /   Illegal to buy with local currency': 'Legal',
}
# Replace legal status values using the mapping
policy['Legal Status'] = policy['Legal Status'].replace(legal_status_mapping)

# Visualize the data distribution
# Convert the 'Citation Date' column to datetime
policy['Citation Date'] = pd.to_datetime(policy['Citation Date'])

# Convert the 'Citation Date' column to datetime
policy['Citation Date'] = pd.to_datetime(policy['Citation Date'])

# Extract month and year from the 'Citation Date' column
policy['Month'] = policy['Citation Date'].dt.strftime('%Y-%m')

# Group the data by 'Month', 'Year', and 'Legal Status' and count the entries
policy_counts = policy.groupby(['Month', 'Legal Status']).size().unstack(fill_value=0)


# Group the data by 'Month' and 'Legal Status' and compute the average log price and log volume
average_log_price = policy.groupby(['Month'])['Log Price'].mean()
average_log_volume = policy.groupby(['Month'])['Log Volume'].mean()

# Add the computed values to the policy_counts DataFrame
policy_counts['Average Log Price'] = average_log_price
policy_counts['Average Log Volume'] = average_log_volume

# If there are missing values in the computed averages, you can fill them with 0 or any other suitable value
policy_counts['Average Log Price'].fillna(0, inplace=True)
policy_counts['Average Log Volume'].fillna(0, inplace=True)

# print(policy_counts)



# Gold price data
file_path = '/Users/jasonji/Desktop/Garg/data/gold_prices.xlsx'
gold_price = pd.read_excel(file_path, sheet_name="Monthly_Avg")

# Data cleanning
# Remove the first five rows
gold_price = gold_price.iloc[5:]
gold_price = gold_price.iloc[:, 2:4]
# Reset the index after removing rows
gold_price.reset_index(drop=True, inplace=True)
gold_price.rename(columns={gold_price.columns[0]: 'Month', gold_price.columns[1]: 'Price_USD'}, inplace=True)
gold_price['Month'] = gold_price['Month'].dt.strftime('%Y-%m')

# Ensure the 'Price_USD' column contains positive values
gold_price['Price_USD'] = gold_price['Price_USD'].apply(lambda x: max(x, 1e-8))  # Replace non-positive values with a small positive value

# Compute the log of the 'Price_USD' column and create a new column 'Log Price'
gold_price['Log_Price_USD'] = np.log(gold_price['Price_USD'])
gold_price['Price_USD_Scaled'] = gold_price['Price_USD']/50

merged_df = pd.merge(gold_price, policy_counts, on='Month', how='inner')

print(merged_df)

# Set the figure size for the plot
plt.figure(figsize=(12, 6))

# Create an array of indices for the x-axis (Month)
x = np.arange(len(merged_df['Month']))

# Set the width of the bars
bar_width = 0.4

# Create bar plots for 'Illegal' and 'Legal' side by side
plt.bar(x - bar_width/2, merged_df['Illegal'], width=bar_width, label='Illegal', color='red', alpha=0.6)
plt.bar(x + bar_width/2, merged_df['Legal'], width=bar_width, label='Legal', color='blue', alpha=0.6)

# Create line plots for 'Average Log Price', 'Average Log Volume', and 'Price_USD'
plt.plot(x, merged_df['Average Log Price'], label='Avg Log Price', color='green', marker='o')
plt.plot(x, merged_df['Average Log Volume'], label='Avg Log Volume', color='orange', marker='o')
plt.plot(x, merged_df['Price_USD_Scaled'], label='Gold Price', color='purple', marker='o')

# Set the tick positions and labels at 3-month intervals
tick_positions = x[::3]
tick_labels = merged_df['Month'][::3]

# Rotate the x-axis labels for better readability
plt.xticks(tick_positions, tick_labels, rotation=45)

# Add labels and legend
plt.xlabel('Month')
plt.ylabel('Count / Log Value / Price (USD)')
plt.title('Policy Analysis and Gold Price')
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()
