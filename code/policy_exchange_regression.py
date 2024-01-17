# 1. preprocess the crypto legality dataset
# 2. preprocess the exchange rate dataset
# 3. It then does regression analysis where 
# y = change in exchange rate for a country 
# x1 = binary (legal vs illegal), x2 = log GDP of that country in that time period

# RESULT: 92 data samples left, all are legal news. No illegal news.


import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Define a function to compute log price percent change for a given row
def compute_percent_change(row, column_name):
    if 'nan' in row[column_name]:
        return None
    log_list = eval(row[column_name])
    if len(log_list) < 2:
        return None  
    # take the first value and the last value and compute the difference
    first_value = log_list[0]
    last_value = log_list[-1]
    percent_change = ((last_value - first_value) / first_value) * 100
    return percent_change



file_path = 'policy_exchange_analysis.csv'
policy = pd.read_csv(file_path)



# Convert legal status to binary
# remove rows with 'Unknown' legal status
policy = policy[policy['Legal Status'] != 'Unknown']
policy.reset_index(drop=True, inplace=True)

# Replace legal status values using the mapping
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
policy['Legal Status'] = policy['Legal Status'].replace(legal_status_mapping)

# Convert the 'Citation Date' column to datetime
policy['Citation Date'] = pd.to_datetime(policy['Citation Date'])
# Extract month and year from the 'Citation Date' column
policy['Month'] = policy['Citation Date'].dt.strftime('%Y-%m')


# drop rows where exchange rate is nan
policy.dropna(subset=['Exchange Rate'], inplace=True)



# Compute percent change for exchange rate
policy['Percent Change Exchange Rate'] = policy.apply(compute_percent_change, axis=1, args=('Exchange Rate',))
policy.dropna(subset=['Percent Change Exchange Rate'], inplace=True)
policy.reset_index(drop=True, inplace=True)
unique_values = policy['Legal Status'].unique()
print(unique_values)
print(len(policy['Legal Status']))





# GDP Data

file_path = 'national-gdp-constant-usd-wb.csv'

gdp = pd.read_csv(file_path)

# Convert 'Citation Date' to Year in policy data
policy['Year'] = pd.to_datetime(policy['Citation Date']).dt.year
# Merge the two DataFrames based on 'Country' and 'Year'
merged_data = policy.merge(gdp, left_on=['Country', 'Year'], right_on=['Entity', 'Year'], how='inner')
merged_data.drop(columns=['Entity'], inplace=True)
merged_data['Log GDP'] = np.log(merged_data['GDP (constant 2015 US$)'])
unique_values = merged_data['Legal Status'].unique()



# Create binary variables for legal status using one-hot encoding
legal_status_dummies = pd.get_dummies(merged_data['Legal Status'])
legal_status_dummies = legal_status_dummies.astype(int)

# Regression Analysis

# Add the one-hot encoded legal status and log GDP as independent variables
X = sm.add_constant(pd.concat([legal_status_dummies, merged_data['Log GDP']], axis=1))
# Dependent variable
y = merged_data['Percent Change Exchange Rate']
# Perform the regression analysis 
model = sm.OLS(y, X).fit()

# Print the regression summaries
print("Regression Summary for Exchange Rate:")
print(model.summary())



