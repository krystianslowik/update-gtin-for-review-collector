import pandas as pd
import os

# File paths (adjust these if your files are in different directories)
gtin_sku_file = 'gtin_sku_from_customer.csv'
metabase_file = 'metabase_product_export.csv'
output_file = 'ready-to-review-collector.csv'

# Check if input files exist
if not os.path.exists(gtin_sku_file):
    raise FileNotFoundError(f"The file '{gtin_sku_file}' does not exist.")
if not os.path.exists(metabase_file):
    raise FileNotFoundError(f"The file '{metabase_file}' does not exist.")

# Read gtin_sku_from_customer.csv
try:
    gtin_sku_df = pd.read_csv(gtin_sku_file, dtype=str,
                              encoding='utf-8')  # Assuming UTF-8
    # Trim whitespace from headers
    gtin_sku_df.rename(columns=lambda x: x.strip(), inplace=True)
except Exception as e:
    raise Exception(f"Error reading '{gtin_sku_file}': {e}")

# Validate required columns in gtin_sku_from_customer.csv
required_gtin_sku_cols = {'gtin', 'sku'}
if not required_gtin_sku_cols.issubset(gtin_sku_df.columns.str.lower()):
    missing = required_gtin_sku_cols - set(gtin_sku_df.columns.str.lower())
    raise ValueError(f"Missing columns in '{gtin_sku_file}': {missing}")

# Normalize column names to lowercase for consistency
gtin_sku_df.columns = gtin_sku_df.columns.str.lower()

# Read metabase_product_export.csv with specified encoding
try:
    # Replace with detected encoding
    metabase_df = pd.read_csv(metabase_file, dtype=str, encoding='ISO-8859-1')
    # Trim whitespace from headers
    metabase_df.rename(columns=lambda x: x.strip(), inplace=True)
except Exception as e:
    raise Exception(f"Error reading '{metabase_file}': {e}")

# Validate required columns in metabase_product_export.csv
required_metabase_cols = {'sku', 'gtin',
                          'name', 'url', 'image_url', 'mpn', 'brand'}
if not required_metabase_cols.issubset(metabase_df.columns.str.lower()):
    missing = required_metabase_cols - set(metabase_df.columns.str.lower())
    raise ValueError(f"Missing columns in '{metabase_file}': {missing}")

# Normalize column names to lowercase for consistency
metabase_df.columns = metabase_df.columns.str.lower()

# Merge the two DataFrames on 'sku' to ensure correct GTIN assignment
merged_df = pd.merge(
    metabase_df,
    gtin_sku_df[['sku', 'gtin']],
    on='sku',
    how='left',
    suffixes=('_metabase', '_customer')
)

# Check for SKUs in metabase_export that do not have a corresponding GTIN in customer file
missing_gtins = merged_df[merged_df['gtin_customer'].isnull()]
if not missing_gtins.empty:
    print("Warning: The following SKUs from 'metabase_product_export.csv' do not have corresponding GTINs in 'gtin_sku_from_customer.csv':")
    print(missing_gtins[['sku', 'name']])
    # Optionally, you can decide to fill missing GTINs with original GTINs or leave them empty
    # For example, using original GTINs where customer GTINs are missing:
    # merged_df['gtin_customer'] = merged_df['gtin_customer'].fillna(merged_df['gtin_metabase'])
    # Or set to empty string:
    # merged_df['gtin_customer'] = merged_df['gtin_customer'].fillna('')

# Replace the GTIN in metabase data with the customer's GTIN
merged_df['final_gtin'] = merged_df['gtin_customer'].combine_first(
    merged_df['gtin_metabase'])

# Prepare the final DataFrame with required columns
# Initialize customer-related fields as empty strings or with default values
final_df = pd.DataFrame({
    'email': 'update_gtin@trustedshops.com',  # Populate as needed
    'reference': 'GTIN_UPDATE',  # Populate as needed
    'firstName': 'GTIN_UPDATE',  # Populate as needed
    'lastName': 'GTIN_UPDATE',  # Populate as needed
    'transactionDate': '20.09.2024',  # Populate as needed
    'productName': merged_df['name'],
    'productSku': merged_df['sku'],
    'productUrl': merged_df['url'],
    'productImageUrl': merged_df['image_url'],
    'productBrand': merged_df['brand'],
    'productGtin': merged_df['final_gtin'],
    'productMpn': merged_df['mpn']
})

# Replace any NaN values with empty strings
final_df.fillna('', inplace=True)

# Reorder columns to match the desired output
final_df = final_df[[
    'email',
    'reference',
    'firstName',
    'lastName',
    'transactionDate',
    'productName',
    'productSku',
    'productUrl',
    'productImageUrl',
    'productBrand',
    'productGtin',
    'productMpn'
]]

# Save to CSV with semicolon delimiter
try:
    final_df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
    print(f"Import file '{output_file}' has been created successfully.")
except Exception as e:
    raise Exception(f"Error writing to '{output_file}': {e}")
