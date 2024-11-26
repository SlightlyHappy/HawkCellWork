import pandas as pd
import re

# Load the Excel file
file_path = '/Users/rishabhkankash/Documents/Coding/DataCleaning/USA/hubspot-crm-exports-all-companies-2024-11-15.xlsx'
df = pd.read_excel(file_path)

# List out all the column names
column_names = df.columns.tolist()
print(column_names)

# Create a new Excel writer object
output_file_path = '/Users/rishabhkankash/Documents/Coding/DataCleaning/USA/separated_companies.xlsx'
writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')

# Convert the "Company Domain Name" column to lowercase for case-insensitive grouping
df['Company Domain Name'] = df['Company Domain Name'].str.lower()

# Dictionary to keep track of sheet name counts
sheet_name_counts = {}

# Function to clean and truncate sheet names
def clean_sheet_name(name):
    # Remove 'http://', 'https://', and 'www.'
    name = re.sub(r'^(http://|https://)?(www\.)?', '', name)
    # Remove invalid characters
    name = re.sub(r'[\\/*?[\]:]', '', name)
    # Truncate to 31 characters
    return name[:31]

# Group by the "Company Domain Name" column and write each group to a separate sheet
for domain_name, group in df.groupby('Company Domain Name'):
    # Clean and truncate the domain name
    clean_name = clean_sheet_name(domain_name)
    if clean_name in sheet_name_counts:
        sheet_name_counts[clean_name] += 1
        sheet_name = f"{clean_name}_{sheet_name_counts[clean_name]}"
        # Ensure the final sheet name is within the 31 character limit
        sheet_name = sheet_name[:31]
    else:
        sheet_name_counts[clean_name] = 1
        sheet_name = clean_name
    
    group.to_excel(writer, sheet_name=sheet_name, index=False)

# Save the new Excel file
writer.close()