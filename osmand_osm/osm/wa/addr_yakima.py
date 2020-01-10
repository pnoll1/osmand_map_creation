"""
Translation rules
Copyright 2019
"""
#import str
import re

def translateName(rawname):
    '''
    A general purpose name expander.
    '''
    suffixlookup = {
    'AVE':'Avenue',
    'AVE.':'Avenue',
    'CIR':'Circle',
    'RD':'Road',
    'RD.':'Road',
    'EXT':'Extension',
    'FRK':'Fork',
    'ST':'Street',
    'STR':'Street',
    'PL':'Place',
    'CRES':'Crescent',
    'BLVD':'Boulevard',
    'DR':'Drive',
    'LN':'Lane',
    'LN RD':'Lane Road',
    'LANE':'Lane',
    'LP':'Loop',
    'CT':'Court',
    'CRT':'Court',
    'CR':'Creek',
    'CRK':'Creek',
    'GR':'Grove',
    'CL':'Close',
    'TER': 'Terrace',
    'TRL':'Trail',
    'AVE CT': 'Avenue Court',
    'AVE PL': 'Avenue Place',
    'ST CT': 'Street Court',
    'ST PL': 'Street Place',
    'HL': 'Hill',
    'VW' : 'View',
    'WY':'Way',
    'PKY':'Parkway',
    'PKWY':'Parkway',
    'RWY':'Railway',
    'DIV':'Diversion',
    'HWY':'Highway',
    'CONN': 'Connector',
    'SR':'State Route'
    }
    
    newName = ''
    newName = suffixlookup.get(rawname.upper(),rawname.title())
    return newName
    
def translateDir(rawname):
    
    suffixlookup = {
    'E':'East',
    'S':'South',
    'N':'North',
    'N.':'North',
    'W':'West',
    'SE':'Southeast',
    'NE':'Northeast',
    'SW':'Southwest',
    'NW':'Northwest'}

    newName = ''
    newName = suffixlookup.get(rawname.upper(),rawname.title())
    return newName

    # expand street name field into pre_dir, street, type
def expand_street(street_name_raw):
    #street_name_array = attrs[street_name_raw].split(' ')
    street_name_array = street_name_raw.split(' ')
    street = ''
    street_name = street_name_array[:-1]
    # handles St Thomas Street case
    street_type = translateName(street_name_array[-1])
    # handle E St case, N 1st
    if len(street_name_array) == 2:
        street_name = street_name[0]
        if re.search(r'^\d', street_name) is not None:
            street_next = street_name.lower()
            street = street_next + ' ' + street_type
        else:
            street = street_name.title()
            street = street + ' ' + street_type
    # handle standard case
    else:
        for i in street_name:
            if re.search(r'^\d', i) is not None:
                street_next = i.lower()
                street = street + ' ' + street_next
            else:
                street_next = translateDir(i)
                street = street + ' ' + street_next
        street = street + ' ' + translateName(street_type)
        street = street.lstrip()
    return street

# test cases
# whatcom
test_address = 'E ST'
test_address2 = '11TH ST'
test_address3 = 'E MARYLAND ST'
test_address4 = 'E 2ND ST'
test_address5 = 'ST PAUL ST'
test_address6 = 'LIMERICK WAY'
# yakima
# McCracken Avenue
test_address7 = 'MC CRACKEN AVE'
test_address8 = '5TH AVE S APT 605'
test_address9 = 'MAPLE AVE #9'
test_address10 = 'S 65TH AVE UNITS 1-2'
test_address11 = 'S 69TH AVE #AB'
test_address12 = 'E E ST'
test_address13 = 'E N ST'
test_address14 = 'E S ST'


def filterTags(attrs):
    if not attrs:
        return
    # raw variables
    address_number = 'number'
    pre_dir_raw = 'PREFIX'
    street_name_raw = 'street'
    street_type_raw = 'STREETTYPE'
    post_dir_raw = 'SUFFIX'
    city = 'city'
    unit_raw = 'unit' # 'Apt'
    postcode_raw = 'postcode'
    # processed variables
    addr = ''
    pre_dir = ''
    street_type = ''
    post_dir = ''
    tags = {}
    if address_number in attrs and attrs[address_number] != '':
        tags['addr:housenumber'] = attrs[address_number]
    #if 'Unit' in attrs and attrs['Unit'] != '':
    #   tags['addr:unit'] = attrs['Unit']
    if pre_dir_raw in attrs and attrs[pre_dir_raw] != '':
        pre_dir = translateName(attrs[pre_dir_raw])
    '''if street_name_raw:
        if re.search(r'^\d', attrs[street_name_raw]) is not None:
            street = attrs[street_name_raw].lower()
        else:
            street = attrs[street_name_raw].title()
    '''
    if post_dir_raw in attrs and attrs[post_dir_raw] != '':
        post_dir = translateName(attrs[post_dir_raw])
    '''if street_type_raw in attrs and attrs[street_type_raw] != '':
        street_type = translateName(attrs[street_type_raw])
    
    if pre_dir:
        addr = pre_dir + ' ' + street
    else:
        addr = street
    if street_type:
        addr = addr + ' ' + street_type
    if post_dir:
        addr = addr + ' ' + post_dir
    '''
    # split address at first '#', UNIT or APT and add that to unit
    tags['addr:street'] = expand_street(attrs[street_name_raw])
    if city in attrs and attrs[city] != '':
        tags['addr:city'] = attrs[city].title()
    if postcode_raw in attrs and attrs[postcode_raw] != '':
        tags['addr:postcode'] = attrs[postcode_raw]

    return tags
