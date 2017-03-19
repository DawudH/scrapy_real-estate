from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource
from bokeh.plotting import figure

import json

# First convert the data to GeoJSON format:
with open('big_first_run.json') as scrapy_data_file:

    scrapy_data = json.loads(scrapy_data_file)

    # GeoJSON format is like:

    #{
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
    #    },
    #}

    # For more info see: https://tools.ietf.org/html/rfc7946

    geoJSON = '{'