from flask import Flask, render_template,request, send_from_directory
import os
import requests
import json
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
RG_API_KEY = os.getenv('RG_API_KEY')

# Loads a file containing all champions and their respective ID numbers
with open('champions.txt') as json_file:
    champion_data = json.load(json_file)

# Reads Champion ID Number and returns the Champion's Name
def identifyChampion(num):
    for x in champion_data:
        if x['id'] == num:
            champ = x['name']
    return champ

# The code below loads the little icon that shows up at the top of the browser next to the website Title.
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')