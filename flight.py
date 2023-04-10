#from bs4 import BeautifulSoup
import requests
import sqlite3
import json

#variables to store the keys for the APIs
aerobox_params = {
	"X-RapidAPI-Key": "6d6bcf99aamsh46a794dad762262p1c7fb9jsn368b4c5aec31",
	"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

aviation_params = {'access_key': '4916bf37e9a67451871a02a2b8e26113'}

#variables to store the urls for the APIs
#this url will answer 'How many daily flights to different destinations from an airport?'
#and "What are the most popular routes from an airport?"
#NOTE: for each airpot of interest, change the IATA code (currently DTW), and rerun the function.
aero_stat_url = "https://aerodatabox.p.rapidapi.com/airports/iata/DTW/stats/routes/daily"

#grabs information using a url and one of the API keys above
def get_API_info(url, params):
    response = requests.get(url, params)
    data = response.text
    res_dict = json.loads(data)
    return res_dict

def main():
    get_API_info(aero_stat_url, aerobox_params)

main()
