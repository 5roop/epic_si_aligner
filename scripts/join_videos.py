try:
    video1 = snakemake.input.video1
    video2 = snakemake.input.video2
    synch = snakemake.input.synch
    outpath = snakemake.output.video
    rodepath = snakemake.input.rode
except NameError:
    video1 = "data/input/PILOT/CAM1/1.MP4"
    video2 = "data/input/PILOT/CAM2/2.MP4"
    synch = "data/synch/PILOT/synch.txt"
    outpath = "data/final/PILOT/video.MP4"
    rodepath = "data/final/PILOT/rode.txt"
from pathlib import Path
from subprocess import run
from loguru import logger as đ

delay = float(Path(synch).read_text())
delay_abs = abs(delay)
audio_source = Path(rodepath).read_text().strip()
# Positive delay: video1 is behind video2 → trim start of video2
# Negative delay: video1 is ahead of video2 → trim start of video1
if delay >= 0:
    trimmed = video2  # video2 starts earlier, trim it
    untrimmed = video1
else:
    trimmed = video1  # video1 starts earlier, trim it
    untrimmed = video2

trim_time = delay_abs

Path(outpath).parent.mkdir(exist_ok=True, parents=True)

đ.info(f"Will use camera {audio_source} for sound")
if audio_source == "2":
    if delay < 0:
        audio_filter = "1:a"  # video1 is untrimmed (2nd input)
    else:
        audio_filter = "0:a"  # video1 is untrimmed (1st input)
elif audio_source == "1":
    if delay < 0:
        audio_filter = "0:a"  # video2 is trimmed (1st input)
    else:
        audio_filter = "1:a"  # video2 is trimmed (2nd input)
else:
    raise AttributeError(f"Got illegal audio source: {audio_source}")

run(
    [
        "ffmpeg",
        "-loglevel",
        "error",
        "-stats",
        "-ss",
        str(trim_time),
        "-i",
        trimmed,
        "-i",
        untrimmed,
        # "-t",
        # "60",
        "-filter_complex",
        "[0:v][1:v]hstack=inputs=2,scale=1080:-2,fps=25[v]",
        "-map",
        "[v]",
        "-map",
        audio_filter,
        "-y",
        outpath,
    ],
    check=True,
    capture_output=False,
)
