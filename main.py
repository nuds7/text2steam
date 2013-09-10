import os, sys
lib_path = os.path.abspath('libs/')
sys.path.append(lib_path)

import smtplib
imap_host = "imap.gmail.com"
smtp_host = "smtp.gmail.com"

user = "nuds55@gmail.com"
passwd = "ssg662560407"

steam_api_key = '3F42782DAF3F62A1AB43A57A8031D5CD'

#server = smtplib.SMTP( smtp_host, 587 )
#server.starttls()
#server.login( user, passwd )
#client.sendmail( 'peepus', '7602842159@mms.att.net', 'hi' )

import imaplib
import email
from email.header import decode_header
from email.parser import Parser
import lxml.html
import re

client = imaplib.IMAP4_SSL(imap_host, 993)
client.login(user, passwd)
client.list()
client.select('INBOX', readonly=True)

result, data = client.search(None, "ALL")

ids = data[0] # data is a list.
id_list = ids.split() # ids is a space separated string
latest_email_id = id_list[-1] # get the latest

result, data = client.fetch(latest_email_id, "(RFC822)")

# decode the email
email_message = email.message_from_bytes(data[0][1])
print(email_message)

headers = Parser().parsestr(str(email_message))
email_from = headers['From']
email_to = headers['To']

print('From: '+email_from)
print('To: '+email_to)

# If message is multi part we only want the text 
# version of the body, this walks the message 
# and gets the body.
if email_message.get_content_maintype() == 'multipart': 
	for part in email_message.walk():       
		print(part.get_content_type())
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

			print(body)

			temp = open("temp.txt", "a")
			temp.write(str(body)+'\n')
			temp.close()
		else:
			continue

client.close()
client.logout()
