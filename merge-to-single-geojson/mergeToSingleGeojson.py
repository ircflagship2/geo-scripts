import os
import sys

#takes an input folder of geojson shapes and merges them to a single featurecollection

if __name__ == "__main__":
	print '{"type":"FeatureCollection","features":['
	filenames = os.listdir(sys.argv[1])

	for filename in filenames[:-1]:
		if filename != ".DS_Store":
			with open (sys.argv[1] + "/" + filename, "r") as myfile:		
				print myfile.read()
				print ","

	with open (sys.argv[1] + "/" + filenames[-1], "r") as myfile:		
		print myfile.read()

	print "]}"
