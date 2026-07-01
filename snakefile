# def temp(x):
#     return x

rule extract_audio:
    input: "data/input/{what}/CAM{num}/{num}.MP4"
    output:
        mono_lowres = temp("data/final/{what}/{num}.mono.wav"),
        stereo_midres = temp("data/final/{what}/{num}.stereo.wav"),
    shell: """
    ffmpeg -loglevel error -stats -i {input} -ac 2 -ar 16000 -y {output.stereo_midres} &
    ffmpeg -loglevel error -stats -i {input} -ac 1 -ar 2000 -y {output.mono_lowres} &
    wait
    """

rule find_delay:
    input:
        wav1 = "data/final/{what}/1.mono.wav",
        wav2 = "data/final/{what}/2.mono.wav",
    output: temp("data/final/{what}/synch.txt")
    script: "scripts/find_delay.py"


rule find_rode:
    input:
        m1 = "data/final/{what}/1.stereo.wav",
        m2 = "data/final/{what}/2.stereo.wav",
        synch = "data/final/{what}/synch.txt"
    output:
        temp("data/final/{what}/rode.txt")
    script:
        "scripts/find_rode.py"

rule join_videos:
    input:
        video1 = "data/input/{what}/CAM1/1.MP4",
        video2 = "data/input/{what}/CAM2/2.MP4",
        synch = rules.find_delay.output[0],
        rode  = rules.find_rode.output[0]
    output:
        video = "data/final/{what}/{what}.MP4"
    script: "scripts/join_videos.py"

rule get_audio_from_video:
    input: rules.join_videos.output[0]
    output: "data/final/{what}/{what}.wav"
    shell: "ffmpeg -loglevel error -stats -i {input} -y {output}"

rule make_exb:
    input:
        audio = rules.get_audio_from_video.output[0],
        video = rules.join_videos.output.video,
        template = "data/templates/template.exb",
        schema = "data/templates/annotation_schema.xml"
    output:
        exb = "data/final/{what}/{what}.exb",
        schema = "data/final/{what}/annotation_schema.xml",
    script: "scripts/make_exb.py"


rule gather:
    default_target: True,
    input: expand("data/final/{recording}/{recording}.{what}", recording = ["EP001", "EP002"], what=["wav", "MP4", "exb"])
