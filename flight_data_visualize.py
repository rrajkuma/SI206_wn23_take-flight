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
    temp_tup_list = []
    #query listed above includes the calculation since SUM is an aggregate function in SQL
    res = cur.execute("SELECT carrier.name, SUM(routes.num_flights) FROM routes JOIN carrier ON carrier.plane_id = routes.carrier_id GROUP BY routes.carrier_id HAVING SUM(routes.num_flights) > 100 ORDER BY SUM(routes.num_flights) DESC")
    #forms the list as (carrier, num_flights)
    for row in res:
        temp_tup_list.append((row[0], int(row[1])))
    #cleans up lists because the API counts "American" and "American Airlines" as two different airlines
    #ditto with "Southwest" and "Southwest Airlines"
    #and "Spirit" and "Spirit Airlines"
    #this is an API issue, not mine
    #finds indicies
    am_index, ama_index, south_index, swa_index, sp_index, spa_index = 0, 0, 0, 0, 0, 0
    for i in range(len(temp_tup_list)):
        if temp_tup_list[i][0] == "American":
            am_index = i
        if temp_tup_list[i][0] == "American Airlines":
            ama_index = i
        if temp_tup_list[i][0] == "Southwest":
            south_index = i
        if temp_tup_list[i][0] == "Southwest Airlines":
            swa_index = i
        if temp_tup_list[i][0] == "Spirit":
            sp_index = i
        if temp_tup_list[i][0] == "Spirit Airlines":
            spa_index = i
    '''
    am_index = carrier_list.index("American")
    ama_index = carrier_list.index("American Airlines")
    south_index = carrier_list.index("Southwest")
    swa_index = carrier_list.index("Southwest Airlines")
    sp_index = carrier_list.index("Spirit")
    spa_index = carrier_list.index("Spirit Airlines")
    '''
    #updates sums
    t1 = temp_tup_list[am_index][1]
    t2 = temp_tup_list[ama_index][1]
    t3 = temp_tup_list[south_index][1]
    t4 = temp_tup_list[swa_index][1]
    t5 = temp_tup_list[sp_index][1]
    t6 = temp_tup_list[spa_index][1]
    am_sum = t1 + t2
    s_sum = t3 + t4
    sp_sum = t5 + t6
    #delete the extraneous rows
    temp_tup_list.remove(("American", t1))
    temp_tup_list.remove(("American Airlines", t2))
    temp_tup_list.remove(("Southwest", t3))
    temp_tup_list.remove(("Southwest Airlines", t4))
    temp_tup_list.remove(("Spirit", t5))
    temp_tup_list.remove(("Spirit Airlines", t6))
    #adds new tuples to the lists
    temp_tup_list.append(("American Airlines", am_sum))
    temp_tup_list.append(("Southwest Airlines", s_sum))
    temp_tup_list.append(("Spirit Airlines", sp_sum))
    #re-sorts lists
    temp = sorted(temp_tup_list, key=lambda x: x[1], reverse=True)
    for item in temp:
        carrier_list.append(item[0])
        num_flight_list.append(item[1])
    #creates list of colors for bar chart- will also probably modify this...later
    col = []
    for item in num_flight_list:
        if item > 300:
            col.append('mediumspringgreen')
        else:
            col.append('mediumaquamarine')
    #makes bar chart
    plt.bar(carrier_list, num_flight_list, color=col)
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
        for item in num_flight_list:
            outfile.write(f"{str(item)},")
    

#pulls data from flights to visualize most popular routes 
#also throws resulting data into text file
'''
SELECT routes.source_id, routes.dest_id, ROUND(AVG(routes.num_flights))
FROM routes 
GROUP BY routes.dest_id
ORDER BY ROUND(AVG(routes.num_flights)) DESC
'''
def parse_route_data(cur):
    routes_list = []
    num_flight_list = []
    cur.execute("SELECT routes.source_id, routes.dest_id, ROUND(AVG(routes.num_flights)) FROM routes GROUP BY routes.dest_id ORDER BY ROUND(AVG(routes.num_flights)) DESC")
    res = cur.fetchall()
    #process query with separate queries for the source and dest ids
    #this can be done with subqueries too, but every implementation I tried had a bug in it
    for row in res:
        s_query = "SELECT iata FROM airports WHERE air_id = " + '"' + str(row[0]) + '"'
        cur.execute(s_query)
        s_iata = cur.fetchone()[0]
        d_query = "SELECT iata FROM airports WHERE air_id = " + '"' + str(row[1]) + '"'
        cur.execute(d_query)
        d_iata = cur.fetchone()[0]
        routes_list.append(s_iata + " -> " + d_iata)
        num_flight_list.append(int(row[2]))
    #makes bar chart
    #this looks cramped as hell- I'll revise this when I have time too
    colors = [{flight<=3: 'yellowgreen', 3<flight<=5: 'limegreen', 5<flight<=10: 'forestgreen', 10<flight<=15: 'mediumseagreen', flight>15: 'seagreen'}[True] for flight in num_flight_list]
    plt.figure(figsize=(8,12))
    plt.margins(y=0)
    plt.barh(routes_list, num_flight_list, height=1, color=colors)
    plt.yticks(fontsize=8)
    plt.xlabel("Number of Flights")
    plt.title("Most Popular Routes")
    plt.savefig('route_chart.png')
    #throws data into text file
    #TEXT FILES USE COMMAS AS DELIMITERS
    with open('routes_outfile.txt', 'w') as outfile:
        for item in routes_list:
            outfile.write(f"{item},")
        outfile.write(f"\n")
        for item in num_flight_list:
            outfile.write(f"{str(item)},")

def main():
    database = "flights.db"
    cur = load_flights(database)
    parse_carrier_data(cur)
    parse_route_data(cur)

main()