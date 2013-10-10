import clr
clr.AddReferenceToFile("SteamKit2.dll")
clr.AddReference('System')
import System
from SteamKit2 import *
import sys
from threading import Thread
from bin.shared.perms import Perm
from bin.shared.commandresponse import CmdResponse
from datetime import datetime
import traceback
import gmail
import time
import isteam
import random

def find_between( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return ""

def find_between_r( s, first, last ):
	try:
		start = s.rindex( first ) + len( first )
		end = s.rindex( last, start )
		return s[start:end]
	except ValueError:
		return ""

def command_finder( message, container ):
	return find_between(message, container[:2], container[2:])

class Txtrbot(object):
	def __init__(self, interface):
		super
		self.interface = interface


		mail_usr 	= 'text2steam@gmail.com'
		mail_pw 	= 'lollerskates'

		self.gmail_reader = gmail.GmailReader(mail_usr, mail_pw)

		self.mail_time = 5
		self.flirt_time = 1200

	def OnConnected(self):
		pass

	def OnDisconnected(self):
		pass

	def OnLoggedOn(self):
		pass

	def OnLoggedOff(self):
		pass

	def OnFriendMsg(self, senderID, message):
		pass

	def checkMail(self):
		if self.mail_time == 0:
			self.mail_time = 5
			print('Checking mail...')
			mails = self.gmail_reader.fetch_unseen()
			for mail in mails:
				self.processMail(mail[0], mail[1])
		else: 
			self.mail_time -= 1

	def processMail(self, mail_from, message):
		message = message.replace('\n-- Sent from Steam using txtrbot. <3', '')

		recepient = command_finder(message, '[*] ')
		if recepient != None:
				for friend in self.interface.friends:
					if friend[0] == recepient:
						recepient = friend[1]
		
				self.interface.sendChatMessage(recepient, 
											   "("+mail_from+")"
											   +message[message.find("] ")+1:])

	def SteamLoop(self):
		self.checkMail()
		#self.flirtCountdown()

	# chat call back commands
	def chat_commands(self, sender, message):
		sender_profile_name = str(self.interface.steamFriends.GetFriendPersonaName(sender))
		# chat commands for the bot
		# say hi!
		if message.lower() == 'hi':
			self.interface.sendChatMessage(sender, 'hi '+sender_profile_name+" <3")
		if message == 'how are you?' or message == 'How are you?':
			self.interface.sendChatMessage(sender, "i'm doing fine =]")
	
	   	# handle special commands between
	   	# angle brackets
		try:
			self.bot_kill			(sender, message)
			self.bot_help			(sender, message)

			self.bot_message		(sender, message)
			self.bot_email			(sender, message)

			self.bot_add_friend		(sender, message)
			self.bot_remove_friend	(sender, message)
		except:
			pass

	# individual commands
	def bot_kill(self, sender, message):
		sender_profile_name = str(self.interface.steamFriends.GetFriendPersonaName(sender))
		submessage = find_between(message, '[', ']')

		if submessage == 'KILL' or message == 'DIE ASSHOLE':
			print 'User "'+sender_profile_name+'" killed txtrbot!'
			self.interface.sendChatMessage(sender, '*shoots robot parts*')
			time.sleep(.5)
			self.interface.destroy(disconnect())
	
	def bot_help(self, sender, message):
		if message.lower() == 'help' or message.lower() == 'hi':
			self.interface.sendChatMessage(sender, '...\nTo text someone from Steam: [@their_number@smsgateway.com] your message\n'+
												   'To send someone a message from Steam and or your phone: [*friend] your message\n'+
												   "Type 'list friends' for a list txtrbot's of friends\n"+
												   'For a list of SMS gateways, visit http://www.emailtextmessages.com/\n')
		# get a list of txtrbot's friends
		if message.lower() == 'list friends':
			self.interface.sendChatMessage(sender, 'txtrbot has '+str(len(self.interface.friends))+' best friends. '+
												   'They are: \n'+str(self.interface.friends)+'\n')

		if message.lower() == '#mizzy#':
			self.interface.sendChatMessage(sender, '...\n[+SteamID] to add\n'+
												   '[-SteamID] to remove\n'+
												   'http://steamid.co/')

	
	def bot_message(self, sender, message):
		sender_profile_name = str(self.interface.steamFriends.GetFriendPersonaName(sender))

		message_log = open("message_log.txt", "a") 												# logging

		recepient = command_finder(message, '[*] ')

		message_log.write("# "+str(datetime.now())+" #\n") 										# logging
		message_log.write(recepient+'\n') 

		if message[1] == '*':
			for friend in self.interface.friends:
				if friend[0] == recepient:
					recepient = friend[1]

			# error handling and feedback
			if str(SteamID(recepient)) == 'STEAM_0:0:0':
				self.interface.sendChatMessage(sender, 'Invalid friend "'+recepient+'."')
				message_log.write('Message send failed')
			else:
				self.interface.sendChatMessage(sender, 'Sent to '+recepient)
				self.interface.sendChatMessage(recepient, "("+sender_profile_name+") "+
										   	              message[message.find("] ")+1:])
				
				message_log.write(sender_profile_name+str(message[message.find("] ")+1:])+'\n') # logging

		message_log.close() 																	# logging
	
	def bot_email(self, sender, message):
		sender_profile_name = str(self.interface.steamFriends.GetFriendPersonaName(sender))
	
		recepient = command_finder(message, '[@] ')
		if message[1] == '@':
	
			email_message = sender_profile_name + ':' + message[message.find("] ")+1:]
			email_message = email_message + '\n-- Sent from Steam using txtrbot. <3'
	
			gmail.send_gmail('text2steam@gmail.com', 
							 'lollerskates', 
							 recepient,
							 email_message)

			self.interface.sendChatMessage(sender, 'Sent to '+recepient)

	def flirtCountdown(self):
		if self.flirt_time == 0:
			self.flirt_time = 1200
			print('Flirting...')
			self.random_flirt()
		else: 
			self.flirt_time -= 1

	def random_flirt(self):
		flirts =   ['Apart from being sexy, what do you do for a living?',
					'So what do you keep doing all day besides looking good?',
					'My parents told me angels arent real... I used to believe them, but then I saw you',
					'I hurt myself real bad while I was falling for you!',
					'I like the way you walk when you walk my way!',
					'Do you believe in love at first sight or should I walk by again?',
					'Hey are you free... for the rest of your life?',
					'Stop thinking about me!',
					'I was a careless girl until I met you!',
					'Listen up! You are under arrest for being that cute!',
					'Stop thinking about me. See, youre doing it... right now',
					'You better have a license, cause you are driving me crazy!',
					'Send me a picture so I can tell Santa my wish list.',
					'Did the sun come out or did you just smile at me?',
					'From A to Z all that really matters is U and I.',
					'Just got out of the shower... Why dont you come over and help me get dirty again?',
					'Come over and take off my lip gloss baby!',
					'I got lost on my way home, can I go home with you?',
					'The hottest thing a guy could wear is the lipstick off of my lips!',
					'I like to study... you!',
					'Tonight ill wear my heels... and nothing else.',
					'It isnt premarital sex if you have no intention of getting married.',
					'If you were an island... could I explore you?',
					'Your dad is one crazy terrorist and you cant deny it... because you are a bomb ;-)',
					'If love is a crime, lock me up, Im guilty',
					'If Santa comes down the chimney this year and tries to stuff you into a sack, dont worry! Thats what Ive wished for this Christmas!',
					'Its gotta be illegal to look this good!',
					"I feel great! And I don't kiss badly either",
					"There's so much to say but your eyes keep interrupting me.",
					"Is it hot in here or is it just you?",
					"If I follow you home, will you keep me?",
					"Please be patient--this is my first time.",
					"BITCH also stands for: Beautiful, Intelligent, Talented, and Charming Human being!"]
		rand_flirt = random.choice(flirts)
		rand_recip = random.choice(self.interface.friends)
		print("Flirting with '"+rand_recip[0]+".'")
		self.interface.sendChatMessage(rand_recip[1], str(rand_flirt))

	def bot_add_friend(self, sender, message):
		sender_profile_name = str(self.interface.steamFriends.GetFriendPersonaName(sender))

		recepient = command_finder(message, '[+] ' )
		if message[1] == '+':
			steam_id = SteamID(recepient)
			self.interface.steamFriends.AddFriend(steam_id)
			self.interface.sendChatMessage(sender, 'Adding '+recepient+'.')
	def bot_remove_friend(self, sender, message):
		sender_profile_name = str(self.interface.steamFriends.GetFriendPersonaName(sender))

		recepient = command_finder(message, '[-] ')
		if message[1] == '-':
			steam_id = SteamID(recepient)
			self.interface.steamFriends.RemoveFriend(steam_id)
			self.interface.sendChatMessage(sender, 'Remove '+recepient+'.')

def connect():
	print('Connected')
def disconnect():
	print('Disconnected')