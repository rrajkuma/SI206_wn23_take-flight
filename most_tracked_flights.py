import requests
import sqlite3
import json
import csv
import os

url = "https://flight-radar1.p.rapidapi.com/flights/list-most-tracked"

header = {
	"X-RapidAPI-Key": "1892ca5890msh839a7ab8c6d638ap1ce3e6jsn9004e032386f",
	"X-RapidAPI-Host": "flight-radar1.p.rapidapi.com"
}

def get_API_info(url, params):

    response = requests.request("GET", url, headers=params)
    data = response.text
    resp_dict = json.loads(data)
    resp_dict = resp_dict['data']
    return resp_dict


def open_database(db_name):

     # Create an SQLite database and establish a connection
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # Create the 'tracked flights' table if it doesn't exist
    cur.execute('''CREATE TABLE IF NOT EXISTS tracked_flights
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 flight_id TEXT,
                 flight TEXT,
                 clicks INTEGER,
                 from_city TEXT,
                 to_city TEXT)''')
    conn.commit()
    return cur, conn


#takes in the dict from get_API_info and puts the top 25 results into a separate dictionary
#stores flight id, flight, clicks, from city and to city

def flight_into_dict(data_dict, start, end):
    
    flight_lst = []

    for flight in data_dict[start:end]:
        flight_id = flight['flight_id']
        flight_name = flight['flight']
        clicks = flight['clicks']
        from_city = flight['from_city']
        to_city = flight['to_city']
        flight_lst = {'flight_id':flight_id,'flight': flight_name, 'clicks': clicks, 'from_city': from_city, 'to_city': to_city}
       
    return flight_lst


def flight_dict_into_database(data_lst, cur, conn):

    for flight in data_lst:
        
        # Check if the flight_id already exists in the database
        cur.execute("SELECT COUNT(*) FROM tracked_flights WHERE flight_id = ?", (flight['flight_id'],))
        
        count = int(cur.fetchone()[0])
       
        if count != 0:
            num_res = count
            #to prevent out of range errors
            if num_res + 5 > len(data_lst):
                data = flight_into_dict(data_lst, num_res-1, len(data_lst))
            else:
                data = flight_into_dict(data_lst, num_res-1, num_res+5)
        
        else:
            data = flight_into_dict(data_lst, 0, 5)
            
        if count == 0:
            # If flight_id doesn't exist, insert the flight_info into the database
                
            flight_id = data.get('flight_id')
            flight = data.get('flight')
            clicks = data.get('clicks')
            from_city = data.get('from_city')
            to_city = data.get('to_city')
            cur.execute('''INSERT INTO tracked_flights (flight_id, flight, clicks, from_city, to_city)
                    VALUES (?, ?, ?, ?, ?)''',
                    (flight_id, flight, clicks, from_city, to_city))

        else:
            print("Flight with flight_id {} already exists in the database".format(flight_id))

    # Commit changes to the database
    conn.commit()


def main():

    api_data = get_API_info(url, header)
    

        # Store API data in a JSON file
    with open('tracked_flights.json', 'w') as json_file:
        json.dump(api_data, json_file)

    # Open SQLite database
    cur, conn = open_database('flights.db')

    # Load data from JSON file into a dictionary
    with open('tracked_flights.json', 'r') as json_file:
        flight_dict = json.load(json_file)
        
    # Insert data from dictionary into SQLite database
    flight_dict_into_database(flight_dict, cur, conn)

    # Close database connection
    conn.close()
    

main()