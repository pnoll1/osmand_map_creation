import ogr2osm

class OaTranslation(ogr2osm.TranslationBase):
    '''
    Overrides for ogr2osm translation from oa to osm
    '''

    def filter_tags(self, tags):
        '''
        translates tags from oa format to osm format
        '''
        if not tags:
            return None
        # raw variables
        address_number = 'number'
        street_name_raw = 'street'
        city = 'city'
        # unit_raw = 'unit' # 'Apt'
        postcode_raw = 'postcode'
        new_tags = {}
        # data with empty address number will be thrown out by filter_data
        if address_number in tags:
            new_tags['addr:housenumber'] = tags[address_number]
        # OSMAnd doesn't support unit
        # if 'Unit' in tags and tags['Unit'] != '':
        #   tags['addr:unit'] = tags['Unit']
        # split address at first '#', UNIT or APT and add that to unit
        if street_name_raw in tags and tags[street_name_raw] != '':
            new_tags['addr:street'] = tags[street_name_raw]
        if city in tags and tags[city] != '':
            new_tags['addr:city'] = tags[city].title()
        if postcode_raw in tags and tags[postcode_raw] != '':
            new_tags['addr:postcode'] = tags[postcode_raw]
        return new_tags

    def merge_tags(self, geometry_type, tags_existing_geometry, tags_new_geometry):
        '''
        overrides method so no merging is done
        '''
        return None
