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
restoredbsuccess=True
if os.path.isfile(cmdFolder+restoredbLog):
    with open(cmdFolder+restoredbLog,'r') as sHDL:
        for line in sHDL.readlines():
            cols=line.strip().split(r' ')
            if re.search('FAIL',cols[1],re.IGNORECASE):
                restoredbsuccess=False
else:
    restoredbsuccess=False
    print 'Error: file not found ['+cmdFolder+restoredbLog+']'

if os.path.isfile(cmdFolder+installproductsLog):
    os.remove(cmdFolder+installproductsLog)
if os.path.isfile(cmdFolder+installproductsErr):
    os.remove(cmdFolder+installproductsErr)
    
if restoredbsuccess:
    print 'checking databases are restored successfully, continue...\n'
    with open(configFile,'r') as f:
        configs=json.load(f)
    for confi in configs:
        for key,value in confi.items():
            if re.search('applicationServers',key,re.IGNORECASE):
                for appconfigs in value:
                    appconfig=OrderedDict(appconfigs)
                    print '====================== running '+str(appconfig['id'])+' ======================'
                    if re.search('^/',appconfig['installfolder'],re.IGNORECASE):#write shell
                        with open(cmdFolder+prefixRemoteCmd+str(appconfig['id'])+'.sh','w') as sHDL:
                            sHDL.write('#!/bin/bash\n')
                            for k,v in appconfig.items():
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
                            with open(configRemoteCmd,'r') as sIIHDL:
                                sHDL.write(sIIHDL.read())
                    
                    if appconfig['id']==0:
                        port=appconfig['port']
                        host=appconfig['host']
                        loginuser=appconfig['loginuser']
                        loginpassword=appconfig['loginpassword']                        
                    if port is None:
                        portStr=r' '
                    else:
                        portStr=r' -P '+port+r' '
                    userinfo=r' -l '+loginuser+r' -pw '+loginpassword+portStr
                    
                    slog=''
                    if appconfig.has_key('appfolder') and appconfig.has_key('app') and appconfig['app'] is not None and appconfig['app']!='' and appconfig['appfolder'] is not None and appconfig['appfolder']!='':
                        slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+appconfig['appfolder']+'/'+appconfig['app']+' to host.\n'
                        writeLog(cmdFolder+installproductsLog,'a',slog)
                        if os.path.isfile(appconfig['appfolder']+'/'+appconfig['app']):
                            returnVal=os.system(r'pscp.exe -batch '+userinfo+r' "'+appconfig['appfolder']+'/'+appconfig['app']+r'" '+host+':'+appconfig['installfolder']+'/')
                        else:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+appconfig['appfolder']+'/'+appconfig['app']+' does not exist.\n'
                            writeLog(cmdFolder+installproductsLog,'a',slog)
                            returnVal=-1
                    else:
                        if appconfig['type']!="0":
                            returnVal=0
                        else:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Warn: id['+str(appconfig['id'])+'] fail to copy file appfolder/app.\n'
                            writeLog(cmdFolder+installproductsErr,'a',slog)
                            returnVal=-1
                    if returnVal==0:
                        if appconfig.has_key('propertiesfolder') and appconfig.has_key('properties') and appconfig['propertiesfolder'].strip() and appconfig['properties'].strip():
                            if os.path.isfile(appconfig['propertiesfolder']+'/'+appconfig['properties']):
                                if re.search('^[^/]',appconfig['propertiesfolder'],re.IGNORECASE) and str(appconfig['type'])=='0':
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' to host.\n'
                                    writeLog(cmdFolder+installproductsLog,'a',slog)
                                    returnVal=os.system(r'pscp.exe -batch '+userinfo+r' "'+appconfig['propertiesfolder']+'/'+appconfig['properties']+r'" '+host+':'+appconfig['installfolder']+'/')
                                elif re.search('^[^/]',appconfig['propertiesfolder'],re.IGNORECASE) and str(appconfig['type'])!='0':
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' to host\'s installfolder/bin folder.\n'
                                    writeLog(cmdFolder+installproductsLog,'a',slog)
                                    returnVal=os.system(r'pscp.exe -batch '+userinfo+r' "'+appconfig['propertiesfolder']+'/'+appconfig['properties']+r'" '+host+':'+appconfig['installfolder']+'/bin/') 
                                else:
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Info: id['+str(appconfig['id'])+'] no need to copy propertiesfolder or properties.\n'
                                    writeLog(cmdFolder+installproductsErr,'a',slog)
                                if returnVal!=0:
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: id['+str(appconfig['id'])+'] copy file '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' failed.\n'
                                    writeLog(cmdFolder+installproductsErr,'a',slog)
                            else:
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' does not exist.\n'
                                writeLog(cmdFolder+installproductsLog,'a',slog)
                                returnVal=-1
                        else:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Warn: id['+str(appconfig['id'])+'] key propertiesfolder or properties doesn\'t exist, please check if it is correct.\n'
                            writeLog(cmdFolder+installproductsErr,'a',slog)
                        ###
                        if returnVal==0:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' execute '+prefixRemoteCmd+str(appconfig['id'])+'.sh'+' in host.\n'
                            writeLog(cmdFolder+installproductsLog,'a',slog)
                            returnVal=os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+cmdFolder+prefixRemoteCmd+str(appconfig['id'])+'.sh')
                            if returnVal==0:
                                #copy log from host
                                if os.path.isfile(cmdFolder+prefixRemoteCmd+str(appconfig['id'])+'.log'):
                                    os.remove(cmdFolder+prefixRemoteCmd+str(appconfig['id'])+'.log')
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+prefixRemoteCmd+str(appconfig['id'])+'.log'+' from host.\n'
                                writeLog(cmdFolder+installproductsLog,'a',slog)
                                os.system(r'pscp.exe -batch '+userinfo+host+':'+appconfig['installfolder']+'/'+prefixRemoteCmd+str(appconfig['id'])+r'.log .\\log\\')
                                #copy installproducts.tmp from host
                                if os.path.isfile(cmdFolder+'installproducts.tmp'):
                                    os.remove(cmdFolder+'installproducts.tmp')
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy installproducts.tmp from host.\n'
                                writeLog(cmdFolder+installproductsLog,'a',slog)
                                os.system(r'pscp.exe -batch '+userinfo+host+':'+appconfig['installfolder']+'/installproducts.tmp'+r' '+'.\\log\\')
                                with open(cmdFolder+installproductsLog,'a') as rHDL:
                                    with open(cmdFolder+'installproducts.tmp','r') as tmpHDL:
                                        for line in tmpHDL.readlines():
                                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+line
                                            rHDL.write(slog)
                                            print slog
                                    rHDL.write('\n')
                            else:
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: id['+str(appconfig['id'])+'] execute file '+prefixRemoteCmd+str(appconfig['id'])+'.sh'+' failed.\n'
                                writeLog(cmdFolder+installproductsErr,'a',slog)
                                
                        #
                
                #os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+configRemoteStartAR)
                #os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+configRemoteStartAR)                
            else:#not search applicationServers
                pass
                
    
else:
    print 'checking databases aren\'t restored successfully, abort.\n'
    