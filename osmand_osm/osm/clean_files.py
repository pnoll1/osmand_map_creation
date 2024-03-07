'''
remove unnecessary oa files
run from osmand_osm/osm
'''
import os
from pathlib import Path
directory = Path(os.getcwd())
for root, dirs, files in os.walk(directory):
    for name in files:
        if 'buildings' in name:
            os.remove(os.path.join(root, name))
        elif 'parcels' in name:
            os.remove(os.path.join(root, name))
