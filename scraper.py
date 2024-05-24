# -*- coding: utf-8 -*-
"""Restaurant-inspection -2023-2024

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HytgStKv0w5ZYX3m9SJsuPNIXK64c4aU
"""

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import time
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Load inspection data
ins_2024 = pd.read_csv('data/2024_inspection.csv')
ins_2023 = pd.read_csv('data/2023_inspection.csv')

df = pd.concat([ins_2024, ins_2023])
df['Address'] = df['Address'].str.strip()
df['Inspection Date'] = pd.to_datetime(df['Inspection Date'])
df = df[df['Inspection Date'] > '2023-04-21']
df['Year'] = df['Inspection Date'].dt.year

# Path to save the scraped data
file_path = 'scraped_data.csv'

# Function to save progress
def save_progress(df, path):
    df.to_csv(path, index=False)

# Initialize or load existing data
if os.path.exists(file_path):
    scraped_df = pd.read_csv(file_path)
else:
    scraped_df = pd.DataFrame(columns=['Inspection Details', 'Violation_Text'])

# Add missing columns to the DataFrame to ensure compatibility
if 'Violation_Text' not in df.columns:
    df['Violation_Text'] = np.nan

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    if pd.notnull(row['Violation_Text']):
        continue  # Skip already processed rows
    url = row['Inspection Details']
    if pd.isnull(url):  # If URL is NaN, set "This row has no violation"
        df.at[index, 'Violation_Text'] = "This row has no violation"
        continue
    print(f"Scraping row {index + 1}: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = bs(response.text, 'html.parser')
            violation_element = soup.find(class_="col-5 CellJustify")
            if violation_element:  # Check if element was found
                violation_text = violation_element.text.strip()
                df.at[index, 'Violation_Text'] = violation_text
            else:
                df.at[index, 'Violation_Text'] = "No violation text found"
        else:
            df.at[index, 'Violation_Text'] = "Error: Unable to fetch data from URL"
    except Exception as e:
        print(f"Error: {e}")
        df.at[index, 'Violation_Text'] = "Error: Unable to fetch data from URL"

    time.sleep(0.5)  # Sleep for 0.5 seconds to avoid overwhelming the server

    # Save progress every 100 rows
    if index % 100 == 0:
        save_progress(df, file_path)
        print(f"Progress saved at row {index}")

# Save final progress
save_progress(df, file_path)
print("Final progress saved")

print(df[df['Violation_Text'].isnull()].head())








