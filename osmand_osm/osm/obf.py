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

def build(area_list):
    '''
    input: area list
    action: runs osmand map creator on files in osmand_osm directory, cleans obf file names and moves pbfs into osm directory
    output: none
    '''
    logging.info('Builds started')
    try:
        run(f'cd ../..;java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx{XMX} -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml', shell=True, capture_output=True, check=True,encoding='utf8')
    except CalledProcessError as error:
        logging.error(str(area_list) + ' OsmAndMapCreator Failure, check osmand_gen/AREA_NAME_2.obf.gen.log file for details', exc_info = True)
    # move files out of build folder
    run('cd ..;mv *.pbf osm/', shell=True, capture_output=True, encoding='utf8')
    clean_file_names()

def calculate_hashes():
    '''
    input: none
    action: create hash file for every obf file in osmand_obf
    output: none
    '''
    for file in Path('../../osmand_obf').iterdir():
        if file.suffix == '.obf':
            with open(file, 'rb') as opened_file:
                data = opened_file.read()
                sha256 = hashlib.sha256(data).hexdigest()
                # write sha256 to file
                with open(file.with_suffix('.sha256'),'w') as sha256_file:
                    sha256_file.write(sha256 + ' ' + file.name)
