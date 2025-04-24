## Intro
Hot Signals is a rating system based on how urgent & maintenance is needed on provided imagery of a cell tower.

It was first created from Verizon's WeHack25 Prompt on cell tower detection. 

## How to Run (Or How I Run It)

I do not include my API keys. Please make your own .env in the project folder. Name the Gemini key 'GEM_API_KEY'.

    Download the repository.
    Traverse to the project folder.
    Run venv and the install the dependant libraries if needed.
    Do "make run" in the terminal and select "http://127.0...".

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