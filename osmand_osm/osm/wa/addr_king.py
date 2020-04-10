"""
Translation rules
Copyright 2019
"""
#import str

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
    if 'addr_num' in attrs and attrs['addr_num'] != '':
        tags['addr:housenumber'] = attrs['addr_num']
    if 'unit' in attrs and attrs['unit'] != '':
        tags['addr:unit'] = attrs['unit']
    if 'fullname' in attrs and attrs['fullname'] != '':
        tags['addr:street'] = translateName(attrs['fullname'])
    if 'ctyname' in attrs and attrs['ctyname'] != '':
        tags['addr:city'] = str.capitalize(attrs['ctyname'])
    if 'zip5' in attrs and attrs['zip5'] != '':
        tags['addr:postcode'] = attrs['zip5']

    return tags
