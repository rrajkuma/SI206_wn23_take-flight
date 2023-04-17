import sqlite3
import matplotlib.pyplot as plt
import os

#loads the flights database
def load_flights(database):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database)
    cur = conn.cursor()
    return cur

#pulls data from flights to visualize the largest carriers between the cities of interest in the data_get file
#the HAVING clause is arbitrary- for more results, decrease the number; for fewer results, increase the number.
#CALCULATIONS ARE DONE VIA SQL
#throws resulting data into text file
'''
SELECT SUM(routes.num_flights), carrier.name
FROM routes JOIN carrier ON carrier.plane_id = routes.carrier_id
GROUP BY routes.carrier_id
HAVING SUM(routes.num_flights) > 100
ORDER BY SUM(routes.num_flights) DESC
'''
def parse_carrier_data(cur):
    carrier_list = []
    num_flight_list = []
    #query listed above includes the calculation since SUM is an aggregate function in SQL
    res = cur.execute("SELECT carrier.name, SUM(routes.num_flights) FROM routes JOIN carrier ON carrier.plane_id = routes.carrier_id GROUP BY routes.carrier_id HAVING SUM(routes.num_flights) > 100 ORDER BY SUM(routes.num_flights) DESC")
    #forms the bar list and the labels 
    for row in res:
        carrier_list.append(row[0])
        num_flight_list.append(int(row[1]))
    #cleans up lists because the API counts "American" and "American Airlines" as two different airlines
    #ditto with "Southwest" and "Southwest Airlines"
    #and "Spirit" and "Spirit Airlines"
    #this is an API issue, not mine
    #finds indicies
    am_index = carrier_list.index("American")
    ama_index = carrier_list.index("American Airlines")
    south_index = carrier_list.index("Southwest")
    swa_index = carrier_list.index("Southwest Airlines")
    sp_index = carrier_list.index("Spirit")
    spa_index = carrier_list.index("Spirit Airlines")
    #updates sums, and assigns them to American Airlines and Southwest Airlines
    am_sum = num_flight_list[am_index] + num_flight_list[ama_index]
    s_sum = num_flight_list[south_index] + num_flight_list[swa_index]
    sp_sum = num_flight_list[sp_index] = num_flight_list[spa_index]
    num_flight_list[ama_index] = am_sum
    num_flight_list[swa_index] = s_sum
    num_flight_list[spa_index] = sp_sum
    #delete the rows for American and Southwest
    num_flight_list.remove(num_flight_list[am_index])
    num_flight_list.remove(num_flight_list[south_index])
    num_flight_list.remove(num_flight_list[sp_index])
    carrier_list.remove("American")
    carrier_list.remove("Southwest")
    carrier_list.remove("Spirit")
    #re-sorts lists
    num_flights = sorted(num_flight_list, reverse=True)
    #this is hard-coded- I might come back and change this later
    carrier_list[0] = "American Airlines"
    carrier_list[1] = "Southwest Airlines"
    carrier_list[2] = "Delta Air Lines"
    carrier_list[3] = "United"
    #creates list of colors for bar chart- will also probably modify this...later
    col = []
    for item in num_flights:
        if item > 300:
            col.append('mediumspringgreen')
        else:
            col.append('mediumaquamarine')
    #makes bar chart
    plt.bar(carrier_list, num_flights, color=col)
    plt.xlabel("Carriers")
    plt.xticks(rotation=30, ha='right', fontsize=6.5)
    plt.ylabel("Number of Flights")
    plt.title("Most Popular Airlines")
    plt.savefig('carrier_chart.png')
    #throws data into text file
    #TEXT FILES USE COMMAS AS DELIMITERS
    with open('carrier_outfile.txt', 'w') as outfile:
        for item in carrier_list:
            outfile.write(f"{item},")
        outfile.write(f"\n")
        for item in num_flights:
            outfile.write(f"{str(item)},")
    

#pulls data from flights to visualize most popular routes 
#also throws resulting data into text file
'''
SELECT routes.source_id, routes.dest_id, ROUND(AVG(routes.num_flights))
FROM routes 
GROUP BY routes.dest_id
ORDER BY ROUND(AVG(routes.num_flights)) DESC
'''


def main():
    database = "flights.db"
    cur = load_flights(database)
    parse_carrier_data(cur)

main()