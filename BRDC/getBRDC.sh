#!/bin/sh
pwd
year=$(date +%Y)
year_duo=$(date +%y)
doy=$((10#$(date +%j)-1))
dlname="brdc"$doy"0."${year_duo}"n.gz"
brdcname="brdc"$doy"0."${year_duo}"n"

if test -f "GPS/"${year}"/"${dlname} || test -f "GPS/"${year}"/"${brdcname};
then
	echo "GPS almanac already exists!"
else 
	wpath="https://cddis.nasa.gov/archive/gps/data/daily/"${year}"/brdc/"${dlname}
	wget --auth-no-challenge ${wpath} -P GPS/${year}
	cd GPS/2024
	gzip -d ${dlname}
	rm -rf ${dlname} 
fi

cd ..
cd ..
dlname="hour"$doy"0."${year_duo}"b"

if test -f "BEIDOU/"${year}"/"${dlname};
then
	echo "Beidou almanac already exists!"
else 
	wpath="ftp://pub:tarc@ftp2.csno-tarc.cn/brdc/"${year}"/"${dlname}
	wget --auth-no-challenge ${wpath} -P BEIDOU/${year}/
fi
