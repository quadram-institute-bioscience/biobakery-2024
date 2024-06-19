#!/usr/bin/env python

import json
import argparse
import os

def rename(fileFrom, fileTo, dry_run):
    if dry_run:
        print(f'Renaming {fileFrom}\n\tto {fileTo}')
    else:
        try:
            os.rename(fileFrom, fileTo)
            print(f'Renamed {fileFrom}\n\tto {fileTo}')
        except OSError as e:
            print(f'Error renaming {fileFrom}\n\tto {fileTo}: {e}')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Rename output files to match input file names based on JSON configurations.')
    parser.add_argument("JSON_FILES", nargs='+', type=str, help='JSON files containing the input and output file names')
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory containing JSON files and output files')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Perform a dry run without renaming files')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

def read_json_files(json_files, verbose=False):
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

def rename_files(json_data, files_dir, dryrun=False):
    directory = os.path.abspath(files_dir)
    for entry in json_data:
        old_name1 = os.path.join(directory, entry[0]['fastq1_out_name'])
        new_name1 = os.path.join(directory, entry[0]['fastq1_in_name'])
        old_name2 = os.path.join(directory, entry[0]['fastq2_out_name'])
        new_name2 = os.path.join(directory, entry[0]['fastq2_in_name'])

        if os.path.exists(old_name1):
            rename(old_name1, new_name1, dryrun)
        else:
            print(f'ERROR: File {old_name1} does not exist and cannot be renamed.')

        if os.path.exists(old_name2):
            rename(old_name2, new_name2, dryrun)
        else:
            print(f'ERROR: File {old_name2} does not exist and cannot be renamed.')

def main():
    args = parse_arguments()
    json_data = read_json_files(args.JSON_FILES)
    print(f"Found {len(json_data)} JSON files in {args.directory}") if json_data else print("No JSON files found.")
    rename_files(json_data, args.directory, args.dry_run)

if __name__ == '__main__':
    main()