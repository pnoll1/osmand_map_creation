import unittest
from addr_island import expand_street

# test cases
test_addresses = ['E ST', 'E E ST', 'E ST E', '11TH ST', 'E 11TH ST', '11TH ST E', 'E MARYLAND ST', 'E 2ND ST', 'ST PAUL ST', 'LIMERICK WAY', 'N COLUMBIA CENTER BLVD', 'HWY 28 E', 'SR 20']
answer_addresses = ['E Street', 'East E Street', 'E Street East', '11th Street','East 11th Street', '11th Street East', 'East Maryland Street', 'East 2nd Street', 'Saint Paul Street', 'Limerick Way', 'North Columbia Center Boulevard', 'Highway 28 East', 'State Route 20']


class TestAddressExpansion(unittest.TestCase):

    def test(self):
        i = 0
        while i < len(test_addresses):
            self.assertEqual(expand_street(test_addresses[i]), answer_addresses[i])
            i += 1
