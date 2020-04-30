#!/usr/bin/env python
# coding=utf-8
#Author by allisnone, 2020-04-30
from exchangelib import Credentials, Account,Configuration,DELEGATE,Folder
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3

urllib3.disable_warnings () 
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

def get_info_from_skyobject(obj):
    """
获取exchange数据发现扫描的结果，网络数据发现调用脚本后，默认会把第一参数送给--动作脚本
    obj={ 'username': 'ets1@skyguardgx.com', 'domain': 'domain-xxx.com', 
       'script_config': {'max_script_instances': 10, 'time_out': 10}, 
       'task_id': '013f16be-fbc1-4b64-9d06-2d6c7d994a66', 'ssl': 'false',
       'file_last_modified_time': '2020-04-30 12:15:16', 
       'file_name': '\xe5\x9b\x9e\xe5\xa4\x8d: \xe6\x9c\xba\xe5\xaf\x86\xe6\x96\x87\xe4\xbb\xb6 \xe6\xb5\x8b\xe8\xaf\x95   ets1 -ets2 ets3-test2-01', 
       'scan_mode': 'FULL', 'file_permission': '', 'ds_id': 5, 'port': 80, 
       'source_type': 'exchangeserver', 'host': '172.16.0.84', 'file_size': 3072, 
       'time_stamp': '2020-04-30 15:32:17', 'dsa_id': 'd1508086-3d71-4b58-ac83-dd99ae841c0c', 
       'password': 'Firewall1', 'file_path': 'ets3@domain-xxx.com/\xe6\x94\xb6\xe4\xbb\xb6\xe7\xae\xb1'
    }
    """
    return obj

class Skyexchange:
    """
    先设置admin的账号比如admin(可以不是administrator账号)，使用该用户对其他用户的违规邮件进行隔离或者删除的操作；
    因此。该用户必须能拥有其他用户的“管理完全访问权限”，主要用户管理和操作其他用户的邮件或者目录；请向exchange管理员申请用户并做权限设置。
    """
    def __init__(self,target_email, action='isolate',admin_username='',admin_password='', server='mail.domain-xxx.com',
            domain='',auth_type='NTLM',port=443,isolate_folder='isolate',task_id=''):
        """
        param admin_username: str, like user1
        param admin_password: password, like "abcdefg1", plant text
        param target_email: the target email account to be handled, should be valid email address in the same domain
        param server: str, domain name should be like as 'mail.xxxx.com', otherwise, set /etc/hosts file in exchange client 
        param auth_type: str, NTLM by defualt
        param port: int, exchange https service port, defualt is 443.
        """ 
        self.set_credentials(user=admin_username,password=admin_password,domain=domain.split('.')[0])
        self.config = Configuration(server=server, credentials=self.credentials,auth_type=auth_type)
        self.admin_account = self.connect_account((admin_username+server).replace('mail.','@'),self.config)
        if action=='isolate':
            self.set_isolate_folder(folder=isolate_folder,task_id=task_id)
    
    def connect_account(self,email,config=None):
        """
        param email: str, like user1@abcd.com
        param config: Configuration
        return: Account object
        """
        if config==None:
            return Account(primary_smtp_address=email, config=self.config,autodiscover=False, access_type=DELEGATE)
        return Account(primary_smtp_address=email, config=config,autodiscover=False, access_type=DELEGATE)
    
    def set_credentials(self,user,password,domain='domain-xxx'):
        """
        param user: str, like user1
        param password: str, like "abcdefg1", plant text
        param domain: str, domain, like  'yuexin', without any dot
        return: None
        """
        self.credentials = Credentials('{0}\\{1}'.format(domain,user), password)
        
    def set_config(self,server,credentials,auth_type='NTLM'):
        self.config = Configuration(server=server, credentials=self.credentials,auth_type=auth_type)
        
    
    def set_isolate_folder(self,folder='isolate',task_id=''):
        """
        在admin账户设置专门的目录，用于收集和隔离的所有账户下的扫描出来的敏感邮件
        param folder: str, folder name
        return: None
        """
        self.isolate_folder = self.admin_account.inbox / folder
        if isolate_folder:
            pass
        else:
            f = Folder(parent=self.admin_account.inbox, name=folder)
            f.save()
            f.name = folder
            f.save()
            self.isolate_folder = f
        if task_id: #create isolated folder based on task if not exist
            task_fold = f / task_id
            if task_fold:
                pass
            else:
                t = Folder(parent=self.admin_account.inbox, name=task_id)
                t.save()
                t.name = folder
                t.save()
            self.isolate_folder = t       
        return 
    
    def isolate_email_by_subject(self,target_email, subject='',startwith='',datetime=''):
        """
       隔离的指定账户下的指定标题邮件
        param target_email: str, target email account
        param subject: str, target email account
        param startwith: str, start with special keyword
        param datetime: str, specify time to get the unique email---todo
        return: 1 - isolated the target mail, 0 - no isolating action 
        """
        user_email_account = self.connect_account(email)
        #emails = user_email_account.inbox.filter(subject__startswith='Invoice')
        emails = user_email_account.inbox().filter(subject=subject)
        #QuerySet(q=subject == 'test2-机密', folders=[Inbox (收件箱)])
        if emails:
            #emails.copy(to_folder=some_folder)
            #emails.move(to_folder=account_admin.inbox / 'ems_fold1')
            emails.move(to_folder=self.isolate_folder)
            return 1
        else:
            pass
        return 0
    
    def delete_email_by_subject(self,target_email, task_id='',subject='',startwith='',datetime=''):
        """
       删除的指定账户下的指定标题邮件
        param target_email: str, target email account
        param subject: str, target email account
        param startwith: str, start with special keyword
        param datetime: str, specify time to get the unique email---todo
        return: 1 - deleted the target mail, 0 - no delete action
        """
        user_email_account = self.connect_account(email)
        #emails = user_email_account.inbox.filter(subject__startswith='Invoice')
        emails = user_email_account.inbox().filter(subject=subject)
        #QuerySet(q=subject == 'test2-机密', folders=[Inbox (收件箱)])
        if emails:
            #emails.delete(page_size=25)
            emails.delete()
            return 1
        else:
            pass
        return 0
    
    def action(self,target_email,action_type='isolate', subject='',startwith='',datetime=''):
        """
       删除或隔离的指定账户下的指定标题邮件
        param target_email: str, target email account
        param subject: str, target email account
        param startwith: str, start with special keyword
        param datetime: str, specify time to get the unique email---todo
        return: str, action type
        """
        if action_type=='delete':
            self.delete_email_by_subject(target_email, subject,startwith,datetime)
            return 'deleted'
        elif action_type=='isolate':
            self.isolate_email_by_subject(target_email, subject,startwith,datetime)
            return 'isolated'
        else:
            pass
        return 'None'
            
    def search_mail(self):
        return
    
    
    def send_mail(self):
        return
    
    def send_mail_bcc(self):
        return
    
    def form_mail(self):
        return
    
if __name__ == '__main__':
    #obj = input()
    #"""
    obj={ 'username': 'ets1@skyguardgx.com', 'domain': 'skyguardgx.com', 
       'script_config': {'max_script_instances': 10, 'time_out': 10}, 
       'task_id': '013f16be-fbc1-4b64-9d06-2d6c7d994a66', 'ssl': 'false',
       'file_last_modified_time': '2020-04-30 12:15:16', 
       'file_name': '\xe5\x9b\x9e\xe5\xa4\x8d: \xe6\x9c\xba\xe5\xaf\x86\xe6\x96\x87\xe4\xbb\xb6 \xe6\xb5\x8b\xe8\xaf\x95   ets1 -ets2 ets3-test2-01', 
       'scan_mode': 'FULL', 'file_permission': '', 'ds_id': 5, 'port': 80, 
       'source_type': 'exchangeserver', 'host': '172.16.0.84', 'file_size': 3072, 
       'time_stamp': '2020-04-30 15:32:17', 'dsa_id': 'd1508086-3d71-4b58-ac83-dd99ae841c0c', 
       'password': 'Firewall1', 'file_path': 'ets3@skyguardgx.com/\xe6\x94\xb6\xe4\xbb\xb6\xe7\xae\xb1'
    }
    #"""
    action='isolate'
    file_path = obj['file_path']
    paths = file_path.split('/')
    if len(paths) !=2:
        import sys
        sys.exist()   
    target_email = paths[0]
    root_folder = paths[1]   #should be inbox by default
    file_name = obj['file_name']
    time_stamp = obj['time_stamp']
    task_id = obj['task_id']
    admin = obj['username'].split('@')[0]
    #admin_username = 'ets1'
    password = obj['password']
    #admin_password = 'Firewall1'
    domain = obj['domain']
    exg_obj = Skyexchange(target_email, action=action,admin_username=admin,admin_password=password, server='mail.skyguardgx.com',domain=domain,auth_type='NTLM',port=443,isolate_folder='isolate',task_id=task_id)
    exg_obj.action(target_email,action_type=action, subject=file_name,startwith='',datetime='')
    print('{0} mail completed: {1} --{2} '.format(action,file_path,file_name))
    