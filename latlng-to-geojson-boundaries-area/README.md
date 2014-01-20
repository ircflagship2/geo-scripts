## Coordinates to Administrative Boundaries Resolver
Small python script that resolves lat/lng coordinates to geoJSON OSM Administrave Boundaries using http://global.mapit.mysociety.org/ .

### Usage
 - Add coordinates to input.csv (83 largest UK urban areas provided as example in file)
 - Run "python scrape.py input.csv" or similar
 - All administrative areas (country, region, city etc.) encapsulating the point are downloaded. GeoJSON files of different precision levels (OSM Boundary levels) are stored in individual folders to make it easier for you to get the precision you want (e.g. a "country" folder, a "region" folder etc.).

 ### Hints
 - The script should be easy to adapt to using UK postcodes, as MapIT has such a service as well, in addition to the lat/lng service.
 - Use Mapquest geocoding to get coordinates from addresses. A Google Calc script exists to make this easier for bulk conversion.
 - The coordinates in the example file are generated based on geocoding (using mapquest) areas found on http://en.wikipedia.org/wiki/List_of_urban_areas_in_the_United_Kingdom .
