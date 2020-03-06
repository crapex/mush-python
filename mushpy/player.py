# -*- coding:utf-8 -*-

import re
import random
from collections import namedtuple

from .mush import MushHelper
from .objects import *
from .commands import *
from .modules import *
from .map import Map
from .triggers import *


class Player(MushObject):
    def __init__(self, world, ax, pid, pwd, name, **options):
        super().__init__(None)                                                  # player is the top-level object
        self._mushHelper = MushHelper(world, ax)                                # the mushhelper
        self._rootPath = self._mushHelper.GetInfo(56) 
        self._mapdbname = r"{}map.db".format(self._rootPath)
        self.mush.Log('map db: ' + self._mapdbname)
        self._map = Map(self._mapdbname)                                        # the map for db
        
        self._id = pid
        self._password = pwd
        self._name = name
        
        self._options = options
        
        self._triggers = {}
        self._commands = {}
        self._modules  = {}
        self._aliases  = {}
        
        self._triggers["hpbrief"]   = TriggerHpbrief(self, "sys", name = "hpbrief")
        self._triggers["response"]  = TriggerResponse(self, "sys", name = "response")
        self._triggers["fullme"]    = TriggerAntiRobot(self, "sys", name = "antirobot")
        self._triggers["room"]      = TriggerRoomTitle(self, "sys", name = "location")
        
        self._commands["skills"]    = CmdSkills(self, "player")
        self._commands["score"]     = CmdScore(self, "player")
        self._commands["enable"]    = CmdEnable(self, "player")
        self._commands["inventory"] = CmdInventory(self, "player")
        
        self._commands["noecho"]    = CmdNoEcho(self, "gps")
        self._commands["walk"]      = CmdWalkDirection(self, "gps")
        self._commands["pause"]     = CmdWalkPause(self, "gps")
        self._commands["river"]     = CmdCrossRiver(self, "gps")
        self._commands["wait"]      = CmdWait(self, "gps")
        self._commands["room"]      = CmdRoom(self, "gps")
        #self._commands["locate"]    = CmdLocate(self, "gps")
        
        self._modules["dazuoto"]    = ModuleDazuoTo(self)
        self._modules["liaoshang"]  = ModuleHeal(self)
        
    @property
    def Commands(self):
        return self._commands
    
    @property
    def Triggers(self):
        return self._triggers
        
        
        