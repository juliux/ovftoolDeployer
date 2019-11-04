#!/usr/bin/env python

# +-+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+
# PERFORMANCE FILE READER
# +-+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+

import sys
from termcolor import colored
import os
from datetime import datetime, timedelta
import math
import csv
import getpass as gp
import string
from random import *
import crypt
import base64
import logging
from subprocess import Popen, PIPE, CalledProcessError
#import progressbar

# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
STATIC_DOTTED_LINE2 = ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
CAR_RET = "\n"
PROVISIONING_MESSAGE = 'Provisioning started!'
MY_FILE = 'deployer.log'
STATIC_DOTTED_LINE = "................................................................."
EMPTY_SPACE = ""
PROVISIONING_MESSAGE = "Provisioning machine: "
PROVISIONING_OK = "Provisioning completed OK"
PROVISIONING_NOK = "Provisioning failed!"
MY_HARDCODED = 'JDYkYWhiN2l3b2hCbyQ1OGs0ckMvT3VKZlBscmQ2MjZWS2I4bXQvL3NKRjd2OC55MVcyMUZZUmQzSmc2TkFQelpsWjlodmdnRjJ2VjBTUVltNUJBa3hmZHdWTUxDWFkzV3RsMA=='
ERROR_READING_FILE = """

File not exist or is not accessible by permissions

----------DEPLOYMENT USAGE----------

./provisioning_vm_zone.py provisioning_file.csv

Where provisioning file is the information for the virtual machines to be
deployed.

The format for the provisioning file is:

"vm_name,ipaddr,gateway,netmask,sshport,ds,nw,hostname,username,timezone,deploymentOption,ova_file,vcenter_address,datacenter,cluster,resource_pool,vf"

----------DEPLOYMENT USAGE----------

"""
MY_PROVISIONING_PARAMETER_LIST =['vm_name','ipaddr','gateway','netmask','sshport','ds','nw','hostname','username','timezone','deploymentOption','ova_file','vcenter_address','datacenter','cluster','resource_pool','vf']

# +-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+
# CLASS DEFINITION
# +-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+

class OsAgent:

    FORMAT_STRING = "%Y-%m-%dT%H:%M"
    FORMAT_STRING2 = "%Y%m%d-%H%M"
    WAIT_REPORT_NAME = "wait-report"
    syslen = 0
    myFile = ""
    myValueList = []
    finalValueList = []
    hoursList = []
    mediaList = []
    xList = []
    yList = []
    myFinalFileName =""
    rawKeyboard = ""
    vcenterAuth = []
    #allchar = string.ascii_letters + string.punctuation + string.digits
    allchar = string.ascii_letters + string.digits
    minMax = (10,10)
    myFinalCommands = []
    fileName = ""
    #myProgressBar = None

    @staticmethod
    def clearScreen():
        os.system('clear')

    @staticmethod
    def elegantExit():
        sys.exit()

    @staticmethod
    def waitPlease(mySeconds):
        time.sleep(mySeconds)

    @staticmethod
    def myFileExist(myfile):
        if os.path.exists(myfile):
            return True
        else:
            return False

    #def progressBarPrint(self, message, listLen):
    #    self.myProgressBar = progressbar.progressbar(listLen)

    @staticmethod
    def executeCommands(listCommando,myFile):
        #os.system(commando)
        try:
            with open(myFile, 'a+') as filen:
                #myCommandExecution = Popen(listCommando, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                myCommandExecution = Popen(listCommando, stdout=filen, stderr=filen, universal_newlines=True)
                while True:
                    returnCode = myCommandExecution.poll()
                    if returnCode is not None:
                        filen.write(STATIC_DOTTED_LINE2)
                        filen.write(CAR_RET)
                        myTempString = 'Finished with execution code: '
                        myTempString = myTempString + str(returnCode) + '\n'
                        filen.write(myTempString)
                        filen.write(STATIC_DOTTED_LINE2)
                        filen.write(CAR_RET)
                        #print('RETURN CODE', returnCode)
                        if returnCode == 0:
                            # Process has finished, read rest of the output
                            #for output in myCommandExecution.stdout.readlines():
                            #    print(output.strip())
                            return True
                        else:
                            return False
                        break
        except OSError as error:
            with open(myFile, 'a+') as filen:
                filen.write(STATIC_DOTTED_LINE2)
                filen.write(CAR_RET)
                myTempString = 'Finished with execution code: '
                myTempString = myTempString + str(error.errno) + '\n'
                filen.write(myTempString)
                myTempString = 'Error presented is: '
                myTempString = myTempString + '"' + error.strerror + '"' + '\n'
                filen.write(myTempString)
                myTempString = '----------ERROR-----------\n'
                filen.write(myTempString)
                filen.write(error.strerror)
                filen.write('\n')
                myTempString = '--------------------------\n'
                filen.write(myTempString)
                filen.write(STATIC_DOTTED_LINE2)
                filen.write('\n')

    def countSysParameter(self):
        self.syslen = len( sys.argv )

    def setFilename(self,myfilename):
        self.fileName = myfilename

    def readKeyboard(self, question_string, flaga):
        if flaga == 1:
            self.rawKeyboard = raw_input( question_string )
        elif flaga == 2:
            self.rawKeyboard = gp.getpass( question_string )

    def printSysParameters(self):
        if self.syslen > 1:
            #for indiceparameter in enumerate(sys.argv):
            self.myFile = sys.argv[1]
            tempString = "Evaluating file: %s" % ( self.myFile )
            print( EMPTY_SPACE )
            print tempString
            print( EMPTY_SPACE )
            print colored( STATIC_DOTTED_LINE , 'yellow')
        else:
            print ( EMPTY_SPACE )
            print colored("No file provided!", 'red')
            print colored( STATIC_DOTTED_LINE , 'red')

    def openMyFile(self):
        with open(self.myFile,'r') as myLog:
            for myLine, myDataLine in enumerate(myLog):
                if myLine != 0:
                    myFields = myDataLine.split(',')
                    # - vm_name,ipaddr,gateway,netmask,sshport,ds,nw,hostname,username,timezone,deploymentOption,ova_file,vcenter_address,datacenter,cluster,resource_pool,vf
                    vm_name = myFields[0]
                    ipaddr = myFields[1]
                    gateway = myFields[2]
                    netmask = myFields[3]
                    sshport = myFields[4]
                    ds = myFields[5]
                    nw = myFields[6]
                    hostname = myFields[7]
                    username = myFields[8]
                    timezone = myFields[9]
                    deploymentOption = myFields[10]
                    ova_file = myFields[11]
                    vcenter_address = myFields[12]
                    datacenter = myFields[13]
                    cluster = myFields[14]
                    resource_pool = myFields[15]
                    vf = myFields[16].rstrip()
                    myTempTuple = ( vm_name,ipaddr,gateway,netmask,sshport,ds,nw,hostname,username,timezone,deploymentOption,ova_file,vcenter_address,datacenter,cluster,resource_pool,vf )
                    #print myTempTuple
                    self.myValueList.append(myTempTuple)

    def collectInteractiveValues(self):
        # - Read vcenter_user, vcenter_password
        print( EMPTY_SPACE )
        self.readKeyboard("Type your Vcenter Username: ",1)
        print colored( STATIC_DOTTED_LINE , 'yellow')
        print( EMPTY_SPACE )
        vcenterUser = self.rawKeyboard
        
        self.readKeyboard("Type your Vcenter Password: ",2)
        print colored( STATIC_DOTTED_LINE , 'yellow')
        print( EMPTY_SPACE )
        vcenterPass = self.rawKeyboard
        
        self.readKeyboard("Type the password to be used for the User installation: ",2)
        print colored( STATIC_DOTTED_LINE , 'yellow')
        print( EMPTY_SPACE )
        osClearPassword= self.rawKeyboard

        min_char, max_char = self.minMax
        randomExtension = "".join(choice(self.allchar) for x in range(randint(min_char,max_char)))
        #print randomExtension

        mySalt = "$6$" + randomExtension
        osCryptPassword = crypt.crypt(osClearPassword,mySalt)
        #print osCryptPassword

        osBase64Password = base64.encodestring(osCryptPassword)
        #print osBase64Password

        tempTuple = ( vcenterUser,vcenterPass,osBase64Password.rstrip())
        self.vcenterAuth.append(tempTuple)
        #print self.vcenterAuth

    def prepareCommands(self):
        #ovftool
        #--noSSLVerify
        #-ds=${ds}
        #--powerOn:1

        #-n=${vm_name}
        #-nw=${nw}
        #-vf=${vf}
        #--prop:ewp.hostname.EWP_VMware_Properties=${hostname}
        #--prop:ewp.ipaddr.EWP_VMware_Properties=${ipaddr}
        #--prop:ewp.gateway.EWP_VMware_Properties=${gateway}
        #--prop:ewp.netmask.EWP_VMware_Properties=${netmask}
        #--prop:ewp.sshport.EWP_VMware_Properties ${sshport}
        #--prop:ewp.username.EWP_VMware_Properties=${username}
        #--prop:ewp.userpasswd.EWP_VMware_Properties=${userpasswd}
        #--prop:ewp.timezone.EWP_VMware_Properties=${timezone}
        #--deploymentOption=${deploymentOption}
        #${ova_file} vi://${vcenter_user}:${vcenter_password}@${vcenter_address}//${datacenter}/host/${cluster}//Resources/${resource_pool}

        # - Authentication parameters
        vcenterUser,vcenterPass,osBase64Password = self.vcenterAuth[0]

        # - Generate commands
        for pametersLine in self.myValueList:
            vm_name,ipaddr,gateway,netmask,sshport,ds,nw,hostname,username,timezone,deploymentOption,ova_file,vcenter_address,datacenter,cluster,resource_pool,vf = pametersLine 
            DS = ' -ds=' + ds
            N = ' -n=' + vm_name
            NW = ' -nw=' + nw
            VF = ' -vf=' + vf
            HOSTNAME = ' --prop:ewp.hostname.EWP_VMware_Properties=' + hostname
            IPAD = ' --prop:ewp.ipaddr.EWP_VMware_Properties=' + ipaddr
            GW = ' --prop:ewp.gateway.EWP_VMware_Properties=' + gateway
            NM = ' --prop:ewp.netmask.EWP_VMware_Properties=' + netmask
            SSH = ' --prop:ewp.sshport.EWP_VMware_Properties=' + sshport
            USERNAME = ' --prop:ewp.username.EWP_VMware_Properties=' + username
            PASS = ' --prop:ewp.userpasswd.EWP_VMware_Properties=' + osBase64Password 
            #PASS = ' --prop:ewp.userpasswd.EWP_VMware_Properties=' + MY_HARDCODED
            TZ = ' --prop:ewp.timezone.EWP_VMware_Properties=' + timezone
            DO = ' --deploymentOption=' + deploymentOption
            VCSTRING = ' vi://' + vcenterUser + ":" + vcenterPass + '@' + vcenter_address + '//' + datacenter + '/host/' + cluster + '//Resources/' + resource_pool
            OVFSTRING = 'ovftool --noSSLVerify'
            OVAFILE = ' ' + ova_file
            POWER = ' --powerOn'
            COMMANDO = OVFSTRING + DS + POWER + N + NW + VF + HOSTNAME + IPAD + GW + NM + SSH + USERNAME + PASS + TZ + DO + OVAFILE + VCSTRING
            self.myFinalCommands.append(COMMANDO)


# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

osbox = OsAgent()
osbox.countSysParameter()
osbox.printSysParameters()
if OsAgent.myFileExist(osbox.myFile):
    osbox.openMyFile()
    osbox.collectInteractiveValues()
    osbox.prepareCommands()
    print osbox.myValueList
    print osbox.vcenterAuth
    print osbox.myFinalCommands
    osbox.setFilename(MY_FILE)
    for indice,myCommand in enumerate(osbox.myFinalCommands):
        myListCommand = list(myCommand.split(" "))
        mycomand = 'ls'
        myNode = str(myListCommand[4]).split("=")[1]
        myTempString = PROVISIONING_MESSAGE + myNode
        print colored(myTempString, 'yellow')
        if OsAgent.executeCommands(myListCommand,osbox.fileName):
        #if OsAgent.executeCommands(mycomand,osbox.fileName):
            print colored(PROVISIONING_OK,'green')
        else:
            print colored(PROVISIONING_NOK,'red')
    print(EMPTY_SPACE)
    print colored(STATIC_DOTTED_LINE,'yellow')
else:
    print colored(ERROR_READING_FILE,'yellow')
