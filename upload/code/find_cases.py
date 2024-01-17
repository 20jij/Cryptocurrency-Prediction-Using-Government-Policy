# This code first calculate the average slope for log price and log volume around new crypto policy releases.
# It then find the 5 steepest slopes for log price and log volume when Legal Status is Legal and Illegal. Visualizes them.


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
time_periods = [ -30,30] 

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
    log_prices.append(temp_price)
    log_volumes.append(temp_volume)

# Add log price and log volume columns to the policy dataframe
policy['Log Price'] = log_prices
policy['Log Volume'] = log_volumes


# Compute the regression lines for log price and log volume for each Citation Date
def compute_regression(data):
    if len(data) == 0:
        return []
    x = np.array(time_periods)
    y = np.array(data)
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return [slope, intercept]

policy['Log Price Regression'] = policy['Log Price'].apply(compute_regression)
policy['Log Volume Regression'] = policy['Log Volume'].apply(compute_regression)


# Calculate the absolute values of the slopes for sorting
policy['Abs Log Price Slope'] = policy['Log Price Regression'].apply(lambda x: abs(x[0]) if x else np.nan)
policy['Abs Log Volume Slope'] = policy['Log Volume Regression'].apply(lambda x: abs(x[0]) if x else np.nan)


# # Calculate the average slope for log price and log volume when Legal Status is 'Legal'
# average_slope_legal_price = policy[policy['Legal Status'] == 'Legal']['Log Price Regression'].apply(lambda x: x[0] if x else np.nan).mean()
# average_slope_legal_volume = policy[policy['Legal Status'] == 'Legal']['Log Volume Regression'].apply(lambda x: x[0] if x else np.nan).mean()

# # Calculate the average slope for log price and log volume when Legal Status is 'Illegal'
# average_slope_illegal_price = policy[policy['Legal Status'] == 'Illegal']['Log Price Regression'].apply(lambda x: x[0] if x else np.nan).mean()
# average_slope_illegal_volume = policy[policy['Legal Status'] == 'Illegal']['Log Volume Regression'].apply(lambda x: x[0] if x else np.nan).mean()

# print("Average Slope for Log Price (Legal Status: Legal):", average_slope_legal_price)
# print("Average Slope for Log Volume (Legal Status: Legal):", average_slope_legal_volume)
# print("Average Slope for Log Price (Legal Status: Illegal):", average_slope_illegal_price)
# print("Average Slope for Log Volume (Legal Status: Illegal):", average_slope_illegal_volume)



# Find the 5 steepest slopes for log price and log volume when Legal Status is 'Legal'
top_steepest_legal_price = policy[policy['Legal Status'] == 'Legal'].nlargest(5, 'Abs Log Price Slope')
top_steepest_legal_volume = policy[policy['Legal Status'] == 'Legal'].nlargest(10, 'Abs Log Volume Slope')

# Find the 5 steepest slopes for log price and log volume when Legal Status is 'Illegal'
top_steepest_illegal_price = policy[policy['Legal Status'] == 'Illegal'].nlargest(5, 'Abs Log Price Slope')
top_steepest_illegal_volume = policy[policy['Legal Status'] == 'Illegal'].nlargest(10, 'Abs Log Volume Slope')

# Display the DataFrames with the top steepest slopes
print("Top 5 Steepest Slopes for Log Price Regression (Legal Status: Legal):")
print(top_steepest_legal_price)
print("\nTop 5 Steepest Slopes for Log Price Regression (Legal Status: Illegal):")
print(top_steepest_illegal_price)
print("\nTop 5 Steepest Slopes for Log Volume Regression (Legal Status: Legal):")
print(top_steepest_legal_volume)
print("\nTop 5 Steepest Slopes for Log Volume Regression (Legal Status: Illegal):")
print(top_steepest_illegal_volume)

# Create directories for saving images
price_dir = 'price_visualizations_1'
volume_dir = 'volume_visualizations_1'
os.makedirs(price_dir, exist_ok=True)
os.makedirs(volume_dir, exist_ok=True)

# Create scatter plots and save images for the top steepest price and volume (Legal Status: Legal)
for idx, row in top_steepest_legal_price.iterrows():
    plt.figure(figsize=(8, 6))
    plt.scatter(time_periods, row['Log Price'], label='Log Price', color='blue')
    plt.plot(time_periods, np.array(time_periods) * row['Log Price Regression'][0] + row['Log Price Regression'][1], label='Log Price Regression', linestyle='--')
    plt.xlabel('Time Periods')
    plt.ylabel('Log Price Value')
    plt.title(f'Trend in Log Price for {row["Country"]} - {row["Legal Status"]} - {row["Citation Date"].date()}')
    plt.legend()
    plt.xticks(time_periods)
    plt.tight_layout()
    image_filename = f'{row["Country"]}_{row["Legal Status"]}_{row["Citation Date"].date()}.png'
    image_filename = image_filename.replace('/', '_')  # Remove backslashes from the filename
    image_path = os.path.join(price_dir, image_filename)
    plt.savefig(image_path)
    plt.close()

# Create scatter plots and save images for the top steepest price and volume (Legal Status: Illegal)
for idx, row in top_steepest_illegal_price.iterrows():
    plt.figure(figsize=(8, 6))
    plt.scatter(time_periods, row['Log Price'], label='Log Price', color='blue')
    plt.plot(time_periods, np.array(time_periods) * row['Log Price Regression'][0] + row['Log Price Regression'][1], label='Log Price Regression', linestyle='--')
    plt.xlabel('Time Periods')
    plt.ylabel('Log Price Value')
    plt.title(f'Trend in Log Price for {row["Country"]} - {row["Legal Status"]} - {row["Citation Date"].date()}')
    plt.legend()
    plt.xticks(time_periods)
    plt.tight_layout()
    image_filename = f'{row["Country"]}_{row["Legal Status"]}_{row["Citation Date"].date()}.png'
    image_filename = image_filename.replace('/', '_')  # Remove backslashes from the filename
    image_path = os.path.join(price_dir, image_filename)
    plt.savefig(image_path)
    plt.close()

# Create scatter plots and save images for the top steepest volume (Legal Status: Legal)
for idx, row in top_steepest_legal_volume.iterrows():
    plt.figure(figsize=(8, 6))
    plt.scatter(time_periods, row['Log Volume'], label='Log Volume', color='orange')
    plt.plot(time_periods, np.array(time_periods) * row['Log Volume Regression'][0] + row['Log Volume Regression'][1], label='Log Volume Regression', linestyle='--')
    plt.xlabel('Time Periods')
    plt.ylabel('Log Volume Value')
    plt.title(f'Trend in Log Volume for {row["Country"]} - {row["Legal Status"]} - {row["Citation Date"].date()}')
    plt.legend()
    plt.xticks(time_periods)
    plt.tight_layout()
    image_filename = f'{row["Country"]}_{row["Legal Status"]}_{row["Citation Date"].date()}.png'
    image_filename = image_filename.replace('/', '_')  # Remove backslashes from the filename
    image_path = os.path.join(volume_dir, image_filename)
    plt.savefig(image_path)
    plt.close()

# Create scatter plots and save images for the top steepest volume (Legal Status: Illegal)
for idx, row in top_steepest_illegal_volume.iterrows():
    plt.figure(figsize=(8, 6))
    plt.scatter(time_periods, row['Log Volume'], label='Log Volume', color='orange')
    plt.plot(time_periods, np.array(time_periods) * row['Log Volume Regression'][0] + row['Log Volume Regression'][1], label='Log Volume Regression', linestyle='--')
    plt.xlabel('Time Periods')
    plt.ylabel('Log Volume Value')
    plt.title(f'Trend in Log Volume for {row["Country"]} - {row["Legal Status"]} - {row["Citation Date"].date()}')
    plt.legend()
    plt.xticks(time_periods)
    plt.tight_layout()
    image_filename = f'{row["Country"]}_{row["Legal Status"]}_{row["Citation Date"].date()}.png'
    image_filename = image_filename.replace('/', '_')  # Remove backslashes from the filename
    image_path = os.path.join(volume_dir, image_filename)
    plt.savefig(image_path)
    plt.close()
