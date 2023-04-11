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

#variables to store the urls for the APIs
#this url will answer 'How many daily flights to different destinations from an airport?'
#and "What are the most popular routes from an airport?"
#NOTE: for each airpot of interest, change the IATA code (currently DTW), and rerun the function.
aero_base_1 = "https://aerodatabox.p.rapidapi.com/airports/iata/"
aero_base_2 = "/stats/routes/daily"

#grabs information using a url and one of the API keys above
def get_API_info(url, params):
    response = requests.request("GET", url, headers=params)
    data = response.text
    res_dict = json.loads(data)
    return res_dict

#opens sql connection
def open_database(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return cur, conn

#takes in the flight_dict from get_API_info for a given airport, and throws the top 25 results into a separate dictionary
#stores IATA code, name, city, the average number of flights to that airport, and carriers
def aero_data_into_database(data_dict, IATA):
    temp = {}
    for i in range(0, 24):
        IATA = data_dict["routes"][i]["destination"]["iata"]
        temp["IATA"] = IATA
        name = data_dict["routes"][i]["destination"]["name"]
        temp["name"] = name
        city = data_dict["routes"][i]["destination"]["municipalityName"]
        temp["city"] = city
        num_flights = data_dict["routes"][i]["averageDailyFlights"]
        temp["num_flights"] = num_flights
        temp_operators = data_dict["routes"][i]["operators"]
        carriers = []
        for i in temp_operators:
            carriers.append(i["name"])
        temp["carriers"] = carriers
    return temp
    
def main():
    #to trim down data collection, I've created a list of IATA codes to take a look at
    #this way I can place all my data collection in a loop
    #if there's something else of interest, add to the list!
    IATA_list = ["DTW", "PHX", "LAX", "ATL", "JFK", "SEA", "ORD", "PHL", "CLE", "RNO"]
    data_dict = {}
    for port in IATA_list:
        if port in data_dict:
            continue
        else:
            aero_stat_url = aero_base_1 + port + aero_base_2
            print(aero_stat_url)
            flight_dict = get_API_info(aero_stat_url, aerobox_params)
            data_dict[port] = aero_data_into_database(flight_dict, port)
    print(data_dict)
    
main()
