# this code combines all individual country data in the coindance_data folder into 1 csv file

import pandas as pd
import os
import glob

# Get a list of all CSV files in the current directory
file_names = glob.glob('*.csv')

# Initialize an empty DataFrame for the combined data
combined_df = pd.DataFrame()

# Loop through each file
for file in file_names:
    # Read the CSV file
    df = pd.read_csv(file)

    # Extract country code from the file name
    # Split the file name by '-' and pick the third element
    country_code = file.split('-')[3]

    # Add a new column for the country
    df['Country'] = country_code

    # Append this DataFrame to the combined DataFrame
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# Rename the 'Label' column to 'Date'
combined_df.rename(columns={'Label': 'Date'}, inplace=True)

# Reorder columns
combined_df = combined_df[['Date', 'Country', 'Value']]

# Save the combined DataFrame to a new CSV file
combined_df.to_csv("combined_data.csv", index=False)
