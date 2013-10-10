import smtplib
import imaplib
#import email
from email.parser import Parser
import emailthree as email
#import lxml
#import xml.etree.ElementTree
import re
from datetime import datetime
import time

# if email_from.endswith('mms.att.net'): # special instructions
# if email_from.endswith('tmomail.net'): # if needed

def strip_tags(html):
	return re.sub('<[^>]*>', '', html)


def send_gmail(user, password, recipient, message, subject = ''):
	# '7602842159@mms.att.net'
	FROM 	= str(user)
	TO 		= [str(recipient)]
	SUBJECT = str(subject)
	TEXT 	= str(message)
	message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
			  """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
	try:
		smtp_host = "smtp.gmail.com"
		server = smtplib.SMTP(smtp_host, 587)
		server.ehlo()
		server.starttls()
		server.login(user, password)
		server.sendmail(FROM, TO, message)
		server.close()
		print('Sent the email')
	except:
		print('Failed sending the email')

#
#   gmail_to_post.py
#   FrenzyLabs, llc (@frenzylabs)
#
#   Created by Wess Cope (@wesscope) on 2011-12-08.
#   Copyright 2011 FrenzyLabs, llc. All rights reserved.
#
#   Using: 
#      Python 2.7
#      Requests: http://python-requests.org
# 
#   A quick and dirty python script to check for unread messages
#   in Gmail account and post them to a web service/url.
#
 
import sys, imaplib, email
from StringIO import StringIO
 
MAIL_SERVER = "imap.gmail.com"
MAIL_PORT   = 993
 
 
class GmailReader(object):
	def __init__(self, username, password):
		self.username   = username
		self.password   = password
		self.connection = imaplib.IMAP4_SSL(MAIL_SERVER, MAIL_PORT)
		self.connection.login(username, password)
		self.connection.select()
	
	def parse_attachment(self, message_part):
		content_disposition = message_part.get("Content-Disposition", None)
		if content_disposition:
			dispositions = content_disposition.strip().split(";")
			if bool(content_disposition and dispositions[0].lower() == "attachment"):
 
				file_data = message_part.get_payload(decode=True)
				attachment = StringIO()
				attachment.write(file_data)
				attachment.content_type = message_part.get_content_type()
				attachment.size = len(file_data)
				attachment.name = None
				attachment.create_date = None
				attachment.mod_date = None
				attachment.read_date = None
				
				
				for param in dispositions[1:]:
					name,value = param.split("=")
					name = name.lower()
					
					attachment.name = value.replace('"', '')
 
				return attachment
 
		return None
	
	def fetch_unseen(self):
		mail_log = open("mail_log.txt", "a")

		self.connection = imaplib.IMAP4_SSL(MAIL_SERVER, MAIL_PORT)
		self.connection.login(self.username, self.password)
		self.connection.select()

		queue_len = len(self.connection.search(None, 'UNSEEN')[1][0].split())
		msg_type, data = self.connection.search(None, "UNSEEN")

		messages_to_be_processed = []
		
		for i in range(queue_len):

			result, new_data = self.connection.search(None, "ALL")
			ids = new_data[0] # data is a list.
			id_list = ids.split() # ids is a space separated string
			latest_email_id = id_list[-1] # get the latest

			for item in data[0].split():
				msg_type, msg_data = self.connection.fetch(item, '(RFC822)')
				
				for part in msg_data:
					if isinstance(part, tuple):
						sent_to     = ""
						sent_from   = ""
						subject     = ""
						body        = ""
						attachments = []
 			
						email_msg   = email.message_from_string(part[1])
						sent_to     = email_msg.get('to')
						sent_from   = email_msg.get('from')
						subject     = email_msg.get('subject')
						
						for step in email_msg.walk():
							if step.get_content_type() == 'text/plain' or \
							   step.get_content_type() == 'text/html':
								body = step.get_payload()
								body = ''.join(body)
								body = body.replace("\"=", "=\"") 

								if step.get_content_type() == 'text/html':
									body = strip_tags(body)
									body = re.sub(r'\s{2,}', ' ', body)

								body = body.replace('\t', '')
								body = body.replace('\r', '')
								body = body.replace('\n \n', '')
								body = body.replace('\n  \n', '')
								# att specific
								body = body.replace(' Multimedia Message ', '')

							'''
							attachment = self.parse_attachment(step)
							
							if attachment:
								attachments.append(attachment)
							'''

						self.move_email(latest_email_id)
						
						message = {
							"to": sent_to,
							"from": sent_from,
							"subject": subject,
							"body-plain": body,
							"attachments": attachments}

						mail_log.write("# "+str(datetime.now())+" #\n")
						mail_log.write(str(message["from"])+'\n'+str(message["body-plain"])+'\n')

						from_and_body = [message["from"],message["body-plain"]]
						messages_to_be_processed.append(from_and_body) 

		mail_log.close()

		return messages_to_be_processed

	def move_email(self, msg_uid):
		# When we're done reading the email,
		# remove it from the inbox.
		self.connection.copy(msg_uid, 'Processed')
		a = self.connection.store(msg_uid,"+FLAGS", r'(\Deleted)')

		self.connection.expunge()

if __name__ == "__main__":
	g = GmailReader('text2steam@gmail.com', 'lollerskates')
	print(g.fetch_unseen())