'''
Created on Nov 2, 2018

This program takes a Markit IR file and integrates the data
into a CSV file.

@author: jsissler
'''

import sys
import argparse
import logging
import csv
import xml.etree.ElementTree as ET
import datetime

logging.basicConfig(level=logging.DEBUG)
logging.info('starting...')

parser = argparse.ArgumentParser(description='integrate Markit IR data into csv')
parser.add_argument('--input_file', help='XML input file')
parser.add_argument('--output_file', help='CSV output file')
parser.add_argument('--date', help='Date rate was observed')
args = parser.parse_args()

logging.info("integrating new IR data from %s into CSV file %s" % (args.input_file, args.output_file))

obsdate = datetime.datetime.strptime(args.date, '%Y%m%d').date()
today = datetime.date.today()
mindate = today - datetime.timedelta(days=90) # keep rolling 90 days of data

# read current rates into dictionary discarding any rates older than mindate

irrates = dict()
header = True

with open(args.output_file) as csvfile:
    reader = csv.reader(csvfile)

    for row in reader:
        if header:
            header = False
            continue

        key, date, rate = row
        ddate = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        if ddate < mindate:
            logging.warn('discarding %s' % str(row))
            continue

        if not irrates.has_key(key):
            irrates[key] = dict()

        irrates[key][date] = rate

# read new rates and add to dictionary

root = ET.parse(args.input_file)
currency = root.find('currency').text

for el in root.findall('./deposits/curvepoint'):
    key = '%s-LIBOR-%s' % (currency, el.find('tenor').text)

    if not irrates.has_key(key):
        irrates[key] = dict()

    irrates[key][obsdate] = el.find('parrate').text

# write new csv

with open(args.output_file, 'w') as csvfile:
    writer = csv.writer(csvfile)

    for ref in irrates:
        for date in irrates[ref]:
            row = (ref, date, irrates[ref][date])
            writer.writerow(row) 

# read and sort new csv

with open(args.output_file) as csvfile:
    reader = csv.reader(csvfile)
    sorted_data = sorted(reader, key=lambda row:row[1], reverse=True)

# write sorted

with open(args.output_file, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(('Reference', 'Date', 'Value'))

    for row in sorted_data:
        writer.writerow(row)

sys.exit(0)

