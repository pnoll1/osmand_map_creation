import ogr2osm

class OaTranslation(ogr2osm.TranslationBase):

    def filter_tags(self, attrs):
        if not attrs:
            return
        # raw variables
        address_number = 'number'
        street_name_raw = 'street' 
        city = 'city'
        # unit_raw = 'unit' # 'Apt'
        postcode_raw = 'postcode'
        tags = {}
        if address_number in attrs and attrs[address_number] != '':
            tags['addr:housenumber'] = attrs[address_number]
        # OSMAnd doesn't support unit
        # if 'Unit' in attrs and attrs['Unit'] != '':
        #   tags['addr:unit'] = attrs['Unit']
        # split address at first '#', UNIT or APT and add that to unit
        if street_name_raw in attrs and attrs[street_name_raw] != '':
            tags['addr:street'] = attrs[street_name_raw]
        if city in attrs and attrs[city] != '':
            tags['addr:city'] = attrs[city].title()
        if postcode_raw in attrs and attrs[postcode_raw] != '':
            tags['addr:postcode'] = attrs[postcode_raw]

        return tags
