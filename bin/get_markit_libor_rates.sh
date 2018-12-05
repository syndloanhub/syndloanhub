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
ZIP_FILE=InterestRates_USD_${YYYYMMDD}.zip
DESTDIR=${VAR}/markitir
FILE=${DESTDIR}/${ZIP_FILE}
URL=https://www.markit.com/news/${ZIP_FILE}

curl ${URL} > ${FILE}

if [ ! -e ${FILE} ]; then
    echo ${URL} not found, exit 1
    exit 1
fi

NA='Interest Rates not available'
if grep -q "${NA}" ${FILE}; then
    echo ${NA}, exit 2
    exit 2
fi

pushd $DESTDIR
unzip -o ${ZIP_FILE}
popd

python3 ${BIN}/import_markitir.py --input_file ${DESTDIR}/InterestRates_USD_${YYYYMMDD}.xml --output_file ${DESTDIR}/markitir.csv --date ${YYYYMMDD}

exit $?


