# -*- coding: utf-8 -*-
import settings
import pandas as pd
import numpy as np
import json
import re
import os
from time import time
from print_progressbar import print_progress
from geoconversions.LatLonConversions import LatLon2WebMercator


# First convert the data to GeoJSON format:
with open(os.path.join(settings.DATAFOLDER, settings.RAW_DATA_FILENAME), 'r', encoding='utf-8') as scrapy_data_file:

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
    geoJSON = '{ "type": "FeatureCollection", "features": ['

    # While looping over the data, also the data can be averaged per zipcode!
    # Store this in a dict
    zipcode_data = {}
    # It will be of format:

    #   {
    #       "1234": {                               <-- The 4 digit zipcode is the key of this entry
    #                   "n_properties": 123         <-- number of properties that this data is based on
    #                   "data_1": value             <-- All the averaged values will come here
    #               },
    #       /* More zipcodes here */
    #   }

    # Loop over the pandas dataframe
    count_extracted_properties = 0
    total_properties = len(scrapy_data)
    # Keep track of time
    start = time()
    for index, row in scrapy_data.iterrows():

        # Print the progress
        if count_extracted_properties > 1:
            remaining_time = (time() - start) / (count_extracted_properties) * total_properties - (time() - start)
            hours_remaining = int(remaining_time // 3600)
            minutes_remaining = int((remaining_time - hours_remaining*3600) // 60)
            seconds_remaining = int(remaining_time - minutes_remaining*60 - hours_remaining*3600)
            print_progress(index, total_properties, prefix = 'Converting to geojson: ', suffix = ' Time remaining: {:02d}:{:02d}:{:02d}'.format(hours_remaining,minutes_remaining,seconds_remaining), decimals = 1, barLength = 25)

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
        x, y = LatLon2WebMercator(lat,lon)

        # Sometimes the Living area is not provided or is zero.. drop the item then
        if np.isnan(row['LivingArea']) or row['LivingArea'] == 0:
            continue

        # sometimes te lotSize is not given and thus converted to 0.. its probably because the lotsize is the LivingArea
        if np.isnan(row['LotSize']):
            row['LotSize'] = row['LivingArea']

        # Sometimes the zipcode cannot really be a zipcode.. (row['Zipcode'] == 'Nicola') :/
        if not bool(re.match('^[0-9]{4}[a-zA-Z]{2}$',row['Zipcode'])):
            # Its not a zipcode!
            continue


        # Add a feature (For the coordinates definition see: http://www.macwright.org/2015/03/23/geojson-second-bite.html )
        geoJSON += ' { "type": "Feature",  "geometry": {  "type": "Point",  "coordinates": [' + str(x) + ', ' + str(y) + ']  },  "properties": { ' + \
                     '"Price": ' + str(row['Price']) + \
                     ',"PPrice": "€{:,}"'.format(row['Price']) + \
                     ',"PriceM2": ' + str(int(row['Price']/row['LivingArea'])) + \
                     ',"LivingArea": ' + str(row['LivingArea']) + \
                     ',"LotSize": ' + str(row['LotSize']) + \
                     ',"Street": "' + row['Street'].replace('\"',"'") + '"' +\
                     ',"BuildingType": "' + row['BuildingType'] + '"' + \
                     ',"BuildYear": ' + str(row['BuildYear']) + \
                     ',"City": "' + row['City'].replace('\\u0027','\u0027').title() + '"' + \
                     ',"Zipcode": "' + row['Zipcode'].upper() + '"' + \
                     '  }  }, '

        # Add it to the zipcode data dict:
        zipcode = int(row['Zipcode'][:-2])
        if zipcode not in zipcode_data.keys():
            # There is no entry of this zipcode yet..
            zipcode_data[zipcode] =  {'n_properties': 1, 
                                      'Price': row['Price'], 
                                      'LivingArea': row['LivingArea'],
                                      'LotSize': row['LotSize'],
                                      'BuildYear': row['BuildYear'],
                                      }
        else: 
            # There is already a zipcode in the keys..
            # Add the new parameters will be averaged afterwards
            zipcode_data[zipcode]['Price'] +=  row['Price']
            zipcode_data[zipcode]['LivingArea'] += row['LivingArea']
            zipcode_data[zipcode]['LotSize'] += row['LotSize']
            zipcode_data[zipcode]['BuildYear'] += row['BuildYear']
            zipcode_data[zipcode]['n_properties'] += 1
            
        # count the number of extracted properties
        count_extracted_properties += 1

    # Close it
    # First replace the last ', ' with ' '
    geoJSON = geoJSON[:-3] + ' '
    geoJSON += ']}'

    # print some info
    print('\nNumber of invalid properties: {}'.format(n_properties - count_extracted_properties))
    print('Total properties extracted: {}'.format(count_extracted_properties))

    with open(os.path.join(settings.DATAFOLDER, settings.GEOJSON_FILENAME), 'w') as output_file:
        output_file.write(geoJSON)

    # Also write the zipcode file 
    # But first create some nices strings for printing! i.e. '€455.200' instead of 455200
    for key, item in zipcode_data.items():
        zipcode_data[key]['Price'] = int(zipcode_data[key]['Price']/zipcode_data[key]['n_properties'])
        zipcode_data[key]['LivingArea'] = int(zipcode_data[key]['LivingArea']/zipcode_data[key]['n_properties'])
        zipcode_data[key]['PriceM2'] = int(zipcode_data[key]['Price']/zipcode_data[key]['LivingArea'])
        zipcode_data[key]['LotSize'] = int(zipcode_data[key]['LotSize']/zipcode_data[key]['n_properties'])
        zipcode_data[key]['BuildYear'] = int(zipcode_data[key]['BuildYear']/zipcode_data[key]['n_properties'])
        zipcode_data[key]['PPrice'] = '€{:,}'.format(zipcode_data[key]['Price'])
        zipcode_data[key]['PPriceM2'] = '€{:,}'.format(zipcode_data[key]['PriceM2'])

    with open(os.path.join(settings.DATAFOLDER,settings.ZIPCODE_FOLDER, settings.ZIPCODE_FILENAME), 'w') as output_file:

        output_file.write(json.dumps(zipcode_data, sort_keys=True))
