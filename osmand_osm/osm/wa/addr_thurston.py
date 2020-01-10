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
    if 'Add_Number' in attrs and attrs['Add_Number'] != '':
        tags['addr:housenumber'] = attrs['Add_Number']
    #if 'Unit' in attrs and attrs['Unit'] != '':
    #   tags['addr:unit'] = attrs['Unit']
    addr = ''
    pre_dir = ''
    street_type = ''
    post_dir = ''
    if 'St_PreTyp' in attrs and attrs['St_PreTyp'] != '':
        pre_dir = translateName(attrs['St_PreTyp'])
    if 'StreetName' in attrs and attrs['StreetName'] != '':
        if re.search(r'^\d', attrs['StreetName']) is not None:
            street = attrs['StreetName'].lower()
        else:
            street = attrs['StreetName'].title()
    if 'St_PosDir' in attrs and attrs['St_PosDir'] != '':
        post_dir = translateName(attrs['St_PosDir'])
    if 'St_PosTyp' in attrs and attrs['St_PosTyp'] != '':
        street_type = translateName(attrs['St_PosTyp'])
    
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
    if 'Post_Comm' in attrs and attrs['Post_Comm'] != '':
        tags['addr:city'] = attrs['Post_Comm'].title()
    if 'Post_Code' in attrs and attrs['Post_Code'] != '':
        tags['addr:postcode'] = attrs['Post_Code']

    return tags
