try:
    audio = snakemake.input.audio
    outfile = snakemake.output.timestamps
except NameError:
    audio = "/cache/peterr/aligning_videos/data/final/EP001/EP001.wav"
    outfile = "brisi.npy"


from funasr import AutoModel
import numpy as np

# Standalone VAD
model = AutoModel(model="funasr/fsmn-vad", hub="hf", device="cuda")
result = model.generate(input=audio)[0]["value"]
# Returns speech segments: [[start_ms, end_ms], [start_ms, end_ms], ...]
result = np.sort(np.array(result).flatten()) / 1000
np.save(outfile, result)
2 + 2
