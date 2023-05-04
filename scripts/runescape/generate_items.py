"""One off functions that are used for the Grand Exchange function"""

def remove_column(file_path, column_name):
    # Steps:
    # Create the tsv: https://chisel.weirdgloop.org/gazproj/cache/tabulate
    #      > Add "tradeable" search arg
    # Run this function on the file to remove the 'tradeable' column to save space.
    #      > remove_column('data/rs3items.tsv', 'tradeable')
    with open(file_path, 'r') as f:
        lines = f.readlines()
        header = lines[0].split('\t')
        column_index = header.index(column_name)
        header.pop(column_index)

        data = [line.split('\t') for line in lines[1:]]
        data = [[row[i] for i in range(len(row)) if i != column_index] for row in data]

    with open(file_path, 'w') as f:
        f.write('\t'.join(header) + '\n')
        for row in data:
            f.write('\t'.join(row) + '\n')

# remove_column('data/rs3items.tsv', 'tradeable')