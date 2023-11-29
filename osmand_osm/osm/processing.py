#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
from subprocess import run, CalledProcessError
from pathlib import Path
import argparse
from multiprocessing import Pool
import hashlib
import logging
import datetime
import psycopg2
import ogr2osm
import addr_oa
import oa
import obf
import osm_utils
# config options
from config import db_name, id, slice_config, batches, log_level
from secrets import oa_token

def parse_meta_commands(args):
    '''
    expands meta commands into lower level commands
    '''
    if args.all:
        args.update_oa = True
        args.update_osm = True
        args.load_oa = True
        args.filter_data = True
        args.merge_oa = True
        args.output_osm = True
        args.merge = True
        args.quality_check = True
        args.slice = True
        args.build = True
        args.calculate_hashes = True
    if args.normal:
        args.update_osm = True
        args.load_oa = True
        args.filter_data = True
        args.merge_oa = True
        args.output_osm = True
        args.merge = True
        args.quality_check = True
        args.slice = True
        args.build = True
        args.calculate_hashes = True

def update_run_all_build(args, area_list):
    '''
    splits areas up for multiprocessing then builds using osmand map creator
    '''
    # Ram can be limit with large files, consider switching pool to 1 or doing 1 state at a time with cron job
    with Pool(args.processes) as p:
        # OA regions don't correspond to states and download slowly, run before main flow
        if args.update_oa:
            oa.update_oa(oa_token)
        area_list_of_tuples = []
        for i in area_list:
            area_list_of_tuples.append((i,args))
        p.starmap(run_all, area_list_of_tuples)
    if args.build:
        obf.build()

def run_all(area, args):
    '''
    runs processing code for single geographic area
    '''
    # root assumed to be child folder of pbf_output
    root = Path(os.getcwd())
    pbf_output = root.parent
    working_area = oa.WorkingArea(area)
    logging.debug(working_area)
    if args.load_oa:
        working_area.decompress_oa()
        working_area.create_master_list()
        working_area.load_oa(db_name)
    if args.filter_data:
        working_area.filter_data(db_name)
    if args.merge_oa:
        working_area.merge_oa(db_name)
    if args.output_osm:
        working_area.output_osm(id, db_name)
    if args.update_osm:
        osm = osm_utils.Osm(working_area)
        osm.update_osm(working_area)
    if args.merge:
        working_area.merge()
    # allows running without quality check
    ready_to_move = True
    if args.quality_check:
        ready_to_move = working_area.quality_check(ready_to_move)
    if args.slice:
        sliced_area = working_area.slice(slice_config)
        logging.info('slice finished for ' + working_area.name)
    if args.output_osm and args.slice:
        working_area.move(ready_to_move, pbf_output, sliced_area)
        logging.info('pbf files moved to build folder for ' + working_area.name)
    elif args.output_osm:
        working_area.move(ready_to_move, pbf_output)
        logging.info('pbf files moved to build folder for ' + working_area.name)

def main(args=None):
    '''
    top level function that sets up logging and cli parser then determines if cli or config file
    driven and sends areas to other function for processing. When done, file names are cleaned and
    checksums created
    '''
    logging.basicConfig(filename=f'processing_{datetime.datetime.today().isoformat()}.log', level=log_level.upper(), format='%(asctime)s %(name)s %(levelname)s %(message)s')
    # commandline argument setup
    parser = argparse.ArgumentParser(description='Process OpenAddresses data and merge with OSM extract to create single osm file per area')
    parser.add_argument('area_list', nargs='*', help='lowercase ISO 3166-1 alpha-2 country code and state/province eg us:wa')
    parser.add_argument('--normal', action='store_true', help='probably what you want, runs all but --update-oa')
    parser.add_argument('--update-oa', action='store_true', help='downloads OA data in oa_urls variable')
    parser.add_argument('--load-oa', action='store_true', help='loads OA data into database, overwriting previous')
    parser.add_argument('--filter-data', action='store_true', help='delete unwanted data from database')
    parser.add_argument('--merge-oa', action='store_true', help='overwrites oa data in db with new oa data if better')
    parser.add_argument('--merge', action='store_true', help='merge extract with address files')
    parser.add_argument('--output-osm', action='store_true', help='output data from database to OSM files')
    parser.add_argument('--update-osm', action='store_true', help='downloads latest area extract, overwrites previous')
    parser.add_argument('--quality-check', action='store_true', help='sort output file and run basic quality checks')
    parser.add_argument('--slice', action='store_true', help='splits areas into smaller regions if config present')
    parser.add_argument('--build', action='store_true', help='runs osmand map creator')
    parser.add_argument('--calculate-hashes', action='store_true', help='creates hashes for obf files')
    parser.add_argument('--processes', type=int, nargs='?', default=2, help='number of processes to use, min=1(best for large areas that need ram), max=number of physical processors(best for small areas)')
    parser.add_argument('--all', action='store_true', help='use all options')
    # allows calling from module
    if not args:
        args = parser.parse_args()
    parse_meta_commands(args)
    area_list = vars(args)['area_list']
    # run commands from cli
    if args:
        logging.debug('run from cli')
        update_run_all_build(args, area_list)
    # use commands from config file if command line doesn't have them
    if len(batches) > 0 and not area_list:
        for batch_string in batches:
            batch_list = batch_string.split(' ')
            args = parser.parse_args(batch_list)
            parse_meta_commands(args)
            logging.debug(args)
            area_list = vars(args)['area_list']
            update_run_all_build(args, area_list)
            logging.info('obfs build stage finished for ' + batch_string)
    if args.calculate_hashes:
        obf.calculate_hashes()
    logging.info('script finished')

if __name__ == '__main__':
    main()
