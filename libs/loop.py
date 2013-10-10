import os, sys
#os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
lib_path = os.path.abspath('isteam/')
sys.path.append(lib_path)
import isteam
import time

class Bot(object):
	def __init__(self, username, password):

		self.username = username
		self.password = password
	
		config = 'config.xml'
		self.bot = isteam.InterfaceSteam(config)

	def update(self):
		while self.bot.client_connected:
			time.sleep(1)

if __name__ == '__main__':
	# use txtrbot, lollerskates after steamguard
	# is enabled on it. make sure you trade
	# everything you want it to have, first!
	bot = Bot('txt2st', 'lollerskates')
	bot.update()

# cd C:\Program Files (x86)\IronPython 2.7
# ipy.exe -X:Frames C:\Users\Everett\Documents\GitHub\text2steam\libs\loop.py