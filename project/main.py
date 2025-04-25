from flask import Flask, jsonify, send_from_directory, request, render_template
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import sqlite3
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
from inference import get_model

# First of all, dont @ me for putting it all in main, I just like to scroll rather then switch tabs
# Also this is like my first time ever coding a full stack web app, so please be nice to me ;-;

# Flask Setup ----------------------------------------------------------

env = Environment(
    loader=FileSystemLoader(["./website"]),
    autoescape=select_autoescape()
)

app = Flask(__name__, template_folder="./website")

@app.route("/")
@app.route("/home")
def homePage():
    return render_template("home.html")


PHOTOS_FOLDER = os.path.join(os.path.dirname(__file__), 'static/photos')
@app.route('/upload')
def uploadPage():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload():

    os.makedirs(PHOTOS_FOLDER, exist_ok=True)

    # Find current number of folders
    curNumFolders = [int(f) for f in os.listdir(PHOTOS_FOLDER) if f.isdigit()]
    nextFolderNum = max(curNumFolders) + 1 if curNumFolders else 1
    newFolderPath = os.path.join(PHOTOS_FOLDER, str(nextFolderNum))
    os.makedirs(newFolderPath)

    # Get media from request
    files = request.files.getlist("media")
    
    fCount = 1 # For renaming original files
    for file in files:
        if file and file.filename:
            ext = os.path.splitext(file.filename)[1]
            filename = f"OM{fCount}{ext}"
            filepath = os.path.join(newFolderPath, filename)
            file.save(filepath)
            fCount += 1

            # If it's a video, extract 5 frames
            if filename.lower().endswith(('.mp4', '.mov', '.avi', '.webm', '.mkv')):
                try:
                    clip = VideoFileClip(filepath, audio=False)
                    duration = clip.duration
                    times = [duration * i / 6 for i in range(1, 6)]  # 5 evenly spaced times

                    # Iterates until frame needed
                    for idx, t in enumerate(times):
                        frame = clip.get_frame(t)
                        img = Image.fromarray(np.uint8(frame))
                        screenshotName = f"SS{idx + 1}.jpg"
                        img.save(os.path.join(newFolderPath, screenshotName))
                        print(f"Saved screenshot: {screenshotName} to {newFolderPath}")
                    
                    clip.reader.close()
                except Exception as e:
                    return f"Error processing video file: {e}"

    return f"Successfully uploaded to the server. Please give up to a minute for media to be processed. Results will be available in the gallery page. <a href='/gallery'>Go to Gallery</a>"


@app.route('/gallery')
def galleryPage():
    # Get all folders
    photoRoot = os.path.join('static', 'photos')
    folders = [f for f in os.listdir(photoRoot) if f.isdigit()]

    towers = []

    # Loop through each folder and get the first image
    # Puts into tower list
    for folder in folders:
        folder_path = os.path.join(photoRoot, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            towers.append({
                'id': folder,
                'thumbnail': f"photos/{folder}/{images[0]}",  
                'images': images  
            })

    return render_template('gallery.html', towers=towers)

@app.route('/profile/<int:profile_id>')
def profilePage(profile_id):
    # Define the folder path for the given profile ID
    folder_path = os.path.join('static', 'photos', str(profile_id))

    # Check if the folder exists
    if not os.path.exists(folder_path):
        return f"Profile with ID {profile_id} not found.", 404

    # Get all images in the folder
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # TODO: Add database query, once done also return data in render_template()

    # Pass the images and profile ID to the template
    return render_template('profile.html', profile_id=profile_id, images=images)


@app.route('/static/photos/<path:filename>')
def send_photo(filename):
    return send_from_directory(PHOTOS_FOLDER, filename)


# Database Setup ----------------------------------------------------------

# Database connection | Helper Function
def getDB():
    conn = sqlite3.connect('database.sql')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def initDB():
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT CHECK(LENGTH(name) < 50),
            antennaDif BOOLEAN,
            rustLevel INTEGER CHECK(rustLevel IN (0, 1, 2, 3)),
            background INTEGER CHECK(background IN (0, 1, 2, 3)),
            unknownObject INTEGER CHECK(unknownObject IN (0, 1, 2, 3)),
            total INTEGER CHECK(total IN (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
        )
    ''')
    conn.commit()
    conn.close()

# Insert a row into the database
def insertData(name, antennaDif, rustLevel, background, unknownObject):
    total = antennaDif + rustLevel + background + unknownObject
    if total > 10 | total < 0: # Something failed if this is true
        total = -1
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO profiles (name, antennaDif, rustLevel, background, unknownObject, total)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, antennaDif, rustLevel, background, unknownObject, total))
    conn.commit()
    conn.close()

# Get a row from the database
def getData(key):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM profiles WHERE id = ?
    ''', (key,))
    row = cursor.fetchone()
    conn.close()
    return row

# Models ---------------------------------------------------------- TODO

# Yolov8 Model (best.pt)
# Returns value of 0 or 1
def runAntennaDifCheck(images): # images is a list of image paths
    model = YOLO('/detectionModels/best.pt')
    compare = -1

    for imagePath in images:
        # Load
        image = cv2.imread(imagePath)
        
        # Model
        results = model(image)
        
        # Taking out data from model
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])

        # If difference
        if compare == -1:
            compare = cls
        else if compare != cls:
            return 1 # Antenna difference 

    return 0 # No antenna difference
        

# RoboFlow Model: https://universe.roboflow.com/yolocorrosionrustdetection/rush_corrosion_detection
'''
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
note = { visited on 2025-04-25 },
}
'''
# Returns value of 0, 1, 2, or 3
def runRustLevelCheck(images):


# My RoboFlow Model: https://app.roboflow.com/workflows/embed/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3JrZmxvd0lkIjoiakY3MzJzeDdoWVFFVWw1UkIwU1giLCJ3b3Jrc3BhY2VJZCI6IjhXYmhKNk1YSHhWV0JWeFhvTXMxWGhWZFJ0RjMiLCJ1c2VySWQiOiI4V2JoSjZNWEh4VldCVnhYb01zMVhoVmRSdEYzIiwiaWF0IjoxNzQ1NTU3NDM2fQ.fN8nf7k95s5uGj3H6EEcFkgozKRA-DgRtz-SqBIpJGI
# Returns value of 0, 1, 2, or 3
def runBackgroundCheck(images):


# Gemini 2.0 Flask 
# I was having trouble making my own model in detecting 'unfamiliar objects'
# So I used Gemini which probably has a better understanding of what should and shouldn't be on a cell tower
# Returns value of 0, 1, 2, or 3
def runUnknownObjectCheck(images):



# Run/Test -----------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)