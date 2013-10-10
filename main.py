import os, sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

sys.path.append(os.path.abspath('libs/'))
sys.path.append(os.path.abspath('libs/isteam/'))

import loop

if __name__ == '__main__':
	bot = loop.Bot('txt2st', 'lollerskates')
	bot.update()