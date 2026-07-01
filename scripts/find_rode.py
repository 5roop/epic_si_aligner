import soundfile as sf
import numpy as np
from scipy import signal
from loguru import logger as đ

try:
    m1 = snakemake.input.m1
    m2 = snakemake.input.m2
    synch = "data/final/PILOT/synch.txt"
    out = snakemake.output[0]
except NameError:
    đ.warning("Running outside snakemake")
    m1 = "data/final/PILOT/1.stereo.wav"
    m2 = "data/final/PILOT/2.stereo.wav"
    synch = "data/final/PILOT/synch.txt"
    out = "data/final/PILOT/rode.txt"

from pathlib import Path

synch = float(Path(synch).read_text().strip())

# Load audio files
audio1, sr1 = sf.read(m1)
audio2, sr2 = sf.read(m2)

# Check if sampling rates are the same
assert sr1 == sr2, "Sampling rates of both audios must be the same"

# Trim audio based on synch value
if synch > 0:
    # Trim second file
    audio2 = audio2[int(synch * sr1) :]
else:
    # Trim first file
    audio1 = audio1[int(synch * sr1) :]

minlen = min(audio1.shape[0], audio2.shape[0])
skip_beginning_idx = 2 * 60 * sr1  # Skip first 2 mins
end_after_idx = 5 * 60 * sr1  # Only process this many seconds of data

start_idx = skip_beginning_idx
end_idx = min(minlen, start_idx + end_after_idx)
audio1 = audio1[start_idx:end_idx, :]
audio2 = audio2[start_idx:end_idx, :]


# Calculate envelope for both channels of both audios (simple moving average)
def calculate_envelope(audio, window_size=100):
    b = np.ones(window_size) / window_size
    envelope = np.zeros((audio.shape[0], 2))
    for channel in range(2):
        abs_signal = np.abs(audio[:, channel])
        envelope[:, channel] = signal.lfilter(b, 1.0, abs_signal)
    return envelope


# Calculate envelopes for both audios
envelope1 = calculate_envelope(audio1)
envelope2 = calculate_envelope(audio2)

# Calculate absolute difference between left and right channels for each audio
diff1 = np.abs(envelope1[:, 0] - envelope1[:, 1])
diff2 = np.abs(envelope2[:, 0] - envelope2[:, 1])

# Decide which file has more variation
diff1_var = np.var(diff1)
diff2_var = np.var(diff2)

if diff1_var > diff2_var:
    result = "1"
else:
    result = "2"

đ.info(f"Found RODE mics on camera {result}.")
Path(out).write_text(result)
