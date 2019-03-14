@Echo off
set username=MAS_21403_KUN_J
set storefolder=E:\ProductDB\APAC_US\MAS
set name=tool_database
set dumpfile=MAS_22201_KS2K8T58U_DATA.BAK
set sidORinstance=sql2008r2
set driver=sqlserver
set loginpassword=password
set port=None
set dumpfolder=E:\ProductDB\APAC_US\MAS\Bak
set host=172.20.20.57
set loginuser=sa
set id=1
::set sqlstore=%dumpfolder:\BAK=%
::call "%~dp0setDBServer.bat"
set logfile=.\log\LocalRestoreDB_%id%.log
set resultLog=.\log\restoredbs.log
::sqlcmd -S %host%\%sidORinstance% -U %loginuser% -P %loginpassword%  -Q "RESTORE FILELISTONLY FROM DISK=N'$(dumpfolder)\$(dumpfile)'; RESTORE DATABASE [$(username)] FROM  DISK =N'$(dumpfolder)\$(dumpfile)' WITH RECOVERY,NOUNLOAD,REPLACE,MOVE N'$(fromuser)' TO N'$(sqlstore)\$(username).mdf',MOVE N'$(fromuser)_log' TO N'$(sqlstore)\$(username)_log.ldf';" -o "%logfile%"
::sqlcmd -S %host%\%sidORinstance% -U %loginuser% -P %loginpassword%  -Q "ALTER DATABASE [$(username)] MODIFY FILE (NAME=N'$(fromuser)', NEWNAME=N'$(username)'); ALTER DATABASE [$(username)] MODIFY FILE (NAME=N'$(fromuser)_Log', NEWNAME=N'$(username)_Log');" >>"%logfile%"
echo sqlcmd -S %host%\%sidORinstance% -U %loginuser% -P %loginpassword%  -i "SQLrestoreDB.sql"
sqlcmd -S %host%\%sidORinstance% -U %loginuser% -P %loginpassword%  -i "SQLrestoreDB.sql"
echo sqlcmd -S %host%\%sidORinstance% -U %loginuser% -P %loginpassword%  -Q "exec RestoreDB @NewDB=N'$(username)',@BakDBFullPath=N'$(dumpfolder)\$(dumpfile)',@NewDBPath=N'$(storefolder)'" -o "%logfile%"
sqlcmd -S %host%\%sidORinstance% -U %loginuser% -P %loginpassword%  -Q "exec RestoreDB @NewDB=N'$(username)',@BakDBFullPath=N'$(dumpfolder)\$(dumpfile)',@NewDBPath=N'$(storefolder)'" -o "%logfile%"
findstr /C:"RESTORE DATABASE successfully processed" "%logfile%" && echo %username% pass>>%resultLog%
if %ERRORLEVEL% GEQ 1 ( echo %username%, fail>>%resultLog%)

:EXIT