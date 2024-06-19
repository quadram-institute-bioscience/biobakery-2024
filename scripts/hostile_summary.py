#!/usr/bin/env python
"""
A script to extract sequencing data from JSON files and save it to a CSV file.
Andrea Telatin 2024
"""

# Check if pandas is available
try:
    import pandas as pd
except ImportError:
    print("Please install pandas using 'pip install pandas'")
    exit(1)

import json
import argparse
import os
import sys

VALID_KEYS = ['fastq1_in_name', 'reads_in', 'reads_out', 'reads_removed_proportion']

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process JSON files to extract sequencing data.')
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory containing JSON files')
    parser.add_argument('-o', '--output', type=str, help='Output CSV file')
    parser.add_argument('--sort',  action='store_true', help='Sort the data by percentage')

    parser.add_argument('--md',  action='store_true', help='Print the table in markdown format')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

def read_json_files(directory, verbose=False):
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
    if verbose:
        print(f'Found {len(json_files)} JSON files in {directory}')
    data = []
    for file in json_files:
        # skip empty files
        if os.path.getsize(file) == 0:
            continue
        try:
            with open(file, 'r') as f:
                data.append(json.load(f))
        except json.JSONDecodeError as e:
            print(f'Error reading {file}: {e}')
            continue
    
    return data

def extract_data(json_data):
    extracted_data = []
    for entry in json_data:
        sample_name = entry[0].get('fastq1_in_name', '').replace('_1.fastq.gz', '')
        reads_raw = entry[0].get('reads_in', 0)
        reads_clean = entry[0].get('reads_out', 0)
        percentage_human = entry[0].get('reads_removed_proportion', 0.0) * 100
        
        extracted_data.append({
            'SampleName': sample_name,
            'Reads_Raw': reads_raw,
            'Reads_Clean': reads_clean,
            'Percentage_Human': percentage_human
        })
    return extracted_data

def create_dataframe(data):
    return pd.DataFrame(data)

def save_to_csv(df, output_file):
    df.to_csv(output_file, index=False)

def main():
    # Parse command line arguments
    args = parse_arguments()
    # Get all the JSON files in the directory
    directory = os.path.abspath(args.directory)
    json_data = read_json_files(directory, args.verbose)
    # Extract the data from the JSON files
    extracted_data = extract_data(json_data)

    # Create a DataFrame from the extracted data
    df = create_dataframe(extracted_data)
    # Set 'SampleName' as the index
    df.set_index('SampleName', inplace=True)

    if args.sort:
        df.sort_values(by='Percentage_Human', inplace=True, ascending=False)

    if args.output:
        save_to_csv(df, args.output)
    else:
        if not args.md:
            print(df)
        else:
            try:
                print(df.to_markdown())
            except Exception as e:
                print(f'Error converting to markdown: {e}', file=sys.stderr)
                print(df)

if __name__ == '__main__':
    main()