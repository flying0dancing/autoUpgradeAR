#!/bin/bash
installfolder=/home/testp/trump_11
properties="ARInstall qa11_testp.properties"
description="agilereport installation"
app=AgileREPORTER-1.15.3.1-b1019.jar
appfolder=Z:\ProductLine\ReportPortalPackage\1.15.3.1
loginpassword=password
host=sha-com-qa-11
loginuser=testp
id=0
type=0
port=None
propertiesfolder=Z:\ProductLine\TrumpTest
logfl="$(basename "$0")"
logfile="${logfl%.*}.tmp"
detaillog="${logfl%.*}.log"
if [ "${installfolder}" = "None" ];then
    echo "error, installfolder is null"
    echo "start AR fail">$logfile
    exit 1
else
    cd "${installfolder}"
    chmod u+x bin/*.sh
    bash bin/start.sh --force 2>&1 | tee $detaillog
    echo "start AR pass">$logfile
    exit 0
fi
