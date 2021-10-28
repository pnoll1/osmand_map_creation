# database info
db_name = 'gis'
# id to count down from for addresses added to each area
id = 2**34
# openaddresses urls to download address data from
# other possible urls: https://data.openaddresses.io/openaddr-collected-us_northeast.zip https://data.openaddresses.io/openaddr-collected-us_midwest.zip https://data.openaddresses.io/openaddr-collected-us_south.zip https://data.openaddresses.io/openaddr-collected-us_west.zip https://www.countries-ofthe-world.com/countries-of-north-america.html https://data.openaddresses.io/openaddr-collected-europe.zip https://data.openaddresses.io/openaddr-collected-asia.zip https://data.openaddresses.io/openaddr-collected-south_america.zip
oa_urls = ['https://data.openaddresses.io/openaddr-collected-global.zip']
# batch settings
# list, each batch is a string
batches = []
# slice configs
# dict entry with value that is list of slices. Each slice is a list with the first entry being the name as a string and second being bounding box coordinates in lon,lat,lon,lat as a string
# file must be sorted for osmium extract to work; running --quality-check handles this
# states above ~200MB can crash osmand map generator, slice into smaller regions before processing
slice_config = {}
slice_config['au'] = [['north', '95.888672,-8.00000,163.081055,-30.372875'],['south', '95.888672,-51.672555,163.081055,-30.372875']]
slice_config['mx'] = [['north', '-122.585449,22.512557,-80.288097,33.578015'],['south', '-116.103516,11.867351,-80.288086,22.512557']]
slice_config['us:co'] = [['north', '-109.11,39.13,-102.05,41.00'], ['south', '-109.11,39.13,-102.04,36.99']]
slice_config['us:fl'] = [['north', '-79.75,27.079,-87.759,31.171'], ['south', '-79.508,24.237,-82.579,27.079']]
slice_config['us:tx'] = [['southeast','-96.680,24.847,-93.028,30.996'],['northeast','-96.680,24.847,-93.028,30.996'],['northwest','-96.028,30.996,-108.391,36.792'],['southwest','-96.028,30.996,-107.556,25.165']]
slice_config['us:ca'] = [['north','-119.997,41.998,-125.365,38.964'],['northcentral','-125.365,38.964,-114.049,37.029'],['central','-114.049,37.029,-123.118,34.547'],['southcentral','-123.118,34.547,-113.994,33.312'],['south','-113.994,33.312,-119.96,31.85']]
# max memory allocated to Java for osmand map creator
Xmx = '3G'
# specify log level. Options are debug, info, warning or error
log_level = 'info'
