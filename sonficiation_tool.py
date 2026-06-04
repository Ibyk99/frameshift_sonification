import os
# Hide the pygame CLI start-up prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from datetime import datetime
from midiutil import MIDIFile
import pygame
from sound_mappings import codons, base_map
from Bio.Blast import NCBIXML


time = 0
tempo = 140

def build_track_nuc(sequence: str, track: int, midi:str, b_map=base_map):
    time = 0
    channel = 0
    duration = 1
    program =  11  # Represents the instrument, full mapping here: https://www.ccarh.org/courses/253/handout/gminstruments/
    midi.addProgramChange(track, channel, time, program)
    for base in sequence:
        volume = 80
        channel = 0
        base = base.upper()
        if base not in b_map and base != '-':
            exit(f"Error: Looks like there's a non-nucleotide character in your sequence: {base}")
        if base == '-':
            channel = 9 # Midi Channel 10 is the reserved channel for percussion instruments, midiutil starts the channel index at 0, hence this is 9 in this case
            pitch = 49  # This is a cymbal clash sound when in channel 9
            volume = 90 # The clash is a little loud and can be startling, so we turn the volume down a little
        else:
            pitch = b_map[base]
        midi.addNote(track, channel, pitch, time, duration, volume)
        time += duration


def build_track_codon(sequence: str, track: int, midi:str, c_map=codons, window_size=3):
    """This option keeps the codon sequence in sync with its respective nucleotide sequence, but causes a desycning of codon seqs after a gap - represents the frameshift better??"""
    channel = 1
    time = 0
    duration = window_size
    volume = 100
    program =  1  # Represents the instrument, full mapping here: https://www.ccarh.org/courses/253/handout/gminstruments/
    midi.addProgramChange(track, channel, time, program)
    codon = [] # Using a list here rather than a string as strings are immutable - very small performance advantage
    for base in sequence:
        base = base.upper()
        # Build up our codon from the bases we're looking at if the base isn't a gap
        if base != '-':  
            if len(codon) == 0:
                codon_start_time = time
            codon.append(base)

            if len(codon) == 3:
                codon_seq = ''.join(codon)  # Concat list to get string of codon
                if c_map[codon_seq]['name'] == "Stop":
                    channel = 9
                    pitch = 39
                else:
                    channel = 1
                    pitch = c_map[codon_seq]['midi']

                midi.addNote(track, channel, pitch, codon_start_time, duration, volume)
                codon = []

        time += 1


if __name__ == "__main__":

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
    print(alignment)


    # Map of Bases - Midi notes (C major scale, mnemonic note names)
    # TODO: Add mapping for N

    # Init a midi file with 2 tracks
    # We don't want to adjust the origin as we may have some leading silences
    midi_file = MIDIFile(2, adjust_origin=False)

    time = 0
    tempo = 140

    # Build both tracks - 1 for query seq and 1 for subject seq
    track = 0
    for seq in [query_seq, subject_seq]:
        midi_file.addTrackName(track, time, f"track_{track}")
        midi_file.addTempo(track, time, tempo)
        build_track_nuc(seq, track, midi_file)
        build_track_codon(seq, track, midi_file)
        print(f"track_{track}", seq)
        track += 1

    # Assign our output file a unique name - if multiple people running this avoids overwriting each others work
    dt = datetime.now()
    out_path = "temp"
    output_file = f"output_file_{dt.strftime('%Y-%m-%d_%H-%M-%S_%f')}"
    out_path_and_file = f"{out_path}/{output_file}.mid"

    with open(out_path_and_file, "wb") as outfile:
        midi_file.writeFile(outfile)

    pygame.mixer.init()
    pygame.mixer.music.load(out_path_and_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.delay(100)

    # Clean up temp file 
    if os.path.exists(out_path_and_file):
        os.remove(out_path_and_file)