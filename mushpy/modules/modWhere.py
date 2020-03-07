# -*- coding:utf-8 -*-

from .module import *

class ModuleWhere(Module): 
    def __init__(self, owner, modulename="where", **options):
        super().__init__(owner, modulename, **options)
        self._map = owner._map
        self.CommandRoom = owner.Commands["room"]
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^where(\s\S+)?$', self._aliasFunction, name='where')
    
    def _aliasFunction(self, sender, args):
        _dir = args.wildcards[0]
        if _dir:
            self.Start(direction = _dir)
        else:
            self.Start(direction = '')   
        
    def _locate_position(self, sender, args):
        if args.state == CommandState.Success:
            self.mudroom = args.result["room"]
            self.dbrooms = self._map.FindRoomsByRoom(self.mudroom)
            
            self.CommandRoom.AfterDone = None
            if len(self.dbrooms) >= 1:
                for rm in self.dbrooms:
                    self.mush.Log('Find a matched room: {1} {2} (ID: {0})'.format(rm.id, rm.city, rm.name))
                    links = self._map.FindRoomLinks(rm.id)
                    for link in links:
                        self.mush.Log('    room link "{0}" to {2} {3}(id: {1})'.format(link.path, link.linkto, link.city, link.name))
                
                self._doEvent('AfterDone')     
            else:
                self.mush.Error("Didn't find matched room...")
                self.mush.Error('name: ' + self.mudroom.Name)
                self.mush.Error('description: ' + self.mudroom.Description)
                self.mush.Error('exits: ' + self.mudroom.Exit)
                
                self._doEvent('AfterFail')            
    
    def Start(self, **options):
        command = 'look' + options.get('direction', '')
        self.CommandRoom.AfterDone = self._locate_position
        self.CommandRoom.Execute(command)