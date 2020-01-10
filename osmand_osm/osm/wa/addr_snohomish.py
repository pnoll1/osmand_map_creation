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
    'RD':'Road',
    'ST':'Street',
    'PL':'Place',
    'CRES':'Crescent',
    'BLVD':'Boulevard',
    'DR':'Drive',
    'LANE':'Lane',
    'CRT':'Court',
    'GR':'Grove',
    'CL':'Close',
    'Rwy':'Railway',
    'Div':'Diversion',
    'Hwy':'Highway',
    'Hwy':'Highway',
    'Conn': 'Connector',
    'E':'East',
    'S':'South',
    'N':'North',
    'W':'West',
    'SE':'Southeast',
    'NE':'Northeast',
    'SW':'Southwest',
    'NW':'Northwest'}

    newName = ''
    for partName in rawname.split():
	    newName = newName + ' ' + str.capitalize(suffixlookup.get(partName,partName))
    newName = newName.lstrip()
    return newName

def filterTags(attrs):
    if not attrs:
        return

    tags = {}
    if 'add_number' in attrs and attrs['add_number'] != '':
        tags['addr:housenumber'] = attrs['add_number']
    if 'unit' in attrs and attrs['unit'] != '':
        tags['addr:unit'] = attrs['unit']
    # postdir
    if 'lst_name' in attrs and attrs['lst_name'] != '' and 'st_postyp' in attrs and attrs['st_postyp'] != '' and 'st_posdir' in attrs and attrs['st_posdir'] != '':
        # numbered street
        if re.search(r'^\d', attrs['lst_name']) is not None:
            address_street = attrs['lst_name'].lower()
            tags['addr:street'] = address_street + ' ' +attrs['st_postyp'].capitalize() + ' ' + attrs['st_posdir'].capitalize()
        else:
            tags['addr:street'] = attrs['lst_name'].title() + ' ' +attrs['st_postyp'].capitalize() + ' ' + attrs['st_posdir'].capitalize()
    # no postdir
    elif 'lst_name' in attrs and attrs['lst_name'] != '' and 'st_postyp' in attrs and attrs['st_postyp'] != '':
        # numbered street
        if re.search(r'^\d', attrs['lst_name']) is not None:
            address_street = attrs['lst_name'].lower()
            tags['addr:street'] = address_street + ' ' +attrs['st_postyp'].capitalize()
        else:
            tags['addr:street'] = attrs['lst_name'].title() + ' ' +attrs['st_postyp'].capitalize()
    if 'post_comm' in attrs and attrs['post_comm'] != '':
        tags['addr:city'] = attrs['post_comm'].title()
    if 'post_code' in attrs and attrs['post_code'] != '':
        tags['addr:postcode'] = attrs['post_code']

    return tags
