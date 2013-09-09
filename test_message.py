import sys
import subprocess
import os
os.chdir(os.path.dirname(sys.argv[0]))
import time
import bot
#import git
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names


class WatchDog:
    def __init__(self, config):
        self.config = config
        self.bot = None

    def startBot(self):
        self._updateBot()
        self._openBot()

    def _restartBot(self):
        print ("-----------------------------")
        self._updateBot()
        self._openBot()

    def _updateBot(self):
        pass
        

    def _openBot(self):

        self.bot = subprocess.Popen(["ipy", '-X:Frames', '-u', 'bot.py', self.config], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT, 
                                    bufsize=1, close_fds=ON_POSIX,)
        print(self.bot.communicate())

        # bot.BOT(self.config)

    def conn_test(self):
        print('Connected!')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        config = sys.argv[1]
    else:
        config = 'config.xml'

    watchdog = WatchDog(config)
    watchdog.startBot()
