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
import hashlib
import logging
import datetime
import psycopg2
import ogr2osm
import addr_oa
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
    '''
    Holds all info for current geographic area being built
    '''
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
    '''
    holds locations for OA source data at any point during processing
    '''
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
        except CalledProcessError as error:
            logging.error('pg2osm fileinfo failure in {0}: '.format(source.table) + error.stderr)
        # handle files with hashes only
        try:
            id_end = json.loads(stats.stdout)['data']['minid']['nodes']
            return id_end
        except Exception as e:                
            logging.info('Error finding id_end in {0}. File is likely hashes only'.format(source.table))
            raise

    ogr2osmlogger = logging.getLogger('ogr2osm')
    ogr2osmlogger.setLevel(logging.ERROR)
    ogr2osmlogger.addHandler(logging.StreamHandler())
    translation_object = addr_oa.OaTranslation()
    ogr2osm.osm_geometries.OsmId.set_id(id)
    datasource = ogr2osm.OgrDatasource(translation_object)
    datasource.open_datasource("PG:dbname={0}".format(db_name))
    datasource.set_query('select * from \"{0}\"'.format(source.table))
    osmdata = ogr2osm.OsmData(translation_object)
    osmdata.process(datasource)
    datawriter = ogr2osm.OsmDataWriter(source.path_osm)

    try:
        osmdata.output(datawriter)
    except CalledProcessError as error:
        logging.exception('ogr2osm failure in ' + source.table)
        raise
    id_end = oa_quality_check(source)
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

def load_oa(working_area, db_name):
    '''
    input: working_area object
    action: loads oa into postgres+postgis db
    output: none
    '''
    logging.info('Starting Load for: ' + working_area.name)
    for source in working_area.master_list:
        logging.debug('Loading: ' + source.path.as_posix())
        try:
            run('ogr2ogr PG:dbname={0} {1} -nln {2} -overwrite -lco OVERWRITE=YES'.format(db_name, source.path, source.table), shell=True, capture_output=True, check=True, encoding='utf8')
        except Exception as e:
            logging.error(working_area.name + ' ' + e)
    logging.info(working_area.name + ' ' + 'Load Finished')

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
        except CalledProcessError as error:
            logging.error(source.path.as_posix() + ' staged for removal due to fileinfo failure')
            removal_list.append(source)
        except UnboundLocalError as error:
            logging.error(source.path.as_posix() + ' staged for removal due to id_end failure. Likely hashes only')
            if source not in removal_list:
                removal_list.append(source)
    # remove file from file list so merge will work
    for source in removal_list:
        working_area.master_list.remove(source)

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
        logging.error(working_area.name + ' ' + e.stderr)
        logging.error(working_area.name + ' Merge Failed')
        return
    logging.info(working_area.name + ' Merge Finished')
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
        logging.error('fileinfo error for last source ran: ' + working_area.master_list[-1].path_osm + ' ' + e)
        ready_to_move=False
        raise
    # get data for OSM extract
    try:
        stats_area = run('osmium fileinfo -ej {0}/{1}-latest.osm.pbf'.format(working_area.directory, working_area.short_name), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        logging.error('fileinfo error in osm extract: ' + working_area.short_name + ' ' + e)
        ready_to_move=False
        raise
    # get data for completed state file
    try:
        stats_final = run('osmium fileinfo -ej {0}/{1}.osm.pbf'.format(working_area.directory, working_area.name_underscore), shell=True, capture_output=True ,check=True , encoding='utf8')
    except Exception as e:
        logging.error('fileinfo error in completed file: ' + working_area.name_underscore + ' ' + e)
        ready_to_move=False
        raise
    return stats, stats_area, stats_final

def quality_check(stats, stats_area, stats_final, ready_to_move, working_area):
    '''
    input: stats for last source ran, state extract, final file and ready_to_move boolean
    output: boolean that is True for no issues or False for issues
    '''
    # file is not empty
    # Check if items have unique ids
    if json.loads(stats_final.stdout)['data']['multiple_versions'] == True:
        logging.error('ERROR: Multiple items with same id ' + working_area.name)
        ready_to_move = False
    # Check if added data overlaps with OSM ids
    if json.loads(stats_area.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
        logging.error('ERROR: Added data overlaps with OSM data ' + working_area.name)
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
    conn = psycopg2.connect('dbname={0}'.format(db_name))
    cur = conn.cursor()
    for source in working_area.master_list:
        logging.info('filtering {0}'.format(source.table))
        # find type of number field
        cur.execute('select pg_typeof({0}) from \"{1}\"limit 1;'.format(number_field, source.table))
        number_type = cur.fetchone()[0]
        # delete records with no or bad number field data
        if 'character' in number_type:
            cur.execute("DELETE from \"{0}\" where {1}='' or {1} is null or {1}='0'".format(source.table, number_field))
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' empty or null')
            # us_wa_snohomish county
            cur.execute("DELETE from \"{0}\" where {1}='UNKNOWN'".format(source.table, number_field))
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' UNKNOWN')
        elif 'integer' in number_type or 'numeric' in number_type:
            cur.execute("DELETE from \"{0}\" where {1} is null or {1}=0".format(source.table, number_field))
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' empty or null')
        else:
            logging.error('Number field in {0} is not character, integer or numeric'.format(source.table))
       # delete record with illegal unicode chars in number field
        cur.execute("delete from \"{0}\" where {1} ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';".format(source.table, number_field))
        logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' illegal xml in number')
       # delete record with illegal unicode chars in street field
        cur.execute("delete from \"{0}\" where street ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';".format(source.table))
        logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' illegal xml in street')
        # delete records with -- in nubmer field eg rancho cucamonga
        cur.execute("DELETE from \"{0}\" where {1}='--'".format(source.table, number_field))
        logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' --')
        # delete records where number=SN eg MX countrywide
        cur.execute("delete from \"{0}\" where {1}='SN'".format(source.table, number_field))
        logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' SN')
        # delete records without geometry
        cur.execute("delete from \"{0}\" where wkb_geometry is null".format(source.table))
        logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' missing geometry')
        # delete records located at 0,0
        cur.execute("delete from \"{0}\" where wkb_geometry='0101000020E610000000000000000000000000000000000000';".format(source.table))
        logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' geometry at 0,0')
        conn.commit()
    cur.close()
    conn.close()

def slice(working_area, config):
    '''
    input: working_area object, slice configs(defined in config file)
    file requirement: file must be sorted for osmium extract to work; running --quality-check handles this
    action: slices merged files according to config
    output: config of sliced state
    '''
    if working_area.name in config.keys():
        for slice_config in config[working_area.name]:
            logging.info('Slicing ' + working_area.name)
            # better as dict?
            slice_name = slice_config[0]
            bounding_box = slice_config[1]
            try:
                run('osmium extract -O -b {3} -o {0}/{1}_{2}.osm.pbf {0}/{1}.osm.pbf'.format(working_area.directory, working_area.name_underscore, slice_name, bounding_box), shell=True, capture_output=True, check=True,encoding='utf8')
            except Exception as e:
                logging.error(working.area.name + e.stderr)
        sliced_state = config[working_area.name]
        return sliced_state

def parse_meta_commands(args):
    '''
    expands meta commands into lower level commands
    '''
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
        args.calculate_hashes = True
    if args.normal:
        args.update_osm = True
        args.load_oa = True
        args.filter_data = True
        args.output_osm = True
        args.merge = True
        args.quality_check = True
        args.slice = True
        args.build = True
        args.calculate_hashes = True

def clean_file_names():
    '''
    remove filename cruft added by osmand map creator
    '''
    for file in Path('../../osmand_obf').iterdir():
        if '_2' in file.name:
            directory = file.parent
            new_filename = file.name.replace('_2','')
            new_file_path = directory.joinpath(Path(new_filename))
            os.replace(file, new_file_path) 

def update_run_all_build(args, area_list):
    '''
    splits areas up for multiprocessing then builds using osmand map creator
    '''
    # Ram can be limit with large files, consider switching pool to 1 or doing 1 state at a time with cron job
    with Pool(args.processes) as p:
        # OA regions don't correspond to states and download slowly, run before main flow
        if args.update_oa:
            update_oa(oa_token)
        area_list_of_tuples = []
        for i in area_list:
            area_list_of_tuples.append((i,args))
        p.starmap(run_all, area_list_of_tuples)
    # build obfs
    if args.build:
        logging.info('Builds started')
        run('cd ../..;java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx{0} -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml'.format(Xmx), shell=True, capture_output=True, check=True,encoding='utf8')
        # move files out of build folder
        run('cd ..;mv *.pbf osm/', shell=True, capture_output=True, encoding='utf8')

def run_all(area, args):
    '''
    runs processing code for single geographic area
    '''
    # root assumed to be child folder of pbf_output
    root = Path(os.getcwd())
    pbf_output = root.parent
    working_area = WorkingArea(area)
    logging.debug(working_area)
    create_master_list(working_area)
    if args.load_oa:
        load_oa(working_area, db_name)
    if args.filter_data:
        filter_data(working_area, db_name)
    if args.output_osm:
        output_osm(working_area, id, db_name)
    if args.update_osm:
        url = geofabrik_lookup(working_area)
        if url is None:
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
        ready_to_move = quality_check(stats, stats_area, stats_final,ready_to_move, working_area)
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

def main(args=None):
    '''
    top level function that sets up logging and cli parser then determines if cli or config file
    driven and sends areas to other function for processing. When done, file names are cleaned and
    checksums created
    '''
    logging.basicConfig(filename='processing_{0}.log'.format(datetime.datetime.today().isoformat()), level=log_level.upper(), format='%(asctime)s %(name)s %(levelname)s %(message)s')
    # commandline argument setup
    parser = argparse.ArgumentParser(description='Process OpenAddresses data and merge with OSM extract to create single osm file per area')
    parser.add_argument('area_list', nargs='*', help='lowercase ISO 3166-1 alpha-2 country code and state/province eg us:wa')
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
    parser.add_argument('--calculate-hashes', action='store_true', help='creates hashes for obf files')
    parser.add_argument('--processes', type=int, nargs='?', default=2, help='number of processes to use, min=1(best for large areas that need ram), max=number of physical processors(best for small areas)')
    parser.add_argument('--all', action='store_true', help='use all options')
    if len(batches) == 0:
        # allows calling from module
        if not args:
            args = parser.parse_args()
        parse_meta_commands(args)
        area_list = vars(args)['area_list']
        update_run_all_build(args, area_list)
    # use commands from config file if present
    if len(batches) > 0:
        for i in batches:
            j = i.split(' ')
            args = parser.parse_args(j)
            parse_meta_commands(args)
            logging.debug(args)
            area_list = vars(args)['area_list']
            update_run_all_build(args, area_list)
            logging.info('obfs build stage finished for ' + i)
    clean_file_names()
    # calculate file hashes
    if args.calculate_hashes:
        for file in Path('../../osmand_obf').iterdir():
            if file.suffix == '.obf':
                with open(file, 'rb') as opened_file:
                    data = opened_file.read()
                    sha256 = hashlib.sha256(data).hexdigest()
                    # write sha256 to file
                    with open(file.with_suffix('.sha256'),'w') as sha256_file:
                        sha256_file.write(sha256 + ' ' + file.name)
    logging.info('script finished')

if __name__ == '__main__':
    main()
