#!/usr/bin/python
#coding:utf-8

import os
import time
import MySQLdb
from paramiko import *
from ConfigParser import ConfigParser
from commands import getstatusoutput


class Miner():
            
    def __init__(self):
       self.ghs = 13000
       self.maillist = 'abc@qq.com'
       self.hostlist = []
       self.onlinelist = []
       self.offlinelist = []
       self.lowerlist = []
       msg = '=================================== start to check miner =================================\n'
       fs = open(os.curdir + '/miner.log','a')
       fs.writelines(msg)
       fs.close()
       self.__check_host__()
       self.__get_config__()

    #check miner list 
    def __check_host__(self):
        minerlist = os.curdir + '/miner.list'
        if not os.path.exists(minerlist):
            msg = 'miner.list is not exist!' 
            exit(msg)
            
        fs = open(minerlist,'r')
        for line in fs:
            line = line.strip()
            if line:
                if line.startswith('#') or line.startswith(';'):
                    continue
                self.hostlist.append(line)
        fs.close()
        self.__check_miner_status(self.hostlist)
        
    #check miner status,online or offline    
    def __check_miner_status(self,hostlist):
        if not hostlist:
            msg = 'no miner host in miner.list'
            exit(msg)
            
        for miner in hostlist:
            cmd = 'ping -c 2 %s &> /dev/null' % miner
            if getstatusoutput(cmd)[0] == 0:
                self.onlinelist.append(miner)
            else:
                msg = ' [ERROR] miner %s is not connected,please check it!' % miner
                self.__save_logs__(msg)
                self.offlinelist.append(miner)
            
    #read config file if exist, or use default
    def __get_config__(self):
        conf =os.curdir + '/miner.conf'
        try:
            if os.path.exists(conf):
                config = ConfigParser()
                config.read(conf)
                self.ghs = int(config.get('default','ghs',self.ghs))
                self.maillist = config.get('default','maillist',self.maillist)
        except:
            pass

    def __save_logs__(self,msg):
        logfile = os.curdir + '/miner.log'
        sj = time.strftime('%F %T',time.localtime())
        fs = open(logfile,'a')
        msg = sj + msg + '\n'
        fs.writelines(msg)
        fs.close()
        
    #calc miner's ghs
    def get_ghs(self,miner):
        cmd = "bmminer-api -o | awk -F',' '{print $7}' | cut -d'=' -f2"
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(miner,22,'root','admin')
            (stdin,stdout,stderr) = ssh.exec_command(cmd)
            curghs = stdout.read()
            if curghs:
                curghs = float(curghs)
            else:
                curghs = self.ghs - 1
                
            if curghs > self.ghs:
                msg = " [INFO] miner %s status is normal,current ghs is: %.2f" % (miner,curghs)
            else:
                msg = " [WARNING] miner %s ghs is lower than %d,current ghs is %.2f" % (miner,self.ghs,curghs)
                msg1 = "miner %s ghs is lower than %d,current ghs is %.2f" % (miner,self.ghs,curghs)
                self.lowerlist.append(msg1)

            self.__save_logs__(msg)
        except Exception as e:
            msg = 'Failed to Connect to miner %s.' % miner
            self.__save_logs__(msg)
            exit(e)
            
        ssh.close()   
        
    def send_mail(self):
        offlinemsg = ''
        lowermsg = ''
        msg = ''

        if self.offlinelist:
            offline = ''
            for host in self.offlinelist:
                offline = offline + host + ' '
            offlinemsg = 'miner [ %s ] can not connect!' % offline
            msg = offlinemsg + '\n'

        if self.lowerlist:
            for host in self.lowerlist:
                lowermsg = lowermsg + host + '\n'
            msg = '\n' + msg + lowermsg + '\n'

        if (not offlinemsg) and (not lowermsg): 
            msg = ' [INFO] all miner is normal!'
            self.__save_logs__(msg)
            exit(0)
        else: 
            sub = '算力服务器异常'
            cmd =  'echo "%s" | mail -s "%s" "%s"' % (msg,sub,self.maillist)
            os.popen(cmd)
            msg = ' [INFO] alert mail sent successfully' 
            self.__save_logs__(msg)

m = Miner()
minerlist = m.onlinelist
if minerlist:
	for i in minerlist:
		m.get_ghs(i)
	m.send_mail()
else:
	exit('unknow error')
