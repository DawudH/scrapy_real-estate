from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource
from bokeh.plotting import figure

import json
import pandas as pd

# First convert the data to GeoJSON format:
with open('big_first_run.json', 'r', encoding='utf-8') as scrapy_data_file:

    scrapy_data = pd.read_json(scrapy_data_file)
    # remove all lists.. this should be done in scrrapy!
    #scrapy_data.loc[:,'BrokerName'] = df['BrokerName'].apply(lambda x: x[0] if type(x) is list else x)
    #scrapy_data.loc[:,'BuildYear'] = df['BuildYear'].apply(lambda x: x[0] if type(x) is list else x)
    #scrapy_data.loc[:,'BuildingType'] = df['BuildingType'].apply(lambda x: x[0] if type(x) is list else x)
    #scrapy_data.loc[:,'City'] = df['City'].apply(lambda x: x[0] if type(x) is list else x)
    #scrapy_data.loc[:,'LivingArea'] = df['LivingArea'].apply(lambda x: x[0] if type(x) is list else x)
    #scrapy_data.loc[:,'BrokerName'] = df['BrokerName'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'propertyID'] = scrapy_data['propertyID'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'Geolocation'] = scrapy_data['Geolocation'].apply(lambda x: x[0] if type(x) is list else x)
    scrapy_data.loc[:,'Price'] = scrapy_data['Price'].apply(lambda x: x[0] if type(x) is list else x)

    # Remove all the duplicates
    scrapy_data = scrapy_data.drop_duplicates('propertyID')

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

    geoJSON = '{\n\t "type": "FeatureCollection",\n\t "features": [\n'

    # Loop over the pandas dataframe
    for index, row in scrapy_data.iterrows():
        

        # Add a feature
        geoJSON += '\t\t {\n\t\t\t "type": "Feature", \n\t\t\t "geometry": { \n\t\t\t\t "type": "Point", \n\t\t\t\t "coordinates": [' + str(row['Geolocation']['Latitude']) + ', ' + str(row['Geolocation']['Longitude']) + ' \n\t\t\t }, \n\t\t\t "properties": { \n\t\t\t\t "Price": ' + str(row['Price']) + ' \n\t\t\t } \n\t\t }, \n'

    # Close it
    geoJSON += '\t]\n}'

    with open('properties.geojson', 'w') as output_file:
        output_file.write(geoJSON)
