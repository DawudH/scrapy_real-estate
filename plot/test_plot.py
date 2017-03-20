from bokeh.io import output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool, LinearColorMapper, WMTSTileSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.palettes import RdYlGn, linear_palette
from bokeh.tile_providers import STAMEN_TONER, CARTODBPOSITRON
import matplotlib as mp
import matplotlib.cm as cm

cmap = cm.get_cmap('coolwarm')
palette = [mp.colors.to_hex(cmap(i)) for i in range(256)]


tiles = {'OpenMap': WMTSTileSource(url='http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png'),
         'ESRI': WMTSTileSource(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'),
         'Wikipedia': WMTSTileSource(url='https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png'),
         'Stamen Toner': STAMEN_TONER,
         'CartoDB Positron': CARTODBPOSITRON}


with open('properties.geojson','r') as properties_data_file:
	geo_source = GeoJSONDataSource(geojson=properties_data_file.read())

with open('townships.geojson','r') as townships_data_file:
	townships_geo_source = GeoJSONDataSource(geojson=townships_data_file.read())

color_mapper = LinearColorMapper(palette=palette, low=1000,high=4000)

hover = HoverTool(tooltips=[('Price','@PPrice'),
                            ('Address','@Street @Zipcode @City'),
                            ('Price/m2','€@PriceM2'),
                            ('BuildingType','@BuildingType')])

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

bound = 10000 # meters
p = figure(title="Real estate in the Netherlands", tools=[TOOLS,hover],x_range=(230000, 1000000), width=1400, height=700, toolbar_location="above")
p.grid.grid_line_color = None
p.axis.visible = False
p.circle(x='x', y='y',alpha=0.7, line_alpha=0, fill_color={'field': 'PriceM2', 'transform': color_mapper}, source=geo_source)
color_bar = ColorBar(color_mapper=color_mapper,
                     label_standoff=12, border_line_color=None, location=(0,0))
p.add_layout(color_bar, 'right')
#p.patches('xs', 'ys', fill_alpha=0.01, fill_color='#333333',
#           line_color='#000000', line_width=0.5, source=townships_geo_source)
p.add_tile(tiles['Wikipedia'])
output_file("geojson.html")
show(p)
