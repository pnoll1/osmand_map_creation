'''
utilities for working with OpenAddresses data and transforming to OSM format
'''
import json
import logging
import os
from pathlib import Path
from subprocess import run, CalledProcessError

import ogr2osm
import psycopg

import addr_oa

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
        self.pbf = f'{self.directory}/{self.name_underscore}.osm.pbf'
        self.pbf_osm = f'{self.directory}/{self.short_name}-latest.osm.pbf'

    def __str__(self):
        return str(self.short_name)

    def __repr__(self):
        return 'WorkingArea(' + self.name + ')'

    def decompress_oa(self, filename):
        '''
        unzips oa data for current working area
        '''
        try:
            run(['unzip', '-qq', '-o', filename, self.directory.as_posix() + '/*addresses*'])
        except CalledProcessError as error:
            logging.error(self.directory.as_posix() + ' ' + error.stderr)

    def create_master_list(self):
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
        try:
            for i in self.directory.iterdir():
                # handle iso3166-1 (country)
                if i.is_dir():
                    for filename in i.iterdir():
                        add_to_master_list(filename)
                else:
                    # handle iso3166-2 (country and subdivision)
                    add_to_master_list(i)
        except FileNotFoundError:
            logging.error(self.name + ' No such file or directory. Is there OA data?')
            raise
        self.master_list = file_list
        logging.debug(self.master_list)
        logging.info(self.name + ' ' + 'Master List Created')

    def load_oa(self, db_name):
        '''
        input: working_area object
        action: loads oa into postgres+postgis db
        output: none
        '''
        logging.info(self.name + ' load oa started')
        for source in self.master_list:
            logging.debug(source.path.as_posix() + 'loading' )
            try:
                run(f'ogr2ogr PG:dbname={db_name} "{source.path}" -nln {source.table_temp} -overwrite -lco OVERWRITE=YES -lco SPATIAL_INDEX=NONE', shell=True, capture_output=True, check=True, encoding='utf8')
            except CalledProcessError as error:
                logging.warning(self.name + ' ' + error.stderr)
            run(['rm', source.path.as_posix(), f'{source.path.as_posix()}.meta'])
        logging.info(self.name + ' ' + 'Load Finished')

    def filter_complex_garbage(self, table, cur):
        suffix_lookup = {
            'AVE': 'Avenue',
            'AV': 'Avenue',
            'CIR': 'Circle',
            'CI': 'Circle',
            'RD': 'Road',
            'EXT': 'Extension',
            'ST': 'Street',
            'PL': 'Place',
            'WY': 'Way', # removed not official abbreviation
            'CRES': 'Crescent',
            'BLVD': 'Boulevard',
            'DR': 'Drive',
            'LN': 'Lane',
            'LN RD': 'Lane Road',
            'LANE': 'Lane',
            'LP': 'Loop',
            'CT': 'Court',
            'CRT': 'Court',
            'GR': 'Grove',
            'CL': 'Close',
            'TER': 'Terrace',
            'TRL': 'Trail',
            'AVE CT': 'Avenue Court',
            'AVE PL': 'Avenue Place',
            'ST CT': 'Street Court',
            'ST PL': 'Street Place',
            'HL': 'Hill',
            'VW': 'View',
            'PKWY': 'Parkway',
            'RWY': 'Railway',
            'DIV': 'Diversion',
            'HWY': 'Highway',
            'CONN': 'Connector'
        }

        dir_lookup = {
            'E': 'East',
            'S': 'South',
            'N': 'North',
            'W': 'West',
            'SE': 'Southeast',
            'NE': 'Northeast',
            'SW': 'Southwest',
            'NW': 'Northwest'
        }
        # create all combos of suffix and dir and store in hit list
        hit_list = []
        for dir_key in dir_lookup:
            for suffix_key in suffix_lookup:
                # create ne st cases
                hit_list.append(f'{dir_key} {suffix_key}')
                hit_list.append(f'{suffix_key} {dir_key}')
                # create ne   st cases
                hit_list.append(f'{suffix_key}   {dir_key}')
                hit_list.append(f'{dir_key}   {suffix_key}')
        for target in hit_list:
            try:
                cur.execute(f"DELETE FROM {table} where street='{target}'")
                logging.info(f'{table} DELETE {str(cur.rowcount)} {target}')
            except Exception as error:
                logging.warning(f'{table} filter complex had issue deleting {target}')

    def filter_data(self, db_name):
        '''
        input: working_area object
        action: delete records with bad data
        output: none
        '''
        number_field = 'number'
        conn = psycopg.connect(f'dbname={db_name}')
        cur = conn.cursor()
        for source in self.master_list:
            logging.info('filtering {0}'.format(source.table_temp))
            # find type of number field
            cur.execute(f'select pg_typeof({number_field}) from \"{source.table_temp}\"limit 1;')
            number_type = cur.fetchone()[0]
            # delete records with no or bad number field data
            if 'character' in number_type:
                cur.execute(f"DELETE from \"{source.table_temp}\" where {number_field}='' or {number_field} is null or {number_field}='0'")
                logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' empty or null')
                # us_wa_snohomish county
                cur.execute(f"DELETE from \"{source.table_temp}\" where {number_field}='UNKNOWN'")
                logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' UNKNOWN')
            elif 'integer' in number_type or 'numeric' in number_type:
                cur.execute(f"DELETE from \"{source.table_temp}\" where {number_field} is null or {number_field}=0")
                logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' empty or null')
            else:
                logging.error('Number field in {0} is not character, integer or numeric'.format(source.table))
            # delete records with nothing in street field
            cur.execute(f"DELETE from \"{source.table_temp}\" where street='' or street is null")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' street empty or null')
           # delete record with illegal unicode chars in number field
            cur.execute(f"delete from \"{source.table_temp}\" where {number_field} ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' illegal xml in number')
           # delete record with illegal unicode chars in street field
            cur.execute(f"delete from \"{source.table_temp}\" where street ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' illegal xml in street')
            # delete records with -- in nubmer field eg rancho cucamonga
            cur.execute(f"DELETE from \"{source.table_temp}\" where {number_field}='--'")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' --')
            # delete records where number=SN eg MX countrywide
            cur.execute(f"delete from \"{source.table_temp}\" where {number_field}='SN'")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' SN')
            # delete records without geometry
            cur.execute(f"delete from \"{source.table_temp}\" where wkb_geometry is null")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' missing geometry')
            # delete records located at 0,0
            cur.execute(f"delete from \"{source.table_temp}\" where wkb_geometry='0101000020E610000000000000000000000000000000000000';")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' geometry at 0,0')
            # delete 1 word streets, allow for US-101 case
            cur.execute(f"delete from \"{source.table_temp}\" where street !~ '.*[- ]+.*';")
            logging.info(source.table + ' DELETE ' + str(cur.rowcount) + ' 1 word street')
            self.filter_complex_garbage(source.table_temp, cur)
            conn.commit()
        cur.close()
        conn.close()

    def merge_oa(self, db_name):
        '''
        action: insert data from temp table if not present in table based on hash
        '''
        conn = psycopg.connect(f'dbname={db_name}')
        cur = conn.cursor()
        for source in self.master_list:
            # create table for first run
            cur.execute(f"create table if not exists {source.table} as table {source.table_temp} with no data")
            conn.commit()
            # create unique constraint for deduping
            try:
                cur.execute(f'alter table {source.table} add constraint {source.table}_unique unique nulls not distinct (number, street, unit, wkb_geometry)')
            except:
                conn.rollback()
            # insert addresses from temp table if not there, using index to autodetect dupes
            try:
                cur.execute(f'insert into {source.table} select * from {source.table_temp} on conflict do nothing')
                logging.info(source.table + ' Insert ' + str(cur.rowcount))
            except psycopg.errors.InvalidParameterValue as error:
                logging.warning(f'{source.table} InvalidParameterValue during merge_oa insert: {error}')
                conn.rollback()
                # get rid of z geometry
                cur.execute(f'alter table {source.table_temp} alter column wkb_geometry type geometry(point, 4326) using ST_Force2D(wkb_geometry);')
                cur.execute(f'insert into {source.table} select * from {source.table_temp} on conflict do nothing')
                logging.info(source.table + ' Insert ' + str(cur.rowcount))
            # get rid of temp table
            cur.execute(f'drop table {source.table_temp}')
            conn.commit()
        cur.close()
        conn.close()

    def pg2osm(self, source, id_start, db_name):
        '''
        input: source object of openaddresses file , id to start numbering at, working_area object
        action: creates osm format file excluding rows with empty or 0 number fields from postgres db
        output: finishing id if successfull, input id if failed
        '''
        def oa_quality_check(source):
            try:
                stats = run(f'osmium fileinfo --no-progress -ej {source.path_osm}', shell=True, capture_output=True, check=True, encoding='utf8')
            except CalledProcessError as error:
                logging.warning('pg2osm fileinfo failure in {0}: '.format(source.table) + error.stderr)
            # handle files with hashes only
            try:
                id_end = json.loads(stats.stdout)['data']['minid']['nodes']
                return id_end
            except Exception:
                logging.info('Error finding id_end in {0}. File is likely hashes only'.format(source.table))
                raise

        ogr2osmlogger = logging.getLogger('ogr2osm')
        ogr2osmlogger.setLevel(logging.ERROR)
        ogr2osmlogger.addHandler(logging.StreamHandler())
        translation_object = addr_oa.OaTranslation()
        datasource = ogr2osm.OgrDatasource(translation_object)
        datasource.open_datasource(f"PG:dbname={db_name}")
        datasource.set_query(f'select * from \"{source.table}\"')
        osmdata = ogr2osm.OsmData(translation_object,start_id=id_start)
        logging.debug('ogr2osm process')
        osmdata.process(datasource)
        logging.debug('ogr2osm writing')
        datawriter = ogr2osm.PbfDataWriter(source.path_osm)

        try:
            osmdata.output(datawriter)
        except CalledProcessError as error:
            logging.warning('ogr2osm failure in ' + source.table + error.stderr)
            raise
        id_end = oa_quality_check(source)
        return id_end

    def output_osm(self, id_start, db_name):
        '''
        input: working_area object, id to start from, root of working path
        action: call pg2osm to write OA data in postgres to osm files, remove failed sources from master list
        output: none
        '''
        removal_list = []
        for source in self.master_list:
            # catch error and log file for removal from master list
            # sql join then output once quicker?
            try:
                logging.info(source.path.as_posix() + 'writing osm file')
                id_start = self.pg2osm(source, id_start, db_name)
                # osmium sort runs everything in memory, may want to use osmosis instead
                run(f'osmium sort --no-progress --overwrite {source.path_osm} -o {source.path_osm}', shell=True, encoding='utf8')
            except CalledProcessError:
                logging.warning(source.path.as_posix() + ' staged for removal due to fileinfo failure')
                removal_list.append(source)
            except UnboundLocalError:
                logging.warning(source.path.as_posix() + ' staged for removal due to id_end failure. Likely hashes only')
                if source not in removal_list:
                    removal_list.append(source)
        # remove file from file list so merge will work
        for source in removal_list:
            self.master_list.remove(source)
        logging.info(f'{self.name} finished writing address files')

    def merge(self):
        '''
        input: working_area object
        action: merged area pbf in area folder
        output: none
        '''
        # create space separated string that lists all source files in osm format
        source_list_string = ''
        for source in self.master_list:
            source_list_string = source_list_string + ' ' + source.path_osm.as_posix()
        source_list_string = source_list_string.lstrip(' ')
        try:
            merge_command = f'osmium merge --no-progress -Of pbf {source_list_string} {self.pbf_osm} -o {self.pbf}'
            logging.debug(self.name + ' merge command: ' + merge_command)
            run(merge_command, shell=True, capture_output=True, check=True, encoding='utf8')
        except CalledProcessError as error:
            logging.error(self.name + ' Merge Failed ' + error.stderr)
            return
        logging.info(self.name + ' Merge Finished')
        return

    def prep_for_qa(self):
        '''
        input: working_area object
        output: stats for last source ran, osm area extract and final file
        '''
        logging.info(f'{self.name} prep_for_qa started')
        def fileinfo(path):
            return run(f'osmium fileinfo --no-progress -ej {path}', shell=True, capture_output=True ,check=True , encoding='utf8')
        # get data for last source ran
        try:
            stats = fileinfo(self.master_list[-1].path_osm)
        except CalledProcessError as error:
            logging.error(self.master_list[-1].path_osm + 'fileinfo error for last source ran' + error.stderr)
            raise
        # get data for OSM extract
        try:
            stats_osm = fileinfo(self.pbf_osm)
        except CalledProcessError as error:
            logging.error(self.short_name + ' fileinfo error in osm extract: ' + error.stderr)
            raise
        # get data for completed state file
        try:
            stats_final = fileinfo(self.pbf)
        except CalledProcessError as error:
            logging.error(self.name_underscore + ' fileinfo error in completed file ' + error.stderr)
            raise
        logging.info(f'{self.name} prep_for_qa finished')
        return stats, stats_osm, stats_final

    def quality_check(self):
        '''
        input: ready_to_move boolean
        output: boolean that is True for no issues or False for issues
        '''
        logging.info(f'{self.name} quality check started')
        stats, stats_osm, stats_final = self.prep_for_qa()
        # file is not empty
        # Check if items have unique ids
        if json.loads(stats_final.stdout)['data']['multiple_versions']:
            logging.error(f'{self.name} Multiple items with same id')
        # Check if added data overlaps with OSM ids
        if json.loads(stats_osm.stdout)['data']['maxid']['nodes'] >= json.loads(stats.stdout)['data']['minid']['nodes']:
            logging.error(f'{self.name} Added data overlaps with OSM data')
        logging.info(f'{self.name} quality check finished')

    def slice(self, config):
        '''
        input: working_area object, slice configs(defined in config file)
        file requirement: file must be sorted for osmium extract to work; running --quality-check handles this
        action: slices merged files according to config
        output: list of subarea objects
        '''
        if self.name in config:
            logging.info(f'{self.name} slice started')
            subarea_list = []
            for subarea_config in config[self.name]:
                subarea = Subarea(self, subarea_config)
                subarea_list.append(subarea)
            for subarea in subarea_list:
                logging.info(f'{subarea.name} slicing')
                try:
                    run(f'osmium extract -O -b {subarea.bounding_box} -o {subarea.pbf} {self.pbf}', shell=True, capture_output=True, check=True,encoding='utf8')
                except CalledProcessError as error:
                    logging.error(self.name + ' osmium extract error ' + error.stderr)
            logging.info(f'{self.name} slice finished') 
            return subarea_list


class Subarea():
    '''
    location and config of sliced sub area
    '''
    def __init__(self, working_area, config):
        self.name = f'{working_area.name_underscore}_{config[0]}'
        self.obf_name = f'{self.name.capitalize()}.obf'
        self.pbf = f'{working_area.directory}/{self.name}.osm.pbf'
        self.bounding_box = config[1]

class Source():
    '''
    holds locations for OA source data at any point during processing
    '''
    def __init__(self, path):
        self.path = path
        self.path_osm = Path(path.as_posix().replace(' ', '_').replace('.geojson', '_addresses.osm.pbf'))
        # - is not allowed in postgres
        self.table = path.as_posix().replace('/','_').replace('-','_').replace(' ','_').replace('.geojson','').lower()
        self.table_temp = f'{self.table}_temp'

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return 'Source(' + str(self.path) + ')'

def update_oa(token):
    '''
    input: url
    action: downloads global oa zip and unzips it, overwriting previous files
    output: none
    '''
    logging.info('update oa started')
    os.replace('data.zip', 'data.zip.1')
    run(['wget', '--header', f'Authorization: Bearer {token}', 'https://batch.openaddresses.io/api/collections/1/data'])
    # check if file finished downloading
    if os.stat('data').st_size > 20480:
        os.rename('data', 'data.zip')
    else:
        logging.warning('update_oa unsuccessful, using old data')
        os.remove('data')
        os.rename('data.zip.1', 'data.zip')
    logging.info('update oa finished')
