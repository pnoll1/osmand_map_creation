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
    'CIR':'Circle',
    'RD':'Road',
    'EXT':'Extension',
    'ST':'Street',
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
    'CONN': 'Connector',
    'E':'East',
    'S':'South',
    'N':'North',
    'W':'West',
    'SE':'Southeast',
    'NE':'Northeast',
    'SW':'Southwest',
    'NW':'Northwest'}

    newName = ''
    newName = suffixlookup.get(rawname.upper(),rawname.title())
    return newName

def filterTags(attrs):
    if not attrs:
        return
    # raw variables
    address_number = 'HOUSE_NUM'
    #AddSfx 1/2 & B
    pre_dir_raw = 'PRE_DIR'
    #prefix_raw = 'StPrefix' # HWY or AVE
    street_name_raw = 'ST_NAME'
    street_type_raw = 'ST_TYPE'
    post_dir_raw = '' #not used
    city = 'CITY'
    #bldg_raw = 'PrUnitID'
    unit_raw = 'SUB_UNIT' # 'Apt'
    postcode_raw = 'ZIPCODE'
    # processed variables
    addr = ''
    pre_dir = ''
    #prefix = ''
    street = ''
    street_type = ''
    post_dir = ''
    tags = {}
    if address_number in attrs and attrs[address_number] != '':
        tags['addr:housenumber'] = attrs[address_number]
    if unit_raw in attrs and attrs[unit_raw] != '':
        tags['addr:unit'] = attrs[unit_raw]
    if pre_dir_raw in attrs and attrs[pre_dir_raw] != '':
        pre_dir = translateName(attrs[pre_dir_raw])
   #if prefix_raw in attrs and attrs[prefix_raw] != '':
   #    prefix = translateName(attrs[prefix_raw])
    if street_name_raw in attrs and attrs[street_name_raw] != '':
        if re.search(r'^\d', attrs[street_name_raw]) is not None:
            street = attrs[street_name_raw].lower()
        else:
            street = attrs[street_name_raw].title()
    if post_dir_raw in attrs and attrs[post_dir_raw] != '':
        post_dir = translateName(attrs[post_dir_raw])
    if street_type_raw in attrs and attrs[street_type_raw] != '':
        street_type = translateName(attrs[street_type_raw])

    if pre_dir:
        addr = pre_dir + ' ' + street
    else:
        addr = street
    if street_type:
        addr = addr + ' ' + street_type
    if post_dir:
        addr = addr + ' ' + post_dir
    tags['addr:street'] = addr
    if city in attrs and attrs[city] != '':
        if attrs[city] == 'COEUR D ALENE':
            tags['addr:city'] = "Coeur d'Alene"
        else:
            tags['addr:city'] = attrs[city].title()
    if postcode_raw in attrs and attrs[postcode_raw] != '':
        tags['addr:postcode'] = attrs[postcode_raw]

    return tags
