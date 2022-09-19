import unittest
from subprocess import run
import types
import logging
import datetime
from pathlib import Path
import processing

logging.basicConfig(filename='processing_test_{0}.log'.format(datetime.datetime.today().isoformat()), level='DEBUG', format='%(asctime)s %(name)s %(levelname)s %(message)s')

# setup object to hold parser args
args = types.SimpleNamespace()

class UnitTests(unittest.TestCase):
    '''
    test each function with crafted minimal cases
    '''

    def test_create_master_list(self):
        '''
        check for proper creation of master list
        currently uses number of entries since checking of exact matches was not working
        '''
        #iso3166-1
        working_area = processing.WorkingArea('aa')
        processing.create_master_list(working_area)
        self.assertEqual(3, len(working_area.master_list))
        #iso3166-2
        working_area = processing.WorkingArea('ab:aa')
        processing.create_master_list(working_area)
        self.assertEqual(1, len(working_area.master_list))

    def test_load_oa(self):
        run(['psql', '-d', 'gis', '-c', "drop table aa_load_oa_addresses_city"], capture_output=True)
        run('psql -d gis < $PWD/aa/load_oa_addresses_city.sql',shell=True)
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/load-oa-addresses-city.geojson'))]
        processing.load_oa(working_area, 'gis')
        r = run('psql -d gis --csv -c "select * from aa_load_oa_addresses_city"', shell=True, capture_output=True)
        # check for street
        self.assertRegex(str(r.stdout),'Di Mario Dr')
        # check for number
        self.assertRegex(str(r.stdout),',,,1')

    def test_filter_data(self):
        # cleanup postgres table
        run(['psql', '-d', 'gis', '-c', "drop table aa_filter_data_addresses_city"], capture_output=True)
        # load data into postgres
        run('psql -d gis < $PWD/aa/filter_data_addresses_city.sql',shell=True)
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/filter-data-addresses-city.geojson'))]
        processing.filter_data(working_area, 'gis')
        # check for --
        r = run(['psql', '-d', 'gis', '-c', "select * from aa_filter_data_addresses_city where number='--'"], capture_output=True)
        self.assertRegex(str(r.stdout),'(0 rows)')
        # check for illegal unicode
        r = run(['psql', '-d', 'gis', '-c', "select * from  aa_filter_data_addresses_city where number ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';"], capture_output=True)
        self.assertRegex(str(r.stdout),'(0 rows)')
        # check for SN
        r = run(['psql', '-d', 'gis', '-c', "select * from  aa_filter_data_addresses_city where number='SN'"], capture_output=True)
        self.assertRegex(str(r.stdout),'(0 rows)')

    def test_output_osm(self):
        # cleanup postgres table
        run(['psql', '-d', 'gis', '-c', "drop table aa_output_osm_addresses_city"], capture_output=True)
        # load data into postgres
        run('psql -d gis < $PWD/aa/output_osm_addresses_city.sql',shell=True)
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/output-osm-addresses-city.geojson'))]
        db_name = 'gis'
        id = 2**34
        processing.output_osm(working_area, id, db_name)
        with open('aa/output-osm-addresses-city_addresses.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, 'Di Mario Dr')
            # check that ogr2osm doesn't merge
            self.assertRegex(file_text, '\"#A01 E CHERRY LN\"')

class IntegrationTests(unittest.TestCase):
    '''
    runs on real data from oa to check if program and data are as expected
    '''
    def setUp(self):
        args.area_list = ['us:pr']
        args.load_oa = True
        args.all = False
        args.normal = False
        args.processes = 2
        args.update_oa = False
        args.filter_data = True
        args.output_osm = True
        args.update_osm = False
        args.merge = True
        args.quality_check = True
        args.slice = False
        args.build = False

    def test_failure(self):
        '''
        '''

    def test_success(self):
        '''
        Should always succeed
        us:ri consistently succeeds and small so runs quick
        '''
        args.area_list = ['us:ri']
        processing.main(args)
