# This code first visualizes the crypto legality dataset through bar chart. 
# It then does regression analysis where 
# y = change in log price/volume
# x1 = binary (legal vs illegal), x2 = log GDP of that country in that time period

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt


file_path = '/Users/jasonji/Desktop/Garg/code/policy_analysis.csv'

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

# Compute percent change for Log Price and Log Volume
policy['Percent Change Price'] = policy.apply(compute_percent_change, axis=1, args=('Log Price',))
policy['Percent Change Volume'] = policy.apply(compute_percent_change, axis=1, args=('Log Volume',))



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

# Plot the bar chart
fig, ax = plt.subplots(figsize=(12, 6))
policy_counts.plot(kind='bar', stacked=False, ax=ax, width=0.4)
ax.set_xlabel('Month and Year')
ax.set_ylabel('Count of Policy Entries')
ax.set_title('Count of Policy Entries by Month and Year (Legal vs. Illegal)')
plt.xticks(rotation=45)
plt.legend(title='Legal Status', loc='upper right')
plt.tight_layout()
plt.show()



# GDP Data

file_path = '/Users/jasonji/Desktop/Garg/code/national-gdp-constant-usd-wb.csv'

gdp = pd.read_csv(file_path)

# Convert 'Citation Date' to Year in policy data
policy['Year'] = pd.to_datetime(policy['Citation Date']).dt.year
# Merge the two DataFrames based on 'Country' and 'Year'
merged_data = policy.merge(gdp, left_on=['Country', 'Year'], right_on=['Entity', 'Year'], how='inner')
merged_data.drop(columns=['Entity'], inplace=True)
merged_data['Log GDP'] = np.log(merged_data['GDP (constant 2015 US$)'])

# Drop rows with missing Percent Change Price and Percent Change Volume
merged_data.dropna(subset=['Percent Change Price', 'Percent Change Volume'], inplace=True)

# Create binary variables for legal status using one-hot encoding
legal_status_dummies = pd.get_dummies(merged_data['Legal Status'], drop_first=True)
merged_data['Legal Status']
legal_status_dummies = legal_status_dummies.astype(int)

# Regression Analysis

# Add the one-hot encoded legal status and log GDP as independent variables
X = sm.add_constant(pd.concat([legal_status_dummies, merged_data['Log GDP']], axis=1))

# Dependent variable
y_price = merged_data['Percent Change Price']
y_volume = merged_data['Percent Change Volume']

# Perform the regression analysis for Log Price
model_price = sm.OLS(y_price, X).fit()
# Perform the regression analysis for Log Volume
model_volume = sm.OLS(y_volume, X).fit()

# Print the regression summaries
print("Regression Summary for Log Price:")
print(model_price.summary())

print("\nRegression Summary for Log Volume:")
print(model_volume.summary())


