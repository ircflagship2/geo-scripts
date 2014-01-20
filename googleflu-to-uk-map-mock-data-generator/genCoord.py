__author__ = 'jkg'

import json
import random
from collections import defaultdict
from collections import deque
import csv
from datetime import datetime
import pytz
from itertools import izip
import calendar
import simplejson
import sys

class CoordinateGenerator:

    __boundaries = []
    __minLat = 99999999.0
    __minLng = 99999999.0
    __maxLat = -99999999.0
    __maxLng = -99999999.0
    misses = defaultdict(int)

    def addGeoJsonBoundaries(self, filename):
        with open(filename, 'r') as content_file:
            geojson = json.loads(content_file.read())

        for coordinateSets in geojson["features"][0]["geometry"]["coordinates"]:
            for coordinates in coordinateSets:
                self.__boundaries.append(coordinates)
                for coord in coordinates:
                    if (coord[0] < self.__minLng): self.__minLng = coord[0]
                    if (coord[0] > self.__maxLng): self.__maxLng = coord[0]
                    if (coord[1] < self.__minLat): self.__minLat = coord[1]
                    if (coord[1] > self.__maxLat): self.__maxLat = coord[1]

    def getRandomCoordinate(self):
        while(True):
            #generate a best-guess coordinate within the bounding box of all coordinates
            lat = random.uniform(self.__minLat, self.__maxLat)
            lng = random.uniform(self.__minLng, self.__maxLng)

            for shape in self.__boundaries:
                if self.__inside(lat, lng, shape):
                    return [lat, lng]

    def getCoordinateNear(self, sourcelat, sourcelng, maxDeltaLat, maxDelateLng):
        while(True):
            while(True):
                lat = random.uniform(sourcelat - maxDeltaLat, sourcelat + maxDeltaLat)
                lng = random.uniform(sourcelng - maxDeltaLat, sourcelng + maxDeltaLat)
                if (lat <= self.__maxLat and lat >= self.__minLat and lng <= self.__maxLng and lng >= self.__minLng):
                    break

            for shape in self.__boundaries:
                if self.__inside(lat, lng, shape):
                    return [lat, lng]
                else:
                    self.misses[str(lat) + "_" + str(lng)] += 1

    #Based on https://github.com/substack/point-in-polygon/blob/master/index.js
    def __inside(self, lat, lng, vs):

        x = float(lng)
        y = float(lat)

        #ray-casting algorithm based on
        #http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html

        inside = False

        i = 0
        j = len(vs) - 1
        while i < len(vs):

            xi = float(vs[i][0])
            yi = float(vs[i][1])

            xj = float(vs[j][0])
            yj = float(vs[j][1])

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

            j = i
            i += 1

        return inside

    def extrapolate(self, start, end, fillBetween, maxVariance):
        fillBetween += 1
        for i in range(fillBetween):
            alpha = float(i)/float(fillBetween)
            val = (end * alpha) + (start * (1-alpha)) + random.uniform(-maxVariance, maxVariance)
            yield float(val)

    def extrapolateGoogleFluTrends(self, csvFile):
        fludata = []
        with open(csvFile, 'rb') as csvfile:
            sheet = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in sheet:
                date = datetime.strptime(row[0], "%Y-%m-%d")
                #date = row[0]
                value = float(row[1])
                fludata.append([date,value])

        extrapolated = []
        last = 0.0

        for cur, next in izip(fludata, fludata[1:]):

            amount = 1000

            dategen = self.extrapolate(calendar.timegm(cur[0].utctimetuple()), calendar.timegm(next[0].utctimetuple()), amount, 1000)
            valuegen = self.extrapolate(cur[1], next[1], amount, 10)

            for date,value in izip(dategen, valuegen):
                date = datetime.fromtimestamp(date, tz=pytz.UTC)

                extrapolated.append({"date":date, "value":value})

        extrapolated.append({"date":fludata[-1][0], "value":fludata[-1][1]})

        #print last
            #extrapolated.append( d.extrapolate(cur[1], next[1], 10) )
        return extrapolated

    def generateGeoDataset(self, dataset, geoJsonBoundariesFile, seedCoords):
        self.addGeoJsonBoundaries(geoJsonBoundariesFile)

        latestCoords = deque(maxlen=500)
        
        for coord in seedCoords:
        	latestCoords.append(coord)

        clustering = 1.0
        maxDeltaLat = 0.1
        maxDeltaLng = 0.15

        for row in dataset:
            flusum = 0.0

            #Hardcoded way of generating data. Change below if you wan to change it
            while (flusum < (row['value'] / 52.78)): #we want the max flu level to be 200

                flulevel = int(random.uniform(10, 100))
                flusum += flulevel

                #gen neighbour or random?
                if (len(latestCoords) == 0 or random.random() > clustering):
                    coord = c.getRandomCoordinate()
                else:
                    source = random.choice(latestCoords)
                    coord = self.getCoordinateNear(source[0], source[1], maxDeltaLat, maxDeltaLng)

                latestCoords.append(coord)
                yield {
                    "time": str(row['date'].isoformat()),
                    "location": {"lat" : coord[0], "lng" : coord[1]},
                    "value" : flulevel
                }

##############################################################################################

if __name__ == "__main__":
    #second (optional) argument is seed coordinates
    seedCoords = []
    if len(sys.argv) >= 4:
        with open (sys.argv[3], "r") as seedfile:
            data = seedfile.readlines()
            for line in data:
                line = line.split(",")
                seedCoords.append([float(line[0]), float(line[1])])

    coordGen = CoordinateGenerator()
    #first argument is the dataset to expand
    expandedUsFluData = coordGen.extrapolateGoogleFluTrends(sys.argv[1])
    #second argument is the geoJSON polygon (featureset boundaries) to stay within
    geoLocatedDataset = coordGen.generateGeoDataset(expandedUsFluData, sys.argv[2], seedCoords)

    #print them all
    for elem in geoLocatedDataset:
    	print "INSERT INTO flupoints(point,value,created) VALUES(ST_SetSRID(ST_MakePoint(" + str(elem["location"]["lng"]) + ", " + str(elem["location"]["lat"]) + "), 4326), " + str(elem["value"]) + ", '" + str(elem["time"]) + "');"