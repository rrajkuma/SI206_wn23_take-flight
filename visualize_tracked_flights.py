import sqlite3
import matplotlib.pyplot as plt
import os

#loads the flights database
def load_flights(database):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database)
    cur = conn.cursor()
    return cur

def visualise_all_from_cities(cur):
    cur.execute("SELECT from_city, SUM(clicks) as total_clicks FROM tracked_flights GROUP BY from_city ORDER BY total_clicks ")
    rows = cur.fetchall()

    from_city_list = []
    from_clicks_list = []
    for row in rows:
        from_city = row[0]
        total_clicks = row[1]
        if from_city is not None and total_clicks is not None:  # Add a check for None values
            from_city_list.append(from_city)
            from_clicks_list.append(total_clicks)

    # Check if the lists are not empty before generating the visualization
    if from_city_list and from_clicks_list:
        plt.bar(from_city_list, from_clicks_list)
        plt.title('From Cities by Clicks')
        plt.xlabel('City')
        plt.xticks(rotation=50, ha='right', fontsize=6.5)
        plt.ylabel('Clicks')
        plt.title("Most Tracked Airlines")
        plt.show()
        plt.savefig('most_tracked_airlines_chart.png')

        #throws data into text file
    #TEXT FILES USE COMMAS AS DELIMITERS
    with open('most_tracked_flights.txt', 'w') as outfile:
        for item in from_city_list:
            outfile.write(f"{item},")
        outfile.write(f"\n")
        for item in from_clicks_list:
            outfile.write(f"{str(item)},")



def main():
    # Connect to the database
    database = "flights.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    
    # Call the functions to visualise the top from cities with the highest number of clicks
    visualise_all_from_cities(cur)
    
    
    # Close the database connection
    conn.close()
main()
