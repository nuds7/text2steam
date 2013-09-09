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
        self._watcher()

    def _restartBot(self):
        print ("-----------------------------")
        self._updateBot()
        self._openBot()

    def _updateBot(self):
        pass
        #g = git.cmd.Git(os.getcwd())
        #print g.pull()
        #print "-----------------------------\n"

    def _openBot(self):
        self.bot = subprocess.Popen(["ipy", '-X:Frames', '-u', 'bot.py', self.config], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT, 
                                    bufsize=1, close_fds=ON_POSIX,)

        # bot.BOT(self.config)

    def _watcher(self):
        while True:
            try:
                # read line without blocking
                try:
                    line = self.bot.stdout.readline()
                except Empty:
                    pass
                else:  # got line
                    print line.rstrip()
                #polling
                status = self.bot.poll()
                if status is not None:
                    time.sleep(2)
                    self._restartBot()
                #thread sleep
                time.sleep(0.02)
            except KeyboardInterrupt:
                self.bot.terminate()
                sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config = sys.argv[1]
    else:
        config = 'config.xml'

    watchdog = WatchDog(config)
    watchdog.startBot()
