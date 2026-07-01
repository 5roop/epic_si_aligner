

# recordings = [
#     {"name": "PILOT",
#     "cam1": "data/input/PILOT/CAM1/1.MP4",
#     "cam1": "data/input/PILOT/CAM2/2.MP4",
#     }
# ]


rule extract_audio:
    input: "data/input/{what}/CAM{num}/{num}.MP4"
    output:
        mono_lowres = "data/final/{what}/{num}.mono.wav",
        stereo_midres = "data/final/{what}/{num}.stereo.wav",
    shell: """
    ffmpeg -loglevel error -stats -i {input} -ac 2 -ar 16000 -y {output.stereo_midres} &
    ffmpeg -loglevel error -stats -i {input} -ac 1 -ar 2000 -y {output.mono_lowres} &
    wait
    """

rule find_delay:
    input:
        wav1 = "data/final/{what}/1.mono.wav",
        wav2 = "data/final/{what}/2.mono.wav",
    output: "data/final/{what}/synch.txt"
    script: "scripts/find_delay.py"


rule find_rode:
    input:
        m1 = "data/final/{what}/1.stereo.wav",
        m2 = "data/final/{what}/2.stereo.wav",
        synch = "data/final/{what}/synch.txt"
    output:
        "data/final/{what}/rode.txt"
    script:
        "scripts/find_rode.py"

rule join_videos:
    input:
        video1 = "data/input/{what}/CAM1/1.MP4",
        video2 = "data/input/{what}/CAM2/2.MP4",
        synch = rules.find_delay.output[0],
        rode  = "data/final/{what}/rode.txt"
    output:
        video = "data/final/{what}/video.MP4"
    script: "scripts/join_videos.py"

rule get_audio_from_video:
    input: "data/final/{what}/video.MP4"
    output: "data/final/{what}/audio.wav"
    shell: "ffmpeg -loglevel error -stats -i {input} -y {output}"



rule gather:
    default_target: True,
    input: expand("data/final/{what}/video.MP4", what = ["PILOT", "TOLIP"]), expand("data/final/{what}/audio.wav", what = ["PILOT", "TOLIP"]),
