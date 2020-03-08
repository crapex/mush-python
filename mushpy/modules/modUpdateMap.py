# -*- coding:utf-8 -*-

import re
from ..objects import Trigger, TriggerFlag
from .module import *

class ModuleUpdateMap(Module):
    _triList = ()
    
    def __init__(self, owner, modulename='updatemap', **options):
        
        super().__init__(owner, modulename, **options)
        self._map = owner._map
        
        self._commands = {}
        self._commands["wait"] = owner.Commands["wait"]
        self._commands["walk"] = owner.Commands["walk"]
        self._commands["noecho"] = owner.Commands["noecho"]
        self._commands["room"] = owner.Commands["room"]

        self._triResponse = owner.Triggers["response"]

        #self._triResponse = TriggerResponse(self.modulename, self._response_updatemap, name='cmdend')
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^updatemap(\sstop)?$', self._aliasFunction, name='updatemap')
    
    def _aliasFunction(self, sender, args):
        cmd = args.line
        if cmd == "updatemap":
            self.Start()
        elif cmd == "updatemap stop":
            self.mush.Log("Stop module [updatemap]!")
            self.Stop()
        
    def _main_loop(self):
        # configuration commands and 
        for cmd in self._commands.values():
            cmd.AfterDone = self._pushCoroutine
        
        self.mush.Log('module [updatemap]: start to update rooms in map database...')
        self.mush.Log('module [updatemap]: path length: %d' % len(self._path))
        self.mush.Log('module [updatemap]: rooms count: %d' % len(self._rooms))
        
        self.mush.Execute('set brief 3')
        self._update_count = 0
        
        for idx in range(len(self._rooms)):
            link = self._path[idx]
            roomid = self._rooms[idx]
            linksteps = link.split(';')
            
            for step in linksteps:
                m = re.match(r'(\S+)\((.+)\)', step)
                if m:
                    if m[1] == 'walk_busy':
                        self._commands['walk'].Execute(m[2])
                    elif m[1] == 'walk_pause':
                        # self._commands['pause'].Execute(m[2])
                        raise Exception('module [updatemap]: dont support walk_pause in update map.')                        
                    elif m[1] == 'walk_wait':
                        # self._commands['wait'].Wait(m[2])
                        raise Exception('module [updatemap]: dont support walk_wait in update map.')
                    elif m[1] == 'cross_river':
                        # self._commands['river'].Execute(m[2])
                        raise Exception('dont support cross_river in update map.')
                    else:
                        raise Exception("Don't recognize the command: {}".format(step))
                else: 
                    if step in self.owner._directions:
                        self._commands['walk'].Execute(step)
                        # print('yes, walk execute: ' + step)
                    else:
                        self._commands['noecho'].Execute(step)    
                        # print('yes, noecho execute: ' + step)
                yield
                        
            self.mush.Execute('response updatemap step')
            yield
            
            if not roomid in self._rooms_updated:
                # print('update here with id: %d' % roomid)
                self._commands["room"].Execute('look') 
                sender, args = yield
                if args.state == CommandState.Success:
                    mudroom = args.result["room"]
                    dbroom = self._map.GetRoomInfo(roomid)
                    if mudroom.Name.find('泥人') >= 0:
                        pass
                    elif dbroom.name == mudroom.Name:
                        self._map.UpdateRoom(roomid, mudroom)
                        self._update_count += 1
                        self.mush.Log('module [updatemap]: update room (ID: {}) ok!'.format(roomid))
                    else:
                        self.mush.Error('module [updatemap]: 此处地名与数据库地名不一致，可能是走路时被拦住了，此处地图请手动尝试')
                        raise StopIteration
                else:
                    self.mush.Error('命令执行失败')
                    raise StopIteration
                
                self._rooms_updated.append(roomid)
            else:
                self.mush.Log('module [updatemap]: id: %d has been updated already, bypass' % roomid)

            self._commands['wait'].Wait(.2)
            yield
            
        self.mush.Execute('response updatemap step')
        yield
    
    def _response_updatemap(self, sender, args):
        resp = args.get('updatemap', None)

        if resp == "step":
            try:
                self._coroutine.send(None)
            except StopIteration:
                for cmd in self._commands.values():
                    cmd.AfterDone = None
                    
                self._triResponse.RemoveCallback(self._response_updatemap)
                
                self.mush.Log('module [updatemap]: all rooms updated, total count: {}'.format(self._update_count))
                self.mush.Execute('set brief 1')

    def _pushCoroutine(self, sender, args):
        try:
            self._coroutine.send((sender, args))
        except StopIteration:
            self.mush.Error('module [updatemap]: rooms update failed')
            self.mush.Execute('set brief 1')
        
    def _after_catch_room(self, sender, args):
        if args.state == CommandState.Success:
            try:
                self._coroutine.send(args.result["room"])
            except StopIteration:
                self.mush.Error('module [updatemap]: rooms update failed')
                self.mush.Execute('set brief 1')
            
    def _after_know_where(self, mod, args):
        # 1. how many db rooms are matched? only start when 
        #dbrooms = mod.dbrooms
        dbrooms = args.result["dbrooms"]
        if len(dbrooms) == 1:
            self._update_start_room = dbrooms[0]
            self._update_traversal = self._map.FindTraversal(self._update_start_room.id, wholecity=True, deep=0)
            
            self._path = self._update_traversal.path
            self._rooms = self._update_traversal.rooms
            self._rooms_updated = []
            
            self._triResponse.AddCallback(self._response_updatemap)
            # create coroutine and start

            self._coroutine = self._main_loop()
            self._coroutine.send(None)
        else:
            self.mush.Error("module [updatemap]: Can't start from an uncertain location, please use 'rt here' to check and retry.")
    
    def Start(self, **options):
        self.owner.RunModule('where', afterDone=self._after_know_where)
    
    def Stop(self, **options):
        try:
            self._coroutine.send(StopIteration)
        except StopIteration:
            self.mush.Log("module [updatemap] stop successfully")
            
        