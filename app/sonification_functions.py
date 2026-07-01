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



def build_track(sequence: str, track: int, midi:str, stop:bool, codons:bool, nucs:bool, b_map=base_map, c_map=codons, window_size=3, codon_inst=1, nuc_inst=11, reading_frame=1):
    time = 0
    stopped = False # Flag to stop the codons from sonifying if a stop codon is hit - start set to false

    gap_volume = 80

    nuc_volume = 60 if codons else 90
    nuc_channel = 0
    nuc_duration = 1
    nuc_program =  nuc_inst  # Represents the instrument, full mapping here: https://www.ccarh.org/courses/253/handout/gminstruments/
    midi.addProgramChange(track, nuc_channel, time, nuc_program)

    codon_volume = 100
    codon_channel = 1
    codon_duration = window_size
    codon_program = codon_inst
    codon_stop_channel = 2
    codon_stop_program = 82
    midi.addProgramChange(track, codon_channel, time, codon_program)
    midi.addProgramChange(track, codon_stop_channel, time, codon_stop_program)

    codon = [] # Using a list here rather than a string as strings are immutable - very small performance advantage
    frame_offset = reading_frame - 1

    for base in sequence[frame_offset:]:
        base = base.upper()
        if stopped:
            break
        # Handle nucleotides
        # Sound for a gap is always played - obvious marker for a frameshift
        if base == '-':
            pitch = 49  # cymbal
            midi.addNote(track, 9, pitch, time, nuc_duration, gap_volume)
        # Add the nucleotides if their inclusion has been selected
        elif nucs:
            pitch = b_map[base]
            midi.addNote(track, nuc_channel, pitch, time, nuc_duration, nuc_volume)

        # Handle codons
        if codons:
            if base != '-': # Ignore gaps as these don't form the actual codon
                # Signify the start point of a new codon - this is the time-point where the note for this codon will be placed.
                if len(codon) == 0:
                    codon_start_time = time
                codon.append(base)
                # When we have a complete codon find what is maps to
                if len(codon) == 3:
                    codon_seq = ''.join(codon)
                    if codon_seq in c_map:
                        if c_map[codon_seq]['name'] == "Stop":
                            codon_channel = 9
                            pitch = 39
                            midi.addNote(track, codon_channel, pitch, codon_start_time, codon_duration, codon_volume)
                            if stop:
                                stopped = True
                        else:
                            codon_channel = 1
                            pitch = c_map[codon_seq]['midi']
                            midi.addNote(track, codon_channel, pitch, codon_start_time, codon_duration, codon_volume)

                    codon = []

        time += 1