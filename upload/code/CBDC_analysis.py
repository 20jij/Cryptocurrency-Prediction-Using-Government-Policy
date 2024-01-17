# This code examines the relationship between central backed digital currency and crypto price.
# NO SIGNIFICANT RESULT FOUND.

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
	

# CBDC data
cbdc = pd.read_csv('/Users/jasonji/Desktop/Garg/data/CBDC.csv')
# data cleaning
cbdc.rename(columns = {'Unnamed: 0':'Country'}, inplace = True)
cbdc = cbdc[['Country', 'Central Banks', 'Month &', 'Year', 'Status']]
# Clean 'Month &' column: remove leading/trailing spaces and fix misspelling
cbdc['Month &'] = cbdc['Month &'].str.strip().str.replace('Decemeber', 'December', case=False)
# Convert 'Month &' and 'Year' to datetime format
cbdc['Date'] = pd.to_datetime(cbdc['Month &'] + ' ' + cbdc['Year'].astype(str), format='%B %Y')

# examine dataset: 8 launches, 187 researches, 44 pilots, 77 proof of concept, 12 cancelled
launches = cbdc.loc[cbdc['Status']=='Launched']
# Remove the row with "Finland" from the launches DataFrame
launches = launches[launches['Country'] != 'Finland']
# Create a copy of the 'launches' DataFrame to avoid SettingWithCopyWarning
launches_copy = launches.copy()
# Convert 'Date' column to Period with monthly frequency
launches_copy['Month_Year'] = launches_copy['Date'].dt.to_period('M')

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
# compute monthly volatility for price and volume
# Resample data to monthly frequency
monthly_data = crypto_data.resample('M').agg({'Change %': 'std', 'Vol.': 'std'})

monthly_data.rename(columns={'Change %': 'Monthly_Price_STD', 'Vol.': 'Monthly_Volume_STD'}, inplace=True)
# Convert 'Date' column in monthly_data to Period with monthly frequency
monthly_data.index = monthly_data.index.to_period('M')

# Merge dataframes based on both 'Date' and 'Month_Year'
merged_data = pd.merge(monthly_data, launches_copy, left_index=True, right_on=['Month_Year'], how='left')

# Calculate average monthly standard deviations for price and volume with and without launches
average_std_without_launch = merged_data[merged_data['Status'].isnull()]
average_std_without_launch = average_std_without_launch[['Monthly_Price_STD', 'Monthly_Volume_STD']].mean()

average_std_with_launch = merged_data[merged_data['Status'] == 'Launched']
average_std_with_launch = average_std_with_launch[['Monthly_Price_STD', 'Monthly_Volume_STD']].mean()

# print("Average Monthly Standard Deviations Without Launches:")
# print(average_std_without_launch)

# print("\nAverage Monthly Standard Deviations With Launches:")
# print(average_std_with_launch)





# Calculate the log of mean price and mean volume for different time periods around launches
launch_periods = launches_copy['Month_Year'].dt.to_timestamp()

# Define the time periods for analysis
time_periods = [-10,-9,-8,-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,7,8,9,10]  # Months before and after the launch

# Create a DataFrame to store the results
launch_analysis = pd.DataFrame(index=launch_periods)

for period in time_periods:
    # Calculate the start and end dates for the current time period
    start_dates = launch_periods + pd.DateOffset(months=period)
    end_dates = start_dates + pd.DateOffset(months=1)
    
    # Initialize lists to store mean log prices and mean log volumes for the current time period
    mean_log_prices = []
    mean_log_volumes = []
    
    # Iterate over launch dates and calculate mean log price and volume for the specified period
    for launch_date, start_date, end_date in zip(launch_periods, start_dates, end_dates):
        
        start_date = start_date.date()
        end_date = end_date.date()
        
        # need to reverse start and end date because crypto_date's index is from current to the past
        price_slice = crypto_data.loc[end_date:start_date, 'Price']
        volume_slice = crypto_data.loc[end_date:start_date, 'Vol.']
       
        if not price_slice.empty and not volume_slice.empty:
            mean_log_price = np.log(price_slice.mean())
            mean_log_volume = np.log(volume_slice.mean())
            mean_log_prices.append(mean_log_price)
            mean_log_volumes.append(mean_log_volume)
        else:
            mean_log_prices.append(np.nan)
            mean_log_volumes.append(np.nan)
       
    # Create a unique label for each entry in the format: "Country - Time Period"
    country_label = [f"{country}" for country in launches_copy['Country']]
    launch_analysis['Country_Period'] = country_label

    # Store the results in the launch_analysis DataFrame
    launch_analysis[f'Mean_Log_Price_{period}'] = mean_log_prices
    launch_analysis[f'Mean_Log_Volume_{period}'] = mean_log_volumes

# Separate mean log price and mean log volume into two separate DataFrames
launch_analysis_price = launch_analysis[['Country_Period'] + [col for col in launch_analysis.columns if 'Mean_Log_Price' in col]]
launch_analysis_volume = launch_analysis[['Country_Period'] + [col for col in launch_analysis.columns if 'Mean_Log_Volume' in col]]

# print(launch_analysis_price)
# print(launch_analysis_volume)

# Visualize the mean log price using a line graph
plt.figure(figsize=(10, 6))

for idx, row in launch_analysis_price.iterrows():
    print(row)
    country_period = row['Country_Period'] 
    plt.plot(time_periods, row[1:], marker='o', label=f"{str(country_period)}")

plt.xlabel('Time Periods')
plt.ylabel('Mean Log Price')
plt.title('Mean Log Price for Different Time Periods around Launches')
plt.xticks(time_periods)
plt.legend()
plt.grid(True)
plt.show()

# Visualize the mean log volume using a line graph
plt.figure(figsize=(10, 6))

for idx, row in launch_analysis_volume.iterrows():
    country_period = row['Country_Period'] 
    plt.plot(time_periods[1:], row[2:], marker='o', label=f"{str(country_period)}")


plt.xlabel('Time Periods')
plt.ylabel('Mean Log Volume')
plt.title('Mean Log Volume for Different Time Periods around Launches')
plt.xticks(time_periods)
plt.legend()
plt.grid(True)
plt.show()



