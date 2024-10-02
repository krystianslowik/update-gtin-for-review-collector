import pandas as pd
import os
import random
import string
import uuid
from datetime import datetime, timedelta

# -------------------------- Mock Data Generation -------------------------- #


def generate_random_email():
    """Generate a random email address."""
    domains = ['example.com', 'test.com', 'mail.com', 'demo.org']
    name_length = random.randint(5, 10)
    name = ''.join(random.choices(string.ascii_lowercase, k=name_length))
    domain = random.choice(domains)
    return f"{name}@{domain}"


def generate_random_reference():
    """Generate a random UUID as a transaction reference."""
    return str(uuid.uuid4())


def generate_random_transaction_date():
    """Generate a random transaction date within the past year."""
    start_date = datetime.now() - timedelta(days=365)
    random_days = random.randint(0, 365)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime('%d.%m.%Y')

# -------------------------- File Operations -------------------------- #


def check_file_exists(file_path):
    """Check if a file exists."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")


def read_csv_file(file_path, encoding='utf-8'):
    """Read a CSV file and return a DataFrame."""
    try:
        df = pd.read_csv(file_path, dtype=str, encoding=encoding)
        df.rename(columns=lambda x: x.strip(), inplace=True)
        return df
    except Exception as e:
        raise Exception(f"Error reading '{file_path}': {e}")


def validate_columns(df, required_columns, file_name):
    """Validate that required columns are present in the DataFrame."""
    df_columns = set(df.columns.str.lower())
    required_lower = {col.lower() for col in required_columns}
    if not required_lower.issubset(df_columns):
        missing = required_lower - df_columns
        raise ValueError(f"Missing columns in '{file_name}': {missing}")


def normalize_columns(df):
    """Normalize column names to lowercase."""
    df.columns = df.columns.str.lower()

# -------------------------- Data Processing -------------------------- #


def merge_dataframes(metabase_df, gtin_sku_df):
    """Merge metabase and GTIN SKU DataFrames on 'sku'."""
    merged_df = pd.merge(
        metabase_df,
        gtin_sku_df[['sku', 'gtin']],
        on='sku',
        how='left',
        suffixes=('_metabase', '_customer')
    )
    return merged_df


def handle_missing_gtins(merged_df, metabase_file, gtin_sku_file):
    """Handle SKUs without corresponding GTINs."""
    missing_gtins = merged_df[merged_df['gtin_customer'].isnull()]
    if not missing_gtins.empty:
        print(f"Warning: The following SKUs from '{
              metabase_file}' do not have corresponding GTINs in '{gtin_sku_file}':")
        print(missing_gtins[['sku', 'name']])
        # Optionally handle missing GTINs here
    return merged_df


def replace_gtin(merged_df):
    """Replace GTIN in metabase data with customer's GTIN where available."""
    merged_df['final_gtin'] = merged_df['gtin_customer'].combine_first(
        merged_df['gtin_metabase'])
    return merged_df


def prepare_final_dataframe(merged_df):
    """Prepare the final DataFrame with required columns and mocked data."""
    final_df = pd.DataFrame({
        # Mocked random emails
        'email': [generate_random_email() for _ in range(len(merged_df))],
        # Mocked random transaction IDs
        'reference': [generate_random_reference() for _ in range(len(merged_df))],
        # Mocked first names
        'firstName': ['MockFirstName' for _ in range(len(merged_df))],
        # Mocked last names
        'lastName': ['MockLastName' for _ in range(len(merged_df))],
        # Mocked dates
        'transactionDate': [generate_random_transaction_date() for _ in range(len(merged_df))],
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

    return final_df

# -------------------------- Save Operations -------------------------- #


def save_to_csv(df, output_file):
    """Save the DataFrame to a CSV file with a semicolon delimiter."""
    try:
        df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
        print(f"Import file '{
              output_file}' has been created successfully with mocked data.")
    except Exception as e:
        raise Exception(f"Error writing to '{output_file}': {e}")

# -------------------------- Main Processing Function -------------------------- #


def process_gtin_files(gtin_sku_file, metabase_file, output_file):
    """Main function to process GTIN and SKU files and generate the output CSV."""
    # Check if input files exist
    check_file_exists(gtin_sku_file)
    check_file_exists(metabase_file)

    # Read and validate gtin_sku_from_customer.csv
    gtin_sku_df = read_csv_file(gtin_sku_file, encoding='utf-8')
    validate_columns(gtin_sku_df, {'gtin', 'sku'}, gtin_sku_file)
    normalize_columns(gtin_sku_df)

    # Read and validate metabase_product_export.csv
    metabase_df = read_csv_file(metabase_file, encoding='ISO-8859-1')
    validate_columns(metabase_df, {
                     'sku', 'gtin', 'name', 'url', 'image_url', 'mpn', 'brand'}, metabase_file)
    normalize_columns(metabase_df)

    # Merge DataFrames
    merged_df = merge_dataframes(metabase_df, gtin_sku_df)

    # Handle missing GTINs
    merged_df = handle_missing_gtins(merged_df, metabase_file, gtin_sku_file)

    # Replace GTINs
    merged_df = replace_gtin(merged_df)

    # Prepare final DataFrame
    final_df = prepare_final_dataframe(merged_df)

    # Save to CSV
    save_to_csv(final_df, output_file)

# -------------------------- Entry Point -------------------------- #


if __name__ == "__main__":
    # Define file paths (adjust these if your files are in different directories)
    gtin_sku_file = 'gtin_sku_from_customer.csv'
    metabase_file = 'metabase_product_export.csv'
    output_file = 'ready-to-review-collector.csv'

    # Process the files
    process_gtin_files(gtin_sku_file, metabase_file, output_file)
