from flask import Flask, jsonify, send_from_directory, request, render_template
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
#import sqlite3
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2


env = Environment(
    loader=FileSystemLoader(["./website"]),
    autoescape=select_autoescape()
)

app = Flask(__name__, template_folder="./website")

@app.route("/")
@app.route("/home")
def homePage():
    template = env.get_template("home.html")
    return template.render()


PHOTOS_FOLDER = os.path.join(os.path.dirname(__file__), 'static/photos')
@app.route('/upload')
def uploadPage():
    template = env.get_template("upload.html")
    return template.render()

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

                    for idx, t in enumerate(times):
                        frame = clip.get_frame(t)
                        img = Image.fromarray(np.uint8(frame))
                        screenshot_name = f"SS{idx + 1}.jpg"
                        img.save(os.path.join(newFolderPath, screenshot_name))
                        print(f"Saved screenshot: {screenshot_name} to {newFolderPath}")
                    
                    clip.reader.close()
                except Exception as e:
                    return f"Error processing video file: {e}"

    return f"Successfully uploaded to the server."


@app.route('/gallery')
def galleryPage():
    photo_root = os.path.join('static', 'photos')
    folders = [f for f in os.listdir(photo_root) if f.isdigit()]

    towers = []

    for folder in folders:
        folder_path = os.path.join(photo_root, folder)
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            towers.append({
                'id': folder,
                'thumbnail': f"photos/{folder}/{images[0]}",  
                'images': images  
            })

    return render_template('gallery.html', towers=towers)

'''
@app.route('/profile.html/<int:profile_id>')
def profilePage(profile_id):
    template = env.get_template("profile.html")
    return template.render(profile_id=profile_id)


def get_profile_pictures(profile_id):

    mypath = f"./static/photos/{profile_id}"
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]



@app.route('/profiles/<int:profile_id>')
def profile(profile_id):
    photos = get_profile_pictures(profile_id)
    tower_id = profile_id
    context = {
        "tower": {
            "id": tower_id,
            "images": photos
        }
    }
    template = env.get_template("profile.html")
    return template.render(context)
'''

@app.route('/static/photos/<path:filename>')
def send_photo(filename):
    return send_from_directory(PHOTOS_FOLDER, filename)




if __name__ == '__main__':
    # init_db()
    app.run(debug=True)