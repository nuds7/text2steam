import xml.etree.ElementTree
import inspect
import datetime
import os
import sys


class LogType:
    manager = 0
    debug = 1
    info = 2
    warning = 3
    error = 4


class Log:
    def __init__(self, config):
        self.logcallbacks = []
        self.logtype = LogType
        elem = xml.etree.ElementTree.parse(config)
        logger = elem.find('logger')
        #log file
        logdir = logger.find('logdir')
        if logdir is None:
            logdir = "logs"
        else:
            logdir = logdir.get('value')
        self._logdir = logdir
        #log level
        loglevel = logger.find('level')
        if loglevel is None:
            loglevel = "info"
            self.loglevel = 2
            msg = 'Logger: No loglevel set in config <logger> <level="info" /> <logger/> assuming info level'
            self._log(self._format("warning", "log", [msg]), self.logtype.warning)
        else:
            loglevel = loglevel.get('value')

        if loglevel == "error":
            self.loglevel = self.logtype.error
        elif loglevel == "warning":
            self.loglevel = self.logtype.warning
        elif loglevel == "info":
            self.loglevel = self.logtype.info
        elif loglevel == "debug":
            self.loglevel = self.logtype.debug
        elif loglevel == "manager":
            self.loglevel = self.logtype.manager

        self._log(self._format("info", "log", ["Level %s" % loglevel]), self.logtype.warning)

        #err hook
        #sys.excepthook = self.excepthook

    def _getName(self):
        retmod = "Module"
        frame, module, line, function, context, index = inspect.stack()[2]
        try:
            retmod = inspect.getmodulename(module)
        except:
            pass
        return retmod

    def _combine(self, message):
        return " ".join(map(str, message))

    def _format(self, level, name, message):
        return "[%s] <%s> %s" % (name, level, self._combine(message))

    def _log(self, logdata, logtype):
        print logdata
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
        timelogdata = "%s: %s" % (timestamp, logdata)
        self.file(timelogdata)
        for callback in self.logcallbacks:
            callback(logdata, logtype)

    def registerLogListener(self, callback):
        self.logcallbacks.append(callback)

    #extra logging
    def file(self, logdata):
        self._filewriter(".log", logdata)

    def fileerr(self, logdata):
        self._filewriter(".log.err", logdata)

    def _filewriter(self, ext, logdata):
        today = datetime.date.today().strftime("%d%m%y")
        #filehandler = open(os.path.join(self._logdir, today + str(ext)), 'a', 0)  # 0 is buffer
        #filehandler.write(logdata + "\n")
        #filehandler.close()

    #message levels
    def error(self, *message):
        if self.loglevel <= 4:
            errformat = self._format("error", self._getName(), message)
            self._log(errformat, self.logtype.error)
            timestamp = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
            logdata = timestamp + "\n" + errformat + "\n"
            self.fileerr(logdata)

    def warning(self, *message):
        if self.loglevel <= 3:
            self._log(self._format("warning", self._getName(), message), self.logtype.warning)

    def info(self, *message):
        if self.loglevel <= 2:
            self._log(self._format("info", self._getName(), message), self.logtype.info)

    def debug(self, *message):
        if self.loglevel <= 1:
            self._log(self._format("debug", self._getName(), message), self.logtype.debug)

    def manager(self, *message):
        if self.loglevel <= 0:
            self._log(self._format("manager", self._getName(), message), self.logtype.manager)

    #stuff for stderr
    def excepthook(self, type, value, traceback):
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
        logdata = timestamp + "\n" + str(traceback) + "\n"
        self.fileerr(logdata)
        self.error("Exception %s: %s" % (type, value))
