#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 00:52:36 2019

@author: pat
"""

import os
import json
from subprocess import run, CalledProcessError
from pathlib import Path
import argparse
from multiprocessing import Pool
# config options
from config import db_name, id
# commandline argument setup
parser = argparse.ArgumentParser(description='Process OpenAddresses data and merge with OSM extract to create single osm file per area')
parser.add_argument('area-list', nargs='+', help='lowercase ISO 3166-1 alpha-2 country code and state/province eg us:wa')
parser.add_argument('--update-oa', action='store_true', help='downloads OA data in oa_urls variable')
parser.add_argument('--load-oa', action='store_true', help='loads OA data into database, overwriting previous')
parser.add_argument('--filter-data', action='store_true', help='delete unwanted data from database')
parser.add_argument('--output-osm', action='store_true', help='output data from database to OSM files')
parser.add_argument('--update-osm', action='store_true', help='downloads latest area extract, overwrites previous')
parser.add_argument('--quality-check', action='store_true', help='sort output file and run basic quality checks')
parser.add_argument('--slice', action='store_true', help='splits areas into smaller regions if config present')
parser.add_argument('--normal', action='store_true', help='runs all but --update-oa')
parser.add_argument('--all', action='store_true', help='use all options')
args = parser.parse_args()
if args.all:
    args.update_oa = True
    args.update_osm = True
    args.load_oa = True
    args.output_osm = True
    args.quality_check = True
    args.filter_data = True
    arg.slice = True
if args.normal:
    args.update_osm = True
    args.load_oa = True
    args.output_osm = True
    args.quality_check = True
    args.slice = True
    args.filter_data = True
area_list = vars(args)['area-list']

# download https://download.geofabrik.de/index-v1.json prior to running
def geofabrik_lookup(working_area):
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
    url = None
    return url
     

class WorkingArea():
    def __init__(self, name):
        self.name = name
        self.name_underscore = self.name.replace(':', '_')
        name_list = name.split(':')
        self.country = name_list[0]
        if len(name_list) == 2:
            # handle iso3166-2 (country and subdivision)
            self.short_name = name_list[1]
            self.directory = Path(self.country + '/' + self.short_name)
            self.is_3166_2 = True
        elif len(name_list) == 1:
            # handle iso3166-1 (country only)
            self.short_name = name_list[0]
            self.directory = Path(self.name)
            self.is_3166_2 = False
        self.master_list = None

    def __string__(self):
        return str(self.short_name)

class Source():
    def __init__(self, path):
        self.path = path
        self.path_osm = Path(path.as_posix().replace('.vrt', '_addresses.osm'))
        self.table = path.as_posix().replace('/','_').replace('.vrt','')

def update_oa(url):
    '''
    input: url
    action: downloads urls and unzips them overwriting previous files
    output: none
    '''
    filename = Path(url).name
    run(['curl', '-o', filename, url])
    run(['unzip', '-o', filename])

def pg2osm(source, id_start, working_area, db_name):
    '''
    input: source object of openaddresses file , id to start numbering at, working_area object
    action: creates osm format file excluding rows with empty or 0 number fields from postgres db
    output: finishing id if successfull, input id if failed
    '''
    number_field = 'number'
    # find type of number field
    r = run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, source.table), shell=True, capture_output=True, encoding='utf8').stdout
    if 'character' in r:
        try:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {1} "PG:dbname={4}"  --sql "select * from \\"{2}\\" where {3} is not null and {3}!=\'\' and {3}!=\'0\'"'.format(id_start, source.path_osm, source.table, number_field, db_name))
        except Exception:
            print('ogr2osm failure')
            raise
            return id_start
        # handle files with hashes only
        stats = run('osmium fileinfo -ej {0}'.format(source.path_osm), shell=True, capture_output=True, encoding='utf8')
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
        except Exception:                
            print('{0} is hashes only'.format(source.table))
            raise
            return id_start
    elif 'integer' in r or 'numeric' in r:
        try:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {1} "PG:dbname={4}" --sql "select * from \\"{2}\\" where {3} is not null and {3}!=0"'.format(id_start, source.path_osm, source.table, number_field, db_name))
        except Exception:
            print('ogr2osm failure')
            raise
            return id_start 
        # handle files with hashes only
        stats = run('osmium fileinfo -ej {0}'.format(source.path_osm), shell=True, capture_output=True, encoding='utf8')
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
        except Exception:                
            print('{0} is hashes only'.format(source.table))
            raise
            return id_start
    # handle empty file
    else:
        print('{0} is empty'.format(source.table))
        raise
        return id_start
    return id_end


def create_master_list(working_area):
    '''
    input: working_area object
    action: updates working_area.master_list with paths of vrt files for working area
    output: none
    '''
    file_list = [] 
    for i in working_area.directory.iterdir():
        if i.is_dir(): 
            for filename in i.iterdir():
                # - is not allowed in postgres
                if '-' in filename.name and filename.suffix == '.vrt':
                    filename_new = filename.parent.joinpath(Path(filename.name.replace('-', '_')))
                    os.rename(filename, filename_new)
                    file_list.append(Source(filename_new))
                elif filename.suffix == '.vrt':
                    file_list.append(Source(filename))
        else:    
            # - is not allowed in postgres
            if '-' in i.name and i.suffix == '.vrt':
                filename_new = i.parent.joinpath(Path(i.name.replace('-', '_')))
                os.rename(i, filename_new)
                file_list.append(Source(filename_new))
            elif i.suffix == '.vrt':
                file_list.append(Source(i))
    working_area.master_list = file_list
    print(working_area.name + ' ' + 'Master List Created')
    return


def load_oa(working_area, db_name):
    '''
    input: working_area object
    action: loads oa csv into postgres+postgis db  
    output: none
    '''
    for source in working_area.master_list:
        run('ogr2ogr PG:dbname={0} {1} -nln {2} -overwrite -lco OVERWRITE=YES'.format(db_name, source.path, source.table), shell=True, capture_output=True, encoding='utf8')
    print(working_area.name + ' ' + 'Load Finished')
    return


def output_osm(working_area, id, db_name):
    '''
    input: working_area object, id to start from, root of working path
    action: call pg2osm to write OA data in postgres to osm files, remove failed sources from master list
    output: none
    '''
    removal_list = []
    for source in working_area.master_list:
        # catch error and log file for removal from master list
        # sql join then output once quicker?
        try:
            print('writing osm file for ' + source.path.as_posix())
            id = pg2osm(source, id, working_area, db_name)
        except Exception as e:
            print(e)
            removal_list.append(source)
    # remove file from file list so merge will work
    for source in removal_list:
        working_area.master_list.remove(source)
    return


def update_osm(working_area, url):
    '''
    input: working_area object, geofabrik extract url
    action: downloads osm extract to corresponding folder
    output: none
    '''
    run('curl --output {0}/{1}-latest.osm.pbf {2}'.format(working_area.directory, working_area.short_name, url), shell=True, capture_output=True, encoding='utf8')
    run('curl --output {0}/{1}-latest.osm.pbf.md5 {2}.md5'.format(working_area.directory, working_area.short_name, url), shell=True, capture_output=True, encoding='utf8')
    # filename in md5 file doesn't match downloaded name
    # pull md5 hash from file
    with open('{0}/{1}-latest.osm.pbf.md5'.format(working_area.directory, working_area.short_name)) as md5:
        md5 = md5.read()
        md5 = md5.split(' ')[0]
    # check md5 from file with correct filename
    try:
        run('echo {0} {1}/{2}-latest.osm.pbf.md5 | md5sum -c'.format(md5, working_area.directory, working_area.short_name), shell=True, capture_output=True, encoding='utf8')
    except Exception as e:
        print('md5 check failed for ' + working_area.name)
        raise e
    return


def merge(working_area):
    '''
    input: working_area object
    action: merged area pbf in area folder
    output: none
    '''
    # create space separated string that lists all source files in osm format
    source_list_string = ''
    for source in working_area.master_list:
        source_list_string = source_list_string + ' ' + source.path_osm.as_posix()
    source_list_string = source_list_string.lstrip(' ')
    try:
        run('osmium merge -Of pbf {0} {1}/{2}-latest.osm.pbf -o {1}/{3}_alpha.osm.pbf'.format(source_list_string, working_area.directory, working_area.short_name, working_area.name_underscore), shell=True, capture_output=True, check=True, encoding='utf8')
    except Exception as e:
        print(e.stderr)
        print(working_area.name + ' ' + 'Merge Failed')
        return
    print(working_area.name + ' ' + 'Merge Finished')
    return

def prep_for_qa(working_area):
    '''
    input: working_area object
    output: stats for last source ran, area extract and final file
    '''
    # osmium sort runs everything in memory, may want to use osmosis instead
    run('osmium sort --overwrite {0}/{1}_alpha.osm.pbf -o {0}/{1}_alpha.osm.pbf'.format(working_area.directory, working_area.name_underscore), shell=True, encoding='utf8')
    # get data for last source ran
    try:
        stats = run('osmium fileinfo -ej {0}'.format(working_area.master_list[-1].path_osm), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        print(e.stderr)
        ready_to_move=False
    # get data for OSM extract
    try:
        stats_area = run('osmium fileinfo -ej {0}/{1}-latest.osm.pbf'.format(working_area.directory, working_area.short_name), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        print(e.stderr)
        ready_to_move=False
    # get data for completed state file
    try:
        stats_final = run('osmium fileinfo -ej {0}/{1}_alpha.osm.pbf'.format(working_area.directory, working_area.name_underscore), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        print(e.stderr)
        ready_to_move=False
    return stats, stats_area, stats_final

def quality_check(stats, stats_area, stats_final, ready_to_move):
    '''
    input: stats for last source ran, state extract, final file and ready_to_move boolean
    output: boolean that is True for no issues or False for issues
    '''
    # file is not empty
    # Check if items have unique ids
    if json.loads(stats_final.stdout)['data']['multiple_versions'] == 'True':
        print('ERROR: Multiple items with same id')
        ready_to_move = False
    # Check if added data overlaps with OSM ids
    if json.loads(stats_area.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
        print('ERROR: Added data overlaps with OSM data')
        ready_to_move = False
    return ready_to_move

def move(working_area, ready_to_move, pbf_output, sliced_area=None):
    '''
    input: working_area object, ready_to_move boolean, pbf_output location, optional sliced_area config
    action: moves final file to pbf_output location
    output: nothing
    '''
    # move sliced files
    if sliced_area is not None and ready_to_move:
        for slice_config in sliced_area:
            slice_name = slice_config[0]
            run(['mv','{0}/{1}_{2}_alpha.osm.pbf'.format(working_area.directory, working_area.name_underscore, slice_name), pbf_output])
    # move all other files
    elif ready_to_move:
        run(['mv','{0}/{1}_alpha.osm.pbf'.format(working_area.directory, working_area.name_underscore), pbf_output])

def filter_data(working_area, db_name):
    '''
    input: working_area object
    action: delete records with bad data
    output: none
    '''
    number_field = 'number'
    for source in working_area.master_list:
        print('filtering {0}'.format(source.table))
        # delete records with -- in nubmer field eg rancho cucamonga
        r = run(['psql', '-d' , '{0}'.format(db_name), '-c', "DELETE from \"{0}\" where {1}='--'".format(source.table, number_field)], capture_output=True, encoding='utf8')
        print('looking for -- ' + r.stdout)
        # print('Removed -- from {0}_{1}'.format(name, state))
        # delete record with illegal unicode chars in number field
        r = run( ['psql', '-d', '{0}'.format(db_name), '-c', "delete from \"{0}\" where {1} ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';".format(source.table, number_field)], capture_output=True, encoding='utf8')
        print('looking for illegal xml ' + r.stdout)
        # print('Removed illegal unicode from {0}_{1}'.format(name, state))
        # delete records where number=SN eg MX countrywide
        r = run( ['psql', '-d', '{0}'.format(db_name), '-c', "delete from \"{0}\" where {1}='SN'".format(source.table, number_field)], capture_output=True, encoding='utf8')
        print('looking for SN ' + r.stdout)

def slice(working_area):
    '''
    input: working_area object, (name of slice and bounding box coordinates in lon,lat,lon,lat)
    file requirement: file must be sorted for osmium extract to work; running --quality-check handles this
    action: slices merged files according to config
    output: config of sliced state

    # states above ~200MB can crash osmand map generator, slice into smaller regions before processing
    '''
    config = {}
    config['us:co'] = [['north', '-109.11,39.13,-102.05,41.00'], ['south', '-109.11,39.13,-102.04,36.99']]
    config['us:fl'] = [['north', '-79.75,27.079,-87.759,31.171'], ['south', '79.508,24.237,-82.579,27.079']]
    config['us:tx'] = [['southeast','-96.680,24.847,-93.028,30.996'],['northeast','-96.680,24.847,-93.028,30.996'],['northwest','-96.028,30.996,-108.391,36.792'],['southwest','-96.028,30.996,-107.556,25.165']]
    config['us:ca'] = [['north','-119.997,41.998,-125.365,38.964'],['northcentral','-125.365,38.964,-114.049,37.029'],['central','-114.049,37.029,-123.118,34.547'],['southcentral','-123.118,34.547,-113.994,33.312'],['south','-113.994,33.312,-119.96,31.85']]
    if working_area.name in config.keys():
        for slice_config in config[working_area.name]:
            # better as dict?
            slice_name = slice_config[0]
            bounding_box = slice_config[1]
            try:
                run('osmium extract -O -b {3} -o {0}/{1}_{2}_alpha.osm.pbf {0}/{1}_alpha.osm.pbf'.format(working_area.directory, working_area.name_underscore, slice_name, bounding_box), shell=True, capture_output=True, check=True,encoding='utf8')
            except Exception as e:
                print(e.stderr)
        sliced_state = config[working_area.name]
        return sliced_state

# main program flow
def run_all(area):
    # root assumed to be child folder of pbf_output
    root = Path(os.getcwd())
    pbf_output = root.parent
    working_area = WorkingArea(area)
    create_master_list(working_area)
    if args.load_oa == True:
        load_oa(working_area, db_name)
    if args.filter_data:
        filter_data(working_area, db_name)
    if args.output_osm:
        output_osm(working_area, id, db_name)
    if args.update_osm == True:
        url = geofabrik_lookup(working_area)
        if url == None:
            print('could not find geofabrik url for ' + working_area.name)
            raise ValueError
        try:
            update_osm(working_area, url)
        except Exception as e:
            raise e
    if args.output_osm:
        merge(working_area)
    # allows running without quality check
    ready_to_move = True
    if args.quality_check:
        stats, stats_area, stats_final = prep_for_qa(working_area)
        ready_to_move = quality_check(stats, stats_area, stats_final,ready_to_move)
    if args.slice:
        sliced_area = slice(working_area)
    if args.output_osm and args.slice:
        move(working_area, ready_to_move, pbf_output, sliced_area) 
    elif args.output_osm:
        move(working_area, ready_to_move, pbf_output) 

if __name__ == '__main__':
    # Ram can be limit with large files, consider switching pool to 1 or doing 1 state at a time with cron job
    with Pool(2) as p:
        # OA regions don't correspond to states and download slowly, run before main flow
        if args.update_oa == True:
            # other possible urls: https://data.openaddresses.io/openaddr-collected-us_northeast.zip https://data.openaddresses.io/openaddr-collected-us_midwest.zip https://data.openaddresses.io/openaddr-collected-us_south.zip https://data.openaddresses.io/openaddr-collected-us_west.zip https://www.countries-ofthe-world.com/countries-of-north-america.html https://data.openaddresses.io/openaddr-collected-europe.zip https://data.openaddresses.io/openaddr-collected-asia.zip https://data.openaddresses.io/openaddr-collected-south_america.zip
            oa_urls = ['https://data.openaddresses.io/openaddr-collected-global.zip']
            p.map(update_oa, oa_urls)
        p.map(run_all, area_list)
