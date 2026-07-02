from scipy import signal
from loguru import logger as đ
from pathlib import Path
from exbee import EXB
from lxml import etree
import datetime
from collections import namedtuple
from subprocess import run
from shutil import copy

try:
    audiopath = snakemake.input.audio
    videopath = snakemake.input.video
    template = snakemake.input.template
    inschema = snakemake.input.schema
    outexb = snakemake.output.exb
    outschema = snakemake.output.schema

except NameError:
    đ.warning("Running outside snakemake!")
    audiopath = "data/final/EP002/EP002.wav"
    videopath = "data/final/EP002/EP002.MP4"
    template = "data/templates/template.exb"
    inschema = "data/templates/annotation_schema.xml"
    outexb = "data/final/EP002/EP002.exb"
    outschema = "data/final/EP002/annotation_schema.xml"

name = Path(audiopath).with_suffix("").name

doc = EXB(template)
đ.info("Fixing referenced files, transcription name, and comments.")
for i in doc.doc.findall(".//meta-information/referenced-file"):
    i.getparent().remove(i)
for j in [audiopath, videopath]:
    newelem = etree.Element("referenced-file", url=Path(j).name)
    doc.doc.find(".//meta-information/transcription-name").addnext(newelem)
comment = doc.doc.find(".//meta-information/comment")
comment.text = f"PR, {datetime.datetime.isoformat(datetime.datetime.now())}: Initial EXB compilation: prep tiers for annotators."
đ.info("Preparing speaker table.")


Speaker = namedtuple("Speaker", ["id", "abbrev", "gender"])
table = [
    Speaker("SPK0", name[0:2] + "01" + name[2:], "x"),
    Speaker("SPK1", name[0:2] + "02" + name[2:], "m"),
    Speaker("SPK2", name[0:2] + "03" + name[2:], "f"),
]
for i in doc.doc.findall(".//speakertable/speaker"):
    i.getparent().remove(i)
for i in table:
    newelem = etree.Element("speaker", id=i.id)
    abbrev = etree.SubElement(newelem, "abbreviation")
    abbrev.text = i.abbrev

    sex = etree.SubElement(newelem, "sex", value=i.gender)
    etree.SubElement(newelem, "languages-used")
    etree.SubElement(newelem, "l1")
    etree.SubElement(newelem, "l2")
    ud_speaker_info = etree.SubElement(newelem, "ud-speaker-information")
    comment = etree.SubElement(newelem, "comment")
    doc.doc.find(".//speakertable").append(newelem)

đ.info("Preparing timeline")
duration = str(float(run(["soxi", "-D", audiopath], capture_output=True).stdout))
for tli in doc.doc.findall(".//tli"):
    tli.getparent().remove(tli)
ct = doc.doc.find(".//common-timeline")
tli = etree.SubElement(ct, "tli")
tli.set("id", "T0")
tli.set("time", "0.0")
tli = etree.SubElement(ct, "tli")
tli.set("id", "T1")
tli.set("time", duration)


đ.info("Preparing tiers")
for tier in doc.doc.findall(".//tier"):
    tier.getparent().remove(tier)
tier_counter = 0
for speaker in table:
    for cat, type in [("v", "t"), ("g", "d"), ("nv", "d"), ("st", "a")]:
        tier = etree.Element(
            "tier", id=f"TIE{tier_counter}", speaker=speaker.id, category=cat, type=type
        )
        tier.set("display-name", f"{speaker.abbrev} [{cat}]")
        tier_counter += 1
        doc.doc.find(".//basic-body").append(tier)
for cat, type in [("a", "d"), ("c", "d")]:
    tier = etree.Element("tier", id=f"TIE{tier_counter}", category=cat, type=type)
    tier.set("display-name", f"[{cat}]")
    tier_counter += 1
    doc.doc.find(".//basic-body").append(tier)

doc.save(outexb)


đ.info("EXB generation completed. Copying annotation schema.")
copy(inschema, outschema)
đ.info("All done.")
2 + 2
