from midiutil import MIDIFile
import pygame
import sys
from sound_mappings import codons
from Bio.Blast import NCBIXML

# TODO: Amend this to use argparse to take input
# Temp way of defining input alignment file
in_file_path = "./test_files"
in_file = "0Y9X9NJY014-Alignment.xml"

input_file = f"{in_file_path}/{in_file}"

# Read the file and extract the first alignment
try:
    with open(input_file, "r") as file:
        alignment = NCBIXML.read(file).alignments[0].hsps[0]
except FileNotFoundError as e:
    exit(f"File not found: {input_file} > {e}")
except PermissionError as e:
    exit(f"Can't read file - please check the permissions on the file > {e}")

query_seq = alignment.query
subject_seq = alignment.sbjct


# Map of Bases - Midi notes
base_map = {"A": 9, "T": 5, "G": 7, "C": 12}

# Init a midi file which we can have multiple channels in
midi_file = MIDIFile(2, adjust_origin=False)

time = 0
tempo = 120


def build_track_nuc(sequence: str, track: int, midi=midi_file, b_map=base_map):
    channel = 0
    time = 0
    duration = 1
    volume = 100
    program =  11  # Represents the instrument, full mapping here: https://www.ccarh.org/courses/253/handout/gminstruments/
    midi.addProgramChange(track, channel, time, program)
    for base in sequence:
        base = base.upper()
        if base not in b_map and base != '-':
            exit(f"Error: Looks like there's a non-nucleotide character in your sequence: {base}")
        if base == '-':
            channel = 9 # Midi Channel 10 is the reserved channel for percussion instruments, midiutil starts the channel index at 0, hence this is 9 in this case
            pitch = 49  # This is a cymbal clash sound when in channel 9
            volume = 80 # The clash is a little loud and can be startling, so we turn the volume down a little
        else:
            pitch = b_map[base]
        midi.addNote(track, channel, pitch, time, duration, volume)
        time += duration


def build_track_codon(sequence: str, track: int, midi=midi_file, c_map=codons, start_index=0, window_size=3):
    time = 0
    duration = 1
    volume = 100
    program =  11  # Represents the instrument, full mapping here: https://www.ccarh.org/courses/253/handout/gminstruments/
    sequence = sequence.replace('-', '')
    for i in range(int(len(sequence)/window_size)):
        channel = 1
        codon = sequence[start_index:(start_index+window_size)]
        if c_map[codon]['name'] == "Stop":
            channel = 9
            pitch = 35
        else:
            pitch = c_map[codon]['midi']
        midi.addNote(track, channel, pitch, time, duration, volume)
        start_index += window_size
        time += duration

# Build both tracks - 1 for query seq and 1 for subject seq
track = 0
for seq in [query_seq, subject_seq]:
    midi_file.addTrackName(track, time, f"track_{track}")
    midi_file.addTempo(track, time, tempo)
    # build_track_nuc(seq, track)
    build_track_codon(seq, track)
    track += 1
    print(f"track_{track}", seq)



with open("temp/output_file.mid", "wb") as outfile:
    midi_file.writeFile(outfile)

pygame.mixer.init()
pygame.mixer.music.load("temp/output_file.mid")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.delay(100)
