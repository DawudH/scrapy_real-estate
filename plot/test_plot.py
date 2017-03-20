from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool, LinearColorMapper, WMTSTileSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.palettes import RdYlGn, linear_palette
from bokeh.tile_providers import STAMEN_TONER, CARTODBPOSITRON
import matplotlib as mp
import matplotlib.cm as cm

# Make a colormap from matplotlib, convert them to a list of hash numbers that bokeh likes 
cmap = cm.get_cmap('coolwarm')
palette = [mp.colors.to_hex(cmap(i)) for i in range(256)]

# The different possible tiles to plot
tiles = {'OpenMap': WMTSTileSource(url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png'),
         'ESRI': WMTSTileSource(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'),
         'Wikipedia': WMTSTileSource(url='https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png'),
         'Stamen Toner': STAMEN_TONER,
         'CartoDB Positron': CARTODBPOSITRON}

# Open the properties data
with open('properties.geojson','r') as properties_data_file:
	geo_source = GeoJSONDataSource(geojson=properties_data_file.read())

# Create a colormapper with the low and high thresholds.
color_mapper = LinearColorMapper(palette=palette, low=1000,high=4000)

# Modify the hover tool to show additional property parameters
hover = HoverTool(tooltips=[('Price','@PPrice'),
                            ('Address','@Street @Zipcode @City'),
                            ('Price/m2','€@PriceM2'),
                            ('BuildingType','@BuildingType')])

# The tools to add to the plot
TOOLS = ["pan,wheel_zoom,box_zoom,reset,save", hover]

# Create a figure
p = figure(title="Real estate in the Netherlands", tools=TOOLS,x_range=(230000, 1000000), width=1400, height=700, toolbar_location="above")
# Remove the axis
p.axis.visible = False
# add a circle to each property with the correct color.
p.circle(x='x', y='y',alpha=0.7, line_alpha=0, fill_color={'field': 'PriceM2', 'transform': color_mapper}, source=geo_source)
# Ad a colorbar to the side of the figure
color_bar = ColorBar(color_mapper=color_mapper,
                     label_standoff=12, border_line_color=None, location=(0,0))
p.add_layout(color_bar, 'right')
# Add a tile (the actual map on the background)
p.add_tile(tiles['Wikipedia'])

# Generate the output
output_file("geojson.html")
show(p)
