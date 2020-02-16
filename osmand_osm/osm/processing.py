#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 00:52:36 2019

@author: pat
"""

'''
accepts list of states to process identified by 2 letter abbreviation
returns pbfs for each state
ex: python3 processing.py wa or id --update-osm
'''

import os
import json
from subprocess import run, CalledProcessError
from pathlib import Path
import argparse
from multiprocessing import Pool

# commandline argument setup
parser = argparse.ArgumentParser(description='Process address data to a single osm file per state')
parser.add_argument('state-list', nargs='+',help='lowercase 2 letter state abbreviation')
parser.add_argument('--update-osm', action='store_true')
parser.add_argument('--load-oa', action='store_true')
parser.add_argument('--output-osm', action='store_true')
args = parser.parse_args()
state_list = vars(args)['state-list']
# state_list = ['mt']

def load_csv(path, state):
    '''
    accepts path object of file to load and state name as string
    loads files into postgres and generates geometry column
    '''
    name = path.stem
    os.system('ogr2ogr PG:dbname=gis {0} -nln {1}_{2} -overwrite'.format(path, name, state))

    
def pg2osm(path, id_start, state):
    '''
    input path object of openaddresses file , id to start numbering at, state name as string
    output osm format file excluding empty rows
    '''
    name = path.stem
    number_field = 'number'
    if 'character' in run('psql -d gis -c "select pg_typeof({0}) from \\"{1}_{2}\\" limit 1;"'.format(number_field, name, state), shell=True, capture_output=True, encoding='utf8').stdout:
        os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {3}/{1}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}_{3}\\" where {2} is not null and {2}!=\'\' and {2}!=\'0\'"'.format(id_start, name, number_field, state))
        stats = run('osmium fileinfo -ej {1}/{0}_addresses.osm'.format(name, state), shell=True, capture_output=True, encoding='utf8')
        # handle files with hashes only
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
        except:
            print('{0}_{1} is hashes only'.format(name, state))
            return id_start
    elif 'integer' in run('psql -d gis -c "select pg_typeof({0}) from \\"{1}_{2}\\" limit 1;"'.format(number_field, name, state), shell=True, capture_output=True, encoding='utf8').stdout:
        os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {3}/{1}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}_{3}\\" where {2} is not null and {2}!=0"'.format(id_start, name, number_field, state))
        stats = run('osmium fileinfo -ej {1}/{0}_addresses.osm'.format(name, state), shell=True, capture_output=True, encoding='utf8')
        id_end = json.loads(stats.stdout)['data']['minid']['nodes']
    # handle empty file
    else:
        os.system('python3 /opt/ogr2osm/ogr2osm.py -f --id={0} -t addr_oa.py -o {3}/{1}_addresses.osm "PG:dbname=gis user=pat password=password host=localhost" --sql "select * from \\"{1}_{3}\\" where {2} is not null and {2}!=\'\' and {2}!=\'0\'"'.format(id_start, name, number_field, state))
        stats = run('osmium fileinfo -ej {1}/{0}_addresses.osm'.format(name, state), shell=True, capture_output=True, encoding='utf8')
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
        except:
            print('{0}_{1} is empty'.format(name, state))
            raise
            return id_start
    return id_end

def create_master_list(state, master_list, oa_root):
    oa_state_folder = oa_root.joinpath(Path(state))
    file_list = []
    for filename in oa_state_folder.iterdir():
        if filename.suffix == '.vrt':
            file_list.append(filename)
    master_list[state] = file_list
    print('Master List Created')
    return master_list
        
def load_oa(state, master_list):
    file_list =  master_list[state]
    for j in file_list:
        load_csv(j, state)
    print('Load Finished')
    return

def output_osm(state, master_list, id, root):
    file_list = master_list.get(state)
    removal_list = []
    # create folder for osm files
    state_folder = root.joinpath(Path(state))
    try:
        os.mkdir(state_folder)
    except  FileExistsError:
        pass
    for j in file_list:
        # catch error and log file for removal from master list
        # sql join then output once quicker?
        try:
            id = pg2osm(j, id, state)
        except:
            print('error with pg2osm of' + j.as_posix())
            removal_list.append(j)
    # remove file from file list so merge will work
    for i in removal_list:
        file_list.remove(j)
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
    list_files_string = []
    file_list = master_list.get(state)
    for i in file_list:
        list_files_string.append(i.as_posix())
    file_list_string = ' '.join(list_files_string).replace('us/', '').replace('.vrt','_addresses.osm')
    state_expanded = state_expander.get(state)
    state_expanded = state_expanded.replace(' ', '-')
    run('osmium merge -Of pbf {0} {1}/{2}-latest.osm.pbf -o Us_{2}_northamerica_improved.osm.pbf'.format(file_list_string, state, state_expanded), shell=True, capture_output=True, check=True, encoding='utf8')
    print('Merge Finished')
    return

# region slicing
# states above ~200MB can crash osmand map generator, slice into smaller regions before processing
# define polyfiles or coordinates for slicing
# osmium extract
    
# move files into osm directory defined in batch.xml
    
# run osmand map creator
# batch.xml needs to be setup
# java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx6300M -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml

def run_all(state):
    state_expander = {'al':'alabama', 'ak':'alaska','ar':'arkansas','az':'arizona','ca':'california','co':'colorado','ct':'connecticut','de':'delaware','fl':'florida','ga':'georgia','hi':'hawaii','ia':'iowa','id':'idaho','il':'illinois','in':'indiana', 'ks':'kansas','ky':'kentucky', 'la':'louisiana','me':'maine','md':'maryland','ma':'massachusetts','mi':'michigan', 'mn':'minnesota','ms':'mississippi','mo':'missouri', 'mt':'montana', 'nd':'north dakota', 'ne':'nebraska','nh':'new hampshire','nj':'new jersey','nm':'new mexico','ny':'new york','nc':'north carolina', 'nv':'nevada','oh':'ohio','ok':'oklahoma', 'or':'oregon','pa':'pennsylvania','ri':'rhode island','sc':'south carolina','sd':'south dakota','tn':'tennessee','tx':'texas','ut':'utah','vt':'vermont','va':'virginia','wa':'washington','wv':'west virginia','wi':'wisconsin','wy':'wyoming'}
    oa_root=Path('/home/pat/projects/osmand_map_creation/osmand_osm/osm/us/')
    root = Path('/home/pat/projects/osmand_map_creation/osmand_osm/osm/')
    master_list = {}
    id = 2**33
    master_list = create_master_list(state, master_list, oa_root)
    if args.load_oa == True:
        load_oa(state, master_list)
    if args.output_osm == True:
        master_list = output_osm(state, master_list, id, root)
    if args.update_osm == True:
        update_osm(state, state_expander)
    merge(state, master_list, state_expander)

if __name__ == '__main__':
    with Pool(2) as p:
        p.map(run_all, state_list)