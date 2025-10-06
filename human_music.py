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
    n_fade = 3 * int(fade_time * SAMPLE_RATE)
    t_in = np.arange(n_fade) / SAMPLE_RATE - 0.5 * fade_time
    fade_in = sigmoid(t_in, 0, 1, fade_time)
    wave[:n_fade] *= fade_in
    # plt.subplot(211)
    # plt.plot(wave)
    # plt.subplot(212)
    # plt.plot(new_wave)
    # plt.show()
    return wave


class Note:
    duration: float

    def play(self) -> np.ndarray:
        t = np.linspace(
            0, self.duration, int(SAMPLE_RATE * self.duration), endpoint=False
        )
        jitter = np.random.uniform(low=0, high=0.001)
        samples = self.generate(t + jitter)
        return apply_fade_in(samples)

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
    def __init__(self, f_init: float, f_final: float, duration: float) -> None:
        self.f_init = f_init
        self.f_final = f_final
        self.duration = duration

    def generate(self, t: np.ndarray) -> np.ndarray:
        freq = sigmoid(t, self.f_init, self.f_final, 0.05)

        amp = np.exp(-2 * t)
        return amp * np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)


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


def generate_music():
    notes = np.array([[0, 1, 0, -1] for _ in range(10)]).flatten()
    total_duration = len(notes) + 2
    samples = np.zeros(total_duration * SAMPLE_RATE)
    # duration = 1.5
    # for i, note in enumerate(notes):
    #     if note == -1:
    #         continue
    #     frequency = (261.6 * 2) * (2 ** (note / 12))
    #     sine = 0.1 * Stringed(duration, frequency).play()
    #     start_time = i * 0.5
    #     start_idx = int(start_time * SAMPLE_RATE)
    #     end_idx = start_idx + len(sine)
    #     if end_idx >= len(samples):
    #         break
    #     samples[start_idx:end_idx] += sine

    the_beat = np.zeros(len(samples))
    beat = [0, 0.8, 1, 1.8, 2, 3]
    # beat = [0, 1, 2, 3]
    # beat = [0, 1, 2]
    for j in range(1000):
        i = j % len(beat)
        num_bars = j // len(beat)
        if i < len(beat) - 1:
            drum = BassDrum(f_init=200, f_final=40, duration=2).play()
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


def save(samples, output_file):
    if samples.dtype != np.int16:
        samples = (samples / samples.max() * (2**15 - 1)).astype(np.int16)
    with wave.open(output_file, "w") as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes for int16
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(samples.tobytes())


def plot_spectrogram(samples: np.ndarray) -> None:
    nperseg = int(0.5 * SAMPLE_RATE)
    f, t, Sxx = spectrogram(samples, nperseg=nperseg, fs=SAMPLE_RATE)
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [sec]")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a 2-second 440Hz sine wave.")
    parser.add_argument("--output_file", help="Output WAV file name", required=False)
    args = parser.parse_args()
    samples = generate_music()
    # plot_spectrogram(samples)
    samples = Stringed(duration=1, frequency=440).play()
    samples = BassDrum(f_final=40, f_init=100, duration=0.6).play()
    if args.output_file is None:
        output_file = NamedTemporaryFile(delete=False).name
    else:
        output_file: str = args.output_file
    save(samples, output_file)
    try:
        subprocess.call(["afplay", output_file])
    except KeyboardInterrupt:
        pass
