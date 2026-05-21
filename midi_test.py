from midiutil import MIDIFile
import pygame
import sys
from sound_mappings import amino_acids
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


query_seq = alignment.query
subject_seq = alignment.sbjct

pygame.mixer.init()

# # Take inputs
# query_seq = sys.argv[1] if len(sys.argv) > 1 else input("Sequence: ")
# subject_seq = sys.argv[2] if len(sys.argv) > 1 else input("Sequence: ")

# Map of Bases - Midi notes
base_map = {"A": 9, "T": 5, "G": 7, "C": 12}

# Init a midi file which we can have multiple channels in
midi_file = MIDIFile(2, adjust_origin=False)

time = 0
tempo = 120


def build_track(sequence: str, track: int, midi=midi_file, b_map=base_map):
    channel = 0
    time = 0
    duration = 1
    volume = 100
    program =  11 # Represents the instrument, full mapping here: https://www.ccarh.org/courses/253/handout/gminstruments/
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


track = 0
for seq in [query_seq, subject_seq]:
    midi_file.addTrackName(track, time, f"track_{track}")
    midi_file.addTempo(track, time, tempo)
    build_track(seq, track)
    track += 1
    print(f"track_{track}", seq)

# track = 0  # Track indexing starts at 0
# midi_file.addTrackName(track, time, "query_seq_track")
# midi_file.addTempo(track, time, tempo)
# build_track(query_seq, track)

# track = 1
# midi_file.addTrackName(track, time, "subject_seq_track")
# midi_file.addTempo(track, time, tempo)
# build_track(subject_seq, track)



with open("temp/output_file.mid", "wb") as outfile:
    midi_file.writeFile(outfile)

pygame.mixer.music.load("temp/output_file.mid")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.delay(100)