"""RUN with pixi run commands:

    [tasks]
    run = "snakemake -j 1 --rerun-incomplete"
    dry = "snakemake -j 1 -n"
    rulegraph = "snakemake --rulegraph | dot -Tpdf > rulegraph.pdf"
    dag = "snakemake --dag | dot -Tpdf > dag.pdf"
    clean = "rm -rf .pixi .snakemake data/final/"

for instance:
pixi run run

"""


def temp(x):
    return x


rule extract_audio:
    input:
        "data/input/{what}/CAM{num}/{num}.MP4",
    output:
        mono_lowres=temp("data/interim/{what}/{num}.mono.wav"),
        stereo_midres=temp("data/interim/{what}/{num}.stereo.wav"),
    shell:
        """
        ffmpeg -loglevel error -stats -i {input} -ac 2 -ar 16000 -y {output.stereo_midres} &
        ffmpeg -loglevel error -stats -i {input} -ac 1 -ar 2000 -y {output.mono_lowres} &
        wait
        """


rule find_delay:
    input:
        wav1="data/interim/{what}/1.mono.wav",
        wav2="data/interim/{what}/2.mono.wav",
    output:
        temp("data/interim/{what}/synch.txt"),
    script:
        "scripts/find_delay.py"


rule find_rode:
    input:
        m1="data/interim/{what}/1.stereo.wav",
        m2="data/interim/{what}/2.stereo.wav",
        synch="data/interim/{what}/synch.txt",
    output:
        temp("data/interim/{what}/rode.txt"),
    script:
        "scripts/find_rode.py"


rule join_videos:
    input:
        video1="data/input/{what}/CAM1/1.MP4",
        video2="data/input/{what}/CAM2/2.MP4",
        synch=rules.find_delay.output[0],
        rode=rules.find_rode.output[0],
    output:
        video="data/interim/{what}/{what}.full_res.MP4",
    script:
        "scripts/join_videos.py"


rule shrink_video:
    input:
        rules.join_videos.output.video,
    output:
        video="data/interim/{what}/{what}.mid_res.MP4",
    shell:
        """
        ffmpeg -i {input} -vf "scale=1080:-2" {output}
        """


rule get_audio_from_video:
    input:
        rules.join_videos.output[0],
    output:
        "data/interim/{what}/{what}.wav",
    shell:
        "ffmpeg -loglevel error -stats -i {input} -y {output}"


rule do_vad:
    input:
        audio=rules.get_audio_from_video.output[0],
    output:
        timestamps=temp("data/interim/{what}/{what}.timestamps.npy"),
    script:
        "scripts/do_vad.py"


rule make_exb:
    input:
        audio=rules.get_audio_from_video.output[0],
        video=rules.shrink_video.output.video,
        timestamps=rules.do_vad.output.timestamps,
        template="data/templates/template.exb",
        schema="data/templates/annotation_schema.xml",
    output:
        exb="data/interim/{what}/{what}.exb",
        schema="data/interim/{what}/annotation_schema.xml",
    script:
        "scripts/make_exb.py"


rule copy_files_from_interim_to_final:
    input:
        exb_in=rules.make_exb.output.exb,
        schema_in=rules.make_exb.output.schema,
        midres_video_in=rules.shrink_video.output[0],
        fulres_video_in=rules.join_videos.output.video,
        wav_in=rules.get_audio_from_video.output[0],
    output:
        exb_out="data/final_for_annotation/{what}/{what}.exb",
        schema_out="data/final_for_annotation/{what}/annotation_schema.xml",
        midres_video_out="data/final_for_annotation/{what}/{what}.MP4",
        fulres_video_out="data/final_for_defacing/{what}/{what}.MP4",
        wav_out="data/final_for_annotation/{what}/{what}.wav",
    shell:
        """
        cp {input.exb_in} {output.exb_out}
        cp {input.schema_in} {output.schema_out}
        cp {input.midres_video_in} {output.midres_video_out}
        cp {input.wav_in} {output.wav_out}
        cp {input.exb_in} {output.exb_out}
        """


rule gather:
    default_target: True
    input:
        expand(
            "data/final_for_annotation/{recording}/{recording}.{what}",
            recording=["EP001", "EP002", "EP003"],
            what=[
                "wav",
                "MP4",
                "exb",
            ],
        )
        + expand(
            "data/final_for_annotation/{recording}/annotation_schema.xml",
            recording=["EP001", "EP002", "EP003"],
        )
        + expand(
            "data/final_for_defacing/{recording}/{recording}.{what}",
            recording=["EP001", "EP002", "EP003"],
            what=[
                "MP4",
            ],
        ),
