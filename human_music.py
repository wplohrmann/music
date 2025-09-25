import numpy as np
import matplotlib.pyplot as plt
import wave
import argparse

sample_rate = 44100  # Samples per second

def generate_sine(frequency):
    duration = 1.0      # seconds
    amplitude = 32767 / 2

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    t0 = 0.15
    envelope = np.exp(-t / t0)
    samples = amplitude * np.sin(2 * np.pi * frequency * t) * envelope
    samples = samples.astype(np.int16)
    return samples

def generate_music():
    notes = np.array([[0, 1, 0, -1] for _ in range(10)]).flatten()
    total_duration = len(notes) + 2
    samples = np.zeros(total_duration * sample_rate, dtype=np.int16)
    t = np.linspace(0, total_duration, int(sample_rate * total_duration), endpoint=False)
    for i, note in enumerate(notes):
        if note == -1:
            continue
        frequency = (261.6 * 2) * (2 ** (note / 6))
        sine = generate_sine(frequency)
        start_idx = int(i * sample_rate * 0.5)
        end_idx = start_idx + len(sine)
        samples[start_idx:end_idx] = sine
    return samples


def save(samples, output_file):
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes for int16
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a 2-second 440Hz sine wave.")
    parser.add_argument('output_file', help='Output WAV file name')
    args = parser.parse_args()
    samples = generate_music()
    # samples = generate_sine(440)
    save(samples, args.output_file)
