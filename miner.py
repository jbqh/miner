#!/usr/bin/python
#coding:utf-8

import os
import time
from ConfigParser import ConfigParser
from paramiko import *
from commands import getstatusoutput

#def app_init():
#if os.path.exists(os.curdir+'/miner.list'):

def get_config():
    conf = os.curdir + '/miner.conf'
    if os.path.exists(conf):
        config = ConfigParser()
        config.read(config)
        ghs = config.get('default','ghs')
        maillist = config.get('default','maillist')
        if ghs.isdigit():
            ghs = int(ghs)
        else:
            ghs = 13000
        if maillist is None:
            maillist = 'jbqh@qq.com'
    else:
        ghs = 13000
        maillist = 'jbqh@qq.com'
        
    return (ghs,maillist)
    
def check_active(host):
    cmd = 'ping -c 2 %s &> /dev/null' % host
    if getstatusoutput(cmd)[0] == 0:
        return 0
    else:
        return 1
        
def get_ghs(host):
    cmd = "bmminer-api -o | awk -F',' '{print $7}' | cut -d'=' -f2"
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    (ghs,maillist) = get_config()
    try:
        ssh.connect(host,22,'root','admin')
        (stdin,stdout,stderr) = ssh.exec_command(cmd)
        curghs = stdout.read()
        if curghs:
            curghs = float(curghs)
        else:
            curghs = 0
        if curghs > ghs:
            return (0,curghs)
        else:
            return (1,curghs)
    except:
		print 'a'

def miner_log(msg):
    #0 - fatal
    #1 - info
    sj = time.strftime('%F %T',time.localtime())
    flog = os.curdir + '/miner.log'
    fs = open(flog,'a+')
    m = sj + msg
    print m
    fs.writelines(m) 
    fs.close()

def main():
    mlist_file = os.curdir + '/miner.list'
    tmpfile = os.curdir + '/tmp'
    if os.path.exists(tmpfile): os.remove(tmpfile)
    try:
        mlist = open(mlist_file,'r').readlines()
        for host in mlist:
            if host is None or host[0] == '#':  continue
            host = host.rstrip('\n')
            act = check_active(host)
    except:
        pass
        
        
#progmar starting...
mlist = os.curdir + '/miner.list'
if not os.path.exists(mlist):
    msg = ' [FATAL] 致命错误，算力服务器列表不存在！\n'
    miner_log(msg)
    exit(99)

t = os.curdir + '/miner.list'
mlist = open(t,'r')
offline = []
lower = []

if mlist:
    for host in mlist:
        host = host.rstrip('\n')
        ip = host.strip()
        if not len(ip) == 0 or not ip.startswith('#'):
            status = check_active(host)
            if status == 0:
                (s,ghs) = get_ghs(host)

