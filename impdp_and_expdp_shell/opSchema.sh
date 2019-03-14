#!/bin/bash

#impdp_colline.sh help
if [ X$1 == X-h -o X$1 == X-help -o X$1 == Xhelp ];then
  echo "--------------------------------------------------------------------------------------------------------"
  echo "When you want to re-import dumpfile into a database, this script maybe help you."
  echo "                               "
  echo "Parameter introduction-- "
  echo "  1 SIDORINSTANCE: choose ora11g or ora12c "
  echo "  2 USERNAME:Custom a new user to import the dumpfile. Note Capital! "
  echo "  3 PASSWORD:Custom a new user's password to import the dumpfile. "
  echo "  4 FROMUSER:You need to know the original user(--USERNAME) of this dumpfile and input it. Note Capital! "
  echo "  5 DIRECTORY:the absolute path of the schema and dumpfile and logfile "
  echo "  6 DUMPFILE:input the dumpfile's name that you want to impdp. Note: Case sensitive! "
  echo "----------------------------------------------------------------------------------------------------------"
  exit
fi



#Impdp script as follows.
SIDORINSTANCE=$1
USERNAME=$2
PASSWORD=$3
FROMUSER=$4
DIRECTORY=$5
DUMPFILE=$6


LOGFILE=${USERNAME/\$/}.log
JOBNAME=$USERNAME

if [ -z ${USERNAME} ];then
   echo "Your input USERNAME is null"
   exit
fi


if [ -z ${SIDORINSTANCE} ];then
   echo "Your input SIDORINSTANCE is null, use default."
   SIDORINSTANCE=ora11g
fi
if [ -z ${PASSWORD} ];then
   echo "Your input PASSWORD is null, use default."
   PASSWORD=password
fi

. /usr/local/bin/oraenv <<< $SIDORINSTANCE >/dev/null
$ORACLE_HOME/bin/sqlplus /nolog <<EOF

  CONNECT / AS SYSDBA

  DECLARE
  coun NUMBER(3):=0;
  BEGIN
  SELECT COUNT(*) INTO coun FROM ALL_USERS WHERE USERNAME='$USERNAME';
  IF coun>0 THEN
  EXECUTE IMMEDIATE 'DROP USER $USERNAME CASCADE';
  END IF;
  END;
  /

  CREATE USER $USERNAME
  IDENTIFIED BY ${PASSWORD}
  DEFAULT TABLESPACE USERS 
  TEMPORARY TABLESPACE TEMP
  PROFILE DEFAULT
  ACCOUNT UNLOCK;

  GRANT SELECT ON sys.dba_pending_transactions TO ${USERNAME};
  GRANT SELECT ON sys.pending_trans$ TO ${USERNAME};
  GRANT SELECT ON sys.dba_2pc_pending TO ${USERNAME};
  GRANT EXECUTE ON sys.dbms_xa TO ${USERNAME};
  GRANT CREATE SESSION TO ${USERNAME};
  GRANT CREATE INDEXTYPE TO ${USERNAME};
  GRANT CREATE PROCEDURE TO ${USERNAME};
  GRANT CREATE SEQUENCE TO ${USERNAME};
  GRANT CREATE TABLE TO ${USERNAME};
  GRANT CREATE TRIGGER TO ${USERNAME};
  GRANT CREATE TYPE TO ${USERNAME};
  GRANT CREATE VIEW TO ${USERNAME};
  GRANT UNLIMITED TABLESPACE TO ${USERNAME};
  GRANT CREATE MATERIALIZED VIEW TO ${USERNAME};


EOF

if [ -z ${FROMUSER} ];then
   echo "Your input FROMUSER is null"
   exit
fi
if [ ! -d ${DIRECTORY} ];then
   echo " The directory ${DIRECTORY} is not exist! "
   exit
fi
if [ -e ${DIRECTORY}/${LOGFILE} ];then
   echo "tool will delete your log file."
   rm ${DIRECTORY}/${LOGFILE}
fi

if [ ! -f ${DIRECTORY}/${DUMPFILE} ];then
   echo " The dumpfile ${DIRECTORY}/${DUMPFILE} is not exist! "
   exit
fi
impdp dumpfile=$DUMPFILE schemas=$FROMUSER remap_schema=$FROMUSER:$USERNAME transform=oid:n,segment_attributes:n userid=system/0racle1 directory=EXPORT_TEMP logfile=$LOGFILE job_name=$JOBNAME 
