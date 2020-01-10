"""
Translation rules
Copyright 2019
"""
#import str
import re

suffixlookup = {
'AVE':'Avenue',
'AV':'Avenue',
'CIR':'Circle',
'CI':'Circle',
'RD':'Road',
'EXT':'Extension',
'ST':'Street',
'PL':'Place',
'WY':'Way',
'CRES':'Crescent',
'BLVD':'Boulevard',
'DR':'Drive',
'LN':'Lane',
'LN RD':'Lane Road',
'LANE':'Lane',
'LP':'Loop',
'CT':'Court',
'CRT':'Court',
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
'PKWY':'Parkway',
'RWY':'Railway',
'DIV':'Diversion',
'HWY':'Highway',
'CONN': 'Connector'
}

dirlookup = {
'E':'East',
'S':'South',
'N':'North',
'W':'West',
'SE':'Southeast',
'NE':'Northeast',
'SW':'Southwest',
'NW':'Northwest'}

stlookup = {
'ST':'Saint',
'LK':'Lake',
'SQ':'Square',
'MTN':'Mountain',
'RD':'Road',
'HWY':'Highway'
}

def translateName(rawname):
    '''
    A general purpose name expander.
    '''
    suffixlookup = {
    'AVE':'Avenue',
    'AV':'Avenue',
    'CIR':'Circle',
    'CI':'Circle',
    'RD':'Road',
    'EXT':'Extension',
    'ST':'Street',
    'PL':'Place',
    'WY':'Way',
    'CRES':'Crescent',
    'BLVD':'Boulevard',
    'DR':'Drive',
    'LN':'Lane',
    'LN RD':'Lane Road',
    'LANE':'Lane',
    'LP':'Loop',
    'CT':'Court',
    'CRT':'Court',
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
    'PKWY':'Parkway',
    'RWY':'Railway',
    'DIV':'Diversion',
    'HWY':'Highway',
    'CONN': 'Connector'
    }
    
    newName = ''
    newName = suffixlookup.get(rawname.upper(),rawname.title())
    return newName
    
def translateDir(rawname):
    
    dirlookup = {
    'E':'East',
    'S':'South',
    'N':'North',
    'W':'West',
    'SE':'Southeast',
    'NE':'Northeast',
    'SW':'Southwest',
    'NW':'Northwest'}

    newName = ''
    newName = dirlookup.get(rawname.upper(),rawname.title())
    return newName

def expand_street(addr):
    street_array = addr.split(' ')
    street = ''
    def normalize_interior(i, street):
        if re.search(r'^\d', i) is not None:
            street = street + ' ' + i.lower()
        elif i.upper() in stlookup.keys():
            street = street + ' ' + stlookup.get(i.upper())
        else:
            street = street + ' ' + i.title()
        return street
    # handle E E ST
    if street_array[0].upper() in dirlookup.keys() and street_array[1].upper() in dirlookup.keys() and len(street_array) > 2:
        for i in street_array[1:-1]:
            street = normalize_interior(i, street)
        street = translateDir(street_array[0]) + street + ' ' + translateName(street_array[-1])
    # handle E ST E postdir
    elif street_array[-1].upper() in dirlookup.keys():
        for i in street_array[:-2]:
            street = normalize_interior(i, street)
        street = street + ' ' + translateName(street_array[-2]) + ' ' + translateDir(street_array[-1])
        street = street.lstrip()
    # handle predir
    elif street_array[0].upper() in dirlookup.keys() and len(street_array) > 2:
        for i in street_array[1:-1]:
            street = normalize_interior(i, street)
        street = translateDir(street_array[0]) + street + ' ' + translateName(street_array[-1])
    # handle no dir
    else:
        for i in street_array[:-1]:
            street = normalize_interior(i, street)
        street = street + ' ' + translateName(street_array[-1])
        street = street.lstrip()
    return street

# test cases
test_addresses = ['E ST', 'E E ST', 'E ST E', '11TH ST', 'E 11TH ST', '11TH ST E', 'E MARYLAND ST', 'E 2ND ST', 'ST PAUL ST', 'LIMERICK WAY', 'N COLUMBIA CENTER BLVD', 'HWY 28 E', 'RD 28 NE']
answer_addresses = ['E Street', 'East E Street', 'E Street East', '11th Street', 'East Maryland Street', 'East Maryland Street', 'East 2nd Street', 'Saint Paul Street', 'Limerick Way', 'North Columbia Center Boulevard', 'Highway 28 East']
'''
test_address = 'E ST'
test_address2 = '11TH ST'
test_address2_predir = 'E 11TH ST'
test_address2_postdir = '11TH ST E'
test_address3 = 'E MARYLAND ST'
test_address4 = 'E 2ND ST'
test_address5 = 'ST PAUL ST'
test_address6 = 'LIMERICK WAY'
test_address7 = 'E ST E'
test_address8 = 'E E ST'
test_address9 = 'N COLUMBIA CENTER BLVD'
HWY 28 E
'''

def filterTags(attrs):
    if not attrs:
        return
    # raw variables
    address_number = 'number'
    pre_dir_raw = ''
    street_name_raw = 'street'
    street_type_raw = ''
    post_dir_raw = ''
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
    tags['addr:street'] = expand_street(attrs[street_name_raw])
    if city in attrs and attrs[city] != '':
        tags['addr:city'] = attrs[city].title()
    if postcode_raw in attrs and attrs[postcode_raw] != '':
        tags['addr:postcode'] = attrs[postcode_raw]

    return tags


