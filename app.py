from flask import Flask, render_template,request, send_from_directory
import os
import requests
import json

app = Flask(__name__)

"""
Loads API key from Heroku configuration variables (confirgured on Heroku dashboard)
"""
RG_API_KEY = os.getenv('RG_API_KEY')

"""
Loads a file containing all champions and their respective ID numbers
"""
with open('champions.txt') as json_file:
    champion_data = json.load(json_file)

"""
Function that reads Champion ID Number and returns the Champion's Name
"""
def identifyChampion(num):
    for x in champion_data:
        if x['id'] == num:
            champ = x['name']
    return champ

"""
The code below loads the little icon that shows up at the top of the browser next to the website Title.
"""
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Recieves Summoner Username as a query and builds API URL and then sends back information recieved from Riot Games
@app.route('/')
def index():
    """Return homepage."""
    """
    Extract Summoner Name query from url
    """
    summonerName = request.args.get('query')
    
    """
    For now the default region is North America and the app only works for NA, will be expanded to include all regions
    """
    region = 'na'
    #request.args.get('region')

    """
    Checks to see if Summoner Name has a space in it and replaces with "%20" so API URL can be Built Properly
    """
    if summonerName != "" and summonerName is not None:
        for check in summonerName:
            if (check.isspace()) == True:
                whiteSpace_fix = summonerName.split(" ")
                summonerName = whiteSpace_fix[0] + "%20" + whiteSpace_fix[1]

        """
        Make parameter dictionary with Region, Summoner Name, and API Key
        """
        params = {
            "region": region,
            "summonerName": summonerName,
            "APIKey": RG_API_KEY
        }

        # Make an API call to Riot Games using the 'requests' library to parse information into JSON dictionaries
        responseJSON_1 = requests.get("https://" + params.get("region") + "1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + params.get("summonerName") + "?api_key=" + params.get("APIKey")).json()
        summonerID = str(responseJSON_1["id"])

        responseJSON_2 = requests.get("https://" + params.get("region") + "1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerID + "?api_key=" + params.get("APIKey")).json()

        print(responseJSON_2)
        responseJSON_3 = requests.get("https://" + params.get("region") + "1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summonerID + "?api_key=" + params.get("APIKey")).json()

        """
        if responseJSON_2[0]["queueType"] == "RANKED_SOLO_5x5":
            infoNum = 0
        elif responseJSON_2[0]["queueType"] == "RANKED_SOLO_5x5":
            infoNum = 1
        else:
            infoNum = 2
        """

        summoner_name = responseJSON_2[0]["summonerName"]
        level =  str(responseJSON_1['summonerLevel'])
        queue_type = responseJSON_2[0]["queueType"]

        tier = responseJSON_2[0]["tier"].lower().capitalize()
        rank = responseJSON_2[0]["rank"]

        if tier == 'Iron':
            rank_img = "Iron.png"
        elif tier == 'Silver':
            rank_img = "Silver.png"
        elif tier == 'Gold':
            rank_img = "Gold.png"
        elif tier == 'Platinum':
            rank_img = "Platinum.png"
        elif tier == 'Diamond':
            rank_img = "Diamond.png"
        elif tier == 'Master':
            rank_img = "Master.png"
        elif tier == 'Grandmaster':
            rank_img = "Grandmaster.png"
        elif tier == 'Challenger':
            rank_img = "Challenger.png"

        league_points = str(responseJSON_2[0]["leaguePoints"])
        
        wins = str(responseJSON_2[0]["wins"])
        losses = str(responseJSON_2[0]["losses"])

        winrate_dec = responseJSON_2[0]["wins"]/(responseJSON_2[0]["wins"] + responseJSON_2[0]["losses"])
        winrate = str(round(winrate_dec * 100, 2))

        champID = [responseJSON_3[0]["championId"], responseJSON_3[1]["championId"], responseJSON_3[2]["championId"], responseJSON_3[3]["championId"], responseJSON_3[4]["championId"]]
        champion_name = []
        for ID in champID:
            champion_name.append(identifyChampion(ID))
        
        champion_img = []
        for champ in champion_name:
            champion_img.append(champ + '.png')

        mastery_level = [str(responseJSON_3[0]["championLevel"]), str(responseJSON_3[1]["championLevel"]), str(responseJSON_3[2]["championLevel"]), str(responseJSON_3[3]["championLevel"]), str(responseJSON_3[4]["championLevel"])]
        mastery_img = []
        for mastery in mastery_level:
            mastery_img.append(mastery + '.png')

        mastery_points = [str(responseJSON_3[0]["championPoints"]), str(responseJSON_3[1]["championPoints"]), str(responseJSON_3[2]["championPoints"]), str(responseJSON_3[3]["championPoints"]), str(responseJSON_3[4]["championPoints"])]
        
        # Render the 'index.html' template, passing all parsed parameters
        return render_template("index.html", summoner_name=summoner_name, level=level, queue_type=queue_type,
            tier=tier, rank=rank, rank_img=rank_img, league_points=league_points, wins=wins, losses=losses, winrate=winrate,
            champion_name=champion_name, champion_img=champion_img, mastery_level=mastery_level, 
            mastery_img=mastery_img, mastery_points=mastery_points)
    else:
        return render_template("index.html")