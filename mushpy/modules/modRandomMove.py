# -*- coding:utf-8 -*-

import random
from .module import *

class ModuleRandMove(Module): 
    def __init__(self, owner, modulename="randmove", **options):
        super().__init__(owner, modulename, **options)
        self._map = owner._map
        self.CommandRoom = owner.Commands["room"]  
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^randmove$', self._aliasFunction, name='randmove')
    
    def _aliasFunction(self, sender, args):
        self.Start()      
        
    def _check_place(self, sender, args):
        self._state = args.state
        if args.state == CommandState.Success:
            self.mudroom = args.result["room"]

            self.dbrooms = self._map.FindRoomsByRoom(self.mudroom)
            if len(self.dbrooms) == 1:
                # randmove ok
                # self.mush.SendNoEcho('set brief 1')
                self.mush.Log('已移动至确认地点：{} {}(ID: {})'.format(self.dbrooms[0].city, self.dbrooms[0].name, self.dbrooms[0].id))
                self.CommandRoom.AfterDone = None
                self._result["mudroom"] = args.result["room"]
                self._result["dbrooms"] = self.dbrooms
                
                self._doEvent('AfterDone')     
            else:
                exit_list = self.mudroom.Exit.split(';')
                step = random.choice(exit_list)
                self.CommandRoom.Execute(step)
        
    def Start(self, **options):
        command = options.get('start', 'look')
        self.mush.SendNoEcho('set brief 0')
        self.CommandRoom.AfterDone = self._check_place
        self.CommandRoom.Execute(command)