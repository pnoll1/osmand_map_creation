"""
Translation rules
Copyright 2019
"""
#import str
import re

suffixlookup = {
    'AVE': 'Avenue',
    'AV': 'Avenue',
    'CIR': 'Circle',
    'CI': 'Circle',
    'RD': 'Road',
    'EXT': 'Extension',
    'ST': 'Street',
    'PL': 'Place',
    'WY': 'Way',
    'CRES': 'Crescent',
    'BLVD': 'Boulevard',
    'DR': 'Drive',
    'LN': 'Lane',
    'LN RD': 'Lane Road',
    'LANE': 'Lane',
    'LP': 'Loop',
    'CT': 'Court',
    'CRT': 'Court',
    'GR': 'Grove',
    'CL': 'Close',
    'TER': 'Terrace',
    'TRL': 'Trail',
    'AVE CT': 'Avenue Court',
    'AVE PL': 'Avenue Place',
    'ST CT': 'Street Court',
    'ST PL': 'Street Place',
    'HL': 'Hill',
    'VW': 'View',
    'PKWY': 'Parkway',
    'RWY': 'Railway',
    'DIV': 'Diversion',
    'HWY': 'Highway',
    'CONN': 'Connector'
}

dirlookup = {
    'E': 'East',
    'S': 'South',
    'N': 'North',
    'W': 'West',
    'SE': 'Southeast',
    'NE': 'Northeast',
    'SW': 'Southwest',
    'NW': 'Northwest'
}

stlookup = {
    'ST': 'Saint',
    'LK': 'Lake',
    'SQ': 'Square',
    'MTN': 'Mountain',
    'RD': 'Road',
    'HWY': 'Highway'
}

srlookup = {
    'SR': 'State Route'
}


def translateName(rawname):
    '''
    A general purpose name expander.
    '''
    suffixlookup = {
        'AVE': 'Avenue',
        'AV': 'Avenue',
        'CIR': 'Circle',
        'CI': 'Circle',
        'RD': 'Road',
        'EXT': 'Extension',
        'ST': 'Street',
        'PL': 'Place',
        'WY': 'Way',
        'CRES': 'Crescent',
        'BLVD': 'Boulevard',
        'DR': 'Drive',
        'LN': 'Lane',
        'LN RD': 'Lane Road',
        'LANE': 'Lane',
        'LP': 'Loop',
        'CT': 'Court',
        'CRT': 'Court',
        'GR': 'Grove',
        'CL': 'Close',
        'TER': 'Terrace',
        'TRL': 'Trail',
        'AVE CT': 'Avenue Court',
        'AVE PL': 'Avenue Place',
        'ST CT': 'Street Court',
        'ST PL': 'Street Place',
        'HL': 'Hill',
        'VW': 'View',
        'PKWY': 'Parkway',
        'RWY': 'Railway',
        'DIV': 'Diversion',
        'HWY': 'Highway',
        'CONN': 'Connector'
    }

    newName = ''
    newName = suffixlookup.get(rawname.upper(), rawname.title())
    return newName


def translateDir(rawname):

    dirlookup = {
        'E': 'East',
        'S': 'South',
        'N': 'North',
        'W': 'West',
        'SE': 'Southeast',
        'NE': 'Northeast',
        'SW': 'Southwest',
        'NW': 'Northwest'
    }

    newName = ''
    newName = dirlookup.get(rawname.upper(), rawname.title())
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
    # handle E ST E, postdir
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
    # handle SR 20
    elif len(street_array) == 2 and street_array[0].upper() in srlookup.keys():
        street = srlookup.get(street_array[0].upper()) + ' ' + street_array[1]
    # handle no dir
    else:
        for i in street_array[:-1]:
            street = normalize_interior(i, street)
        street = street + ' ' + translateName(street_array[-1])
        street = street.lstrip()
    return street

def filterTags(attrs):
    if not attrs:
        return
    # raw variables
    address_number = 'addrnum'
    pre_dir_raw = ''
    street_name_raw = 'fullname'
    street_type_raw = ''
    post_dir_raw = ''
    city = 'newcitst'
    unit_raw = '' # 'Apt'
    postcode_raw = 'newzip'

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

    tags['addr:street'] = expand_street(attrs[street_name_raw])
    if city in attrs and attrs[city] != '':
        tags['addr:city'] = attrs[city].title()
    if postcode_raw in attrs and attrs[postcode_raw] != '':
        tags['addr:postcode'] = attrs[postcode_raw]

    return tags
