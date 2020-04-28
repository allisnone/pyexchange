#!/usr/bin/env python
# coding=utf-8

import commands
import sys
import json
import os
import locale
import md5

reload(sys)
sys.setdefaultencoding('utf8')

def rename():
    obj = input()
    print 'json_str111:', obj
    print 'type of json_str111:', type(obj)
    file_path = obj['file_path']
    file_path=file_path.replace('\\', '/')
    user = obj['username']
    password = obj['password']
    source_type = obj['source_type']
    task_id = obj['task_id']
    mount_cmd = ''
    mount_root = '/opt/skyguard/ucs/var/dsa/discovery_mount'
    print 'aaa'
    print 'argv:', sys.argv
    if len(sys.argv) < 2:
        print 'please input incident path!!!'
        return 
    incident_path = sys.argv[1] + '/' + obj['task_id']
    if not os.path.exists(incident_path):
        os.makedirs(incident_path)
    full_path = file_path + '/' + obj['file_name']
    m = md5.new()
    m.update(full_path)
    incident_name = m.hexdigest()
    incident_full_path = incident_path + '/' + incident_name +'.txt'
    f = open(incident_full_path, 'w')
    f.write(obj['incident'])
    f.close()
    
    
    print 'file_path:', file_path
    print 'user:', user
    print 'password:', password
    
if __name__ == '__main__':
    print 'Exchange action start...'
    rename()
    print 'Exchange action completed!'