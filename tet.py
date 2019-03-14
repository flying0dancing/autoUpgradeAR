#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,sys, getopt

def main(argv):
    configFile = ''
    executeFilePath=os.path.dirname(sys.argv[0])
    executeFileName=os.path.basename(sys.argv[0])
    print executeFilePath
    print executeFileName
    try:
        opts, args = getopt.getopt(argv,"hc:",["configfile="])
    except getopt.GetoptError:
        print executeFileName+' -c <configFile>'
        sys.exit(2)
    if len(sys.argv)==1:
        print 'usage: '+executeFileName+' -c <configfile> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'usage: '+executeFileName+' -c <configfile> '
            sys.exit(0)
        elif opt in ('-c', '--configfile'):
            configFile = arg

    print '输入的文件为：', configFile

if __name__ == "__main__":
    main(sys.argv[1:])