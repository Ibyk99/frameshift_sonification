from midiutil import MIDIFile
import pygame
import sys
from Bio.Seq import Seq


pygame.mixer.init()

# Take inputs
seq = sys.argv[1] if len(sys.argv) > 1 else input("Sequence: ")
seq2 = sys.argv[2] if len(sys.argv) > 1 else input("Sequence: ")

# Map of Bases - Midi notes
base_map = {"A": 9, "T": 5, "G": 7, "C": 12}

# Init a midi file which we can have multiple channels in
midi_file = MIDIFile(2, adjust_origin=False)

track = 0 # Track indexing starts at 0
time = 0
midi_file.addTrackName(track, time, "seq1_track")
midi_file.addTempo(track, time, 120)

midi_file.addTrackName(1, time, "seq1_track")
midi_file.addTempo(1, time, 120)
# midi_file.addProgramChange(0, 0, 0, 102)


track = 0
channel = 0
pitch = 60
time = 0
duration = 1
volume = 100

for base in seq:
    base = base.upper()
    if base in base_map:
        pitch = base_map[base]
        midi_file.addNote(track, channel, pitch, time, duration, volume)
        time += duration
        
time = 0
for base in seq2:
    base = base.upper()
    track = 1
    channel = 1
    if base in base_map:
        pitch = base_map[base]
        midi_file.addNote(track, channel, pitch, time, duration, volume)
        time += duration

with open("temp/output_file.mid", "wb") as outfile:
    midi_file.writeFile(outfile)

pygame.mixer.music.load("temp/output_file.mid")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.delay(100)