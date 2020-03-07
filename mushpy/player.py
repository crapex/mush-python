# -*- coding:utf-8 -*-


from .objects import *
from .triggers import *
from .commands import *
from .modules import *
from .jobs import *
from .map import Map
from .fight import Fight

class Player(MushObject):
    _directions = ('n', 's', 'e', 'w', 'nw', 'ne', 'sw', 'se',
                   'nu', 'nd', 'su', 'sd', 'wu', 'wd', 'eu', 'ed', 'u', 'd', 'enter', 'out',
                   'north', 'south', 'east', 'west', 'northwest', 'northeast', 'southwest', 'southeast',
                   'northup', 'northdown', 'southup', 'southdown', 'westup', 'westdown', 'eastup', 'eastdown', 'up', 'down',
                   'enter shudong', 'enter hole', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                   'hire', 'jump wall', 'cai qinyun', 'cai tingxiang', 'cai yanziwu',
                   'look',
                    )
    
    _jobsLoaded = {
        "murong"        : JobMurong,
        "wananta"       : JobWananta,
        }
    
    _commandsLoaded = {
        "gps" : {
            "noecho"    : CmdNoEcho,
            "walk"      : CmdWalkDirection,
            "pause"     : CmdWalkPause,
            "river"     : CmdCrossRiver,
            "room"      : CmdRoom,
            "wait"      : CmdWait,
            },
        "player" : {
            "skills"    : CmdSkills,
            "score"     : CmdScore,
            "enable"    : CmdEnable,
            "inventory" : CmdInventory,
            }
        }
    
    _modulesLoaded = {
        "where"     : ModuleWhere,
        "randmove"  : ModuleRandMove,
        "runto"     : ModuleRunto,
        "searchnpc" : ModuleSearchNPC,
        "updatemap" : ModuleUpdateMap,
        
        "dazuoto"   : ModuleDazuoTo,
        "liaoshang" : ModuleHeal,
        "savemoney" : ModuleSaveMoney,
        "sellthings" : ModuleSellThings,
        }
    
    _commandAliases = {
        "yr"        : "exert recover",
        "yg"        : "exert regenerate",
        "yi"        : "exert inspire",
        "yh"        : "exert heal",
        "gg"        : "get all from corpse",
        }
    
    def __init__(self, world, ax, **options):
        super().__init__(None)                                                  # player is the top-level object
        self._mushHelper = MushHelper(world, ax)                                # the mushhelper
        self._rootPath = self._mushHelper.GetInfo(56) 
        self._mapdbname = r"{}map.db".format(self._rootPath)
        self.mush.Log('map db: ' + self._mapdbname)
        self._map = Map(self._mapdbname)                                        # the map for db
        
        self._options = options
        
        self._triggers = {}
        self._commands = {}
        self._modules  = {}
        self._aliases  = {}
        
        self._triggers["hpbrief"]   = TriggerHpbrief(self, "sys", name = "hpbrief")
        self._triggers["response"]  = TriggerResponse(self, "sys", name = "response")
        self._triggers["fullme"]    = TriggerAntiRobot(self, "sys", name = "antirobot")
        self._triggers["roomname"]  = TriggerRoomName(self, "sys", name = "location")
        
        self._triggers["connected"] = Trigger(self, "sys", r"^目前权限：\(player\)|^重新连线完毕。", self._onConnected, flag=TriggerFlag.Enabled, name = "connected")
        
        for group, values in self._commandsLoaded.items():
            for name, cmdclass in values.items():
                self._loadCommand(name, cmdclass, group)

        for name, modclass in self._modulesLoaded.items():
            self._loadModule(name, modclass)
            
        self._aliases['score'] = Alias(self, 'player', r'^sc$', self._buildinCmd, name='score') 
        self._aliases['skills'] = Alias(self, 'player', r'^cha$', self._buildinCmd, name='skills') 
        self._aliases['enable'] = Alias(self, 'player', r'^jifa$', self._buildinCmd, name='enable')    
        self._aliases['inventory'] = Alias(self, 'player', r'^i1$', self._buildinCmd, name='inventory')
        
        self._aliases['drawall'] = Alias(self, 'player', r'^ddd$', self._drawAll, name="drawall")
        
        for name in self._commandAliases.keys():
            self._aliases[name] = Alias(self, 'player', '^{}(\s\S+)?$'.format(name), self._simpleCmd, name = name)
    
    def _buildinCmd(self, sender, args):
        cmd = args.name[7:]  # the actual alias name is player_xxxx, because the group name is "player"
        self._commands[cmd].Execute()
    
    def _simpleCmd(self, sender, args):
        cmd_base = self._commandAliases[args.name[7:]]  # the actual alias name is player_xxxx, because the group name is "player"
        cmd_extra = args.wildcards[1]
        cmd = cmd_base + cmd_extra
        self.mush.Execute(cmd)
    
    def _drawAll(self, sender, args): 
        self.mush.Execute('draw armor')
        self.mush.Execute('draw surcoat')
        self.mush.Execute('draw cloth')
        self.mush.Execute('draw head')
        self.mush.Execute('draw boots')
        self.mush.Execute('remove all')
        self.mush.Execute('wear all')
        if self.playerMenpai == "GB":
            self.mush.Execute('draw staff')
        elif self.playerMenpai in ('TL', 'TH'):
            self.mush.Execute('draw sword')
       
    @property
    def Commands(self):
        return self._commands
    
    @property
    def Triggers(self):
        return self._triggers
          
    def _onConnected(self, sender, args):
        self._commands["score"].AfterDone = self._checkScore
        self._commands["score"].Execute()
        
    def _checkScore(self, sender, args):
        self._commands["score"].AfterDone = None
        if args.state == CommandState.Success:      
            self.playerID = args.result["id"]
            self.playerName = args.result["name"]
            self.playerMenpai = args.result["menpai"]
            
            self.mush.Info("Loading fight module {} for player {}({}) in menpai: {} ...".format(repr(Fight), self.playerName, self.playerID, self.playerMenpai))
            self._fight = Fight(self)
            self.mush.Info('done!\n')
            
            #self.mush.Info("character information {}({}):{} done! starting to load jobs...".format(self.playerID, self.playerName, self.playerMenpai))
            
            for name, jobclass in self._jobsLoaded.items():
                self._loadJobs(name, jobclass)     
                
            self.mush.Info("All job's modules have been loaded!")
    
    def _loadJobs(self, name, jobclass):
        if issubclass(jobclass, Job):
            self.mush.Info("Loading job {} ...".format(repr(jobclass)))
            self._modules[name] = jobclass(self)
            self.mush.Info('【{}】done!\n'.format(self._modules[name].job))
        else:
            self.mush.Error('The class: {} is not a valid Job'.format(repr(jobclass)))
          
    def _loadCommand(self, name, cmdclass, group):
        if issubclass(cmdclass, MudCommand):
            self.mush.Info("Loading command {} with name '{}' ...".format(repr(cmdclass), name))
            self._commands[name] = cmdclass(self, group)
            self.mush.Info('done!\n')
        else:
            self.mush.Error('The command: {} is not a valid MudCommand'.format(repr(cmdclass)))        
            
    def _loadModule(self, name, modclass):
        if issubclass(modclass, Module):
            self.mush.Info("Loading module {} with name '{}' ...".format(repr(modclass), name))
            self._modules[name] = modclass(self)
            self.mush.Info('done!\n')
        else:
            self.mush.Error('The class: {} is not a valid Module'.format(repr(modclass)))
            
    def RunModule(self, name, afterDone = None, afterFail = None, **params):
        if name in self._modules.keys():
            module = self._modules[name]
            
            module.AfterDone = afterDone
            module.AfterFail = afterFail
            module.AfterStop = None
            module.Start(**params)
        else:
            self.mush.Error("module %s doesn't exist." % name)
            
    def StopModule(self, name, afterStop = None, **params):
        if name in self._modules.keys():
            module = self._modules[name]
            
            module.AfterDone = None
            module.AfterFail = None
            module.AfterStop = afterStop
            module.Stop(**params)
        else:
            self.mush.Error("module %s doesn't exist." % name)
        