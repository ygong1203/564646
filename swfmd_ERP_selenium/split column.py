import pandas as pd
import re
import os
import glob


def extract_info(text, category):
    if not isinstance(text, str):
        return None
    pattern = rf'({category}):([^;]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    else:
        return None


def process_csv_files(directory, output_directory):
    path_pattern = os.path.join(directory, '*.csv')
    csv_files = glob.glob(path_pattern)

    for file_path in csv_files:
        print(f'Processing {file_path}...')
        try:
            df = pd.read_csv(file_path, encoding='utf-8')  # Default encoding
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Alternative encoding
            except UnicodeDecodeError:
                print(f"Failed to read {file_path} with standard encodings.")
                continue  # Skip to the next file

        if 'PARTY OF CONCERNS' in df.columns:
            df['PARTY OF CONCERNS'] = df['PARTY OF CONCERNS'].fillna('No data available')
            df['Engr_Consultant_Info'] = df['PARTY OF CONCERNS'].apply(
                lambda x: extract_info(x, 'Engr Consultant|agent'))
            df['Applicant_Info'] = df['PARTY OF CONCERNS'].apply(lambda x: extract_info(x, 'Applicant'))

            output_file = os.path.join(output_directory, os.path.basename(file_path).replace('.csv', '_modified.csv'))
            df.to_csv(output_file, index=False)
            print(f'Data saved to {output_file}')
        else:
            print(f"The column 'PARTY OF CONCERNS' does not exist in {file_path}.")


# Define directories
input_directory = r'C:\Users\lily\OneDrive\Desktop\Large Language Model shits\ERP_SFWMD Engineer'
output_directory = r'C:\Users\lily\OneDrive\Desktop\Large Language Model shits\ERP_SFWMD Engineer\Modified Files'

# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Process files
process_csv_files(input_directory, output_directory)
