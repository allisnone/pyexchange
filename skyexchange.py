#!/usr/bin/env python
from exchangelib import Credentials, Account,Configuration,DELEGATE

email= 'zhoubaodong@skyguardex.com'
pwd = 'Firewall1'
credentials = Credentials(email, pwd)

config = Configuration(server='mail.skyguardex.com', credentials=credentials)

account = Account(primary_smtp_address=email, config=config,
                  autodiscover=False, access_type=DELEGATE)

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