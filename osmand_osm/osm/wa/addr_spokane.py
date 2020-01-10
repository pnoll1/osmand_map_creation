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
    address_number = 'ADDRNUM'
    pre_dir_raw = 'PrefixDire'
    street_name_raw = 'StreetName'
    street_type_raw = 'StreetType'
    post_dir_raw = ''
    city = 'CITY'
    postcode_raw = ''
    unit_raw = '' # 'UNITID'
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
    '''
    # predir, streetname, street type
    if 'PrefixDire' in attrs and attrs['PrefixDire'] != '' and 'StreetName' in attrs and attrs['StreetName'] != '' and 'StreetType' in attrs and attrs['StreetType'] != '':
        # numbered street
        if re.search(r'^\d', attrs['StreetName']) is not None:
            address_street = attrs['StreetName'].lower()
            tags['addr:street'] = translateName(attrs['PrefixDire']) + ' ' + address_street + ' ' + translateName(attrs['StreetType'])
        tags['addr:street'] = translateName(attrs['PrefixDire']) + ' ' + attrs['StreetName'].title() + ' ' + translateName(attrs['StreetType'])
    # postdir, streetname, street type
    if 'StreetName' in attrs and attrs['StreetName'] != '' and 'StreetType' in attrs and attrs['StreetType'] != '' and 'PostDirect' in attrs and attrs['PostDirect'] != '':
        # numbered street
        if re.search(r'^\d', attrs['StreetName']) is not None:
            address_street = attrs['StreetName'].lower()
            tags['addr:street'] = address_street + ' ' + translateName(attrs['StreetType']) + ' ' + translateName(attrs['PostDirect'])
        else:
            tags['addr:street'] = attrs['StreetName'].title() + ' ' + translateName(attrs['StreetType']) + ' ' + translateName(attrs['PostDirect'])
    # no dir, street name, street type
    if 'StreetName' in attrs and attrs['StreetName'] != '' and 'StreetType' in attrs and attrs['StreetType'] != '' and 'PostDirect' not in attrs and 'PrefixDire' not in attrs:
        # numbered street
        if re.search(r'^\d', attrs['StreetName']) is not None:
            address_street = attrs['StreetName'].lower()
            tags['addr:street'] = address_street + ' ' + translateName(attrs['StreetType'])
        else:
            tags['addr:street'] = attrs['StreetName'].title() + ' ' + translateName(attrs['StreetType'])
    # predir, streetname, no street type
    if 'PrefixDire' in attrs and attrs['PrefixDire'] != '' and 'StreetName' in attrs and attrs['StreetName'] != '' and 'StreetType' not in attrs:
         # numbered street
        if re.search(r'^\d', attrs['StreetName']) is not None:
            address_street = attrs['StreetName'].lower()
            tags['addr:street'] = translateName(attrs['PrefixDire']) + ' ' + address_street
        tags['addr:street'] = translateName(attrs['PrefixDire']) + ' ' + attrs['StreetName'].title()
    # postdir,street name, no street type
    if 'StreetName' in attrs and attrs['StreetName'] != '' and 'PostDirect' in attrs and attrs['PostDirect'] != '' and 'StreetType' not in attrs:
        # numbered street
        if re.search(r'^\d', attrs['StreetName']) is not None:
            address_street = attrs['StreetName'].lower()
            tags['addr:street'] = address_street + ' ' + translateName(attrs['PostDirect'])
        else:
            tags['addr:street'] = attrs['StreetName'].title() + ' ' + translateName(attrs['PostDirect'])
    # street name only
    if 'StreetName' in attrs and attrs['StreetName'] != '' and 'PostDirect' not in attrs and 'PrefixDire' not in attrs and 'StreetType' not in attrs:
        tags['addr:street'] = attrs['StreetName'].title()
    '''
    if city in attrs and attrs[city] != '':
        tags['addr:city'] = attrs[city].title()
    if postcode_raw in attrs and attrs[postcode_raw] != '':
        tags['addr:postcode'] = attrs[postcode_raw]

    return tags
