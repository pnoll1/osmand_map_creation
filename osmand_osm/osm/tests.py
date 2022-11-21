import unittest
from subprocess import run
import types
import logging
import datetime
from pathlib import Path
import psycopg2
import processing

logging.basicConfig(filename='processing_test_{0}.log'.format(datetime.datetime.today().isoformat()), level='DEBUG', format='%(asctime)s %(name)s %(levelname)s %(message)s')

# setup object to hold parser args
args = types.SimpleNamespace()

class UnitTests(unittest.TestCase):
    '''
    test each function with crafted minimal cases
    '''

    def setUp(self):
        self.conn = psycopg2.connect('dbname=gis')
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.rollback()
        self.cur.close()
        self.conn.close()

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

    def test_load_oa_first_run(self):
        # cleanup postgres table
        self.cur.execute('drop table if exists aa_load_oa_addresses_city')
        self.conn.commit()
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/load-oa-addresses-city.geojson'))]
        processing.load_oa(working_area, 'gis')
        self.cur.execute('select * from aa_load_oa_addresses_city')
        data = self.cur.fetchall()
        # check for street
        self.assertRegex(data[0][4],'Di Mario Dr')
        # check for number
        self.assertRegex(data[0][3],'1')

    def test_load_oa(self):
        '''
        ensure overwriting table works
        '''
        # cleanup postgres table
        self.cur.execute('drop table if exists aa_load_oa_addresses_city')
        self.conn.commit()
        # load data into postgres
        self.cur.execute("create table aa_load_oa_addresses_city (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                city character varying, district character varying, region character varying, \
                postcode character varying, hash character varying, wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_load_oa_addresses_city (ogc_fid, number, street) values (%s, %s, %s)", (3, '2', 'Luigi Dr'))
        self.conn.commit()
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/load-oa-addresses-city.geojson'))]
        processing.load_oa(working_area, 'gis')
        self.cur.execute('select * from aa_load_oa_addresses_city')
        data = self.cur.fetchall()
        # check for street
        self.assertRegex(data[0][4],'Di Mario Dr')
        # check for number
        self.assertRegex(data[0][3],'1')

    def test_filter_data(self):
        # cleanup postgres table
        self.cur.execute('drop table aa_filter_data_addresses_city')
        self.conn.commit()
        # load data into postgres
        run('psql -d gis < $PWD/aa/filter_data_addresses_city.sql',shell=True)
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/filter-data-addresses-city.geojson'))]
        processing.filter_data(working_area, 'gis')
        # check for --
        self.cur.execute("select * from aa_filter_data_addresses_city where number='--'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for illegal unicode in number
        self.cur.execute("select * from aa_filter_data_addresses_city where number ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';")
        data = self.cur.fetchall()
        self.assertEqual(data,[]) 
        # check for illegal unicode in street
        self.cur.execute("select * from aa_filter_data_addresses_city where street ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';")
        data = self.cur.fetchall()
        self.assertEqual(data,[]) 
        # check for SN
        self.cur.execute("select * from aa_filter_data_addresses_city where number='SN'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for records without geometry
        self.cur.execute("select * from aa_filter_data_addresses_city where wkb_geometry is null")
        # check for records with geometry at 0,0
        self.cur.execute("select * from aa_filter_data_addresses_city where wkb_geometry='0101000020E610000000000000000000000000000000000000'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])

    def test_output_osm(self):
        # cleanup postgres table
        self.cur.execute('drop table aa_output_osm_addresses_city')
        self.conn.commit()
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
        args.calculate_hashes = False

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
