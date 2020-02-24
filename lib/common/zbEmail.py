import os, pdb, email, imaplib

from O365 import *

class Email_Client:
    def __init__(self, host, email, pwd): #remove default for email
        self.email = email
        self.pwd = pwd

        # self.auth = (self.email, self.pwd)
        try :self.mail_protocol = self._login(host)
        except:
            raise


    def getEmails(self, search_key=None, search_value=None): 
        #date format is DD-MMM-YYYY i.e. 25-Jan-2019
        
        '''
        # old getEmail code using O365 library

        inbox = Inbox(self.auth, getNow=False)
        if sender is not None:
            formattedStr = "From/EmailAddress/Address eq '{}'".format(sender)
            inbox.setFilter(formattedStr)
        inbox.getMessages(number)
        return inbox.messages
        '''

        self.mail_protocol.select() #selects inbox as default folder

        if search_value is None:
            criteria = search_key if search_key else None
        else:
            criteria = '({} "{}")'.format(search_key, search_value)

        rcode, data = self.mail_protocol.search(None, 'ALL' if criteria is None else criteria) #rcode is 'Ok' string
        
        if not data[0]:
            print('Email inbox is empty')
            return False

        inbox = []
        for num in data[0].split():
            rcode, data = self.mail_protocol.fetch(num, '(RFC822)')

            if not data[0][1]:
                continue

            mail = email.message_from_string(data[0][1].decode('utf-8'))
            message_body = ''

            if mail.is_multipart():
                for message in mail.walk():
                    if message.get_content_type() == "text/plain":
                        message_body = message.get_payload(decode=True).decode('utf-8').replace('\n', '\n').replace('\r', ' ')
            
            else:
                if mail.get_content_type() == 'text/html':
                    message_body = mail.get_payload(decode=True).decode('utf-8')
                    #parse html

            inbox.append({'from': mail['From'], 'subject': mail['Subject'], 'body': message_body})

        return inbox


    def _login(self, host):
        mailbox = imaplib.IMAP4_SSL(host) #'outlook.office365.com', 'imap.gmail.com'
        mailbox.login(self.email, self.pwd)
        return mailbox


'''
# Other operations on https://github.com/Narcolapser/python-o365

email_client = Email_Client("jeffrey.lee@zingbox.com", "your_password")
emails = email_client.getEmails(sender="jeffrey.lee@zingbox.com")
for email in emails:
	print('Email address {}'.format(email.getSender()["EmailAddress"]["Address"]))

'''
