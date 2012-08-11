from imaplib import IMAP4_SSL
import time
import email, uniblab_message
import smtplib
import re
from email.mime.text import MIMEText
from twisted.internet import task
import datetime

email_pattern = re.compile("([^<]*)<?([^<>]*)>?")

class EmailTransport:
    transport_type = 'email'
    def __init__(self, uniblab):
        self.uniblab = uniblab

    def config(self, config):
        self.mail_host = config.get('email', 'imap_host')
        self.mail_port = config.getint('email', 'imap_port')
        self.mail_user = config.get('email', 'user')
        self.mail_from = config.get('email', 'mail_from')
        self.mail_pass = config.get('email', 'pass')
        self.emailaddress = config.get('email', 'email_address')
        self.smtp_server = config.get('email', 'smtp_host')
        self.smtp_port = config.getint('email', 'smtp_port')

    def connect(self):
        l = task.LoopingCall(self.read_new_messages)
        l.start(60, True)

    def read_new_messages(self):
        try:
            s = IMAP4_SSL(self.mail_host, self.mail_port)
            s.login(self.mail_user, self.mail_pass)
            s.select()
            typ, data = s.search(None, '(UNDELETED)')
            messages = list()
            for msgnum in data[0].split():
                env,parts = s.fetch(msgnum, 'RFC822')
                for part in parts:
                    if(len(part) > 1):
                        msg = email.message_from_string(part[1])
                        datestr = msg.get('Date')
                        if datestr != None:
                            senddate = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(datestr)))
                            now = datetime.date.today()
                            if senddate.date() == now:
                                for m in msg.walk():
                                    if m.get_content_type() == 'text/plain':
                                        body = m.get_payload()
                                        break
                                    elif m.get_content_type() == 'text/html':
                                        body = m.get_payload()
                                        break
                                from_addr = msg['from']
                                email_match = email_pattern.search(from_addr)
                                if email_match:
                                    from_addr = email_match.group(2)
                                    username = self.uniblab.username_from_email(from_addr)
                                    print 'Processing email from', msg['from'], 'which is user', username
                                message = uniblab_message.uniblab_message(from_addr,msg['to'], msg['subject'], body, self.transport_type, username)
                                self.uniblab.message(message,self)
                            else:
                                print "Found a message that wasn't sent today, but on", senddate.date()
                        s.store(msgnum, '+FLAGS', '\\Deleted')
            s.expunge()
            s.logout()
        except:
            print 'Encountered an error in the email loop'

    def respond(self, m, response):
        msg = MIMEText(response.text)
        msg['Subject'] = ' '.join(['RE: ', m.subject])
        msg['To'] = m.sender
        msg['From'] = self.emailaddress

        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.mail_user, self.mail_pass)
        print 'sending mail from', self.mail_user,'to',m.sender
        server.sendmail(self.mail_from, m.sender, msg.as_string())
        server.close()
