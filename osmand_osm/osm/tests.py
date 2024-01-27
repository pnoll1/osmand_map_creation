import unittest
from subprocess import run
import types
import logging
import datetime
from pathlib import Path

import psycopg

from config import DB_NAME, ID_START
import oa
import processing

time_current = datetime.datetime.today().isoformat()
log_filename = f'processing_test_{time_current}'
logging.basicConfig(filename=log_filename, level='DEBUG', format='%(asctime)s %(name)s %(levelname)s %(message)s')

# setup object to hold parser args
args = types.SimpleNamespace()

class UnitTests(unittest.TestCase):
    '''
    test each function with crafted minimal cases
    '''

    def setUp(self):
        self.conn = psycopg.connect(f'dbname={DB_NAME}')
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
        working_area = oa.WorkingArea('aa')
        working_area.create_master_list()
        self.assertEqual(4, len(working_area.master_list))
        #iso3166-2
        working_area = oa.WorkingArea('ab:aa')
        working_area.create_master_list()
        self.assertEqual(1, len(working_area.master_list))

    def test_load_oa(self):
        # cleanup postgres table
        self.cur.execute('drop table if exists aa_load_oa_addresses_city_temp')
        self.conn.commit()
        working_area = oa.WorkingArea('aa')
        working_area.master_list = [oa.Source(Path('aa/load-oa-addresses-city.geojson'))]
        run(['cp', 'aa/load-oa-addresses-city.geojson', 'aa/load-oa-addresses-city.geojson.bak'])
        run(['mv', 'data', 'data.bak'])
        run(['cp', '-n', 'aa/data.zip', 'data'])
        working_area.decompress_oa()
        working_area.load_oa('gis')
        run(['mv', 'aa/load-oa-addresses-city.geojson.bak', 'aa/load-oa-addresses-city.geojson'])
        run(['mv', 'data.bak', 'data'])
        self.cur.execute('select * from aa_load_oa_addresses_city_temp')
        data = self.cur.fetchall()
        # check for street
        self.assertRegex(data[0][4],'Di Mario Dr')
        # check for number
        self.assertRegex(data[0][3],'1')

    def test_filter_data(self):
        # cleanup postgres table
        self.cur.execute('drop table if exists aa_filter_data_addresses_city_temp')
        self.conn.commit()
        # load data into postgres
        self.cur.execute("create table aa_filter_data_addresses_city_temp (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                unit character varying, city character varying, district character varying, \
                region character varying, postcode character varying, hash character varying, \
                wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (1, '1', 'Di Mario Dr', '02904', '908f551defc1295a', 'POINT(-71.4188401 41.8572897)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (2, 'SN', 'CALLE EMILIO GARCÍA', '02904', '59a2672f7f81bc31', 'POINT(-102.2759162 21.8011834)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (3, '--', 'Linwood Ave', '02907', 'e1262d57e0077c2e', 'POINT(-71.4373704 41.8076377)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (4, '1127\b', 'TANGELOS ST', '93306', '11e4eb3ece546426', 'POINT(-118.901449 35.3685914)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (5, '2857', 'RAYMOND J REED \u001b SE', '', '45e2b88e896ed2e6', 'POINT(-107.7285659 32.2526736)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash) \
                values (%s, %s, %s, %s, %s)" \
                , (6, '119', 'MAIN ST', '', '5f1f1bb28879f693'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (7, '147', 'ABBOTSFORD Road', '4006', '183080127302f78f', 'POINT(0 0)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (8, '93', '', '1420', 'aaff5827c1009fba', 'POINT(4.381707 50.6860641)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (9, '14588', 'NE   ST', '98052', 'a37a7633f6dcb608', 'POINT(-122.1459303 47.6875332)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (10, '8528', 'AVE NE', '98052', '7304e2aa3d0db8df', 'POINT(-122.134164 47.6791909)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (11, '3724', 'S  141ST ST', '98168', 'f8380204c38d325d', 'POINT(-122.2853131 47.477565)'))
        self.cur.execute("insert into aa_filter_data_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (12, '171353', 'US-101', '98331', '', 'POINT(-124.3131452 47.7630055)'))
        self.conn.commit()
        working_area = oa.WorkingArea('aa')
        working_area.master_list = [oa.Source(Path('aa/filter-data-addresses-city.geojson'))]
        working_area.filter_data(DB_NAME)
        # check for empty street
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where street='' or street is null")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for --
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where number='--'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for illegal unicode in number
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where number ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for illegal unicode in street
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where street ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for SN
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where number='SN'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for records without geometry
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where wkb_geometry is null")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for records with geometry at 0,0
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where wkb_geometry='0101000020E610000000000000000000000000000000000000'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check for incomplete street
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where street='NE   ST' or street='AVE NE'")
        data = self.cur.fetchall()
        self.assertEqual(data,[])
        # check correct data still exists
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where street='S  141ST ST' and number='3724';")
        data = self.cur.fetchall()
        self.assertEqual(len(data), 1)
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where street='Di Mario Dr' and number='1';")
        data = self.cur.fetchall()
        self.assertEqual(len(data), 1)
        self.cur.execute("select * from aa_filter_data_addresses_city_temp where street='US-101' and number='171353';")
        data = self.cur.fetchall()
        self.assertEqual(len(data), 1)


    def test_merge_oa(self):
        '''       
        test additional data inserted from temp table when table already exists with data
        test that only 1 of each address gets inserted when there's duplicates
        '''
        # cleanup postgres table
        self.cur.execute("drop table if exists aa_merge_oa_addresses_city;")
        self.cur.execute("drop table if exists aa_merge_oa_addresses_city_temp;")
        self.conn.commit()
        # load data into postgres
        self.cur.execute("create table aa_merge_oa_addresses_city_temp (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                unit character varying, city character varying, district character varying, \
                region character varying, postcode character varying, hash character varying, \
                wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_merge_oa_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (4, '119', 'NW 41st ST', '98107', 'e8605a496593386e', 'POINT(-122.3580529 47.6561133)'))
        self.cur.execute("insert into aa_merge_oa_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (3, '115', 'NW 41st ST', '98107', '87d28792bee6b164', 'POINT(-122.3578935 47.6561136)'))
        # insert dupe test
        self.cur.execute("insert into aa_merge_oa_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (5, '71', 'Linwood Ave', '02907', 'e1262d57e0077c2e', 'POINT(-71.4373704 41.8076377)'))
        self.cur.execute("insert into aa_merge_oa_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (6, '71', 'Linwood Ave', '02907', 'e1262d57e0077c2e', 'POINT(-71.4373704 41.8076377)'))
        # create table
        self.cur.execute("create table aa_merge_oa_addresses_city (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                unit character varying, city character varying, district character varying, \
                region character varying, postcode character varying, hash character varying, \
                wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute('alter table aa_merge_oa_addresses_city add constraint aa_merge_oa_addresses_city_unique unique nulls not distinct (number, street, unit, wkb_geometry)')
        self.cur.execute("insert into aa_merge_oa_addresses_city (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (4, '119', 'NW 41st ST', '98107', 'e8605a496593386e', 'POINT(-122.3580529 47.6561133)'))
        self.conn.commit()
        working_area = oa.WorkingArea('aa')
        working_area.master_list = [oa.Source(Path('aa/merge-oa-addresses-city.geojson'))]
        working_area.merge_oa(DB_NAME)
        self.cur.execute("select * from aa_merge_oa_addresses_city;")
        data = self.cur.fetchall()
        # check that temp table copied over
        self.assertIn((3, None, '115', 'NW 41st ST', None, None, None, None, '98107', '87d28792bee6b164', '0101000020E6100000DD7C23BAE7965EC0FC3ACB87FBD34740'), data)
        self.assertIn((4, None, '119', 'NW 41st ST', None, None, None, None, '98107', 'e8605a496593386e', '0101000020E61000003BEFB556EA965EC03EFC4685FBD34740'), data)
        self.assertIn((5, None, '71', 'Linwood Ave', None, None, None, None, '02907', 'e1262d57e0077c2e', '0101000020E6100000430F6BE0FDDB51C0224212AC60E74440'), data)
        count = 0
        for address in data:
            if address[2] == '71':
                count += 1
        self.assertEqual(count, 1, 'deduping did not work')

    def test_merge_oa_first_run(self):
        '''
        test with temp table loading with no existing table
        '''
        # cleanup postgres table
        self.cur.execute("drop table if exists aa_merge_oa_addresses_city;")
        self.cur.execute("drop table if exists aa_merge_oa_addresses_city_temp;")
        self.conn.commit()
        # load data into postgres
        self.cur.execute("create table aa_merge_oa_addresses_city_temp (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, unit character varying, \
                city character varying, district character varying, region character varying, \
                postcode character varying, hash character varying, wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_merge_oa_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (1, '119', 'NW 41st ST', '98107', 'e8605a496593386e', 'POINT(-122.3580529 47.6561133)'))
        self.cur.execute("insert into aa_merge_oa_addresses_city_temp (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (2, '115', 'NW 41st ST', '98107', '87d28792bee6b164', 'POINT(-122.3578935 47.6561136)'))
        self.conn.commit()
        working_area = oa.WorkingArea('aa')
        working_area.master_list = [oa.Source(Path('aa/merge-oa-addresses-city.geojson'))]
        working_area.merge_oa(DB_NAME)
        self.cur.execute("select * from aa_merge_oa_addresses_city;")
        data = self.cur.fetchall()
        # check that temp table copied over
        self.assertIn((2, None, '115', 'NW 41st ST', None, None, None, None, '98107', '87d28792bee6b164', '0101000020E6100000DD7C23BAE7965EC0FC3ACB87FBD34740'), data)
        self.assertIn((1, None, '119', 'NW 41st ST', None, None, None, None, '98107', 'e8605a496593386e', '0101000020E61000003BEFB556EA965EC03EFC4685FBD34740'), data)

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
        working_area = oa.WorkingArea('aa')
        working_area.master_list = [oa.Source(Path('aa/output-osm-ids.geojson')) \
                , oa.Source(Path('aa/output-osm-ids2.geojson'))]
        working_area.output_osm(ID_START, DB_NAME)
        # check output files have ids different and descending
        run('osmium cat --no-progress -f osm aa/output-osm-ids_addresses.osm.pbf > aa/output-osm-ids_addresses.osm', shell=True)
        with open('aa/output-osm-ids_addresses.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, '17179869183', 'osm id did not start at right location')
        run('osmium cat --no-progress -f osm aa/output-osm-ids2_addresses.osm.pbf > aa/output-osm-ids2_addresses.osm', shell=True)
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
        self.cur.execute("create table aa_output_osm_addresses_city (ogc_fid integer NOT NULL, \
                id character varying, number character varying, street character varying, \
                city character varying, district character varying, region character varying, \
                postcode character varying, hash character varying, wkb_geometry public.geometry(Point, 4326));")
        self.cur.execute("insert into aa_output_osm_addresses_city (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (1, '1', 'Di Mario Dr', '02904', '908f551defc1295a', 'POINT(-71.4188401 41.8572897)'))
        self.cur.execute("insert into aa_output_osm_addresses_city (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (2, '500', '#A01 E CHERRY LN', '98926', '2dcd70d0ba3021b8', 'POINT(-120.540328 46.9862581)'))
        self.cur.execute("insert into aa_output_osm_addresses_city (ogc_fid, number, street, postcode, hash, wkb_geometry) \
                values (%s, %s, %s, %s, %s, ST_GEOMFromText(%s, 4326))" \
                , (3, '500', '#A02 E CHERRY LN', '98926', 'bc0d5eb064e9d91a', 'POINT(-120.540328 46.9862581)'))
        self.conn.commit()
        working_area = oa.WorkingArea('aa')
        working_area.master_list = [oa.Source(Path('aa/output-osm-addresses-city.geojson'))]
        working_area.output_osm(ID_START, DB_NAME)
        run('osmium cat --no-progress -f osm aa/output-osm-addresses-city_addresses.osm.pbf > aa/output-osm-addresses-city_addresses.osm', shell=True)
        with open('aa/output-osm-addresses-city_addresses.osm') as test_file:
            file_text = test_file.read()
            self.assertRegex(file_text, 'Di Mario Dr')
            # check that ogr2osm doesn't merge
            self.assertRegex(file_text, '\"#A01 E CHERRY LN\"')

    def test_slice_do_nothing(self):
        slice_config = {}
        slice_config['au'] = [['north', '95.888672,-8.00000,163.081055,-30.372875'],['southwest', '95.888672,-30.372875,140,-51.672555'],['southeast','140,-51.672555,163.081055,-30.372875']]
        working_area = oa.WorkingArea('aa')
        sliced_area = working_area.slice(slice_config)
        self.assertEqual(sliced_area, None)

    def test_slice(self):
        slice_config = {}
        slice_config['aa'] = [['north', '-79.75,27.079,-87.759,31.171'], ['south', '-79.508,24.237,-82.579,27.079']]
        working_area = oa.WorkingArea('aa')
        sliced_area = working_area.slice(slice_config)
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
        args.merge_oa = True
        args.filter_data = True
        args.output_osm = True
        args.update_osm = False
        args.merge = True
        args.quality_check = True
        args.slice = False
        args.build = False
        args.calculate_hashes = False

    def tearDown(self):
        run(['mv', '../us_ri.osm.pbf', './us_ri_test.osm.pbf'])

    def test_success(self):
        '''
        Should always succeed
        us:ri consistently succeeds and small so runs quick
        '''
        args.area_list = ['us:ri']
        processing.main(args)
        with open(log_filename) as log_file:
            file_text = log_file.read()
            self.assertNotRegex(file_text, 'ERROR')

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
        args.merge_oa = True
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
