#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os
import time
import sys
from collections import OrderedDict

def writeLog(filefullpath,operate,logdiscription):
    with open(filefullpath,operate) as wlHDL:
        wlHDL.write(logdiscription)
    print logdiscription

def searchStrInFile(filefullpath,str):
    flag=False
    with open(filefullpath,'r') as rHDL:
        for line in rHDL.readlines():
            #print 'compare '+line.strip()+' with '+str
            if cmp(line.strip().upper(),str.upper())==0:
                #print 'find '+str
                flag=True
                break
    return flag

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
monitorsvnFileListLog='monitorfiles.txt'
monitorsvnLog='monitorsvn.log'
monitorsvnResult='monitorsvnresult.log'

if os.path.isfile(cmdFolder+monitorsvnFileListLog):
    os.remove(cmdFolder+monitorsvnFileListLog)
if os.path.isfile(cmdFolder+monitorsvnLog):
    os.remove(cmdFolder+monitorsvnLog)

with open(configFile,'r') as f:
    configs=json.load(f)

for confi in configs:
    for key,value in confi.items():
        if re.search('svnSettings',key,re.IGNORECASE):
            for appconfigs in value:
                appconfig=OrderedDict(appconfigs)
            for k,v in appconfig.items():    
                userinfo=r' --username "'+appconfig['loginuser']+'" --password '+appconfig['loginpassword']+r' '
                fileList=appconfig['files']
                if cmp(appconfig['url'][-1],'/')!=0:
                    appconfig['url']=appconfig['url']+'/'
                time_start=time.time()
                writeLog(cmdFolder+monitorsvnLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' start to monitor '+appconfig['url'])
                monitorTmp=-1
                while appconfig['bemonitored'] is not None and re.search(appconfig['bemonitored'],'yes',re.IGNORECASE):
                    print 'we are bemonitored is yes'
                    os.system(r'svn list "'+appconfig['url']+'"'+userinfo+r'--depth "infinity">'+cmdFolder+monitorsvnFileListLog)
                    monitorTmp=0
                    for fileTmp in fileList:
                        print fileTmp
                        if searchStrInFile(cmdFolder+monitorsvnFileListLog,fileTmp):
                            slog=appconfig['url']+fileTmp+' find\n'
                            writeLog(cmdFolder+monitorsvnLog,'a',slog)
                            os.system(r'svn export "'+appconfig['url']+fileTmp+r'" "'+appconfig['localpath']+'"'+userinfo+r'--no-auth-cache --force')#run svn
                            fileList.remove(fileTmp)
                        else:
                            monitorTmp=1
                    if monitorTmp==0:
                        appconfig['bemonitored']='n'
                    if appconfig['timeout']>-1 and time.time()-time_start>appconfig['timeout']:
                        monitorTmp=2
                        break     
                if appconfig['bemonitored'] is not None and re.search(appconfig['bemonitored'],'no',re.IGNORECASE):
                    print 'we are bemonitored is no'
                    os.system(r'svn list "'+appconfig['url']+'"'+userinfo+r'--depth "infinity">'+cmdFolder+monitorsvnFileListLog)
                    for fileTmp in fileList:                    
                        if searchStrInFile(cmdFolder+monitorsvnFileListLog,fileTmp):    
                            slog=appconfig['url']+fileTmp+' find\n'
                            writeLog(cmdFolder+monitorsvnLog,'a',slog)
                            os.system(r'svn export "'+appconfig['url']+fileTmp+r'" "'+appconfig['localpath']+'"'+userinfo+r'--no-auth-cache --force')#run svn
                        else:
                            slog=appconfig['url']+fileTmp+' miss\n'
                            writeLog(cmdFolder+monitorsvnLog,'a',slog)
                writeLog(cmdFolder+monitorsvnLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' stop to monitor '+appconfig['url'])
                if monitorTmp==0:
                    writeLog(cmdFolder+monitorsvnResult,'a',str(appconfig['id'])+' pass\n')
                elif monitorTmp==2:
                    writeLog(cmdFolder+monitorsvnResult,'a',str(appconfig['id'])+' timeout\n')  

    