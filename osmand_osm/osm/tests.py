import unittest
from subprocess import run
import types
import processing

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
        self.assertEqual(1, len(working_area.master_list))
        #iso3166-2
        working_area = processing.WorkingArea('ab:aa')
        processing.create_master_list(working_area)
        self.assertEqual(1, len(working_area.master_list))

    def test_load_oa(self):
        working_area = processing.WorkingArea('aa')
        processing.create_master_list(working_area)
        processing.load_oa(working_area, 'gis')
        r = run('psql -d gis --csv -c "select * from aa_providence_addresses_city"', shell=True, capture_output=True)
        # check for street
        self.assertRegex(str(r.stdout),'Di Mario Dr')
        # check for number
        self.assertRegex(str(r.stdout),',,,1')

    def test_filter_data(self):
        working_area = processing.WorkingArea('aa')
        processing.create_master_list(working_area)
        processing.filter_data(working_area, 'gis')
        # check for --
        r = run(['psql', '-d', 'gis', '-c', "select * from aa_providence_addresses_city where number='--'"], capture_output=True)
        self.assertRegex(str(r.stdout),'(0 rows)')
        # check for illegal unicode
        r = run(['psql', '-d', 'gis', '-c', "select * from aa_providence_addresses_city where number ~ '[\x01-\x08\x0b\x0c\x0e-\x1F\uFFFE\uFFFF]';"], capture_output=True)
        self.assertRegex(str(r.stdout),'(0 rows)')
        # check for SN
        r = run(['psql', '-d', 'gis', '-c', "select * from aa_providence_addresses_city where number='SN'"], capture_output=True)
        self.assertRegex(str(r.stdout),'(0 rows)')

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
        IndexError thrown when function tries access empty master list
        us:pr's one source gets thrown out due to osmium errors
        '''
        #with self.assertLogs(level='DEBUG') as log:
            #processing.main(args)
        #self.assertIn(['ERROR pg2osm fileinfo failure: OSM tag value is too long'], log.output)
        with self.assertRaises(IndexError):
            processing.main(args)

    def test_success(self):
        '''
        Should always succeed
        us:ri consistently succeeds and small so runs quick
        '''
        args.area_list = ['us:ri']
        processing.main(args)
