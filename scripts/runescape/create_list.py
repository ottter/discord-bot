"""One off functions that are used for the Grand Exchange function"""
import csv

def remove_column(file_path, column_name):
    # Steps:
    # Create the tsv: https://chisel.weirdgloop.org/gazproj/cache/tabulate
    #      > Add "tradeable" search arg
    # Run this function on the file to remove the 'tradeable' column to save space.
    #      > remove_column('data/rs3items.tsv', 'tradeable')
    with open(file_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        header = lines[0].split('\t')
        column_index = header.index(column_name)
        header.pop(column_index)

        data = [line.split('\t') for line in lines[1:]]
        data = [[row[i] for i in range(len(row)) if i != column_index] for row in data]

    with open(file_path, 'w', encoding='UTF-8') as f:
        f.write('\t'.join(header) + '\n')
        for row in data:
            f.write('\t'.join(row) + '\n')

def osrs_txt_to_csv(in_path='osrsitems.txt', out_path='osrsitems.csv'):
    with open(in_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()

    names = []
    for line in lines:
        name = line.split('\t', 1)[1].strip() # Get name field and remove leading/trailing spaces
        if name not in names:
            names.append(name)

    with open(out_path, 'w', newline='', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name']) # Write header row
        for name in names:
            writer.writerow([name])

osrs_txt_to_csv(in_path='data/osrsitems.txt', out_path='data/osrsitems.csv')
# remove_column('data/rs3items.tsv', 'tradeable')
