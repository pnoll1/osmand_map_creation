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
        self.cur.execute('drop table if exists aa_filter_data_addresses_city')
        self.conn.commit()
        # load data into postgres
        run('psql -d gis < $PWD/aa/filter_data_addresses_city.sql',shell=True)
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/filter-data-addresses-city.geojson'))]
        processing.filter_data(working_area, 'gis')
        # check for empty street
        self.cur.execute("select * from aa_filter_data_addresses_city where street='' or street is null")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
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
        data = self.cur.fetchall()
        self.assertEqual(data,[]) 
        # check for records with geometry at 0,0
        self.cur.execute("select * from aa_filter_data_addresses_city where wkb_geometry='0101000020E610000000000000000000000000000000000000'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])

    def test_output_osm_ids(self):
        '''
        make sure address ids in output files don't overlap
        '''
        # cleanup tables
        self.cur.execute('drop table if exists aa_output_osm_ids')
        self.cur.execute('drop table if exists aa_output_osm_ids2')
        self.conn.commit()
        # setup tables
        self.cur.execute("create table aa_output_osm_ids (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                city character varying, district character varying, region character varying, \
                postcode character varying, hash character varying, wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_output_osm_ids (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (2, '71', 'Linwood Ave', '02907', 'e1262d57e0077c2e', 'POINT(-71.4373704 41.8076377)'))
        self.cur.execute("create table aa_output_osm_ids2 (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                city character varying, district character varying, region character varying, \
                postcode character varying, hash character varying, wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_output_osm_ids2 (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (3, '1', 'Di Mario Dr', '02904', '908f551defc1295a', 'POINT(-71.4188401 41.8572897)'))
        self.conn.commit()
        working_area = processing.WorkingArea('aa')
        working_area.master_list = [processing.Source(Path('aa/output-osm-ids.geojson')) \
                , processing.Source(Path('aa/output-osm-ids2.geojson'))]
        db_name = 'gis'
        id = 2**34
        processing.output_osm(working_area, id, db_name)
        # check output files have ids different and descending
        with open('aa/output-osm-ids_addresses.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, '17179869183', 'osm id did not start at right location')
        with open('aa/output-osm-ids2_addresses.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, '17179869182', 'osm id did not decrease in second file')
        self.conn.commit()

    def test_output_osm_merge(self):
        '''
        make sure osm doesn't merge addresses at same position
        '''
        # cleanup postgres table
        self.cur.execute('drop table if exists aa_output_osm_addresses_city')
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

    def test_slice_do_nothing(self):
        slice_config = {}
        slice_config['au'] = [['north', '95.888672,-8.00000,163.081055,-30.372875'],['southwest', '95.888672,-30.372875,140,-51.672555'],['southeast','140,-51.672555,163.081055,-30.372875']]
        working_area = processing.WorkingArea('aa')
        sliced_area = processing.slice(working_area, slice_config)
        self.assertEqual(sliced_area, None)

    def test_slice(self):
        slice_config = {}
        slice_config['aa'] = [['north', '-79.75,27.079,-87.759,31.171'], ['south', '-79.508,24.237,-82.579,27.079']]
        working_area = processing.WorkingArea('aa')
        sliced_area = processing.slice(working_area, slice_config)
        # check function output
        self.assertEqual(sliced_area, slice_config['aa'])
        # check file output
        run('osmium cat --no-progress -f osm aa/aa_south.osm.pbf > aa/aa_south.osm', shell=True)
        with open('aa/aa_south.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, 'SW 223 ST')
        run('osmium cat --no-progress -f osm aa/aa_north.osm.pbf > aa/aa_north.osm', shell=True)
        with open('aa/aa_north.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, 'OLD BELLAMY RD')

class IntegrationTests(unittest.TestCase):
    '''
    runs on real data from oa to check if program and data are as expected
    requires oa and osm data already downloaded
    '''
    def setUp(self):
        args.area_list = ['']
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

class BuildTests(unittest.TestCase):
    '''
    runs build with real data
    requires oa and osm already downloaded
    '''
    def setUp(self):
        args.area_list = ['']
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
        args.slice = True
        args.build = True
        args.calculate_hashes = False

    def test_ri(self):
        '''
        build ri using data on hand
        '''
        args.area_list = ['us:ri']
        processing.main(args)
