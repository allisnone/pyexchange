#!/usr/bin/env python
# coding=utf-8
#Author by allisnone, 2020-04-30
from exchangelib import Credentials, Account,Configuration,DELEGATE,Folder
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
#import urllib3
import logging
from logging.handlers import TimedRotatingFileHandler
import sys,os,datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8') 

#urllib3.disable_warnings () 
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

def initial_logger(logfile='all.log',errorfile='error.log',logname='mylogger'):
    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)
    if sys.version_info.major==3: 
        rf_handler = TimedRotatingFileHandler(logfile, when='midnight', encoding='utf-8',interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0))
    else:
        rf_handler = TimedRotatingFileHandler(logfile, when='midnight', encoding='utf-8',interval=1, backupCount=7)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    #f_handler = logging.FileHandler(errorfile)
    #f_handler.setLevel(logging.ERROR)
    #f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
    logger.addHandler(rf_handler)
    #logger.addHandler(f_handler)
    return logger

def get_info_from_skyobject(obj):
    """
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
    """
    def __init__(self,target_email, action='isolate',admin_username='',admin_password='', server='mail.domain-xxx.com',
            domain='',auth_type='NTLM',port=443,isolate_folder='isolate',task_id='',logger=None):
        """
        param admin_username: str, like user1
        param admin_password: password, like "abcdefg1", plant text
        param target_email: the target email account to be handled, should be valid email address in the same domain
        param server: str, domain name should be like as 'mail.xxxx.com', otherwise, set /etc/hosts file in exchange client 
        param auth_type: str, NTLM by defualt
        param port: int, exchange https service port, defualt is 443.
        """ 
        self.logger =logger
        self.admin = admin_username
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
        param folder: str, folder name
        return: None
        """
        isolate_folder = None
        try:
            try:
                isolate_folder = self.admin_account.inbox / folder
                #i_folder = self.admin_account.inbox.glob(folder)
                #print('i_folder=',i_folder,i_folder._folders)
                if self.logger!=None: self.logger.info('isolated folder exist:{}'.format(isolate_folder))
            except Exception as e:
                f = Folder(parent=self.admin_account.inbox, name=folder)
                print 'isolate_folder=',f
                f.save()
                f.name = folder
                f.save()
                isolate_folder = f
                print 'isolate_folder=',f
                if self.logger!=None: self.logger.info('create isolated folder: inbox/{0}'.format(folder))
            if task_id: #create isolated folder based on task if not exist
                try:
                    task_fold = f / task_id
                    isolate_folder = task_fold
                    if self.logger!=None: 
                        self.logger.info('folder-task_id={0} already existed'.format(task_id))
                except Exception as e:
                    t = Folder(parent=isolate_folder, name=task_id)
                    t.save()
                    t.name = task_id
                    t.save()
                    isolate_folder = t
                    if self.logger!=None: 
                        self.logger.info('Create folder-task_id={0}.'.format(task_id))
            else:
                pass 
        except Exception as e:
            if self.logger!=None: self.logger.info(e)
        self.logger.info('this_isolated_folder={0}.'.format(isolate_folder))
        self.isolate_folder = isolate_folder     
        return 
    
    def isolate_email_by_subject(self,target_email, subject='',startwith='',datetime=''):
        """
        param target_email: str, target email account
        param subject: str, target email account
        param startwith: str, start with special keyword
        param datetime: str, specify time to get the unique email---todo
        return: 1 - isolated the target mail, 0 - no isolating action 
        """
        user_email_account = self.connect_account(target_email)
        #emails = user_email_account.inbox.filter(subject__startswith='Invoice')
        emails = user_email_account.inbox.filter(subject=subject)
        if emails:
            #emails.copy(to_folder=some_folder)
            #emails.move(to_folder=account_admin.inbox / 'ems_fold1')
            emails.move(to_folder=self.isolate_folder)
            if self.logger!=None: 
                self.logger.info('Isolated mail-subject={0} from email={1} to folder={2} of admin-mail={3}.'.format(subject,target_email,self.isolate_folder,self.admin))
            return 1
        else:
            pass
        return 0
    
    def delete_email_by_subject(self,target_email, task_id='',subject='',startwith='',datetime=''):
        """
        param target_email: str, target email account
        param subject: str, target email account
        param startwith: str, start with special keyword
        param datetime: str, specify time to get the unique email---todo
        return: 1 - deleted the target mail, 0 - no delete action
        """
        user_email_account = self.connect_account(email)
        #emails = user_email_account.inbox.filter(subject__startswith='Invoice')
        emails = user_email_account.inbox.filter(subject=subject)
        if emails:
            #emails.delete(page_size=25)
            emails.delete()
            if self.logger!=None: 
                self.logger.info('Deleted mail-subject={0} from email={1} by admin-mail={2}.'.format(subject,target_email,self.admin))
            return 1
        else:
            pass
        return 0
    
    def action(self,target_email,action_type='isolate', subject='',startwith='',datetime=''):
        """
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
            if self.logger!=None: 
                self.logger.error('Invalid action type: {0}, please input valid action: delete or isolate.')
            pass
        return 'None'
    
    def is_existing_isolated_mail(self):
        #
        #message_id='<2020043011174772583356@skyguardgx.com>',
        return False        
    
    def search_mail(self):
        return
    
    
    def send_mail(self):
        return
    
    def send_mail_bcc(self):
        return
    
    def form_mail(self):
        return

def get_json_event():
    obj = input()
    #print 'sys.argv1=',sys.argv[1]   
    
    return obj

 
if __name__ == '__main__':
    #obj = get_json_event()
    obj = input()
    """
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
    """
    #type = args.type
    #proxy = args.proxy
    print 'obj=',obj
    print 'obj_type=',type(obj)
    action='isolate'
    file_path = obj['file_path'].decode('utf-8')
    paths = file_path.split('/')
    sys.setrecursionlimit(100000000)
    ucss_log_path = '/root/exchange/'
    #ucss_log_path ='.'
    if not os.path.exists(ucss_log_path):
        os.makedirs(ucss_log_path)
    #{0}/sky_exchange.log'.format(ucss_log_path)
    logger = initial_logger(logfile=ucss_log_path+'sky_exchange.log',errorfile=ucss_log_path+'sky_exchange_error.log',logname='sky_exchange')
    logger.info('Start {0} action ...'.format(action))
    logger.info('argv: {0}'.format(sys.argv))
    logger.info('json_event: {0}'.format(obj))
    if len(sys.argv) < 2:
        logger.info('please input incident path! Otherwise, ignore incident path--v3.6 will support discover incident.') 
    #incident_path = sys.argv[1] + '/' + obj['task_id']
    #if not os.path.exists(incident_path):
    #    os.makedirs(incident_path)
    #full_path = file_path + '/' + obj['file_name']
    if len(paths) !=2:
        logger.error('Invalid email path: {0}'.format(paths))
        logger.info('Special file_path={0}, need special handling'.format(file_path))
        import sys
        sys.exist()   
    target_email = paths[0]
    root_folder = paths[1]   #should be inbox by default
    file_name = obj['file_name'].decode('utf-8')
    logger.info('file_path={0}'.format(file_path))
    logger.info('file_name={0}'.format(file_name))
    time_stamp = obj['time_stamp']
    task_id = obj['task_id']
    admin = obj['username'].split('@')[0]
    #admin_username = 'ets1'
    password = obj['password']
    #admin_password = 'Firewall1'
    domain = obj['domain']
    
    exg_obj = Skyexchange(target_email, action=action,admin_username=admin,admin_password=password, 
            server='mail.skyguardgx.com',domain=domain,auth_type='NTLM',port=443,
            isolate_folder='isolate',task_id=task_id,logger=logger)
    exg_obj.action(target_email,action_type=action, subject=file_name,startwith='',datetime='')
    logger.info('{0} mail completed: {1} --{2} '.format(action,file_path,file_name))
    