try:
    wav1 = snakemake.input.wav1
    wav2 = snakemake.input.wav2
    outpath = snakemake.output[0]
except NameError:
    wav1 = "data/wavs/PILOT/CAM1/1.wav"
    wav2 = "data/wavs/PILOT/CAM2/2.wav"
    outpath = "brisi.MP4"

from pathlib import Path
from scipy import signal
import soundfile as sf
import numpy as np
from loguru import logger as đ

sig1, sr1 = sf.read(wav1)
sig2, sr2 = sf.read(wav2)

assert sr1 == sr2, "samplerates should match!"


corr = signal.correlate(sig2, sig1, mode="same", method="fft")
delay = np.argmax(np.abs(corr)) - len(sig1) // 2
đ.info(f"Delay: {delay} samples ({delay / sr1:.4f} seconds)")
delay_s = delay / sr1
Path(outpath).write_text(f"{delay_s:.4f}")

2 + 2
