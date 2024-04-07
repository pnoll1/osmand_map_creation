'''
utilites for working with Osmand's obf format
'''
import hashlib
import logging
import os
from pathlib import Path
from subprocess import run, CalledProcessError
from config import XMX

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

def build(working_area, areas):
    '''
    input: area list
    action: runs osmand map creator on files in osmand_osm directory, cleans obf file names and moves pbfs into osm directory
    output: none
    '''
    if isinstance(areas, list):
        for subarea in areas:
            # construct string for merge index call
            subareas_string = ''
            subareas_string += f' {subarea.obf}'
            subareas_string.lstrip(' ')
            try:
                logging.info(f'{subarea.name} build started')
                run(f'JAVA_OPTS="-Xmx{XMX}" ../../osmand_map_creator/utilities.sh generate-obf {subarea.pbf}', shell=True, capture_output=True, check=True,encoding='utf8')
                logging.info(f'{subarea.name} build finished')
            except CalledProcessError as error:
                logging.error(str(subarea.name) + ' OsmAndMapCreator Failure, check osmand_gen/AREA_NAME_2.obf.gen.log file for details ' + error.stderr)
        try:
            run(f'JAVA_OPTS="-Xmx{XMX}" ../../osmand_map_creator/utilities.sh merge-index {working_area.obf_name} --address --poi {subareas_string}', shell=True, capture_output=True, check=True,encoding='utf8')
        except CalledProcessError as error:
            logging.error(f'{subarea.name} map creator merge index issue {error.stderr}')
    else:
        try:
            logging.info(f'{areas.name} build started')
            run(f'JAVA_OPTS="-Xmx{XMX}" ../../osmand_map_creator/utilities.sh generate-obf {areas}', shell=True, capture_output=True, check=True,encoding='utf8')
            logging.info(f'{areas.name} build finished')
        except CalledProcessError as error:
            logging.error(str(areas) + ' OsmAndMapCreator Failure, check osmand_gen/AREA_NAME_2.obf.gen.log file for details ' + error.stderr)
    #clean_file_names()

def calculate_hashes():
    '''
    input: none
    action: create hash file for every obf file in osmand_obf
    output: none
    '''
    for file in Path('./').iterdir():
        if file.suffix == '.obf':
            with open(file, 'rb') as opened_file:
                data = opened_file.read()
                sha256 = hashlib.sha256(data).hexdigest()
                # write sha256 to file
                with open(file.with_suffix('.sha256'),'w') as sha256_file:
                    sha256_file.write(sha256 + ' ' + file.name)
