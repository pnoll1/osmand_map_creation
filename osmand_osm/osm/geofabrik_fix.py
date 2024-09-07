import json

# dict area name to iso
iso_translation = {'baden-wuerttemberg':'de-bw', 'bayern':'de-by', 'berlin':'de-be', 'brandenburg':'de-bb', \
        'hamburg':'de-hh', 'hessen':'de-he', 'mecklenburg-vorpommern':'de-mv', 'niedersachsen':'de-ni', \
        'nordrhein-westfalen':'de-nw', 'rheinland-pfalz':'de-rp', 'saarland':'de-sl', 'sachsen':'de-sn', \
        'sachsen-anhalt':'de-st', 'schleswig-holstein':'de-sh', 'thueringen':'de-th'}
# find area
with open('geofabrik_index-v1.json', 'r+') as index_file:
    geofabrik_index = json.load(index_file)
    area_list = geofabrik_index['features']
    for area in area_list:
        area_name = area['properties']['id']
        for full_name in iso_translation:
            if area_name == full_name:
                area['properties']['iso3166-2'] = [iso_translation[area_name].upper()]
    index_file.seek(0)
    index_file.write(json.dumps(geofabrik_index))
    index_file.truncate()
