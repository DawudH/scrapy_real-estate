import pandas as pd
import math
import numpy as np
import geojson
import re

# The coordinates need to be converted to web mercator format create a function to do that.
# From http://wiki.openstreetmap.org/wiki/Mercator#Python
def toWebMercator(lon, lat):

	r_major=6378137.000

	# Spherical earth
	y = r_major/2 * math.log((1.0 + math.sin(math.radians(lat))) / (1.0 - math.sin(math.radians(lat))))
	x = r_major * lon * math.pi/180


	return [x, y]


# First convert the data to GeoJSON format:
with open('books.json', 'r', encoding='utf-8') as scrapy_data_file:

    scrapy_data = pd.read_json(scrapy_data_file)
    # remove all lists.. this should be done in scrrapy!
    scrapy_data.loc[:,'BrokerName'] = scrapy_data['BrokerName'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'BuildYear'] = scrapy_data['BuildYear'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'BuildingType'] = scrapy_data['BuildingType'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'City'] = scrapy_data['City'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'LivingArea'] = scrapy_data['LivingArea'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'BrokerName'] = scrapy_data['BrokerName'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'propertyID'] = scrapy_data['propertyID'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'Geolocation'] = scrapy_data['Geolocation'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'Price'] = scrapy_data['Price'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'LotSize'] = scrapy_data['LotSize'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'Street'] = scrapy_data['Street'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'Zipcode'] = scrapy_data['Zipcode'].apply(lambda x: x[0] if type(x) is list else x)

    # Remove all the duplicates
    n_properties = len(scrapy_data)
    
    scrapy_data = scrapy_data.drop_duplicates('propertyID')
    n_duplicates = n_properties - len(scrapy_data)
    n_properties = len(scrapy_data)
    print('Number of properties: ' + str(n_properties))
    print('Number of duplicates removed: ' + str(n_duplicates))

    # GeoJSON format is like:


    #    {
    #       "type": "FeatureCollection",
    #       "features": [{
    #           "type": "Feature",
    #           "geometry": {
    #               "type": "Point",
    #               "coordinates": [102.0, 0.5]
    #           },
    #           "properties": {
    #               "prop0": "value0"
    #           }
    #       },

    # For more info see: https://tools.ietf.org/html/rfc7946

    # start with the header
    geoJSON = '{\n\t "type": "FeatureCollection",\n\t "features": [\n'

    # Loop over the pandas dataframe
    for index, row in scrapy_data.iterrows():

        if not isinstance(row['Geolocation'],dict):
            # There is no geoinfo
            ## TODO do something smart here
            continue

		# The coordinates need to be converted to Web Mercator (EPSG:4326 to EPSG:3857)
        lat = row['Geolocation']['Latitude']
        lon = row['Geolocation']['Longitude']

		# Sometimes the latitude and longitude are switched around for some reason...
		# Fortunately we know that they are all in the Netherlands so.. Latitude ~52.3, Longitude ~4.9
        if lon > lat:
            # Switch them around!
            lon = row['Geolocation']['Latitude']
            lat = row['Geolocation']['Longitude']

        # check if property is on null-island
        if lon == 0 and lat == 0:
            # dont plot it
            continue

		# Do the conversion to UTM-WGS84
        x, y = toWebMercator(lon,lat)

        # sometimes te lotSize is not given and thus converted to 0.. its probably because the lotsize is the LivingArea
        if np.isnan(row['LotSize']):
            row['LotSize'] = row['LivingArea']


        # Add a feature (For the coordinates definition see: http://www.macwright.org/2015/03/23/geojson-second-bite.html )
        geoJSON += '\t\t {\n\t\t\t "type": "Feature", \n\t\t\t "geometry": { \n\t\t\t\t "type": "Point", \n\t\t\t\t "coordinates": [' + str(x) + ', ' + str(y) + '] \n\t\t\t }, \n\t\t\t "properties": { \n\t\t\t\t' + \
                     '"Price": ' + str(row['Price']) + \
                     ',\n\t\t\t\t"PPrice": "€{:,}"'.format(row['Price']) + \
                     ',\n\t\t\t\t"PriceM2": ' + str(int(row['Price']/row['LivingArea'])) + \
                     ',\n\t\t\t\t"LivingArea": ' + str(row['LivingArea']) + \
                     ',\n\t\t\t\t"LotSize": ' + str(row['LotSize']) + \
                     ',\n\t\t\t\t"Street": "' + row['Street'] + '"' +\
                     ',\n\t\t\t\t"BuildingType": "' + row['BuildingType'] + '"' + \
                     ',\n\t\t\t\t"BuildYear": ' + str(row['BuildYear']) + \
                     ',\n\t\t\t\t"City": "' + row['City'].replace('\\u0027','\u0027').title() + '"' + \
                     ',\n\t\t\t\t"Zipcode": "' + row['Zipcode'] + '"' + \
                     ' \n\t\t\t } \n\t\t }, \n'

    # Close it
    # First replace the last ', \n' with ' \n'
    geoJSON = geoJSON[:-3] + ' \n'
    geoJSON += '\t]\n}'

    with open('properties.geojson', 'w') as output_file:
        output_file.write(geoJSON)
