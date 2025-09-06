import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_data(file_path):
    """Load the raw e-commerce data"""
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def clean_data(df):
    """Comprehensive data cleaning for e-commerce dataset"""
    
    print("Starting data cleaning process...")
    original_shape = df.shape
    
    # 1. Handle missing values
    print("\n1. Handling missing values...")
    print("Missing values per column:")
    print(df.isnull().sum())
    
    # Fill missing customer_age with median
    if 'customer_age' in df.columns:
        df['customer_age'].fillna(df['customer_age'].median(), inplace=True)
    
    # Fill missing product_category with 'Unknown'
    if 'product_category' in df.columns:
        df['product_category'].fillna('Unknown', inplace=True)
    
    # Drop rows with missing critical information
    critical_columns = ['order_id', 'customer_id', 'order_date', 'total_amount']
    df.dropna(subset=[col for col in critical_columns if col in df.columns], inplace=True)
    
    # 2. Remove duplicates
    print("\n2. Removing duplicates...")
    initial_count = len(df)
    df.drop_duplicates(subset=['order_id'], keep='first', inplace=True)
    duplicates_removed = initial_count - len(df)
    print(f"Removed {duplicates_removed} duplicate records")
    
    # 3. Clean and standardize data types
    print("\n3. Cleaning and standardizing data types...")
    
    # Clean order_date
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        df.dropna(subset=['order_date'], inplace=True)
    
    # Clean customer_email
    if 'customer_email' in df.columns:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        df = df[df['customer_email'].str.match(email_pattern, na=False)]
    
    # Clean phone numbers (remove non-digits and standardize)
    if 'customer_phone' in df.columns:
        df['customer_phone'] = df['customer_phone'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df['customer_phone'] = df['customer_phone'].replace('', np.nan)
    
    # 4. Handle outliers
    print("\n4. Handling outliers...")
    
    # Remove negative quantities and amounts
    if 'quantity' in df.columns:
        df = df[df['quantity'] > 0]
    
    if 'unit_price' in df.columns:
        df = df[df['unit_price'] > 0]
    
    if 'total_amount' in df.columns:
        df = df[df['total_amount'] > 0]
        
        # Remove extreme outliers (beyond 3 standard deviations)
        mean_amount = df['total_amount'].mean()
        std_amount = df['total_amount'].std()
        df = df[abs(df['total_amount'] - mean_amount) <= 3 * std_amount]
    
    # 5. Standardize categorical data
    print("\n5. Standardizing categorical data...")
    
    # Standardize product categories
    if 'product_category' in df.columns:
        df['product_category'] = df['product_category'].str.title().str.strip()
    
    # Standardize customer gender
    if 'customer_gender' in df.columns:
        gender_mapping = {
            'M': 'Male', 'm': 'Male', 'male': 'Male', 'MALE': 'Male',
            'F': 'Female', 'f': 'Female', 'female': 'Female', 'FEMALE': 'Female'
        }
        df['customer_gender'] = df['customer_gender'].map(gender_mapping).fillna('Unknown')
    
    # Standardize payment methods
    if 'payment_method' in df.columns:
        df['payment_method'] = df['payment_method'].str.title().str.strip()
    
    # 6. Create derived columns
    print("\n6. Creating derived columns...")
    
    # Extract date components
    if 'order_date' in df.columns:
        df['order_year'] = df['order_date'].dt.year
        df['order_month'] = df['order_date'].dt.month
        df['order_day'] = df['order_date'].dt.day
        df['order_weekday'] = df['order_date'].dt.day_name()
        df['order_quarter'] = df['order_date'].dt.quarter
    
    # Create customer age groups
    if 'customer_age' in df.columns:
        df['age_group'] = pd.cut(df['customer_age'], 
                                bins=[0, 25, 35, 50, 65, 100], 
                                labels=['18-25', '26-35', '36-50', '51-65', '65+'])
    
    # Create revenue per item
    if 'total_amount' in df.columns and 'quantity' in df.columns:
        df['revenue_per_item'] = df['total_amount'] / df['quantity']
    
    # 7. Final validation
    print("\n7. Final validation...")
    
    # Check data quality
    final_shape = df.shape
    print(f"Data cleaning completed!")
    print(f"Original shape: {original_shape}")
    print(f"Final shape: {final_shape}")
    print(f"Records removed: {original_shape[0] - final_shape[0]}")
    
    # Data quality report
    print("\nData Quality Report:")
    print(f"- Missing values: {df.isnull().sum().sum()}")
    print(f"- Duplicate order_ids: {df['order_id'].duplicated().sum()}")
    print(f"- Date range: {df['order_date'].min()} to {df['order_date'].max()}")
    
    return df

def save_cleaned_data(df, output_path):
    """Save the cleaned dataset"""
    try:
        df.to_csv(output_path, index=False)
        print(f"\nCleaned data saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def generate_data_profile(df):
    """Generate a data profiling report"""
    print("\n" + "="*50)
    print("DATA PROFILING REPORT")
    print("="*50)
    
    print(f"\nDataset Shape: {df.shape}")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\nColumn Information:")
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        print(f"- {col}: {dtype} | Nulls: {null_count} ({null_pct:.1f}%) | Unique: {unique_count}")
    
    if 'total_amount' in df.columns:
        print(f"\nRevenue Statistics:")
        print(f"- Total Revenue: ${df['total_amount'].sum():,.2f}")
        print(f"- Average Order Value: ${df['total_amount'].mean():.2f}")
        print(f"- Median Order Value: ${df['total_amount'].median():.2f}")
    
    if 'customer_id' in df.columns:
        print(f"\nCustomer Statistics:")
        print(f"- Total Customers: {df['customer_id'].nunique():,}")
        print(f"- Total Orders: {len(df):,}")
        print(f"- Avg Orders per Customer: {len(df) / df['customer_id'].nunique():.2f}")

def main():
    """Main execution function"""
    
    # File paths
    input_file = 'raw_ecommerce_data.csv'
    output_file = 'cleaned_ecommerce_data.csv'
    
    # Load data
    df = load_data(input_file)
    if df is None:
        return
    
    # Clean data
    cleaned_df = clean_data(df)
    
    # Generate profile
    generate_data_profile(cleaned_df)
    
    # Save cleaned data
    save_cleaned_data(cleaned_df, output_file)
    
    print("\n" + "="*50)
    print("DATA CLEANING PROCESS COMPLETED SUCCESSFULLY!")
    print("="*50)

if __name__ == "__main__":
    main()