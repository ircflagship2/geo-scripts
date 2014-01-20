import csv
import urllib2
import simplejson
import os
import sys

def readFile(file):
	with open(file, 'rb') as csvfile:
		sheet = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in sheet:
			url = "http://global.mapit.mysociety.org/point/4326/" + row[1] + "," + row[0]
			yield {"file": getJson(url), "lat": row[0], "lng" : row[1] }
            
def getJson(url):
	req = urllib2.Request(url)
	opener = urllib2.build_opener()
	f = opener.open(req)
	return simplejson.load(f)

def download(jsonElem):
	type = jsonElem['type']
	typename = jsonElem['type_name']
	name = jsonElem['name']
	id = jsonElem['id']
	dir = "./" + type
	path = dir + "/" + str(name) + ".json"
	
	url = "http://global.mapit.mysociety.org/area/" + str(id) + ".geojson"

	try:
		os.makedirs(dir)
	except:
		pass
	
	if not os.path.exists(path):
		with open(path, "w+") as output:
			
			jsonout = {}
			jsonout["type"] = "Feature"
			jsonout["properties"] = {"name": name, "id": id, "osm_type": type, "osm_type_name": typename}
			jsonout["geometry"] = getJson(url)
			output.write(simplejson.dumps(jsonout))
	
	return path

for input in readFile(sys.argv[1]):
	layers = {}
	for i in input["file"]:
		type = input["file"][i]['type']
		layers[type] = input["file"][i]

	#download all layers
	files = []
	for i in input["file"]:
		files.append(download(input["file"][i]))

	print input["lat"] + "," + input["lng"] + " => " + ",".join(sorted(files))
	#download the layer we actually want for our purpose
	#do we have a layer 5?
	
	#if 'O06' in layers:
	#	download(layers['O06'], 'out')
	#elif 'O05' in layers:
	#	download(layers['O05'], 'out')
	#else:
	#	out = "Not found: "
	#	for i in layers:
	#		out += layers[i]['name'] + " , "
	#	print out


	
		