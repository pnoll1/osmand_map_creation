from subprocess import run
from config import Xmx

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

def build():
    '''
    runs osmand map creator, cleans obf file names and moves pbfs out of build folder
    '''
        logging.info('Builds started')
        try:
            run(f'cd ../..;java -Djava.util.logging.config.file=logging.properties -Xms64M -Xmx{Xmx} -cp "./OsmAndMapCreator.jar:lib/OsmAnd-core.jar:./lib/*.jar" net.osmand.util.IndexBatchCreator batch.xml', shell=True, capture_output=True, check=True,encoding='utf8')
        except CalledProcessError as error:
            logging.error(str(area_list) + ' OsmAndMapCreator Failure, check osmand_gen/AREA_NAME_2.obf.gen.log file for details', exc_info = True)
        # move files out of build folder
        run('cd ..;mv *.pbf osm/', shell=True, capture_output=True, encoding='utf8')
        clean_file_names()
        
def calculate_hashes():
    for file in Path('../../osmand_obf').iterdir():
        if file.suffix == '.obf':
            with open(file, 'rb') as opened_file:
                data = opened_file.read()
                sha256 = hashlib.sha256(data).hexdigest()
                # write sha256 to file
                with open(file.with_suffix('.sha256'),'w') as sha256_file:
                    sha256_file.write(sha256 + ' ' + file.name)
