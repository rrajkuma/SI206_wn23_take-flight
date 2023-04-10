from bs4 import BeautifulSoup
import requests
import sqlite3
import json

#variables to store the keys for the APIs
aerobox_params = {
	"X-RapidAPI-Key": "6d6bcf99aamsh46a794dad762262p1c7fb9jsn368b4c5aec31",
	"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

aviation_params = {'access_key': '4916bf37e9a67451871a02a2b8e26113'}

#grabs information using a url and one of the API keys above
def get_API_info(url, params):
    response = requests.get(url, params)
    data = response.text
    res_dict = json.loads(data)
    return res_dict