# CBDC and Crypto Analysis Project

## Data/Code Summary

### Code

- `CBDC_analysis.py`: Examines the relationship between central-backed digital currency (CBDC) and cryptocurrency price but finds no significant result. Refer to Slide 5 for details.
- `find_cases.py`: Calculates the average slope for log price and log volume around new cryptocurrency policy releases. Identifies the 5 steepest slopes for log price and log volume when Legal Status is Legal and Illegal. Visualizations are included. See Slides 7-17.
- `news_analysis.py`: Analyzes the relationship between the number of CBDC news each month and the price of cryptocurrency. Details on Slide 23.
- `policy_crypto_gold_visualization.py`: Visualizes policy, cryptocurrency volume and price, and gold price on the same graph. Refer to Slide 22.
- `policy_crypto_regression.py`: Regression analysis where y = change in log price/volume, x1 = binary policy (legal vs illegal), x2 = log GDP of the country in that time period. See Slides 18-19.
- `policy_exchange_regression.py`: Conducts regression analysis where y = percentage change in the exchange rate for a country, x1 = binary policy (legal vs illegal), x2 = log GDP of that country in that time period. Details on Slide 25.
- `preprocess_crypto.py`: Preprocesses and joins cryptocurrency and legality policy data, then saves it to 'policy_crypto_analysis.csv'.
- `preprocess_exchange_rate.py`: Preprocesses and joins exchange rate and legality policy data, then saves it to 'policy_exchange_analysis.csv'. Refer to Slide 24 for more information.

### Data (SharedCryptoTax/Jason/upload/data)

- `national-gdp-constant-usd-wb.csv`: GDP data by country.
- `policy_analysis1.csv`: Joined cryptocurrency and policy data, log price/volume for the policy date.
- `policy_crypto_analysis.csv`: Joined cryptocurrency and policy data, log price/volume is 1 month before and after the policy date.
- `policy_exchange_analysis.csv`: Joined exchange rate and policy data, exchange rate is 1 month before and after the policy date.
- `price.xlsx`: Cryptocurrency price data from Qing.
- `Research_result_3.14.csv`: Policy data from Qing.

### Result (SharedCryptoTax/Jason/upload/data)

- `Weekly updates.pptx`: PowerPoint file containing weekly updates on the project.
