from cluster import get_cluster
import pandas as pd
import json
import requests
DATA_PATH = "data_retrieval/data/points_of_interest_clean.csv"

cities = {}
city_list = [] 
data = pd.read_csv(DATA_PATH)

for i in data["base_city"]:
	if cities.has_key(i):
		cities[i]+=1
	else:
		cities[i] = 1
	

for key in cities:
	if cities[key] > 5:
		city_list.append(key)

def create_cluster_file():
	for city in city_list:
		create_cluster_city(file)

def get_distances(geolocation):
	
	distances = []
	BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="
	KEY = "&key=AIzaSyC5Cd047LqwkP9KVoFKjS-WtRdktusONWI"
	geolocation =  geolocation.replace(",", "%2C")
	REQUEST_URL  = BASE_URL + geolocation + "&destinations=" + geolocation + KEY
	
	print REQUEST_URL

	res = requests.get(REQUEST_URL).text
	res = json.loads(res)
	for i in res["rows"]:
		distance_vector = []
		for element in i["elements"]:
			distance_vector.append(element["duration"]["value"])
		
		distances.append(distance_vector)
	return distances
	
def create_cluster_city(city):
	
	filename = city + "_cluster.json"
	f = open(filename, "w")
	r = get_cluster(city)
	f.write(json.dumps(r))
	f.close()

problem_text_start = """
(define (problem problem1)
    (:domain
        travel-domain    
    )
"""


problem_text_mid1 = """
    
    (:init
        (= (total-score) 0)
        (= (current-time) 10)
        (= (end-time) 20)
        (user user1)
"""

problem_text_end = """
    	)
    )
    (:metric 
        maximize (total-score)         
    )
)
"""

def create_problem_file(city):

	all_clusters = get_cluster(city, cluster_size=8)
	problem_text_mids = []

	for index in range(0, len(all_clusters)):
		
		cluster = all_clusters[index]["data"]
		problem_text_mid = ""
		object_text_def = """
		(:objects
        	user1
        	waypoint"""
		geolocation = ""
		poi_index = 1
		for s in cluster:
			object_text_def += " waypoint" + str(poi_index)
			problem_text_mid += "\t\t(waypoint waypoint" + str(poi_index) + ")\n"
			problem_text_mid += "\t\t(= (score waypoint" + str(poi_index) + ") " + str(s["score"]) +")\n"
			problem_text_mid += "\t\t(= (duration waypoint" + str(poi_index) + ") " + str(s["duration"]*60) +")\n"
			geolocation += str(s["geolocation"]) + "%7C"
			poi_index += 1
			if poi_index >8:
				break
		object_text_def += "\n)"
		
		geolocation = geolocation[:-3]

		distancematrix = get_distances(geolocation)
		
		for i in range(1, poi_index):
			for j in range(i+1, poi_index):
				problem_text_mid +="\t\t(= (drive-time waypoint" + str(i) + " waypoint" + str(j) + ") " + str(distancematrix[i-1][j-1])+ " )\n"
				problem_text_mid +="\t\t(= (drive-time waypoint" + str(j) + " waypoint" + str(i) + ") " + str(distancematrix[i-1][j-1])+ " )\n" 

		for i in range(1,poi_index):
			problem_text_mid += "\t\t(not ( visited user1 waypoint" + str(i) + ") )\n"
		

		problem_text_mid += "\t\t(user-at user1 waypoint1) ) \n\n\t(:goal\n\t\t(and\n"

		for i in range(1,poi_index):
			problem_text_mid += "\t\t\t(visited user1 waypoint" + str(i) + ")\n"

		problem_text_mids.append(object_text_def + problem_text_mid1 + problem_text_mid)
		
	all_file_data = []
	for i in problem_text_mids:
		all_file_data.append(problem_text_start + i + problem_text_end)
	
	return all_file_data

def write_file(city):
	all_file_data = create_problem_file(city)
	end = "_problem.pddl"

	for i in range(0, len(all_file_data)):
		f = open(city + str(i) + end, "w")
		f.write(all_file_data[i])
		f.close()

write_file(city_list[0])
