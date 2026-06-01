from sound_mappings import codons, base_map

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