#!/bin/bash
username=auto_trump_pp\$OWNER
name=ar_database
dumpfile=auto_trump_11OWNER.dmp
userpassword=password
sidORinstance=ora11g
driver=oracle
loginpassword=0racle11
port=None
dumpfolder=/home/oracle/backup
host=172.20.20.49
loginuser=oracle
fromuser=auto_trump_11\$OWNER
id=0
logfile1=RemoteRestoreDB_${id}.log
. /usr/local/bin/oraenv <<< $sidORinstance >/dev/null
cd impdp_and_expdp_shell
sh impdp.sh $username $userpassword $fromuser $dumpfile $dumpfolder
logfile=${username/\$/}.log
cp ${dumpfolder}/${logfile} .
mv ${logfile} ${logfile1}
if [ -e ${logfile1} ];then
 grep -i "^. . imported \"${username}\".*rows$" ${logfile1}>temp
 if [ ! -s temp ];then
  echo "database does not restore successfully, please check ${logfile}."
  #echo $username", fail, \"check ${logfile}\"">restoredbs.tmp
  echo $username" fail">restoredbs.tmp
 else
  echo "database restores successfully."
  #echo $username", pass">restoredbs.tmp
  echo $username" pass">restoredbs.tmp
 fi
 rm temp
else
 echo "database is not restored, please check configuration."
 #echo $username", fail, \"check configuration\"">restoredbs.tmp
 echo $username" fail">restoredbs.tmp
fi