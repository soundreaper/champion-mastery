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

# Recieves Summoner Username as a query and builds API URL and then sends back information recieved from Riot Games
@app.route('/')
def index():
    """Return homepage."""
    # Extract Summoner Name query from url
    summonerName = request.args.get('query')
    region = 'na'
    #request.args.get('region')

    #Checks to see if Summoner Name has a space in it and replaces with "%20" so API URL can be Built Properly
    if summonerName != "":
        for check in summonerName:
            if (check.isspace()) == True:
                whiteSpace_fix = summonerName.split(" ")
                summonerName = whiteSpace_fix[0] + "%20" + whiteSpace_fix[1]

        # Make parameter dictionary with Region, Summoner Name, and API Key
        params = {
            "region": region,
            "summonerName": summonerName,
            "APIKey": RG_API_KEY
        }

        # Make an API call to Riot Games using the 'requests' library to parse information into JSON dictionaries
        responseJSON_1 = requests.get("https://" + params.get("region") + "1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + params.get("summonerName") + "?api_key=" + params.get("APIKey")).json()
        summonerID = str(responseJSON_1["id"])

        responseJSON_2 = requests.get("https://" + params.get("region") + "1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerID + "?api_key=" + params.get("APIKey")).json()
        responseJSON_3 = requests.get("https://" + params.get("region") + "1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summonerID + "?api_key=" + params.get("APIKey")).json()

        if responseJSON_2[0]["queueType"] == "RANKED_SOLO_5x5":
            infoNum = 0
        else:
            infoNum = 1

        summoner_name = responseJSON_2[infoNum]["summonerName"]
        level =  str(responseJSON_1['summonerLevel'])
        queue_type = "Ranked Solo/Duo"

        tier = responseJSON_2[infoNum]["tier"].lower().capitalize()
        rank = responseJSON_2[infoNum]["rank"]
        league_points = str(responseJSON_2[infoNum]["leaguePoints"])
        
        wins = str(responseJSON_2[infoNum]["wins"])
        losses = str(responseJSON_2[infoNum]["losses"])

        winrate_dec = responseJSON_2[infoNum]["wins"]/(responseJSON_2[infoNum]["wins"] + responseJSON_2[infoNum]["losses"])
        winrate = str(round(winrate_dec * 100, 2))

        champID = responseJSON_3[0]["championId"]
        champion_name = identifyChampion(champID)
        mastery_level = str(responseJSON_3[0]["championLevel"])
        mastery_points = str(responseJSON_3[0]["championPoints"])
        
        # Render the 'index.html' template, passing all parsed parameters
        return render_template("index.html", summoner_name=summoner_name, level=level, queue_type=queue_type,
            tier=tier, rank=rank, league_points=league_points, wins=wins, losses=losses, winrate=winrate,
            champion_name=champion_name, mastery_level=mastery_level, mastery_points=mastery_points)
    else:
        return render_template("index.html")