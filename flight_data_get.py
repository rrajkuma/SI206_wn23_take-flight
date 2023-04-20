import requests
import sqlite3
import json
import os

#variables to store the keys for the APIs
aerobox_params = {
    'X-RapidAPI-Key': 'e172162659msh3c9b2ce1528b672p116317jsna0362bb1f951',
    'X-RapidAPI-Host': 'aerodatabox.p.rapidapi.com'
  }

#variables to store the urls for the APIs
#this url will answer 'How many daily flights to different destinations from an airport?'
#and "What are the most popular routes from an airport?"
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
    cur.execute("CREATE TABLE IF NOT EXISTS airports (air_id INTEGER PRIMARY KEY, iata TEXT UNIQUE, name TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS carrier (plane_id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS routes (id INTEGER PRIMARY KEY, source_id INTEGER, dest_id INTEGER, num_flights INTEGER, carrier_id INTEGER)")
    #these are the airports from the IATA list in main, so it makes sense to hardcode them here
    cur.execute("INSERT OR IGNORE INTO airports (iata, name) VALUES (?, ?)", ("DTW", "Detroit Metropolitan Wayne County, Detroit"))
    cur.execute("INSERT OR IGNORE INTO airports (iata, name) VALUES (?, ?)", ("PHX", "Phoenix Sky Harbor, Phoenix"))
    cur.execute("INSERT OR IGNORE INTO airports (iata, name) VALUES (?, ?)", ("ATL", "Hartsfield Jackson Atlanta, Atlanta"))
    cur.execute("INSERT OR IGNORE INTO airports (iata, name) VALUES (?, ?)", ("SEA", "Seattle Tacoma, Seattle"))
    cur.execute("INSERT OR IGNORE INTO airports (iata, name) VALUES (?, ?)", ("ORD", "Chicago O'Hare, Chicago"))
    conn.commit()
    return cur, conn

#takes in the flight_dict from get_API_info for a given airport, and throws the top 25 results into a separate dictionary
#stores IATA code, name, city, the average number of flights to that airport, and carriers
def aero_data_into_dict(data_dict, start, end):
    temp = {}
    for i in range(start, end):
        blah = {}
        IATA = data_dict["routes"][i]["destination"]["iata"]
        name = data_dict["routes"][i]["destination"]["name"]
        blah["name"] = name
        city = data_dict["routes"][i]["destination"]["municipalityName"]
        blah["city"] = city
        num_flights = data_dict["routes"][i]["averageDailyFlights"]
        blah["num_flights"] = num_flights
        temp_operators = data_dict["routes"][i]["operators"]
        carriers = []
        for i in temp_operators:
            carriers.append(i["name"])
        blah["carriers"] = carriers
        temp[IATA] = blah
    return temp
    
def helper_planes_into_database(plane_list, cur, conn):
    for plane in plane_list:
        query = "SELECT plane_id FROM carrier WHERE name = " + '"' + plane + '"'
        cur.execute(query)
        res = cur.fetchone()
        if res == None:
            print("Inserting new carrier into database: " + plane)
            cur.execute("INSERT OR IGNORE INTO carrier (name) VALUES (?)", (plane,))
    conn.commit()

def aero_dict_into_database(data_dict, port, cur, conn):
    #finds how many results we currently have for this airport in the database
    data = {}
    query = "SELECT COUNT(id) FROM routes JOIN airports ON routes.source_id = airports.air_id WHERE airports.iata = " + '"' + port + '"'
    cur.execute(query)
    #if there currently are results
    res = int(cur.fetchone()[0])
    if res != 0:
        num_res = res
        #to prevent out of range errors
        if num_res + 5 > len(data_dict["routes"]):
            print("Loading the last results for " + port)
            data = aero_data_into_dict(data_dict, num_res-1, len(data_dict))
        else:
            print("Loading the next 5 results for " + port)
            data = aero_data_into_dict(data_dict, num_res-1, num_res+5)
    else:
        print("Loading the first 5 results for " + port)
        data = aero_data_into_dict(data_dict, 0, 5)
    #add items into database
    for item in data:
        #checks whether the destination was in the airport table. if it isn't, it adds it
        dest = item
        query = "SELECT air_id FROM airports WHERE iata = " + '"' + dest + '"'
        cur.execute(query)
        if cur.fetchone() == None:
            print("Inserting new airport into database: " + dest)
            cur.execute("INSERT OR IGNORE INTO airports (iata, name) VALUES (?,?)", (dest, data[item]["name"]))
        conn.commit()
        #checks the carrier list to see if any new carriers should be added. if so, adds them.
        helper_planes_into_database(data[item]["carriers"], cur, conn)
        #actually adds the information into the main table
        source_query = "SELECT air_id FROM airports WHERE iata = " + '"' + port + '"'
        cur.execute(source_query)
        s_id = cur.fetchone()[0]
        dest_query = "SELECT air_id FROM airports WHERE iata = " + '"' + dest + '"'
        cur.execute(dest_query)
        d_id = cur.fetchone()[0]
        #adds route to table
        print("Adding route from " + port + " to " + dest + " into database")
        for plane in data[item]["carriers"]:
            query = "SELECT plane_id FROM carrier WHERE name = " + '"' + plane + '"'
            cur.execute(query)
            c_id = cur.fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO routes (source_id, dest_id, num_flights, carrier_id) VALUES (?,?,?,?)", (s_id, d_id, int(data[item]["num_flights"]), c_id))
    #commits changes
    conn.commit()

    

def main():
    #to trim down data collection, I've created a list of IATA codes to take a look at
    #this way I can place all my data collection in a loop
    #if there's something else of interest, add to the list!
    #IATA_list = ["DTW", "PHX"]
    IATA_list = ["DTW", "PHX", "ATL", "SEA", "ORD"]
    db_name = "flights.db"
    cur, conn = open_database(db_name)
    path = os.path.dirname(os.path.abspath(__file__))
    for port in IATA_list:
        filename = port + "_data.json"
        aero_stat_url = aero_base_1 + port + aero_base_2
        flight_dict = {}
        if(os.path.isfile(path + "/" + filename)):
            print("Reading existing file " + filename)
            with open(filename) as json_file:
                flight_dict = json.load(json_file)
        else:
            print("Grabbing historical flight data for " + port)
            flight_dict = get_API_info(aero_stat_url, aerobox_params)
            with open(filename, "w") as outfile:
                json.dump(flight_dict, outfile)
        print("Opening database " + db_name)
        print("Loading into database")
        aero_dict_into_database(flight_dict, port, cur, conn)
        
    

main()
