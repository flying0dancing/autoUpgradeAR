#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os
import time
from collections import OrderedDict

def writeLog(filefullpath,operate,logdiscription):
    with open(filefullpath,operate) as wlHDL:
        wlHDL.write(logdiscription)
    print logdiscription

def searchResultFlag(filefullpath,searchedStr):
    flagsuccess=True
    if os.path.isfile(filefullpath):
        with open(filefullpath,'r') as sHDL:
            for line in sHDL.readlines():
                if re.search(searchedStr,line,re.IGNORECASE):
                    flagsuccess=False
    else:
        print 'Error: file not found ['+filefullpath+'].'
    return flagsuccess

configFile='autoUpgrade.json'
configLocalCmd='LocalInstallII.txt'
configRemoteCmd='RemoteInstallII.txt'
prefixRemoteCmd='RemoteInstall_'
prefixLocalCmd='LocalInstall_'
restoredbLog='restoredbs.log'
installproductsLog='installproducts.log'
installproductsErr='installproducts.err'
cmdFolder='.\\log\\'
configRemoteStartAR='RemoteStartAR.txt'
prefixRemoteStartAR='RemoteStartAR'
configRemoteStopAR='RemoteStopAR.txt'
prefixRemoteStopAR='RemoteStoptAR'
flagsuccess=searchResultFlag(cmdFolder+installproductsLog,'FAIL')
flagsuccess=searchResultFlag(cmdFolder+installproductsErr,'ERROR')
   
if flagsuccess:
    print 'checking products are installed successfully, continue...\n'
    with open(configFile,'r') as f:
        configs=json.load(f)
    for confi in configs:
        for key,value in confi.items():
            if re.search('applicationServers',key,re.IGNORECASE):
                if value[0].has_key('installfolder') and value[0]['installfolder'] is not None and re.search('^/',value[0]['installfolder'],re.IGNORECASE):
                    with open(cmdFolder+prefixRemoteStopAR+'.sh','w') as sHDL:
                        sHDL.write('#!/bin/bash\n')
                        for k,v in value[0].items():
                            #delete last operator
                            i=re.search(r'(.*)(\\|/)$',str(v))
                            if i is None:
                                if re.search(r' ',str(v),re.IGNORECASE):
                                    sHDL.write(k+'="'+str(v)+'"\n')
                                else:
                                    sHDL.write(k+'='+str(v)+'\n')
                            else:
                                if re.search(r' ',str(v),re.IGNORECASE):
                                    sHDL.write(k+'="'+i.group(1)+'"\n')
                                else:
                                    sHDL.write(k+'='+i.group(1)+'\n')
                        with open(configRemoteStopAR,'r') as sIIHDL:
                            sHDL.write(sIIHDL.read())
                    if value[0]['id']==0:
                        port=value[0]['port']
                        host=value[0]['host']
                        loginuser=value[0]['loginuser']
                        loginpassword=value[0]['loginpassword']                        
                    if port is None:
                        portStr=r' '
                    else:
                        portStr=r' -P '+port+r' '
                    userinfo=r' -l '+loginuser+r' -pw '+loginpassword+portStr
                    print userinfo
                    slog=''
                    returnVal=os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+cmdFolder+prefixRemoteStopAR+'.sh')
                    if returnVal==0:
                        slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' stop Agile REPORTER pass\n'
                        writeLog(cmdFolder+installproductsLog,'a',slog)
                        #copy log from host
                        if os.path.isfile(cmdFolder+prefixRemoteStopAR+'.log'):
                            os.remove(cmdFolder+prefixRemoteStopAR+'.log')
                        slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+prefixRemoteStopAR+'.log'+' from host.\n'
                        writeLog(cmdFolder+installproductsLog,'a',slog)
                        os.system(r'pscp.exe -batch '+userinfo+host+':'+value[0]['installfolder']+'/'+prefixRemoteStopAR+r'.log .\\log\\')
                    else:
                        slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' stop Agile REPORTER fail\n'
                        writeLog(cmdFolder+installproductsLog,'a',slog)       
                else:#local install
                    print 'please check "installfolder" does exist and not null in configuration.'
         
else:
    print 'checking products aren\'t installed successfully, abort.\n'
    