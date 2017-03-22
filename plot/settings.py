# -*- coding: utf-8 -*-

# Folder where all the data is stored
DATAFOLDER = 'data'

# Raw data from the spider (must be located in DATAFOLDER)
RAW_DATA_FILENAME = 'big_run_2_102147.json'

# Folder where the zipcode geojson file is located (inside the DATAFOLDER)
ZIPCODE_FOLDER = 'NLPostcodes4PP'

# Input zipcode geojson file (is used by the function convert_zipcode_areas)
# This file can be created from a kml file with the kml2geojson function in the geoconversion folder
ZIPCODE_GEOJSON = 'NLPostcodes4PP.geojson'

# Output zipcode geojson file with the coordinates in web mercator format
ZIPCODE_GEOJSON_WM = 'NLPostcodes4PP_WM.geojson'

# Output geojson filename
GEOJSON_FILENAME = 'properties.geojson'

# output zipcode filename (json format)
ZIPCODE_FILENAME = 'zipcode.json'


# output folder, to store the generated plots
OUTPUT_FOLDER = 'output'

