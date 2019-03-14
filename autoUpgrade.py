#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,sys, getopt,json,re,time
from collections import OrderedDict

executeFilePath=os.path.dirname(sys.argv[0])
executeFileName=os.path.basename(sys.argv[0])

cmdFolder=executeFilePath+'\\log\\'

restoredbLog=cmdFolder+'restoredbs.log'
restoredbErr=cmdFolder+'restoredbs.err'
installproductsLog=cmdFolder+'installproducts.log'
installproductsErr=cmdFolder+'installproducts.err'
monitorsvnFileListLog=cmdFolder+'monitorSVNfilelist.txt'
monitorsvnDetails=cmdFolder+'monitorSVNDetails.log'
monitorsvnLog=cmdFolder+'monitorSVN.log'

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

def makedirs(fileFullPath):
    if os.path.exists(fileFullPath):
        pass
    else:
       os.makedirs(fileFullPath) 
def deletefile(fileFullPath):
    if os.path.isfile(fileFullPath):
        os.remove(fileFullPath)

def restoredbs(configs):
    configShellFolderName='impdp_and_expdp_shell'
    configLocalCmd=executeFilePath+'\\LocalRestoreDBII.txt'
    configRemoteCmd=executeFilePath+'\\RemoteRestoreDBII.txt'
    prefixRemoteCmd='RemoteRestoreDB_'
    prefixLocalCmd='LocalRestoreDB_'
    if os.path.exists(executeFilePath+'\\'+configShellFolderName) and os.path.isfile(configLocalCmd) and os.path.isfile(configRemoteCmd) and os.path.isfile('plink.exe') and os.path.isfile('pscp.exe'):
        pass
    else:
        print('please check these folders or files are exists.\n')
        print('folders: '+configShellFolderName+'\n')
        print('files: '+configLocalCmd+', '+configRemoteCmd+', plink.exe, pscp.exe')
        sys.exit(0)
    deletefile(restoredbLog)
    deletefile(restoredbErr)
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
                        returnVal=os.system(r'pscp.exe -r -batch '+userinfo+r' '+executeFilePath+'\\'+configShellFolderName+r' '+dbconfig['host']+':'+'/home/'+dbconfig['loginuser']+'/')
                        if returnVal==0:
                            returnVal=os.system(r'plink.exe -ssh -batch -v '+dbconfig['loginuser']+'@'+dbconfig['host']+' -pw '+dbconfig['loginpassword']+' -m '+cmdFolder+prefixRemoteCmd+str(dbconfig['id'])+'.sh')
                            if returnVal==0:
                                #logfile=dbconfig['username'].replace('\\$', '')+'.log'
                                os.system(r'pscp.exe -batch '+userinfo+dbconfig['host']+':/home/'+dbconfig['loginuser']+'/'+configShellFolderName+'/'+prefixRemoteCmd+str(dbconfig['id'])+'.log '+cmdFolder)
                                os.system(r'pscp.exe -batch '+userinfo+dbconfig['host']+':/home/'+dbconfig['loginuser']+'/'+configShellFolderName+'/restoredbs.tmp'+r' '+cmdFolder)
                                with open(restoredbLog,'a') as rHDL:
                                    with open(cmdFolder+'restoredbs.tmp','r') as tmpHDL:
                                        rHDL.write(tmpHDL.read())
                            else:
                                writeLog(restoredbErr,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: execute file '+prefixRemoteCmd+str(dbconfig['id'])+'.sh'+r' failed.\n')
                        else:
                            writeLog(restoredbErr,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: copy folder '+configShellFolderName+r' failed.\n')
                            
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
                            writeLog(restoredbErr,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: execute file '+prefixLocalCmd+str(dbconfig['id'])+r'.bat failed.\n')
                            
def installproducts(configs):
    configLocalCmd=executeFilePath+'\\LocalInstallII.txt'
    configRemoteCmd=executeFilePath+'\\RemoteInstallII.txt'
    prefixRemoteCmd='RemoteInstall_'
    prefixLocalCmd='LocalInstall_'
    deletefile(installproductsLog)
    deletefile(installproductsErr)
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
                        writeLog(installproductsLog,'a',slog)
                        if os.path.isfile(appconfig['appfolder']+'/'+appconfig['app']):
                            returnVal=os.system(r'pscp.exe -batch '+userinfo+r' "'+appconfig['appfolder']+'/'+appconfig['app']+r'" '+host+':'+appconfig['installfolder']+'/')
                        else:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+appconfig['appfolder']+'/'+appconfig['app']+' does not exist.\n'
                            writeLog(installproductsLog,'a',slog)
                            returnVal=-1
                    else:
                        if appconfig['type']!="0":
                            returnVal=0
                        else:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Warn: id['+str(appconfig['id'])+'] fail to copy file appfolder/app.\n'
                            writeLog(installproductsErr,'a',slog)
                            returnVal=-1
                    if returnVal==0:
                        if appconfig.has_key('propertiesfolder') and appconfig.has_key('properties') and appconfig['propertiesfolder'].strip() and appconfig['properties'].strip():
                            if os.path.isfile(appconfig['propertiesfolder']+'/'+appconfig['properties']):
                                if re.search('^[^/]',appconfig['propertiesfolder'],re.IGNORECASE) and str(appconfig['type'])=='0':
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' to host.\n'
                                    writeLog(installproductsLog,'a',slog)
                                    returnVal=os.system(r'pscp.exe -batch '+userinfo+r' "'+appconfig['propertiesfolder']+'/'+appconfig['properties']+r'" '+host+':'+appconfig['installfolder']+'/')
                                elif re.search('^[^/]',appconfig['propertiesfolder'],re.IGNORECASE) and str(appconfig['type'])!='0':
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' to host\'s installfolder/bin folder.\n'
                                    writeLog(installproductsLog,'a',slog)
                                    returnVal=os.system(r'pscp.exe -batch '+userinfo+r' "'+appconfig['propertiesfolder']+'/'+appconfig['properties']+r'" '+host+':'+appconfig['installfolder']+'/bin/') 
                                else:
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Info: id['+str(appconfig['id'])+'] no need to copy propertiesfolder or properties.\n'
                                    writeLog(installproductsErr,'a',slog)
                                if returnVal!=0:
                                    slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: id['+str(appconfig['id'])+'] copy file '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' failed.\n'
                                    writeLog(installproductsErr,'a',slog)
                            else:
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+appconfig['propertiesfolder']+'/'+appconfig['properties']+' does not exist.\n'
                                writeLog(installproductsLog,'a',slog)
                                returnVal=-1
                        else:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Warn: id['+str(appconfig['id'])+'] key propertiesfolder or properties doesn\'t exist, please check if it is correct.\n'
                            writeLog(installproductsErr,'a',slog)
                        ###
                        if returnVal==0:
                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' execute '+prefixRemoteCmd+str(appconfig['id'])+'.sh'+' in host.\n'
                            writeLog(installproductsLog,'a',slog)
                            returnVal=os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+cmdFolder+prefixRemoteCmd+str(appconfig['id'])+'.sh')
                            if returnVal==0:
                                #copy log from host
                                deletefile(cmdFolder+prefixRemoteCmd+str(appconfig['id'])+'.log')
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+prefixRemoteCmd+str(appconfig['id'])+'.log'+' from host.\n'
                                writeLog(installproductsLog,'a',slog)
                                os.system(r'pscp.exe -batch '+userinfo+host+':'+appconfig['installfolder']+'/'+prefixRemoteCmd+str(appconfig['id'])+r'.log '+cmdFolder)
                                #copy installproducts.tmp from host
                                deletefile(cmdFolder+'installproducts.tmp')
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy installproducts.tmp from host.\n'
                                writeLog(installproductsLog,'a',slog)
                                os.system(r'pscp.exe -batch '+userinfo+host+':'+appconfig['installfolder']+'/installproducts.tmp'+r' '+cmdFolder)
                                with open(installproductsLog,'a') as rHDL:
                                    with open(cmdFolder+'installproducts.tmp','r') as tmpHDL:
                                        for line in tmpHDL.readlines():
                                            slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+line
                                            rHDL.write(slog)
                                            print slog
                                    rHDL.write('\n')
                            else:
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' Error: id['+str(appconfig['id'])+'] execute file '+prefixRemoteCmd+str(appconfig['id'])+'.sh'+' failed.\n'
                                writeLog(installproductsErr,'a',slog)                              
                        #             
            else:#not search applicationServers
                pass
def searchResultFlag(filefullpath,searchedStr):
    flagsuccess=True
    if os.path.isfile(filefullpath):
        with open(filefullpath,'r') as sHDL:
            for line in sHDL.readlines():
                if cmp(line.strip().upper(),searchedStr.upper())==0:
                    flagsuccess=False
    else:
        print 'Error: file not found ['+filefullpath+'].'
    return flagsuccess
    
def startAR(configs):
    configRemoteStartAR=executeFilePath+'\\RemoteStartAR.txt'
    prefixRemoteStartAR='RemoteStartAR'
    flagsuccess=searchResultFlag(installproductsLog,'FAIL')
    flagsuccess=searchResultFlag(installproductsErr,'ERROR')
    if !flagsuccess:
        sys.exit(1)
    for confi in configs:
        for key,value in confi.items():
            if re.search('applicationServers',key,re.IGNORECASE):
                if value[0].has_key('installfolder') and value[0]['installfolder'] is not None and re.search('^/',value[0]['installfolder'],re.IGNORECASE):
                    with open(cmdFolder+prefixRemoteStartAR+'.sh','w') as sHDL:
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
                        with open(configRemoteStartAR,'r') as sIIHDL:
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
                    returnVal=os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+cmdFolder+prefixRemoteStartAR+'.sh')
                    if returnVal==0:
                        writeLog(installproductsLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' start Agile REPORTER pass\n')
                        #copy log from host
                        deletefile(cmdFolder+prefixRemoteStartAR+'.log')
                        writeLog(installproductsLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+prefixRemoteStartAR+'.log'+' from host.\n')
                        os.system(r'pscp.exe -batch '+userinfo+host+':'+value[0]['installfolder']+'/'+prefixRemoteStartAR+r'.log '+cmdFolder)
                    else:
                        writeLog(installproductsLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' start Agile REPORTER fail\n')       
                else:#local install
                    print 'please check "installfolder" does exist and not null in configuration.'

def stopAR(configs):
    configRemoteStopAR=executeFilePath+'\\RemoteStopAR.txt'
    prefixRemoteStopAR='RemoteStoptAR'
    flagsuccess=searchResultFlag(installproductsLog,'FAIL')
    flagsuccess=searchResultFlag(installproductsErr,'ERROR') 
    if !flagsuccess:
        sys.exit(1)
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
                    returnVal=os.system(r'plink.exe -ssh -batch -v '+loginuser+'@'+host+' -pw '+loginpassword+' -m '+cmdFolder+prefixRemoteStopAR+'.sh')
                    if returnVal==0:
                        writeLog(cmdFolder+installproductsLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' stop Agile REPORTER pass\n')
                        #copy log from host
                        deletefile(cmdFolder+prefixRemoteStopAR+'.log')
                        writeLog(cmdFolder+installproductsLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' copy '+prefixRemoteStopAR+'.log'+' from host.\n')
                        os.system(r'pscp.exe -batch '+userinfo+host+':'+value[0]['installfolder']+'/'+prefixRemoteStopAR+r'.log '+cmdFolder)
                    else:
                        writeLog(cmdFolder+installproductsLog,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' stop Agile REPORTER fail\n')       
                else:#local install
                    print 'please check "installfolder" does exist and not null in configuration.'
                    
def monitorSVN(configs):
    flag=True
    deletefile(monitorsvnFileListLog)
    deletefile(monitorsvnDetails)
    deletefile(monitorsvnLog)
    for confi in configs:
        for key,value in confi.items():
            if re.search('svnSettings',key,re.IGNORECASE):
                for appconfigs in value:
                    appconfig=OrderedDict(appconfigs)
                    makedirs(appconfig['localpath'])
                    userinfo=r' --username "'+appconfig['loginuser']+'" --password '+appconfig['loginpassword']+r' '
                    fileList=appconfig['files']
                    fileDic={}
                    for fileA in fileList:
                        fileDic[fileA]=False
                    if cmp(appconfig['url'][-1],'/')!=0:
                        appconfig['url']=appconfig['url']+'/'
                    time_start=time.time()
                    writeLog(monitorsvnDetails,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' start to monitor '+appconfig['url']+'\n')
                    monitorTmp=-1#initial
                    while appconfig['bemonitored'] is not None and re.search(appconfig['bemonitored'],'yes',re.IGNORECASE):
                        print 'we are bemonitored is yes'
                        os.system(r'svn list "'+appconfig['url']+'"'+userinfo+r'--depth "infinity">'+monitorsvnFileListLog)
                        for fileTmp,val in fileDic.items():
                            print 'fileTmp: '+fileTmp
                            if val==True:
                                continue
                            if searchStrInFile(monitorsvnFileListLog,fileTmp):
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+fileTmp+' find\n'
                                writeLog(monitorsvnDetails,'a',slog)
                                os.system(r'svn export "'+appconfig['url']+fileTmp+r'" "'+appconfig['localpath']+'"'+userinfo+r'--no-auth-cache --force')#run svn
                                fileDic[fileTmp]=True
                        if False in fileDic.values():
                            if appconfig['timeout']>-1 and time.time()-time_start>appconfig['timeout']:
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' id:'+str(appconfig['id'])+' timeout\n'
                                writeLog(monitorsvnDetails,'a',slog)
                                monitorTmp=1
                                break
                        else:
                            monitorTmp=0
                            break
                        
                    if appconfig['bemonitored'] is not None and re.search(appconfig['bemonitored'],'no',re.IGNORECASE):
                        print 'we are bemonitored is no'
                        os.system(r'svn list "'+appconfig['url']+'"'+userinfo+r'--depth "infinity">'+monitorsvnFileListLog)
                        monitorTmp=2#standalone no monitor                            
                        for fileTmp in fileList:                    
                            if searchStrInFile(monitorsvnFileListLog,fileTmp):    
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+fileTmp+' find\n'
                                writeLog(monitorsvnDetails,'a',slog)
                                os.system(r'svn export "'+appconfig['url']+fileTmp+r'" "'+appconfig['localpath']+'"'+userinfo+r'--no-auth-cache --force')#run svn
                            else:
                                slog=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+fileTmp+' miss\n'
                                writeLog(monitorsvnDetails,'a',slog)       
                    writeLog(monitorsvnDetails,'a',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' stop to monitor '+appconfig['url']+'\n')
                    if monitorTmp==0:
                        writeLog(monitorsvnLog,'a','id:'+str(appconfig['id'])+' pass\n')
                    elif monitorTmp==1:
                        writeLog(monitorsvnLog,'a','id:'+str(appconfig['id'])+' fail\n')
                        flag=False
                    elif monitorTmp==2 or monitorTmp==-1:
                        writeLog(monitorsvnLog,'a','id:'+str(appconfig['id'])+' skip\n')
    return flag                    
                        
def main(argv):
    configFile = ''
    makedirs(cmdFolder)
    try:
        opts, args = getopt.getopt(argv,"hc:m:",["configfile=","module="])
    except getopt.GetoptError:
        print executeFileName+' -c <configFile> -m <monitorsvn|restoredb|install|startar|stopar>'
        sys.exit(2)
    if len(sys.argv)==1:
        print 'usage: '+executeFileName+' -c <configfile> -m <monitorsvn|restoredb|install|startar|stopar>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'usage: '+executeFileName+' -c <configfile> -m <monitorsvn|restoredb|install|startar|stopar>'
            sys.exit(0)
        elif opt in ('-c', '--configfile'):
            configFile = arg
            with open(executeFilePath+'\\'+configFile,'r') as f:
                configs=json.load(f)
    for opt,arg in opts:
        if opt in ('-m','--module'):
            if cmp(arg.lower(),'monitorsvn')==0:
                if monitorSVN(configs):
                    sys.exit(0)
                else:
                    sys.exit(1)
            elif cmp(arg.lower(),'restoredb')==0:
                restoredbs(configs)
            elif cmp(arg.lower(),'install')==0:
                installproducts(configs)
            elif cmp(arg.lower(),'startar')==0:
                startAR(configs)
            elif cmp(arg.lower(),'stopar')==0:
                stopAR(configs)
if __name__ == "__main__":
    main(sys.argv[1:])