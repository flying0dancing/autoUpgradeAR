#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os
import time
from collections import OrderedDict

configFile='autoUpgrade.json'
configLocalCmd='LocalRestoreDBII.txt'
configRemoteCmd='RemoteRestoreDBII.txt'
prefixRemoteCmd='RemoteRestoreDB_'
prefixLocalCmd='LocalRestoreDB_'
configShellFolderName='impdp_and_expdp_shell'
restoredbLog='restoredbs.log'
restoredbErr='restoredbs.err'
cmdFolder='.\\log\\'
if os.path.exists(configShellFolderName) and os.path.isfile(configFile) and os.path.isfile(configLocalCmd) and os.path.isfile(configRemoteCmd) and os.path.isfile('plink.exe') and os.path.isfile('pscp.exe'):
    pass
else:
    print('please check these folders or files are exists.\n')
    print('folders: '+configShellFolderName+'\n')
    print('files: '+configFile+', '+configLocalCmd+', '+configRemoteCmd+', plink.exe, pscp.exe')
    exit()
if not os.path.exists(cmdFolder):
    os.makedirs(cmdFolder)
if os.path.isfile(cmdFolder+restoredbLog):
    os.remove(cmdFolder+restoredbLog)
    #os.mknod(cmdFolder+restoredbLog)
if os.path.isfile(cmdFolder+restoredbErr):
    os.remove(cmdFolder+restoredbErr)
    
with open(configFile,'r') as f:
    configs=json.load(f)
for confi in configs:
    for key,value in confi.items():
        if re.search('DATABASESERVERS',key,re.IGNORECASE):
            for dbconfigs in value:
                dbconfig=OrderedDict(dbconfigs)
                if re.search('ORACLE',dbconfig['driver'],re.IGNORECASE):
                    with open(cmdFolder+prefixRemoteCmd+str(dbconfig['id'])+'.sh','w') as sHDL:
                        sHDL.write('#!/bin/bash\n')
                        for k,v in dbconfig.items():
                            i=re.search(r'(.*)(\\|/)$',str(v))
                            if i is None:
                                sHDL.write(k+'='+str(v)+'\n')
                            else:
                                sHDL.write(k+'='+i.group(1)+'\n')
                        with open(configRemoteCmd,'r') as sIIHDL:
                            sHDL.write(sIIHDL.read())
                    if dbconfig['port'] is None:
                        portStr=r' '
                    else:
                        portStr=r' -P '+dbconfig['port']+r' '
                    userinfo=r' -l '+dbconfig['loginuser']+r' -pw '+dbconfig['loginpassword']+portStr
                    returnVal=os.system(r'pscp.exe -r -batch '+userinfo+r' .\\'+configShellFolderName+r' '+dbconfig['host']+':'+'/home/'+dbconfig['loginuser']+'/')
                    if returnVal==0:
                        returnVal=os.system(r'plink.exe -ssh -batch -v '+dbconfig['loginuser']+'@'+dbconfig['host']+' -pw '+dbconfig['loginpassword']+' -m '+cmdFolder+prefixRemoteCmd+str(dbconfig['id'])+'.sh')
                        if returnVal==0:
                            #logfile=dbconfig['username'].replace('\\$', '')+'.log'
                            os.system(r'pscp.exe -batch '+userinfo+dbconfig['host']+':/home/'+dbconfig['loginuser']+'/'+configShellFolderName+'/'+prefixRemoteCmd+str(dbconfig['id'])+'.log .\\log\\')
                            os.system(r'pscp.exe -batch '+userinfo+dbconfig['host']+':/home/'+dbconfig['loginuser']+'/'+configShellFolderName+'/restoredbs.tmp'+r' '+'.\\log\\')
                            with open(cmdFolder+restoredbLog,'a') as rHDL:
                                with open(cmdFolder+'restoredbs.tmp','r') as tmpHDL:
                                    rHDL.write(tmpHDL.read())
                        else:
                            with open(cmdFolder+restoredbErr,'a') as errHDL:
                                errHDL.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: execute file '+prefixRemoteCmd+str(dbconfig['id'])+'.sh'+r' failed.')
                    else:
                        with open(cmdFolder+restoredbErr,'a') as errHDL:
                            errHDL.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: copy folder .\\'+configShellFolderName+r' failed.')
                    
                else:
                    with open(cmdFolder+prefixLocalCmd+str(dbconfig['id'])+'.bat','w') as sHDL:
                        sHDL.write('@Echo off\n')
                        for k,v in dbconfig.items():
                            i=re.search(r'(.*)(\\|/)$',str(v))
                            if i is None:
                                sHDL.write('set '+k+'='+str(v)+'\n')
                            else:
                                sHDL.write('set '+k+'='+i.group(1)+'\n')
                        with open(configLocalCmd,'r') as sIIHDL:
                            sHDL.write(sIIHDL.read())
                    returnVal=os.system(r'start /WAIT /B '+cmdFolder+prefixLocalCmd+str(dbconfig['id'])+'.bat')
                    if returnVal!=0:
                        with open(cmdFolder+restoredbErr,'a') as errHDL:
                            errHDL.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: execute file '+prefixLocalCmd+str(dbconfig['id'])+r'.bat failed.')                                      
                 
                    
                    
                    
                    