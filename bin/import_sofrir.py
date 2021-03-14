'''
Created on Dec 13, 2020

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

parser = argparse.ArgumentParser(description='integrate Fed SOFR data into csv')
parser.add_argument('--input_file', help='XML input file')
parser.add_argument('--output_file', help='CSV output file')
parser.add_argument('--date', help='Date rate was observed')
args = parser.parse_args()

logging.info("integrating new IR data from %s into CSV file %s" % (args.input_file, args.output_file))

obsdate = datetime.datetime.strptime(args.date, '%Y%m%d').date()

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

        if key not in irrates:
            irrates[key] = dict()

        irrates[key][date] = rate

OBS_POINT_TARGET = '50%'
TYPE_TARGET = 'SOFR'

root = ET.parse(args.input_file)

for el in root.findall('.//Series'):
    if el.attrib['FUNDRATE_OBS_POINT'] == OBS_POINT_TARGET and \
       el.attrib['FUNDRATE_TYPE'] == TYPE_TARGET:
        for el2 in el.findall("Obs"):
            date = datetime.datetime.strptime(el2.attrib['TIME_PERIOD'], '%Y-%m-%d').date()
            rate = float(el2.attrib['OBS_VALUE'])
            logging.info("found rate %.2f as of %s" % (rate, date))
            
            if TYPE_TARGET not in irrates:
                irrates[TYPE_TARGET] = dict()
            
            irrates[TYPE_TARGET][date] = rate

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

logging.info("exit 0");
sys.exit(0);