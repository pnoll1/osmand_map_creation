import unittest
import logging
import processing
import types
from pathlib import Path

args = types.SimpleNamespace()


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
        
    def testFailureEmptyMasterlist(self):
        '''
        IndexError thrown when function tries access empty master list
        us:pr's one source gets thrown out due to osmium errors
        '''
        #with self.assertLogs(level='DEBUG') as log:
            #processing.main(args)
        #self.assertIn(['ERROR pg2osm fileinfo failure: OSM tag value is too long'], log.output)
        with self.assertRaises(IndexError):
            processing.main(args)
    
    def testSuccess(self):
        '''
        Should always succeed
        us:ri consistently succeeds and small so runs quick
        '''
        args.area_list = ['us:ri']
        processing.main(args)



