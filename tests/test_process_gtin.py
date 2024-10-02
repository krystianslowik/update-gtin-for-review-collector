import pytest
import pandas as pd
import os
from unittest.mock import patch, mock_open
from io import StringIO
from process_gtin import (
    generate_random_email,
    generate_random_reference,
    generate_random_transaction_date,
    read_csv_file,
    validate_columns,
    merge_dataframes,
    replace_gtin,
    prepare_final_dataframe,
    process_gtin_files
)
from datetime import datetime

# -------------------------- Mock Data -------------------------- #

GTIN_SKU_CSV = """gtin,sku
0123456789123,SKU123
9876543210987,SKU456
"""

METABASE_CSV = """sku,gtin,name,url,image_url,mpn,brand
SKU123,0123456789123,Product A,http://example.com/a,http://example.com/img/a,MPN123,BrandX
SKU456,9876543210987,Product B,http://example.com/b,http://example.com/img/b,MPN456,BrandY
SKU789,5555555555555,Product C,http://example.com/c,http://example.com/img/c,MPN789,BrandZ
"""

# -------------------------- Test Functions -------------------------- #


def test_generate_random_email():
    email = generate_random_email()
    assert "@" in email
    local_part, domain = email.split("@")
    assert len(local_part) >= 5
    assert domain in ['example.com', 'test.com', 'mail.com', 'demo.org']


def test_generate_random_reference():
    reference = generate_random_reference()
    assert isinstance(reference, str)
    assert len(reference) == 36  # UUID length


def test_generate_random_transaction_date():
    date_str = generate_random_transaction_date()
    assert isinstance(date_str, str)
    # Simple check for format DD.MM.YYYY
    parts = date_str.split(".")
    assert len(parts) == 3
    day, month, year = parts
    assert 1 <= int(day) <= 31
    assert 1 <= int(month) <= 12
    assert 2000 <= int(year) <= datetime.now().year


def test_read_csv_file():
    with patch("builtins.open", mock_open(read_data=GTIN_SKU_CSV)):
        df = read_csv_file("gtin_sku_from_customer.csv")
        assert not df.empty
        assert list(df.columns) == ['gtin', 'sku']
        assert len(df) == 2


def test_validate_columns_success():
    df = pd.DataFrame({
        'gtin': ['0123456789123', '9876543210987'],
        'sku': ['SKU123', 'SKU456']
    })
    # Should not raise an exception
    validate_columns(df, {'gtin', 'sku'}, 'gtin_sku_from_customer.csv')


def test_validate_columns_failure():
    df = pd.DataFrame({
        'gtin': ['0123456789123', '9876543210987'],
        'product_code': ['SKU123', 'SKU456']
    })
    with pytest.raises(ValueError) as excinfo:
        validate_columns(df, {'gtin', 'sku'}, 'gtin_sku_from_customer.csv')
    assert "Missing columns" in str(excinfo.value)


def test_merge_dataframes():
    metabase_df = pd.DataFrame({
        'sku': ['SKU123', 'SKU456', 'SKU789'],
        'gtin': ['0123456789123', '9876543210987', '5555555555555'],
        'name': ['Product A', 'Product B', 'Product C'],
        'url': ['http://example.com/a', 'http://example.com/b', 'http://example.com/c'],
        'image_url': ['http://example.com/img/a', 'http://example.com/img/b', 'http://example.com/img/c'],
        'mpn': ['MPN123', 'MPN456', 'MPN789'],
        'brand': ['BrandX', 'BrandY', 'BrandZ']
    })
    gtin_sku_df = pd.DataFrame({
        'sku': ['SKU123', 'SKU456'],
        'gtin': ['0123456789123', '9876543210987']
    })
    merged_df = merge_dataframes(metabase_df, gtin_sku_df)
    assert len(merged_df) == 3
    assert 'gtin_customer' in merged_df.columns
    assert merged_df.loc[merged_df['sku'] ==
                         'SKU789', 'gtin_customer'].isnull().all()


def test_replace_gtin():
    merged_df = pd.DataFrame({
        'gtin_metabase': ['0123456789123', '9876543210987', '5555555555555'],
        'gtin_customer': ['0123456789123', '9876543210987', None]
    })
    merged_df = replace_gtin(merged_df)
    assert merged_df['final_gtin'].tolist(
    ) == ['0123456789123', '9876543210987', '5555555555555']


def test_prepare_final_dataframe():
    merged_df = pd.DataFrame({
        'name': ['Product A', 'Product B'],
        'sku': ['SKU123', 'SKU456'],
        'url': ['http://example.com/a', 'http://example.com/b'],
        'image_url': ['http://example.com/img/a', 'http://example.com/img/b'],
        'brand': ['BrandX', 'BrandY'],
        'final_gtin': ['0123456789123', '9876543210987'],
        'mpn': ['MPN123', 'MPN456']
    })
    final_df = prepare_final_dataframe(merged_df)
    assert list(final_df.columns) == [
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
    ]
    assert len(final_df) == 2
    # Check mocked data
    for email in final_df['email']:
        assert "@" in email
    for reference in final_df['reference']:
        assert len(reference) == 36  # UUID length
    for date in final_df['transactionDate']:
        parts = date.split(".")
        assert len(parts) == 3


def test_process_gtin_files(tmp_path):
    """End-to-end test of the process_gtin_files function."""
    # Create temporary CSV files
    gtin_sku_path = tmp_path / "gtin_sku_from_customer.csv"
    metabase_path = tmp_path / "metabase_product_export.csv"
    output_path = tmp_path / "ready-to-review-collector.csv"

    gtin_sku_path.write_text(GTIN_SKU_CSV)
    metabase_path.write_text(METABASE_CSV)

    # Run the processing function
    process_gtin_files(
        gtin_sku_file=str(gtin_sku_path),
        metabase_file=str(metabase_path),
        output_file=str(output_path)
    )

    # Check if output file is created
    assert output_path.exists()

    # Read the output file
    output_df = pd.read_csv(output_path, sep=';', dtype=str)

    # Check columns
    expected_columns = [
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
    ]
    assert list(output_df.columns) == expected_columns

    # Check number of rows (3 from metabase, 2 with GTIN from customer, 1 without)
    assert len(output_df) == 3

    # Check that 'final_gtin' is correctly populated
    product_c_gtin = output_df.loc[output_df['productSku']
                                   == 'SKU789', 'productGtin'].values[0]
    assert product_c_gtin == '5555555555555'
