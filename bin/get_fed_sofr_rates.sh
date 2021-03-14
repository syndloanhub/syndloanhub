#!/bin/bash
#set -x

YYYYMMDD=`date +%Y%m%d`

usage() { echo "Usage: $0 [-d YYYYMMDD ]" 1>&2; exit 1; }

while getopts "d:" o; do
    case "${o}" in
        d)
            YYYYMMDD=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

shift $((OPTIND-1))

BIN=`dirname $0`
VAR=${BIN}/../var
XML_FILE=SOFR.xml
DESTDIR=${VAR}/fedsofr
FILE=${DESTDIR}/${XML_FILE}
URL='https://websvcgatewayx2.frbny.org/mktrates_external_httponly/services/v1_0/mktRates/xml/retrieveLastN?typ=RATE&rateType=R3&n=25'

rm -f ${FILE}
curl ${URL} > ${FILE}

if [ ! -e ${FILE} ]; then
    echo ${URL} not found, exit 1
    exit 1
fi

python3 ${BIN}/import_sofrir.py --input_file ${FILE} --output_file ${DESTDIR}/SOFR.csv --date ${YYYYMMDD}

exit $?
