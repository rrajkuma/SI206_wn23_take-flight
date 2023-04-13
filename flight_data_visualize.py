import sqlite3
import matplotlib.pyplot as plt
import os

#loads the flights database
def load_flights(database):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database)
    cur = conn.cursor()
    return conn, cur

def main():
    database = "flights.db"
    load_flights(database)

main()