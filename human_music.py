import subprocess
import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile
from scipy.signal import spectrogram
import numpy as np

import wave
import argparse

SAMPLE_RATE = 44100  # Samples per second


def sigmoid(t: np.ndarray, start: float, end: float, move_time: float) -> np.ndarray:
    return start + (end - start) * (1 / (1 + np.exp(-t / move_time)))


def apply_fade_in(wave, fade_time=0.01) -> np.ndarray:
    n_fade = int(fade_time * SAMPLE_RATE)
    wave[:n_fade] *= np.linspace(0, 1, n_fade)
    return wave


class Note:
    duration: float

    def play(self) -> np.ndarray:
        t = np.linspace(
            0, self.duration, int(SAMPLE_RATE * self.duration), endpoint=False
        )
        samples = self.generate(t)
        samples = apply_fade_in(samples)
        samples[::-1] = apply_fade_in(samples[::-1])
        return samples

    def generate(self, t: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class Stringed(Note):
    def __init__(
        self, duration: float, frequency: float, num_overtones: int = 5
    ) -> None:
        self.duration = duration
        self.frequency = frequency
        self.num_overtones = num_overtones

    def generate(self, t) -> np.ndarray:
        samples = np.zeros(t.shape)
        for n in range(self.num_overtones):
            samples += np.sin(2 * np.pi * self.frequency * (n + 1) * t)
        return samples


class BassDrum(Note):
    def __init__(
        self,
        amp: float,
        f_init: float,
        f_final: float,
        duration: float,
        f_decay: float = 0.05,
        attack: float = 1 / 3,
    ) -> None:
        self.amp = amp
        self.f_init = f_init
        self.f_final = f_final
        self.f_decay = f_decay
        self.duration = duration
        self.attack = attack

    def generate(self, t: np.ndarray) -> np.ndarray:
        freq = sigmoid(t, self.f_init, self.f_final, self.f_decay)

        envelope = self.amp * np.exp(-t / self.attack)
        return envelope * np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)


BASS_DRUM = BassDrum(
    amp=1,
    f_final=40,
    f_init=100,
    duration=1,
    f_decay=0.1,
    attack=0.2,
).play()

bass = lambda f, a: BassDrum(
    amp=a,
    f_init=f * 1.1,
    f_final=f,
    duration=1,
    f_decay=0.1,
    attack=0.1,
)


class HiHat(Note):
    def __init__(self) -> None:
        self.duration = 0.5

    def generate(self, t) -> np.ndarray:
        freqs = np.array([2000, 3000, 3200, 4100, 5100, 6400])
        partials = [np.sign(np.sin(2 * np.pi * f * t)) for f in freqs]
        hat = np.sum(partials, axis=0)
        hat = hat / np.max(np.abs(hat))

        # Apply fast-decay envelope
        env = np.exp(-30 * t)
        hat *= env
        return hat


def halloween():
    notes = np.array([[0, 1, 0, -1] for _ in range(10)]).flatten()
    total_duration = len(notes) + 2
    samples = np.zeros(total_duration * SAMPLE_RATE)
    duration = 1.5
    for i, note in enumerate(notes):
        if note == -1:
            continue
        frequency = (261.6 * 2) * (2 ** (note / 12))
        sine = 0.1 * Stringed(duration, frequency).play()
        start_time = i * 0.5
        start_idx = int(start_time * SAMPLE_RATE)
        end_idx = start_idx + len(sine)
        if end_idx >= len(samples):
            break
        samples[start_idx:end_idx] += sine

    the_beat = np.zeros(len(samples))
    beat = [0, 0.8, 1, 1.8, 2, 3]
    # beat = [0, 1, 2, 3]
    # beat = [0, 1, 2]
    for j in range(1000):
        i = j % len(beat)
        num_bars = j // len(beat)
        if i < len(beat) - 1:
            drum = BASS_DRUM
        else:
            drum = HiHat().play()
        start_time = 0.5 * (num_bars * 4 + beat[i])
        start_idx = int(start_time * SAMPLE_RATE)
        end_idx = start_idx + len(drum)
        if end_idx >= len(the_beat):
            break
        the_beat[start_idx:end_idx] += drum

    together = samples + the_beat
    samples = (together / together.max() * (2**15 - 1)).astype(np.int16)

    return samples

def bass_line():
    np.random.seed(1)
    scale = np.array([0, 1, 2, 2.5, 3.5, 4.5, 5.5, 6])
    jump_weight = np.array([3, 3, 5, 2, 1, 0, 0, 1])
    assert len(jump_weight) == len(scale)
    diffs = np.abs(np.arange(len(scale))[:, None] - np.arange(len(scale))[None, :])
    unscaled_probs = jump_weight[diffs]
    scaled_probs = unscaled_probs / unscaled_probs.sum(axis=1)[:, None]
    total_duration = 36
    samples = np.zeros(total_duration * SAMPLE_RATE)
    note_index = 0
    num_notes = 100
    start_time = 0
    num_bars = 30
    big = 4
    small = 1
    possible_amps = [
        [big, small, small, big, small, small, big, small],
        [big, small, big, small, small, big, small, small],
        [big, small, small, big, small, big, small, small],
    ]
    eighth = 0.15
    bass_root = 80
    for _ in range(num_bars):
        num_notes = 8
        amps = possible_amps[np.random.randint(len(possible_amps))]
        skip_small = False
        for i in range(num_notes):
            note_f = bass_root * 2**(scale[note_index] / 6)
            note = bass(note_f, amps[i]).play()
            if amps[i] == big and np.random.rand() < 0.1:
                skip_small = True
            start_idx = int(start_time * SAMPLE_RATE)
            end_idx = start_idx + len(note)
            if end_idx >= len(samples):
                break
            if not (amps[i] == small and skip_small):
                samples[start_idx:end_idx] += note
                note_index = np.random.choice(len(scale), p=scaled_probs[note_index])

            # Next note
            start_time += eighth

    note_index =  0
    root = bass_root * 4
    start_time = 0
    for i in range(num_bars):
        np.random.seed({
            0: 0,
            1: 2,
            2: 2,
            3: 3,
            }[i % 4])
        if i % 4 == 0:
            note_index = 0
        for duration in [4, 2, 2]:
            note_f = root * 2**(scale[note_index] / 6)
            note = bass(note_f, 1).play()
            start_idx = int(start_time * SAMPLE_RATE)
            end_idx = start_idx + len(note)
            if end_idx >= len(samples):
                break
            if i >= 4:
                samples[start_idx:end_idx] += 0.2 * note
                note_index = np.random.choice(len(scale), p=scaled_probs[note_index])
            start_time += duration * eighth
    return samples




def scale(samples) -> np.ndarray:
    return (samples / np.abs(samples).max() * (2**15 - 1)).astype(np.int16)


def save(samples, output_file):
    if samples.dtype != np.int16:
        samples = scale(samples)
    # plt.plot(samples)
    # plt.show()
    with wave.open(output_file, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(samples.tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a 2-second 440Hz sine wave.")
    parser.add_argument("--output_file", help="Output WAV file name", required=False)
    args = parser.parse_args()
    # samples = halloween()
    samples=  bass_line()
    # samples = Stringed(duration=1, frequency=440).play()
    # samples = BASS_DRUM
    if args.output_file is None:
        output_file = NamedTemporaryFile(delete=False).name
    else:
        output_file: str = args.output_file
    save(samples, output_file)
    try:
        subprocess.call(["afplay", output_file])
    except KeyboardInterrupt:
        pass
