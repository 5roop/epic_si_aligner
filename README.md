# EPIC-SI pipeline

This pipeline does the following:
+ Aligns the two camera recordings automatically in time
+ Finds out which camera has RODE mics
+ Joins the two videos side by side
+ Extracts audio
+ Compiles a barren EXB for the annotators to populate, with linked audio, video, and adjacent annotation schema

## Data structure


```
data
├── final            -> output of the pipeline
│   ├── EP001
│   │   ├── EP001.MP4
│   │   ├── EP001.exb
│   │   ├── EP001.wav
│   │   └── annotation_schema.xml
│   └── EP002
│       ├── EP002.MP4
│       ├── EP002.exb
│       ├── EP002.wav
│       └── annotation_schema.xml
├── input            -> input data
│   ├── EP001        -> recording 1
│   │   ├── CAM1     -> camera 1
│   │   │   └── 1.MP4
│   │   └── CAM2     -> camera 2
│   │       └── 2.MP4
│   └── EP002
│       ├── CAM1
│       │   └── 1.MP4
│       └── CAM2
│           └── 2.MP4
└── templates        -> frozen, don't alter
    ├── annotation_schema.xml
    └── template.exb
```
## Running the pipeline

Install [pixi](https://pixi.prefix.dev/latest/installation/) by runnign `curl -fsSL https://pixi.sh/install.sh | sh`. Then the pipeline can be run as with `pixi run run`.