'''
script to run filters on data already in database
'''
import datetime
import logging
import psycopg

import oa

logging.basicConfig(filename=f'cleaning_db_{datetime.datetime.today().isoformat()}.log', level='DEBUG', format='%(asctime)s %(name)s %(levelname)s %(message)s')
db_name = 'gis'
conn = psycopg.connect(f'dbname={db_name}')
cur = conn.cursor()
working_area = oa.WorkingArea('filler')
cur.execute("SELECT tablename FROM pg_catalog.pg_tables where schemaname='pat';")
table_list = cur.fetchall()
# remove osm tables from table list
del table_list[table_list.index(('planet_osm_nodes',))]
del table_list[table_list.index(('planet_osm_ways',))]
del table_list[table_list.index(('planet_osm_rels',))]
# filter addrs and streets tables?
for table_tuple in table_list:
    table = table_tuple[0]
    cur.execute(f"delete from \"{table}\" where street !~ '.*[- ]+.*';")
    logging.info(table + ' DELETE ' + str(cur.rowcount) + ' 1 word street')
    working_area.filter_complex_garbage(table, cur)
conn.commit()
conn.close()
