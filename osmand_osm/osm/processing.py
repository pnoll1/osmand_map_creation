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
from pathlib import Path
import hashlib
import logging
import datetime
# config options
from config import db_name, id, slice_config, batches, Xmx, log_level
from secrets import oa_token

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
        self.obf_name = self.name_underscore.capitalize() + '.obf'

    def __string__(self):
        return str(self.short_name)

    def __repr__(self):
        return 'WorkingArea(' + self.name + ')'

class Source():
    def __init__(self, path):
        self.path = path
        self.path_osm = Path(path.as_posix().replace('.geojson', '_addresses.osm'))
        # - is not allowed in postgres
        self.table = path.as_posix().replace('/','_').replace('-','_').replace('.geojson','')

    def __string__(self):
        return str(self.path)

    def __repr__(self):
        return 'Source(' + str(self.path) + ')'

def update_oa(token):
    '''
    input: url
    action: downloads global oa zip and unzips it, overwriting previous files
    output: none
    '''
    run(['wget', '--backups=1', '--header', 'Authorization: Bearer ' + token, 'https://batch.openaddresses.io/api/collections/1/data'])
    run(['unzip', '-o', 'data'])

def pg2osm(source, id_start, working_area, db_name):
    '''
    input: source object of openaddresses file , id to start numbering at, working_area object
    action: creates osm format file excluding rows with empty or 0 number fields from postgres db
    output: finishing id if successfull, input id if failed
    '''
    def oa_quality_check(source):
        try:
            stats = run('osmium fileinfo -ej {0}'.format(source.path_osm), shell=True, capture_output=True, check=True, encoding='utf8')
        except Exception as e:
            logging.error('pg2osm fileinfo failure: ' + e.stderr)
        # handle files with hashes only
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
            return id_end
        except Exception as e:                
            logging.info('Error finding id_end in {0}. File is likely hashes only'.format(source.table))
            raise
            return id_start

    number_field = 'number'
    # find type of number field
    r = run('psql -d gis -c "select pg_typeof({0}) from \\"{1}\\" limit 1;"'.format(number_field, source.table), shell=True, capture_output=True, encoding='utf8').stdout
    if 'character' in r:
        try:
            run('ogr2osm -f --id={0} -t addr_oa.py -o {1} "PG:dbname={4}"  --sql "select * from \\"{2}\\" where {3} is not null and {3}!=\'\' and {3}!=\'0\'"'.format(id_start, source.path_osm, source.table, number_field, db_name), shell=True, capture_output=True, check=True, encoding='utf8')
        except Exception as e:
            logging.exception('ogr2osm failure ')
            raise
            return id_start
        id_end = oa_quality_check(source)
    elif 'integer' in r or 'numeric' in r:
        try:
            run('ogr2osm -f --id={0} -t addr_oa.py -o {1} "PG:dbname={4}" --sql "select * from \\"{2}\\" where {3} is not null and {3}!=0"'.format(id_start, source.path_osm, source.table, number_field, db_name), shell=True, capture_output=True, check=True, encoding='utf8')
        except Exception as e:
            logging.exception('ogr2osm failure ')
            raise
            return id_start 
        id_end = oa_quality_check(source)
    # handle empty file
    else:
        logging.warning('{0} is empty'.format(source.table))
        raise
        return id_start
    return id_end


def create_master_list(working_area):
    '''
    input: working_area object
    action: updates working_area.master_list with paths of oa files for working area
    output: none
    '''
    filename = Path('')
    def add_to_master_list(filename):
        # gets only OA address files
        if '-addresses-' in filename.name and filename.suffix == '.geojson':
            file_list.append(Source(filename))

    file_list = [] 
    for i in working_area.directory.iterdir():
        # handle iso3166-1 (country)
        if i.is_dir(): 
            for filename in i.iterdir():
                add_to_master_list(filename)
        else:    
            # handle iso3166-2 (country and subdivision)
            add_to_master_list(i) 
    working_area.master_list = file_list
    logging.debug(working_area.master_list)
    logging.info(working_area.name + ' ' + 'Master List Created')
    return


def load_oa(working_area, db_name):
    '''
    input: working_area object
    action: loads oa into postgres+postgis db  
    output: none
    '''
    for source in working_area.master_list:
        try:
            run('ogr2ogr PG:dbname={0} {1} -nln {2} -overwrite -lco OVERWRITE=YES'.format(db_name, source.path, source.table), shell=True, capture_output=True, check=True, encoding='utf8')
        except Exception as e:
            logging.error(e)
    logging.info(working_area.name + ' ' + 'Load Finished')
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
            logging.info('writing osm file for ' + source.path.as_posix())
            id = pg2osm(source, id, working_area, db_name)
            # osmium sort runs everything in memory, may want to use osmosis instead
            run('osmium sort --overwrite {0} -o {0}'.format(source.path_osm), shell=True, encoding='utf8')
        except Exception as e:
            logging.error(e)
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
        logging.error('md5 check failed for ' + working_area.name)
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
        run('osmium merge -Of pbf {0} {1}/{2}-latest.osm.pbf -o {1}/{3}.osm.pbf'.format(source_list_string, working_area.directory, working_area.short_name, working_area.name_underscore), shell=True, capture_output=True, check=True, encoding='utf8')
    except Exception as e:
        logging.error(e.stderr)
        logging.error(working_area.name + ' ' + 'Merge Failed')
        return
    logging.info(working_area.name + ' ' + 'Merge Finished')
    return

def prep_for_qa(working_area):
    '''
    input: working_area object
    output: stats for last source ran, area extract and final file
    '''
    # get data for last source ran
    try:
        stats = run('osmium fileinfo -ej {0}'.format(working_area.master_list[-1].path_osm), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        logging.error(e.stderr)
        ready_to_move=False
    # get data for OSM extract
    try:
        stats_area = run('osmium fileinfo -ej {0}/{1}-latest.osm.pbf'.format(working_area.directory, working_area.short_name), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        logging.error(e.stderr)
        ready_to_move=False
    # get data for completed state file
    try:
        stats_final = run('osmium fileinfo -ej {0}/{1}.osm.pbf'.format(working_area.directory, working_area.name_underscore), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        logging.error(e.stderr)
        ready_to_move=False
    return stats, stats_area, stats_final

def quality_check(stats, stats_area, stats_final, ready_to_move):
    '''
    input: stats for last source ran, state extract, final file and ready_to_move boolean
    output: boolean that is True for no issues or False for issues
    '''
    # file is not empty
    # Check if items have unique ids
    if json.loads(stats_final.stdout)['data']['multiple_versions'] == True:
        logging.error('ERROR: Multiple items with same id')
        ready_to_move = False
    # Check if added data overlaps with OSM ids
    if json.loads(stats_area.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
        logging.error('ERROR: Added data overlaps with OSM data')
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
            run(['mv','{0}/{1}_{2}.osm.pbf'.format(working_area.directory, working_area.name_underscore, slice_name), pbf_output])
    # move all other files
    elif ready_to_move:
        run(['mv','{0}/{1}.osm.pbf'.format(working_area.directory, working_area.name_underscore), pbf_output])

def filter_data(working_area, db_name):
    '''
    input: working_area object
    action: delete records with bad data
    output: none
    '''
    number_field = 'number'
    for source in working_area.master_list:
        logging.info('filtering {0}'.format(source.table))
        # delete records with -- in nubmer field eg rancho cucamonga
        r = run(['psql', '-d' , '{0}'.format(db_name), '-c', "DELETE from \"{0}\" where {1}='--'".format(source.table, number_field)], capture_output=True, encoding='utf8')
        logging.info('looking for -- ' + r.stdout)
        # print('Removed -- from {0}_{1}'.format(name, state))
        # delete record with illegal unicode chars in number field
        r = run( ['psql', '-d', '{0}'.format(db_name), '-c', "delete from \"{0}\" where {1} ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';".format(source.table, number_field)], capture_output=True, encoding='utf8')
        logging.info('looking for illegal xml ' + r.stdout)
        # print('Removed illegal unicode from {0}_{1}'.format(name, state))
        # delete records where number=SN eg MX countrywide
        r = run( ['psql', '-d', '{0}'.format(db_name), '-c', "delete from \"{0}\" where {1}='SN'".format(source.table, number_field)], capture_output=True, encoding='utf8')
        logging.info('looking for SN ' + r.stdout)

def slice(working_area, config):
    '''
    input: working_area object, slice configs(defined in config file)
    file requirement: file must be sorted for osmium extract to work; running --quality-check handles this
    action: slices merged files according to config
    output: config of sliced state
    '''
    if working_area.name in config.keys():
        for slice_config in config[working_area.name]:
            # better as dict?
            slice_name = slice_config[0]
            bounding_box = slice_config[1]
            try:
                run('osmium extract -O -b {3} -o {0}/{1}_{2}.osm.pbf {0}/{1}.osm.pbf'.format(working_area.directory, working_area.name_underscore, slice_name, bounding_box), shell=True, capture_output=True, check=True,encoding='utf8')
            except Exception as e:
                logging.error(e.stderr)
        sliced_state = config[working_area.name]
        return sliced_state

def parse_meta_commands():
    if args.all:
        args.update_oa = True
        args.update_osm = True
        args.load_oa = True
        args.filter_data = True
        args.output_osm = True
        args.merge = True
        args.quality_check = True
        args.slice = True
        args.build = True
    if args.normal:
        args.update_osm = True
        args.load_oa = True
        args.filter_data = True
        args.output_osm = True
        args.merge = True
        args.quality_check = True
        args.slice = True
        args.build = True

def clean_file_names():
    for file in Path('../../osmand_obf').iterdir():
        if '_2' in file.name:
            directory = file.parent
            new_filename = file.name.replace('_2','')
            new_file_path = directory.joinpath(Path(new_filename))
            os.replace(file, new_file_path)
    

def update_run_all_build(args): 
    # Ram can be limit with large files, consider switching pool to 1 or doing 1 state at a time with cron job
    with Pool(args.processes) as p:
        # OA regions don't correspond to states and download slowly, run before main flow
        if args.update_oa == True:
            update_oa(oa_token)
        p.map(run_all, area_list)
    # build obfs
    if args.build:
        logging.info('Builds started')
        run('cd ../..;java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx{0} -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml'.format(Xmx), shell=True, capture_output=True, check=True,encoding='utf8')
        # move files out of build folder
        run('cd ..;mv *.pbf osm/', shell=True, capture_output=True, encoding='utf8')

# main program flow
def run_all(area):
    # root assumed to be child folder of pbf_output
    root = Path(os.getcwd())
    pbf_output = root.parent
    working_area = WorkingArea(area)
    logging.debug(working_area)
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
            logging.error('could not find geofabrik url for ' + working_area.name)
            raise ValueError
        try:
            update_osm(working_area, url)
        except Exception as e:
            raise e
        logging.info('osm update finished for ' + working_area.name)
    if args.merge:
        merge(working_area)
    # allows running without quality check
    ready_to_move = True
    if args.quality_check:
        stats, stats_area, stats_final = prep_for_qa(working_area)
        ready_to_move = quality_check(stats, stats_area, stats_final,ready_to_move)
        logging.info('quality check finished for ' + working_area.name)
    if args.slice:
        sliced_area = slice(working_area, slice_config)
        logging.info('slice finished for ' + working_area.name)
    if args.output_osm and args.slice:
        move(working_area, ready_to_move, pbf_output, sliced_area) 
        logging.info('pbf files moved to build folder for ' + working_area.name)
    elif args.output_osm:
        move(working_area, ready_to_move, pbf_output) 
        logging.info('pbf files moved to build folder for ' + working_area.name)

if __name__ == '__main__':
    log_level = getattr(logging, log_level.upper())
    logging.basicConfig(filename='processing_{0}.log'.format(datetime.datetime.today().isoformat()), level=log_level, format='%(asctime)s %(message)s')
    # commandline argument setup
    parser = argparse.ArgumentParser(description='Process OpenAddresses data and merge with OSM extract to create single osm file per area')
    parser.add_argument('area-list', nargs='*', help='lowercase ISO 3166-1 alpha-2 country code and state/province eg us:wa')
    parser.add_argument('--normal', action='store_true', help='probably what you want, runs all but --update-oa')
    parser.add_argument('--update-oa', action='store_true', help='downloads OA data in oa_urls variable')
    parser.add_argument('--load-oa', action='store_true', help='loads OA data into database, overwriting previous')
    parser.add_argument('--filter-data', action='store_true', help='delete unwanted data from database')
    parser.add_argument('--merge', action='store_true', help='merge extract with address files')
    parser.add_argument('--output-osm', action='store_true', help='output data from database to OSM files')
    parser.add_argument('--update-osm', action='store_true', help='downloads latest area extract, overwrites previous')
    parser.add_argument('--quality-check', action='store_true', help='sort output file and run basic quality checks')
    parser.add_argument('--slice', action='store_true', help='splits areas into smaller regions if config present')
    parser.add_argument('--build', action='store_true', help='runs osmand map creator')
    parser.add_argument('--processes', type=int, nargs='?', default=2, help='number of processes to use, min=1(best for large areas that need ram), max=number of physical processors(best for small areas)')
    parser.add_argument('--all', action='store_true', help='use all options')
    if len(batches) == 0:
        args = parser.parse_args()
        parse_meta_commands()
        area_list = vars(args)['area-list']  
        update_run_all_build(args)
    # use commands from config file if present
    if len(batches) > 0:
        for i in batches:
            j = i.split(' ')
            args = parser.parse_args(j)
            parse_meta_commands()
            logging.debug(args)
            area_list = vars(args)['area-list']
            update_run_all_build(args)
            logging.info('obfs build stage finished for ' + i)
    clean_file_names()
    # calculate file hashs
    for file in Path('../../osmand_obf').iterdir():
        if file.suffix == '.obf':
            with open(file, 'rb') as opened_file:
                data = opened_file.read()
                sha256 = hashlib.sha256(data).hexdigest()
                # write sha256 to file
                with open(file.with_suffix('.sha256'),'w') as sha256_file:
                    sha256_file.write(sha256 + ' ' + file.name)
    logging.info('script finished')
