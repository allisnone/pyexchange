#!/usr/bin/env python
from exchangelib import Credentials, Account,Configuration,DELEGATE
#172.22.3.166    mail.skyguardex.com
server = '172.22.3.166'
#server = 'mail.skyguardex.com'
email= 'it@skyguardex.com'
pwd = 'Firewall!3'

pwd = 'Firewall1!'
#* PrimarySMTPAddress
#* WINDOMAIN\\username
#* User Principal Name (UPN)

#credentials = Credentials(email, pwd)

credentials = Credentials('skyguardex\\it', pwd)
#email= 'Administrator@skyguardex.com'
#credentials = Credentials('skyguardex\\Administrator', pwd)

config = Configuration(server=server, credentials=credentials,auth_type='NTLM')
#config = Configuration(service_endpoint='https://mail.example.com/EWS/Exchange.asmx', credentials=credentials)

account = Account(primary_smtp_address=email, config=config,
                  autodiscover=False, access_type=DELEGATE)

"""
version = Version(build=Build(15, 0, 12, 34))
config = Configuration(
    server='example.com', credentials=credentials, version=version, auth_type=NTLM
)
"""
#account = Account(email, credentials=credentials, autodiscover=True)

for item in account.inbox.all().order_by('-datetime_received')[:100]:
    print(item.subject, item.sender, item.datetime_received)
    

class Skyexchange():
    def __init__(self):
        self.acc = ''
    
    def connect_account(self):
        return
    
    def search_mail(self):
        return
    
    def del_mail(self):
        return
    
    def isolate_mail(self):
        return
    
    def send_mail(self):
        return
    
    def send_mail_bcc(self):
        return
    
    def form_mail(self):
        return