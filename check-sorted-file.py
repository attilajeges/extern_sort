#!/usr/bin/python

import argparse
import os
import random

RECORD_SIZE = 4096

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='check-sorted-file.py',
            description='Checks if the given file containing 4K ascii records is sorted')

    parser.add_argument('sorted_file', type=str)
    parser.add_argument('input_file', type=str)
    args = parser.parse_args()

    # Check filesize
    fsorted_stats = os.stat(args.sorted_file)
    finput_stats = os.stat(args.input_file)
    expected_size = finput_stats.st_size // RECORD_SIZE * RECORD_SIZE
    if (fsorted_stats.st_size != expected_size):
        print(f'Size of file {args.sorted_file} ({fsorted_stats.st_size}) should be {expected_size}')
        exit(1)


    # Collect first, last records and a random record from the input file
    input_records = set()
    with open(args.input_file, 'rb') as finput:
        # first
        input_records.add(finput.read(RECORD_SIZE))
        # last
        if RECORD_SIZE <= expected_size - RECORD_SIZE:
            finput.seek(expected_size - RECORD_SIZE)
            input_records.add(finput.read(RECORD_SIZE))
        # random
        if RECORD_SIZE <= expected_size - RECORD_SIZE - 1:
            rand_pos = random.randint(RECORD_SIZE, expected_size - RECORD_SIZE - 1)
            finput.seek(rand_pos // RECORD_SIZE * RECORD_SIZE)
            input_records.add(finput.read(RECORD_SIZE))

    # Check sorted file
    with open(args.sorted_file, 'rb') as fsorted:
        prev_record = None
        dup_record_count = 0;
        while True:
            record = fsorted.read(RECORD_SIZE)
            if not record:
                break;

            if len(record) != RECORD_SIZE:
                print(f'File {args.sorted_file} ends with an incomplete record')
                exit(1);
            if prev_record is not None and record < prev_record:
                print(f'File {args.sorted_file} is NOT sorted')
                exit(1);
            if record == prev_record:
                dup_record_count += 1

            input_records.discard(record)
            prev_record = record

    print(f'File {args.sorted_file} is sorted.\nFound {dup_record_count} duplicate records.')

    # Check that all input_records were found in the sorted file
    if input_records:
        print(f"File {args.sorted_file} doesn't contain the following input records:")
        for rec in input_records:
            print(rec)
        exit(1)
    else:
        print(f'Found all selected input records in {args.sorted_file}.')
