# -*- coding: utf-8 -*-
import math
import json
import os

# The coordinates need to be converted to web mercator format create a function to do that.
# From http://wiki.openstreetmap.org/wiki/Mercator#Python
def LatLon2WebMercator(lat, lon):

	r_major=6378137.000

	# Spherical earth
	y = r_major/2 * math.log((1.0 + math.sin(math.radians(lat))) / (1.0 - math.sin(math.radians(lat))))
	x = r_major * lon * math.pi/180


	return [x, y]


def __coordinates2WebMercator(geomtype,coordinates):
    """"This function converts a geojson coordinates value to WebMercator
        It depends on the geometry type 
    """

    # Geojson has the format [lon, lat] for some weird reason

    if geomtype.lower() == 'point':
        # Now it is just a list
        # Only extract the lat and lon, ignore the height
        # update the coordinates
        return LatLon2WebMercator(coordinates[1],coordinates[0])

    elif geomtype.lower() == 'lineString':
        # Now its a list of lists
        # use a list comprehension to loop over the list and create an equally sized list
        # Only extract the lat and lon, ignore the height
        return [LatLon2WebMercator(coord[1],coord[0]) for coord in coordinates]

    elif geomtype.lower() == 'polygon':
        # Now its a list of lists of lists.. 
        # use a nested list comprehension to loop over the list of lists and create an equally sized list of lists of lists.. or something haha
        return [[LatLon2WebMercator(coord[1],coord[0]) for coord in coordlist] for coordlist in coordinates]
    else:
        # Other types are currently not supported.
        # raise an error
        print('Not supported geometry type: {}'.format(geomtype))
        raise




def geojson2WebMercator(geojson_file, outputfile,zipcode_data_file=None):
    """ This file convers the coordinates in a geojson file from latlon to web mercator
    And saves it into a new geojson file 
    INPUT:
            - geojson_file: the input file location (including extension)
            - outputfile: the output file location (including extension)
            - zipcode_data_file: (optional) File location of additional zipcode data 
                --> NOTE this Only works if the original file has a propertie called 'PC4CODE' <--
                            The extra zipcode data that will be added to the properties of the geojson file
                            It should be a json file with format:
                                   {
                                       "1234": {                               <-- The 4 digit zipcode is the key of this entry
                                                   "n_properties": 123         <-- number of properties that this data is based on
                                                   "data_1": value             <-- All the averaged values will come here
                                               },
                                       /* More zipcodes here */
                                   }


    NOTE: This function is specifically made for conversion of the zipcode data of the netherlands
            In no way is this applyable to any geojson file..
    """

    # Open the file
    with open(geojson_file) as f:
        data = json.load(f)
    
    # OPTIONALLY open the zipcode_data_file
    if zipcode_data_file:
        with open(zipcode_data_file) as f:
            zipcode_data = json.load(f)

    # GeoJSON format is like:
    #   {
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
    #       }, etc ..
    #      ]
    #   }

    print('The file contains {} features.'.format(len(data['features'])))

    # Loop over all the features
    for feature in data['features']:

        # For each feature we want to modify the coordinates in the geometry
        # Each feature is a dict
        # Each geometry is also a dict
        # Each coordinates entry can be a list, or a list of lists or a list of lists of lists.. depending on the geometry type..
        geomtype = feature['geometry']['type']

        # It can even be a collection of more geommetries.... 
        if geomtype.lower() == 'geometrycollection':
            # In this case feature['geometry'] is again a dict with a key geometries
            # feature['geometry']['geometries'] is a list of geometries, just  like other feature['geometry'] entries..
            
            for i, geometry in enumerate(feature['geometry']['geometries']):
                feature['geometry']['geometries'][i]['coordinates'] = __coordinates2WebMercator(geometry['type'],geometry['coordinates'])
        
        else:

            # Now its not some weird nested this (or not as weirdly nested haha)
            feature['geometry']['coordinates'] = __coordinates2WebMercator(geomtype,feature['geometry']['coordinates'])


        # OPTIONAL: add the optional zipcode data:
        if zipcode_data and 'PC4CODE' in feature['properties'].keys():

            # Check if zipcode exists in data
            if feature['properties']['PC4CODE'] in zipcode_data.keys():
                # It does!
                properties = zipcode_data[feature['properties']['PC4CODE']]

            else: 
                # No data for this zipcode..
                # For all properties fill in zero!
                properties = {key: 0 for key in list(list(zipcode_data.values())[0].keys())}

            # Add the PC4CODE
            properties['PC4CODE'] = feature['properties']['PC4CODE']

            # Overwrite all the other properties
            feature['properties'] = properties


            
           

    # Now the conversion is done
    # Write it to a file
    jsonstring = json.dumps(data, separators=(',', ':'))
    with open(outputfile, 'w') as output_f:
        output_f.write(jsonstring)



