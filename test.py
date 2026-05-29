import numpy as np
import sound_mappings as sound_mappings
import sys

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


freq = 44100
pygame.mixer.init(frequency=freq, size=-16, channels=1)


seq = sys.argv[1] if len(sys.argv) > 1 else input("Sequence: ")

seq_1 = []

for s in seq:
    s = s.upper()
    if s in sound_mappings.bases:
        t = np.linspace(start=0, stop=0.15, num=int(freq * 0.15), endpoint=False)
        tone = (np.sin(2 * np.pi * sound_mappings.bases[s] * t) * 8000).astype(np.int16)
        seq_1.append(tone)
        seq_1.append(np.zeros(500, dtype=np.int16))
    else:
        print(f"Looks like you have an invalid character in your sequence > {s}")
        exit(1)


samples = np.concatenate(seq_1)
sound = pygame.sndarray.make_sound(samples)
sound.play()
pygame.time.wait(int(sound.get_length() * 1000))

print(len(samples))