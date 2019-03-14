#!/bin/bash

#impdp_colline.sh help
if [ X$1 == X-h -o X$1 == X-help -o X$1 == Xhelp -o $# -gt 0 ];then
  echo "--------------------------------------------------------------------------------------------------------"
  echo "When you want to re-import dumpfile into a database, this script maybe help you."
  echo "Steps(1-4): "
  echo "1. vi impdp_colline.sh "
  echo "2. input four parameters in the script "
  echo "3. save and exit the script "
  echo "4. ./impdp_colline.sh "
  echo "                               "
  echo "Parameter introduction-- "
  echo "   DUMPFILE:input the dumpfile's name that you want to impdp. Note: Case sensitive! "
  echo "   FROMUSER:You need to know the original user(--USERNAME) of this dumpfile and input it. Note Capital! "
  echo "   DIRECTORY:the absolute path of the dumpfile "
  echo "   USERNAME:Custom a new user to import the dumpfile. Note Capital! "
  echo "----------------------------------------------------------------------------------------------------------"
  exit
fi



#Impdp script as follows.

FROMUSER=DSDBSHQA
USERNAME=ZDSDBSHQA
DUMPFILE=DSDBSHQA.dmp
DIRECTORY=/home/oracle/backup/


LOGFILE=${USERNAME}.log
JOBNAME=$USERNAME

if [ -z ${FROMUSER} ];then
   echo "Your input FROMUSER is null"
   exit
fi


if [ -z ${USERNAME} ];then
   echo "Your input USERNAME is null"
   exit
fi

if [ ! -d ${DIRECTORY} ];then
   echo " The directory ${DIRECTORY} is not exist! "
   exit
fi

if [ ! -f ${DIRECTORY}/${DUMPFILE} ];then
   echo " The dumpfile ${DIRECTORY}/${DUMPFILE} is not exist! "
   exit
fi


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
  IDENTIFIED BY creditderivative
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
  CREATE OR REPLACE DIRECTORY EXPORT_TEMP AS '$DIRECTORY';



EOF

impdp dumpfile=$DUMPFILE schemas=$FROMUSER remap_schema=$FROMUSER:$USERNAME transform=oid:n,segment_attributes:n userid=system/0racle1 directory=EXPORT_TEMP logfile=$LOGFILE job_name=$JOBNAME EXCLUDE=MATERIALIZED_VIEW,TABLE:\"like \'%MV%\'\"
