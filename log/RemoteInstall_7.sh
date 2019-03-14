#!/bin/bash
installfolder=/home/testp/trump_11
description="ar for HKMA data alias"
DIDimplementationVersion=5.22.2.4
DIDprefix=HKMA
id=7
DIDaliasName="STB Data HKMA:STB CORE Data"
type=1
properties=HKMAoracleDataaliasinfo.properties
propertiesfolder=Z:\ProductLine\TrumpTest
logfile=installproducts.tmp
detaillog=RemoteInstall_$id.log

if [ -f "${installfolder}/${logfile}" ];then
    echo "delete file ${installfolder}/${logfile}"
    rm "${installfolder}/${logfile}"
fi

if [ -f "${installfolder}/${detaillog}" ];then
    echo "delete file ${installfolder}/${detaillog}"
    rm "${installfolder}/${detaillog}"
fi
if [ -n "${description}" ];then
    echo "================= ${description} ================="
fi
if [ "${installfolder}" = "None" ];then
    echo "error, installfolder is null"
    echo "installation is interrupted, because installfolder is null.">$logfile
else
    if [ -f "${installfolder}/bin/run.lock" ];then
        echo "stopping service"
        cd "${installfolder}"
        bash bin/stop.sh
        bash bin/cleanup.sh
        rm -f bin/run.lock
        rm -f bin/stop.lock
        rm -f bin/stop.error
        cd ~
    fi
    if [ "${type}" = "0" ];then
        cd "${installfolder}"
        port_base=`awk -F '=' /^host.port[^.]/'{print $2}' "${properties}"`
        port_offset=`awk -F '=' /^host.port.offset/'{print $2}' "${properties}"`
        port_zookeeper=`awk -F '=' /^zookeeper.port/'{print $2}' "${properties}"`
        
        if [ -n "${port_offset}" ];then
            let port=${port_base}+${port_offset}
        else
            port=${port_base}
        fi
        echo "port_base:${port_base},port_offset:${port_offset}"
        echo "port:${port}, port_zookeeper:${port_zookeeper}"
        netstat -atunlp | grep ${port}
        if [ "$?" = "0" ]; then
            echo "killing progress port:${port}"
            netstat -atunlp | awk '/${port}/{print substr($7,1,index($7,"/")-1)}' | sort | uniq | xargs kill -9
        fi
        netstat -atunlp | grep ${port_zookeeper}
        if [ "$?" = "0" ]; then
            echo "killing progress port_zookeeper:${port_zookeeper}"
            netstat -atunlp | awk '/${port_zookeeper}/{print substr($7,1,index($7,"/")-1)}' | sort | uniq | xargs kill -9
        fi
        cd "${installfolder}"
        java -jar "${app}" -options "${properties}" 2>&1 | tee $detaillog
        tail -5 $detaillog | grep -i "AgileREPORTER has been installed"
        if [ "$?" = "0" ]; then
            echo "${app} install or upgrade successfully."
            echo "install ${app} pass">$logfile
            if [ -n "${port_offset}" ];then
                cd jboss-eap*/standalone/configuration
                sed -i "s/port-offset:[0-9]/port-offset:${port_offset}/g" standalone.xml
            fi
        else
            echo "${app} install or upgrade fail, please check."
            echo "install ${app} fail">$logfile
        fi
        
    elif [ "${type}" = "1" ];then
        cd "${installfolder}"
        if [ -n "${app}" ];then
            echo "./bin/config.sh -a ${app}" >$detaillog
            echo "================================================================================" >>$detaillog
            ./bin/config.sh -a "${app}"  2>&1 | tee -a $detaillog
            tail -5 $detaillog | grep -i "successfully"
            if [ "$?" = "0" ]; then
                echo "${app} install or upgrade successfully."
                echo "install ${app} pass">$logfile
            else
                echo "${app} install or upgrade fail, please check."
                echo "install ${app} fail">$logfile
            fi
        fi
        if [ -n "${properties}" ];then 
            i=1
            while((1==1))
            do
               split=`echo ${DIDaliasName}|cut -d ":" -f$i`
                if [ "$split" != ""  -a "$split" != "${DIDaliasName}" ];then
                    ((i++))
                    echo "${split}"
                    echo "./bin/config.sh -ea ${DIDprefix} -iv ${DIDimplementationVersion} -alias \"${split}\" -aif \"bin/${properties}\"" >>$detaillog
                    echo "================================================================================" >>$detaillog
                    ./bin/config.sh -ea "${DIDprefix}" -iv "${DIDimplementationVersion}" -alias "${split}" -aif "bin/${properties}"  2>&1 | tee -a $detaillog
                    tail -5 $detaillog | grep -i "successfully"
                    if [ "$?" = "0" ]; then
                        echo "${split} configuration successfully."
                        echo "configure ${split} pass">>$logfile
                    else
                        echo "${split} configuration fail, please check."
                        echo "configure ${split} fail">>$logfile
                    fi
                elif [ "$split" != "" -a "$split" = "${DIDaliasName}" ];then
                    echo "${split}"
                    echo "./bin/config.sh -ea ${DIDprefix} -iv ${DIDimplementationVersion} -alias \"${split}\" -aif \"bin/${properties}\"" >>$detaillog
                    echo "================================================================================" >>$detaillog
                    ./bin/config.sh -ea "${DIDprefix}" -iv "${DIDimplementationVersion}" -alias "${split}" -aif "bin/${properties}" 2>&1 | tee -a $detaillog
                    tail -5 $detaillog | grep -i "successfully"
                    if [ "$?" = "0" ]; then
                        echo "${split} configuration successfully."
                        echo "configure ${split} pass">>$logfile
                    else
                        echo "${split} configuration fail, please check."
                        echo "configure ${split} fail">>$logfile
                    fi
                    break
                else
                    break
                fi 
            done
        fi
    else
        echo "type is wrong."
        echo "configure type fail">$logfile
    fi
fi
