Extrapolate Datasets and add Coordinates
=======================================

Takes a dataset, and a geoJSON polygon. Extrapolates the dataset, and attaches a coordinate to each data point.

Is pretty hardcoded to take a google flu trends file, a geoJSON file (in this case UK), and create a semi-realistic UK flu trends dataset. Think of this script as generating flu "events", where each event is a flu level + a coordinate. 

Can also take a set of "seed" coordinates. That's useful for generating "cities" on the map, by passing in larger cities as seed coordinates, and upping the probability (look in the script) of having "randomly" generated coordinates staying close to existing coordinates.

The script can extrapolate the dataset to however many (temporal) data points you want, and can create however many geographical coordinates from that dataset you want.

The script is used to generate mock data for the first flu dashboard mockup

=== Example
python genCoord.py res/google-flu-data-us.csv res/GBR.geo.json res/seedCoords.txt