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
import shutil

# commandline argument setup
parser = argparse.ArgumentParser(description='Process address data to a single osm file per state')
parser.add_argument('state-list', nargs='+', help='lowercase 2 letter state abbreviation')
parser.add_argument('--update-oa', action='store_true')
parser.add_argument('--update-osm', action='store_true')
parser.add_argument('--load-oa', action='store_true')
parser.add_argument('--output-osm', action='store_true')
args = parser.parse_args()
state_list = vars(args)['state-list']
# state_list = ['mt']


def update_oa(url):
    '''
    downloads US files from OpenAddresses and unzips them, overwriting previous files
    '''
    filename = Path(url).name
    run(['curl', '-o', filename, url])
    run(['unzip', '-o', filename])


def load_csv(path, state):
    '''
    accepts path object of file to load and state name as string
    loads files into postgres and generates geometry column
    '''
    name = path.stem
    os.system('ogr2ogr PG:dbname=gis {0} -nln {1}_{2} -overwrite -lco OVERWRITE=YES'.format(path, name, state))


def pg2osm(path, id_start, state):
    '''
    input path object of openaddresses file , id to start numbering at, state name as string
    output osm format file excluding empty rows
    '''
    name = path.stem
    number_field = 'number'
    r = run('psql -d gis -c "select pg_typeof({0}) from \\"{1}_{2}\\" limit 1;"'.format(number_field, name, state), shell=True, capture_output=True, encoding='utf8').stdout
    if 'character' in r:
        try:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {3}/{1}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}_{3}\\" where {2} is not null and {2}!=\'\' and {2}!=\'0\'"'.format(id_start, name, number_field, state))
        except Exception:
            print('ogr2osm failure')
            raise
            return id_start
        stats = run('osmium fileinfo -ej {1}/{0}_addresses.osm'.format(name, state), shell=True, capture_output=True, encoding='utf8')
        # handle files with hashes only
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
        except Exception:
            print('{0}_{1} is hashes only'.format(name, state))
            raise
            return id_start
    elif 'integer' in r or 'numeric' in r:
        try:
            os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {3}/{1}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}_{3}\\" where {2} is not null and {2}!=0"'.format(id_start, name, number_field, state))
        except Exception:
            print('ogr2osm failure')
            raise
            return id_start
        stats = run('osmium fileinfo -ej {1}/{0}_addresses.osm'.format(name, state), shell=True, capture_output=True, encoding='utf8')
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
        except Exception:
            print('{0}_{1} is hashes only'.format(name, state))
            raise
            return id_start
    # handle empty file
    else:
        print('{0}_{1} is empty'.format(name, state))
        raise
        return id_start
    return id_end


def create_master_list(state, master_list, oa_root):
    '''
    input: state as 2 letter abbrev., dict for sources to go into, root directory for oa
    output: dict with 2 letter state abbrev. as key and list of sources as value
    goes through each state folder and creates list of vrt files
    '''
    oa_state_folder = oa_root.joinpath(Path(state))
    file_list = [] 
    for filename in oa_state_folder.iterdir():
        # - is not allowed in postgres
        if '-' in filename.name and filename.suffix == '.vrt':
            filename_new = filename.parent.joinpath(Path(filename.name.replace('-', '_')))
            os.rename(filename, filename_new)
            file_list.append(filename_new)
        elif filename.suffix == '.vrt':
            file_list.append(filename)
        
    master_list[state] = file_list
    print(state + ' ' + 'Master List Created')
    return master_list


def load_oa(state, master_list):
    file_list = master_list[state]
    for j in file_list:
        load_csv(j, state)
    print(state + ' ' + 'Load Finished')
    return


def output_osm(state, master_list, id, root):
    file_list = master_list.get(state)
    removal_list = []
    # create folder for osm files
    state_folder = root.joinpath(Path(state))
    try:
        os.mkdir(state_folder)
    except FileExistsError:
        pass
    for j in file_list:
        # catch error and log file for removal from master list
        # sql join then output once quicker?
        try:
            id = pg2osm(j, id, state)
        except Exception:
            print('error with pg2osm of' + j.as_posix())
            removal_list.append(j)
    # remove file from file list so merge will work
    for i in removal_list:
        file_list.remove(i)
    master_list[state] = file_list 
    return master_list


# update osm data
def update_osm(state, state_expander):
    state_expanded = state_expander.get(state)
    # format for url
    state_expanded = state_expanded.replace(' ', '-')
    run('curl --output {1}/{0}-latest.osm.pbf https://download.geofabrik.de/north-america/us/{0}-latest.osm.pbf'.format(state_expanded, state), shell=True, capture_output=True, encoding='utf8')
    return


def merge(state, master_list, state_expander):
    '''
    input: state as 2 letter abbrev., dict of sources to be merged, dict to expand state abbrev. to full name
    output: merged state pbf in state folder
    '''
    list_files_string = []
    file_list = master_list.get(state)
    for i in file_list:
        list_files_string.append(i.as_posix())
    file_list_string = ' '.join(list_files_string).replace('us/', '').replace('.vrt', '_addresses.osm')
    state_expanded = state_expander.get(state)
    state_expanded = state_expanded.replace(' ', '-')
    try:
        run('osmium merge -Of pbf {0} {1}/{2}-latest.osm.pbf -o {1}/Us_{2}_northamerica_alpha.osm.pbf'.format(file_list_string, state, state_expanded), shell=True, capture_output=True, check=True, encoding='utf8')
    except Exception as e:
        print(e.stderr)
        print(state + ' ' + 'Merge Failed')
        return
    print(state + ' ' + 'Merge Finished')
    return

def prep_for_qa(state, state_expander, master_list):
    '''
    input: state abbrev, state_expander dict, master_list
    output: stats for last source ran, state extract and final file
    '''
    state_expanded = state_expander.get(state)
    # osmium sort runs everything in memory, may want to use osmosis instead
    run('osmium sort --overwrite {0}/Us_{1}_northamerica_improved.osm.pbf -o {0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded), shell=True, encoding='utf8')
    # find last source ran
    file_list = master_list.get(state)
    last_source = Path(file_list[-1]).with_suffix('.osm')
    # get data for last source ran
    stats = run('osmium fileinfo -ej {0}'.format(last_source), shell=True, capture_output=True, encoding='utf8')
    # get data for OSM extract
    stats_state = run('osmium fileinfo -ej {0}-latest.osm.pbf'.format(state_expanded), shell=True, capture_output=True, encoding='utf8')
    # get data for completed state file
    stats_final = run('osmium fileinfo -ej Us_{0}_northamerica_alpha.osm.pbf'.format(state_expanded), shell=True, capture_output=True, encoding='utf8')
    return stats, stats_state, stats_final

def quality_check(stats, stats_state, stats_final):
    '''
    input: stats for last source ran, state extract and final file
    output: boolean that is True for no issues or False for issues
    '''
    # file is not empty
    # Check if items have unique ids
    if json.loads(stats_final.stdout)['data']['multiple_versions'] == 'True':
        print('ERROR: Multiple items with same id')
        ready_to_move = False
    # Check if added data overlaps with OSM ids
    if json.loads(stats_state.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
        print('ERROR: Added data overlaps with OSM data')
        ready_to_move = False
    return ready_to_move

def move(state, state_expander, ready_to_move, pbf_output):
    '''
    input: state abbrev, state_expander dict, ready_to_move boolean, pbf_output location
    output: nothing
    '''
    state_expanded = state_expander.get(state)
    if ready_to_move:
        shutil.move('{0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded), pbf_output)

def filter_data(state, master_list):
    file_list = master_list.get(state)
    for j in file_list:
        # check for unicode control characters
        r = run('psql -d gis -c "select pg_typeof({0}) from \\"{1}_{2}\\" limit 1;"'.format(number_field, name, state), shell=True, capture_output=True, encoding='utf8')


def slice(state, state_expander):
    '''
    input: state, state_expander, (name of slice and bounding box coordinates in lon,lat,lon,lat)
    output: sliced files name according to config

    # states above ~200MB can crash osmand map generator, slice into smaller regions before processing
    '''
    config = {}
    config['colorado'] = [['north', '-109.11,39.13,-102.05,41.00'], ['south', '-109.11,39.13,-102.04,36.99']]
    config['florida'] = [['north', '-79.75,27.079,-87.759,31.171'], ['south', '79.508,24.237,-82.579,27.079']]
    state_expanded = state_expander.get(state)
    for state in config.keys():
        for slice_config in config[state]:
            # better as dict?
            slice_name = slice_config[0]
            bounding_box = slice_config[1]
            run('osmium extract -b {3} -o {0}/Us_{1}_{2}_northamerica_alpha.osm.pbf {0}/Us_{1}_northamerica_alpha.osm.pbf'.format(state, state_expanded, slice_name, bounding_box), shell=True, capture_output=True, encoding='utf8')

# run osmand map creator
# batch.xml needs to be setup
# move files into osm directory defined in batch.xml
# java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx6300M -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml


def run_all(state):
    state_expander = {'al':'alabama', 'ak':'alaska','ar':'arkansas','az':'arizona','ca':'california','co':'colorado','ct':'connecticut','de':'delaware','fl':'florida','ga':'georgia','hi':'hawaii','ia':'iowa','id':'idaho','il':'illinois','in':'indiana', 'ks':'kansas','ky':'kentucky', 'la':'louisiana','me':'maine','md':'maryland','ma':'massachusetts','mi':'michigan', 'mn':'minnesota','ms':'mississippi','mo':'missouri', 'mt':'montana', 'nd':'north dakota', 'ne':'nebraska','nh':'new hampshire','nj':'new jersey','nm':'new mexico','ny':'new york','nc':'north carolina', 'nv':'nevada','oh':'ohio','ok':'oklahoma', 'or':'oregon','pa':'pennsylvania','ri':'rhode island','sc':'south carolina','sd':'south dakota','tn':'tennessee','tx':'texas','ut':'utah','vt':'vermont','va':'virginia','wa':'washington','wv':'west virginia','wi':'wisconsin','wy':'wyoming'}
    oa_root = Path('/home/pat/projects/osmand_map_creation/osmand_osm/osm/us/')
    # root assumed to be child folder of pbf_output
    root = Path('/home/pat/projects/osmand_map_creation/osmand_osm/osm/')
    pbf_output = root.parent
    master_list = {}
    # id to count down from for each state
    id = 2**33
    master_list = create_master_list(state, master_list, oa_root)
    if args.load_oa == True:
        load_oa(state, master_list)
    # filter_data(state, master_list)
    if args.output_osm == True:
        master_list = output_osm(state, master_list, id, root)
    if args.update_osm == True:
        update_osm(state, state_expander)
    merge(state, master_list, state_expander)
    # prep_for_qa(state, state_expander, pbf_output)
    ready_to_move = True
    # ready_to_move = quality_check(state, master_list)
    slice(state, state_expander)
    move(state, state_expander, ready_to_move, pbf_output) 

if __name__ == '__main__':
    # memory can be limit with large files, consider switching pool to 1 or doing 1 state at a time with cron job
    with Pool(2) as p:
        if args.update_oa == True:
            oa_urls = ['https://data.openaddresses.io/openaddr-collected-us_midwest.zip', 'https://data.openaddresses.io/openaddr-collected-us_south.zip', 'https://data.openaddresses.io/openaddr-collected-us_west.zip', 'https://data.openaddresses.io/openaddr-collected-us_northeast.zip']
            p.map(update_oa, oa_urls)
        p.map(run_all, state_list)
