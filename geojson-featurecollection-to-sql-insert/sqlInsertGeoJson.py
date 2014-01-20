import os
import simplejson as json
import sys

if __name__ == "__main__":
	group = sys.argv[1].replace(".geojson","").replace(".Geojson","").replace(".GeoJSON","").replace(".GeoJson","").replace(".json","").replace(".Json","").replace(".JSON","")
	
	with open (sys.argv[1], "r") as f:		
		data = json.load(f)
		for obj in data['features']:
			obj = obj["geometry"]
			print "INSERT INTO public.mapregions(groupname, area) VALUES(\'" + group + "\', ST_SetSRID(ST_GeomFromGeoJSON(\'" + json.dumps(obj) + "\'), 4326));"