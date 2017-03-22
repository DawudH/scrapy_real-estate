# -*- coding: utf-8 -*-
import settings
import os
from geoconversions.LatLonConversions import geojson2WebMercator


# Convert the file 
geojson2WebMercator(os.path.join(settings.DATAFOLDER, settings.ZIPCODE_FOLDER, settings.ZIPCODE_GEOJSON),
                    os.path.join(settings.DATAFOLDER, settings.ZIPCODE_FOLDER, settings.ZIPCODE_GEOJSON_WM),
                    zipcode_data_file=os.path.join(settings.DATAFOLDER, settings.ZIPCODE_FOLDER, settings.ZIPCODE_FILENAME)
                    )
