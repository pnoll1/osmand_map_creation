from subprocess import run, CalledProcessError
import hashlib
import logging
import json

class Osm():
    '''
    working openstreetmap data
    '''
    def __init__(self, working_area):
        self.pbf = f'{working_area.directory}/{working_area.short_name}-latest.osm.pbf'
        self.pbf_md5 = f'{working_area.directory}/{working_area.short_name}-latest.osm.pbf.md5' 

    # download https://download.geofabrik.de/index-v1.json prior to running
    def geofabrik_lookup(self, working_area):
        '''
        input: working_area object
        output: geofabrik pbf url
        '''
        with open('geofabrik_index-v1.json') as index_file:
            geofabrik_index = json.load(index_file)
            area_list = geofabrik_index['features']
            for i in area_list:
                # handle countries iso3166-1
                if working_area.is_3166_2 == False:
                    try:
                        if i['properties']['iso3166-1:alpha2']==[working_area.name.upper()]:
                            return i['properties']['urls']['pbf']
                    except:
                        pass
                # handle subdivisions iso3166-2
                elif working_area.is_3166_2:
                    try:
                        if i['properties']['iso3166-2']==[working_area.country.upper()+'-'+working_area.short_name.upper()]:
                            return i['properties']['urls']['pbf']
                    except:
                        pass
        # could not find matching area
        return ValueError

    def update_osm(self, working_area):
        '''
        input: working_area object, geofabrik extract url
        action: downloads osm extract to corresponding folder
        output: none
        '''
        logging.info(f'{working_area.name} updating OSM data')
        url = self.geofabrik_lookup(working_area)
        try:
            run(f'curl --output {self.pbf} {url}', shell=True, capture_output=True, check=True, encoding='utf8')
        except CalledProcessError as error:
            logging.error(f'{working_area.name} osm data download error {error.stderr}')
        try:
            run(f'curl --output {self.pbf_md5} {url}.md5', shell=True, capture_output=True, check=True, encoding='utf8')
        except CalledProcessError as error:
            logging.error(f'{working_area.name} osm data md5 download error {error.stderr}')
        # pull md5 hash from file
        with open(self.pbf_md5) as md5:
            md5 = md5.read()
            md5 = md5.split(' ')[0]
        # check md5 from file with correct filename
        with open(self.pbf, 'rb') as file:
            data = file.read()
            md5_calced = hashlib.md5(data).hexdigest()
        if md5 != md5_calced:
            logging.error('md5 check failed for ' + working_area.name)
            raise ValueError
        logging.info(f'{working_area.name} osm update finished')
