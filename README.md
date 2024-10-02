[![Python Tests](https://github.com/krystianslowik/update-gtin-for-review-collector/actions/workflows/python-tests.yml/badge.svg)](https://github.com/krystianslowik/update-gtin-for-review-collector/actions/workflows/python-tests.yml)
# Prepare Review Collector file to update GTIN

## Description

This script merges two CSV files to create an Review Collector file for customer reviews.
It ensures that **GTINs** are correctly assigned to **SKUs** based on the provided mapping.

## Input Files

### `metabase_product_export.csv`

- **Source**: Exported directly from the product table in Metabase.
- **Format**: CSV (Comma-Separated Values)
- **❗Note**: **Do not modify** this file after exporting.

**Structure:**

| Column Name     | Description                       |
| --------------- | --------------------------------- |
| id              | Unique identifier for the product |
| version         | Version number                    |
| created_at      | Creation timestamp                |
| updated_at      | Last update timestamp             |
| account_id      | Associated account ID             |
| channel_id      | Sales channel ID                  |
| sku             | Stock Keeping Unit identifier     |
| name            | Product name                      |
| url             | Product URL                       |
| image_url       | URL to the product image          |
| gtin            | Global Trade Item Number          |
| mpn             | Manufacturer Part Number          |
| brand           | Brand name                        |
| attributes_hash | Attributes in hashed format       |
| product_version | Product version details           |
| image_id        | Image identifier                  |

### `gtin_sku_from_customer.csv`

- **Source**: Provided by the customer.
- **Format**: CSV (Comma-Separated Values)

**Structure:**

| Column Name | Description                   |
| ----------- | ----------------------------- |
| gtin        | Global Trade Item Number      |
| sku         | Stock Keeping Unit identifier |

**Example:**

```csv
gtin,sku
4242002996950,4242002996950_01
4242002996967,4242002996967_01
4242002871035,4242002871035_01
4242002849102,4242002849102_01
4242002845043,4242002845043_01
```

## Installation

### 1. Clone the Repository

Navigate to your desired directory and clone the repository:

```bash
git clone https://github.com/yourusername/import-reviews-script.git
cd import-reviews-script
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

#### **On macOS and Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### **On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

> **Note:** To deactivate the virtual environment later, simply run:

```bash
deactivate
```

### 3. Install Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install pandas chardet
```

## Usage

1. **Prepare Input Files**

   - Ensure that both `metabase_product_export.csv` and `gtin_sku_from_customer.csv` are placed in the same directory as the script (`update-gtin.py`).
   - **Important**: `metabase_product_export.csv` should be exported directly from the product table in Metabase, in CSV format, without any modifications.

2. **Run the Script**

   Execute the Python script to generate the Review Collector file.

   #### **On macOS and Linux:**

   ```bash
   python3 update-gtin.py
   ```

   #### **On Windows:**

   ```bash
   python update-gtin.py
   ```

3. **Output**

   After successful execution, an `ready-to-review-collector.csv` file will be created in the same directory with the following structure:

   | Column Name     | Description                                            |
   | --------------- | ------------------------------------------------------ |
   | email           | **mocked**                                             |
   | reference       | **mocked**                                             |
   | firstName       | **mocked**                                             |
   | lastName        | **mocked**                                             |
   | transactionDate | **mocked**                                             |
   | productName     | Name of the product FROM METABASE                      |
   | productSku      | Stock Keeping Unit identifier FROM METABASE            |
   | productUrl      | URL to the product FROM METABASE                       |
   | productImageUrl | URL to the product image FROM METABASE                 |
   | productBrand    | Brand name of the product FROM METABASE                |
   | productGtin     | Global Trade Item Number (GTIN) FROM **CUSTOMER FILE** |
   | productMpn      | Manufacturer Part Number (MPN) FROM METABASE           |

## Troubleshooting

### 1. `ModuleNotFoundError: No module named 'pandas'`

**Cause**: The `pandas` library is not installed in your current Python environment.

**Solution**:

- Ensure that you have activated the virtual environment:

  #### **On macOS and Linux:**

  ```bash
  source venv/bin/activate
  ```

  #### **On Windows:**

  ```bash
  venv\Scripts\activate
  ```

- Install the required dependencies:

  ```bash
  pip install pandas chardet
  ```

### 2. `UnicodeDecodeError: 'utf-8' codec can't decode byte...`

**Cause**: The CSV file is not encoded in UTF-8.

**Solution**:

- The script uses the `chardet` library to detect the encoding automatically. Ensure that your `metabase_product_export.csv` is not corrupted.
- If the error persists, you may need to manually specify the encoding in the script. Open `update-gtin.py` and modify the `read_csv` line for `metabase_product_export.csv`:

  ```python
  metabase_df = pd.read_csv(metabase_file, dtype=str, encoding='ISO-8859-1')
  ```

  Replace `'ISO-8859-1'` with the correct encoding as detected.

### 3. `error: externally-managed-environment`

**Cause**: Attempting to install packages system-wide in an environment managed by Homebrew or another package manager.

**Solution**:

- **Use a Virtual Environment**: This is the recommended approach to avoid conflicts.

  #### **On macOS and Linux:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install pandas chardet
  ```

  #### **On Windows:**

  ```bash
  python -m venv venv
  venv\Scripts\activate
  pip install pandas chardet
  ```

- **Alternative**: If you need to install packages system-wide (not recommended), use Homebrew.

  ```bash
  brew install pandas
  ```

  However, using virtual environments is strongly recommended to prevent breaking your system's Python installation.

### 4. General Tips

- **Ensure Correct File Paths**: Make sure that the CSV files are in the correct directory and that their filenames match exactly.
- **Check CSV Integrity**: Open the CSV files to ensure they are not corrupted and are properly formatted.
- **Activate Virtual Environment**: Always activate the virtual environment before running the script to ensure all dependencies are available.

## Customization

- **Populating Customer Fields**: The script initializes customer-related fields (`email`, `reference`, `firstName`, `lastName`, `transactionDate`) as empty strings. You can modify the script to populate these fields based on your data sources or add default values as needed.

## License

This project is licensed under the [MIT License](LICENSE).
