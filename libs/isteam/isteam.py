import clr
clr.AddReferenceToFile("SteamKit2.dll")
clr.AddReference('System')
import System
from SteamKit2 import *
import sys
from threading import Thread
from bin.shared.perms import Perm
from bin.shared.commandresponse import CmdResponse
import traceback
import time
import commandmanager
import xml.etree.ElementTree
import gmail
import txtrbot

import os, sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


class ConfigThing():
    def __init__(self, config):
        self.xml = xml.etree.ElementTree.parse(config)

    def getConfig(self, key):
        subconfig = self.xml.find('subconfigs').find(key)
        afile = subconfig.get("file")
        if afile is None:
            return subconfig
        else:
            return et.parse(afile)

# txt2st, lollerskates

class InterfaceSteam:
    def __init__(self, xml):
        self.chatcallbacks = []
        #get steamcfg from main config
        '''
        steamcfg = manager.config.getConfig('steamcfg')
        #username
        self.username = manager.config.getValue(steamcfg, 'username')
        #password
        self.password = manager.config.getValue(steamcfg, 'password')

        self.superuser = self.IDtoLong(manager.config.getValue(steamcfg, 'superuser'))
        '''

        self.txtrbot = txtrbot.Txtrbot(self)

        self.username = 'txt2st'
        self.password = 'lollerskates'
        self.superuser = self.IDtoLong('STEAM_0:1:73104763')

        commandm = commandmanager.CommandManager(xml)
        commandm.registerCommand("joinchat", self.joinChatCommand, perm=Perm.Super)
        commandm.registerCommand("leavechat", self.leaveChatCommand, perm=Perm.Super)
        commandm.registerCommand("sendmsg", self.sendMsgCommand, perm=Perm.Super)

        #steamcfg = ConfigThing('config.xml')
        #steamcfg = steamcfg.getConfig('steamcfg')
        
        self.cfgchatrooms = {}

        #chatroomscfg = steamcfg.find('chatrooms')
        #for chatroom in chatroomscfg.findall("room"):
        #    roomname = str(chatroom.get("name"))
        #    roomid = long(chatroom.get("id"))
        #    self.cfgchatrooms[roomname] = roomid
        
        self.chatrooms = []

        #connect to steam
        self.steamClient = SteamClient()
        callbackManager = CallbackManager(self.steamClient)
        self.steamUser = self.steamClient.GetHandler[SteamUser]()
        self.steamFriends = self.steamClient.GetHandler[SteamFriends]()

        #callbacks
        Callback[SteamClient.ConnectedCallback](self.OnConnected, callbackManager)
        Callback[SteamClient.DisconnectedCallback](self.OnDisconnected, callbackManager)

        Callback[SteamUser.LoggedOnCallback](self.OnLoggedOn, callbackManager)
        Callback[SteamUser.LoggedOffCallback](self.OnLoggedOff, callbackManager)

        Callback[SteamUser.AccountInfoCallback](self.OnAccountInfo, callbackManager)
        Callback[SteamFriends.ChatEnterCallback](self.OnChatEnter, callbackManager)
        Callback[SteamFriends.ChatMsgCallback](self.OnChatMsg, callbackManager)
        Callback[SteamFriends.FriendMsgCallback](self.OnFriendMsg, callbackManager)

        self.steamClient.Connect()

        self._isRunning = True
        #self._callbackthread(callbackManager)

        #start callback thread
        steamthread = Thread(target=self._steamloop, args=[callbackManager])
        #t.daemon = True  # thread dies with the program
        steamthread.start()

        self.client_connected = False
        self.friends = []

    def joinChatCommand(self, command, args, source):
        if len(args) >= 1:
            self.joinChatRoom(long(args[0]))
            return "Connected to %s" % args[0]

    def leaveChatCommand(self, command, args, source):
        if len(args) >= 1:
            chatroom = long(args[0])
        else:
            chatroom = self.IDtoLong(source['SourceID'])
        return self.leaveChatRoom(chatroom)

    def sendMsgCommand(self, command, args, source):
        steamid = SteamID(long(args[0]))
        msg = " ".join(args[1:])
        #print("sending msg", args, steamid, msg)
        #log.info("sending msg", args, steamid, msg)
        self.steamFriends.SendChatRoomMessage(steamid, EChatEntryType.ChatMsg, msg)

    def _steamloop(self, callbackManager):
        while self._isRunning:
            self.txtrbot.SteamLoop()
            #print('bot running...')
            callbackManager.RunWaitCallbacks(System.TimeSpan.FromSeconds(1))

    #log happend
    def logCallback(self, logdata, level):
        '''
        if level >= log.logtype.warning:
            try:
                steamid = SteamID(self.superuser)
                self.steamFriends.SendChatMessage(steamid, EChatEntryType.ChatMsg, logdata)
            except:
                pass
        '''
        pass

    #callbacks
    def OnConnected(self, callback):
        '''
        if callback.Result != EResult.OK:
            #log.error("Unable to connect to steam %s" % callback.Result)
            print("Unable to connect to steam %s" % callback.Result)
        '''

        #log.info("Connected to steam, logging in %s" % self.username)

        self.txtrbot.OnConnected()

        print("Connected to steam, logging in %s" % self.username)
        
        logondetails = SteamUser.LogOnDetails()
        logondetails.Username = self.username
        logondetails.Password = self.password

        try:
            self.steamUser.LogOn(logondetails)
        except:
            print('Could not login')
            pass
            #log.error("Could not login")

    def OnDisconnected(self, callback):
        #log.info("Disconnected from steam")
        self.txtrbot.OnDisconnected()

        print("Disconnected from steam")
        self._isRunning = False
        self.client_connected = False
        try:
            self._destorycallback("isteam")
        except:
            pass

    def OnLoggedOn(self, callback):
        #log.info("Logged into steam as %s" % self.username)
        print('Logged in')
        self.client_connected = True
        time.sleep(2)

        num_of_friends = self.steamFriends.GetFriendCount()

        self.friends = []
        for i in range(num_of_friends):
            persona_id = self.steamFriends.GetFriendByIndex(i)
            persona = self.steamFriends.GetFriendPersonaName(persona_id)
            self.friends.append([str(persona),str(persona_id)])

        #print(self.friends)

        for chatname in self.cfgchatrooms.keys():
            self.joinChatRoom(self.cfgchatrooms[chatname])

        self.txtrbot.OnLoggedOn()

    def OnLoggedOff(self, callback):
        print("Logged off from steam")
        #log.info("Logged off from steam")

        self.txtrbot.OnLoggedOff()

    def OnAccountInfo(self, callback):
        self.steamFriends.SetPersonaState(EPersonaState.Online)

    def OnChatEnter(self, callback):

        chatroom = self.IDtoLong(callback.ChatID)
        #log.info("Joined Chat %s" % chatroom)
        self.chatrooms.append(chatroom)

    def OnChatMsg(self, callback):

        chatterid = self.IDtoLong(callback.ChatterID)
        chatroomid = self.IDtoLong(callback.ChatRoomID)
        message = callback.Message
        if chatterid == self.superuser:
            chatperm = Perm.Super
        else:
            chatperm = Perm.User
        source = {'SourceID': chatroomid, 'SenderRank': chatperm, 'SenderID': chatterid}
        print(source)
        self._processCommand(source, message)

    def OnFriendMsg(self, callback):

        if callback.EntryType == EChatEntryType.ChatMsg:
            senderid = self.IDtoLong(callback.Sender)
            message = callback.Message

            try:
                print(str(self.steamFriends.GetFriendPersonaName(callback.Sender))+
                      ': '+str(message))
                # logging
                message_log = open("message_log.txt", "a")
        
                message_log.write("# "+str(datetime.now())+" #"+"\n")
                message_log.write(str(sender)+": "+str(message)+'\n')
        
                message_log.close()
            except:
                pass
                #self.sendChatMessage(callback.Sender, "emoticon...")

            if senderid == self.superuser:
                chatperm = Perm.Super
            else:
                chatperm = Perm.User
            source = {'SourceID': senderid, 'SenderRank': chatperm, 'SenderID': senderid}
            self._processCommand(source, message)

            self.txtrbot.chat_commands(callback.Sender, message)

    def _processCommand(self, source, message):
        #log.info(source['SourceID'], message)
        messagesplit = message.strip().split(" ")
        try:
            if messagesplit[0] == "wb":
                response = manager.commandmanager.processCommand(source, messagesplit[1:])
                if response == CmdResponse.Continue or response is None:
                    self._fireChatCallbacks(source, message)
                else:
                    if isinstance(response, tuple):
                        chatroomresponse = str(response[0]).strip()
                        friendresponse = str(response[1]).strip()
                        if chatroomresponse != "":
                            self.sendChatMessage(source['SourceID'], chatroomresponse)
                        if friendresponse != "":
                            self.sendChatMessage(source['SenderID'], friendresponse)
                    else:
                        msgresponse = str(response).strip()
                        if msgresponse != "":
                            self.sendChatMessage(source['SourceID'], msgresponse)
            else:
                self._fireChatCallbacks(source, message)
        except Exception:
            print('Error processing.')
            #log.error("Error while processing command \n %s" % traceback.format_exc())

    def _fireChatCallbacks(self, source, chatmsg):
        for callback in self.chatcallbacks:
            callback(source, chatmsg)

    def registerChatCallback(self, callback):
        self.chatcallbacks.append(callback)

    def sendChatMessage(self, chatid, msg):

        #print(self.username + ': ' + msg)
        steamid = SteamID(chatid)
        #print(steamid)
        if self.IDtoLong(chatid) in self.chatrooms:
            self.steamFriends.SendChatRoomMessage(steamid, EChatEntryType.ChatMsg, str(msg))
        else:
            self.steamFriends.SendChatMessage(steamid, EChatEntryType.ChatMsg, str(msg))

    def joinChatRoom(self, room):
        chatroom = SteamID(room)
        #log.info("Joining room %s" % chatroom)
        print("Joining room %s" % chatroom)

        self.steamFriends.JoinChat(chatroom)

        self.steamFriends.SetPersonaState(EPersonaState.Online)

    def leaveChatRoom(self, room):
        if self.IDtoLong(room) in self.chatrooms:
            chatroom = SteamID(room)
            #log.info("Disconnecting from room %s" % self.IDtoLong(room))
            self.steamFriends.LeaveChat(chatroom)
            self.chatrooms.remove(self.IDtoLong(room))
            return "", "Left Room %s" % room
        else:
            return "I'm not currently there"

    def IDtoStr(self, steamid):
        return str(SteamID(steamid).Render())

    def IDtoLong(self, steamid):
        return long(SteamID(steamid).ConvertToUInt64())

    def destroy(self, callback):
        self.steamUser.LogOff()
        self._destorycallback = callback
        return True

if __name__ == '__main__':
    pass

# me    'STEAM_0:0:19372398'
# 2.0   'STEAM_0:1:24841292'
# steve 'STEAM_0:0:21322082'


# cd C:\Program Files (x86)\IronPython 2.7
# ipy.exe -X:Frames C:\Users\Everett\Documents\GitHub\text2steam\isteam\isteam.py