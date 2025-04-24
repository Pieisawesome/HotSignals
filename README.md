## Intro
Hot Signals is a rating system based on how urgent & maintenance is needed on provided imagery of a cell tower.

It was first created from Verizon's WeHack25 Prompt on cell tower detection. 

## How It's Ran
    Ran locally on my desktop using flask.
    Can upload files through the website.
    Files are then put through 4 different test.
        Rust: Find corrosion on cell tower
        Buildings: Find buildings in background
        Unknown Objects: Find odd or unusual objects on the cell tower
        Antennas: Find antenna and placement
    Using this data, a rating based on maintenance can be calculated. The higher the rating the higher the maintenance.
    On the website, the end results are presented.

## Demo


## Credits

    Rust Corrosion Detection: 
    @misc{
        rush_corrosion_detection_dataset,
        title = { rush_corrosion_detection Dataset },
        type = { Open Source Dataset },
        author = { yolocorrosionrustdetection },
        howpublished = { \url{ https://universe.roboflow.com/yolocorrosionrustdetection/rush_corrosion_detection } },
        url = { https://universe.roboflow.com/yolocorrosionrustdetection/rush_corrosion_detection },
        journal = { Roboflow Universe },
        publisher = { Roboflow },
        year = { 2024 },
        month = { sep },
        note = { visited on 2025-04-23 },
    }

## All Libraries Used 
#### (Or What I Needed to Install / For Reference for Me Later)

    Virtual Enviroment (venv):
        python3 -m venv <nameofvenv>
        source venv/bin/activate
        deactivate (when done)
    Flask              : pip install flask
    Gemini             : pip install google-gemini
    Ultralytics/OpenCV : pip install ultralytics 
    OpenCV             : pip install opencv-python
    Inference          : pip install inference (maybe)