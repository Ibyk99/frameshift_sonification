#  Little code snippet I made to parse BLAST XML output (outfmt 5) and grab the top match and each of the 2 seqs
from Bio.Blast import NCBIXML

in_file_path = "./test_files"
in_file = "0Y9X9NJY014-Alignment.xml"

input_file = f"{in_file_path}/{in_file}"

try:
    with open(input_file, "r") as file:
        alignment = NCBIXML.read(file).alignments[0].hsps[0]
except FileNotFoundError as e:
    exit(f"File not found: {input_file} > {e}")
except PermissionError as e:
    exit(f"Can't read file - please check the permissions on the file > {e}")


sequence_1 = alignment.query
sequence_2 = alignment.sbjct

print(sequence_1)
print(sequence_2)