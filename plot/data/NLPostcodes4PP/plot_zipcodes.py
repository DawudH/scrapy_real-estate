from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool, LinearColorMapper, WMTSTileSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.palettes import RdYlGn, linear_palette
from bokeh.tile_providers import STAMEN_TONER, CARTODBPOSITRON
import matplotlib as mp
import matplotlib.cm as cm

# The different possible tiles to plot
tiles = {'OpenMap': WMTSTileSource(url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png'),
         'ESRI': WMTSTileSource(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'),
         'Wikipedia': WMTSTileSource(url='https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png'),
         'Stamen Toner': STAMEN_TONER,
         'CartoDB Positron': CARTODBPOSITRON}


# Open the zipcode data
with open('NLPostcodes4PP_WM.geojson','r') as zipcode_data_file:
	geo_source = GeoJSONDataSource(geojson=zipcode_data_file.read())

# Modify the hover tool to show additional property parameters
hover = HoverTool(tooltips=[('Zipcode','@PC4CODE')])

# The tools to add to the plot
TOOLS = ["pan,wheel_zoom,box_zoom,reset,save", hover]

# Create a figure
p = figure(title="Zipcodes in the Netherlands", tools=TOOLS, width=1400, height=700, toolbar_location="above")
# Remove the axis
#p.axis.visible = False

# Plot each zipcode area
p.patches('xs', 'ys', source=geo_source,
          fill_color='#333333',
          fill_alpha=0.2, line_color="#000000", line_width=0.5)
		  
# Add a tile (the actual map on the background)
p.add_tile(tiles['Wikipedia'])


# Generate the output
output_file("zipcodes.html")
show(p)
