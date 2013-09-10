import smtplib
import imaplib
import email
from email.parser import Parser
import lxml
import re
from datetime import datetime
import time

# if email_from.endswith('mms.att.net'): # special instructions
# if email_from.endswith('tmomail.net'): # if needed

class GmailSender(object):
	def __init__(self, user, password):
		smtp_host = "smtp.gmail.com"

		self.server = smtplib.SMTP( smtp_host, 587 )
		self.server.starttls()
		self.server.login( user, passwd )

	def send(self, recipient, message, subject = ''):
		#recipient = '7602842159@mms.att.net'
		self.client.sendmail( subject, recipient, message )


class GmailReader(object):
	def __init__(self, user, password):
		imap_host = "imap.gmail.com"

		self.client = imaplib.IMAP4_SSL(imap_host, 993)
		self.client.login(user, password)
		self.client.list()
		self.client.select('INBOX', readonly=False)

	def get_unread(self):
		retcode, messages = self.client.search(None, '(UNSEEN)')
		if retcode == 'OK':
			for num in messages[0]:
				print('Processing :', num)
				typ, data = self.client.fetch(str(num),'(RFC822)')
				msg = email.message_from_bytes(data[0][1])
				#typ, data = self.client.store(num,'-FLAGS','\\Seen')
				if typ == 'OK':
					print(data,'\n',30*'-')
					print(msg)

	def process_inbox(self):

		result, data = self.client.search(None, "ALL")
		queue_len = len(self.client.search(None, 'UnSeen')[1][0].split())

		if queue_len == 0:
			print('No emails in inbox to process')

		for i in range(queue_len):
			print("Processing: "+str(i+1)+' of '+str(queue_len))

			result, data = self.client.search(None, "ALL")
			ids = data[0] # data is a list.
			id_list = ids.split() # ids is a space separated string
			latest_email_id = id_list[-1] # get the latest
			
			result, data = self.client.fetch(latest_email_id, "(RFC822)")
			
			# decode the email
			email_message = email.message_from_bytes(data[0][1])
			
			headers = Parser().parsestr(str(email_message))
			email_from = headers['From']
			email_to = headers['To']

			print('To: '+email_to)
			print('From: '+email_from)
	
			if email_message.get_content_maintype() == 'multipart': 
				for part in email_message.walk():       
					if part.get_content_type() == "text/html":
		
						body = part.get_payload(decode=True)
						body = str(email.message_from_bytes(body))
			
						# http://stackoverflow.com/a/37512/2308849
						# removing html tags from email body
						body = lxml.html.fromstring(body).text_content()
		
						# http://stackoverflow.com/a/6130119/2308849
						# removing extra white space
						body = re.sub(r'\s{2,}', ' ', body)
			
						if email_from.endswith('mms.att.net'):
							body = body.replace(' Multimedia Message ', '')
			
						temp = open("temp.txt", "a")
						temp.write(str(datetime.now())+'\n'+str(body)+'\n')
						temp.close()
	
						print('Message: '+body)
						print('---------------')
	
						self.move_email(latest_email_id)
	
						#return body
					else:
						continue
			time.sleep(.5)

	def move_email(self, msg_uid):
		# When we're done reading the email,
		# remove it from the inbox.
		self.client.copy(msg_uid, 'Processed')
		a = self.client.store(msg_uid,"+FLAGS", r'(\Deleted)')
		#print(a)
		self.client.expunge()

	def close(self):
		self.client.close()
		self.client.logout()


if __name__ == '__main__':
	reader = GmailReader('text2steam@gmail.com', 'lollerskates')
	reader.process_inbox()
	reader.close()