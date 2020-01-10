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

    tags = {}
    if 'HouseNumbe' in attrs and attrs['HouseNumbe'] != '':
        tags['addr:housenumber'] = attrs['HouseNumbe']
    #if 'UNIT' in attrs and attrs['UNIT'] != '':
    #   tags['addr:unit'] = attrs['UNIT']
    addr = ''
    pre_dir = ''
    street_type = ''
    post_dir = ''
    if 'PrefixDire' in attrs and attrs['PrefixDire'] != '':
        pre_dir = translateName(attrs['PrefixDire'])
    if 'StreetName' in attrs and attrs['StreetName'] != '':
        if re.search(r'^\d', attrs['StreetName']) is not None:
            street = attrs['StreetName'].lower()
        else:
            street = attrs['StreetName'].title()
    if 'PostDirect' in attrs and attrs['PostDirect'] != '':
        post_dir = translateName(attrs['PostDirect'])
    if 'StreetType' in attrs and attrs['StreetType'] != '':
        street_type = translateName(attrs['StreetType'])
    
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
    if 'City' in attrs and attrs['City'] != '':
        tags['addr:city'] = attrs['City'].title()
    if 'ZipCode' in attrs and attrs['ZipCode'] != '':
        tags['addr:postcode'] = attrs['ZipCode']

    return tags
