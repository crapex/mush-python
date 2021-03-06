# -*- coding:utf-8 -*-

import re
from ..objects import Trigger, TriggerFlag
from ..commands import CommandEventArgs
from .module import *

class ModuleSearchNPC(Module):   
    def __init__(self, owner, modulename="search", **options):
        super().__init__(owner, modulename, **options)
        self._map = owner._map
        
        self._commands = {}
        self._commands["noecho"] = owner.Commands["noecho"]
        self._commands["walk"]   = owner.Commands["walk"]
        self._commands["wait"]   = owner.Commands["wait"]
        self._directions = owner._directions
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^bl\s+(.*)$', self._aliasFunction, name='traverse')
    
    def _aliasFunction(self, sender, args):
        param = args.wildcards[0]

        if param == 'stop':
            self.mush.Warning('module [searchnpc]: abort manually!')
            self.Stop()
        else:
            m = re.match(r'(\S+)\s+(\S+)\s+(.+)$', param)
            
            to = m[1]
            npcname = m[2]
            npcid = m[3]
            
            self.AfterDone = None
            self.AfterFail = None
            self.Start(to=to, npcname=npcname, npcid=npcid) 
    
    def _resetall(self):
        for cmd in self._commands.values():
            cmd.Enable(False)
            cmd.AfterDone = None
    
    def _npc_found(self, sender, args):
        print('the npc has been found.')
        self._resetall()
        
        self.mush.Execute('follow ' + self._npcid.lower())
        self.mush.Execute('response traverse ok')
        
        self._state = CommandState.Success
        self._doEvent('AfterDone')
    
    def _on_step_over(self, sender, args):
        # print('command done, wait 200ms')
        if args.state == CommandState.Success:
            self._commands['wait'].AfterDone = self._on_wait_over
            self._commands['wait'].Wait(.4)
        
    def _on_wait_over(self, sender, args): 
        if args.state == CommandState.Success:                 
            if self._stepIndex < self._stepCount:
                step = self._stepList[self._stepIndex]
                self._stepIndex += 1
                
                # print('wait done, do next command: %s' % step)
                
                m = re.match(r'(\S+)\((.+)\)', step)
                if m:
                    if m[1] == 'walk_busy':
                        self._commands['walk'].Execute(m[2])
                    elif m[1] == 'walk_retry':
                        self._commands['walk'].Execute(m[2])  
                    elif m[1] == 'walk_pause':
                        self._commands['pause'].Execute(m[2])
                        # print('dont support walk_pause in traverse.')
                    elif m[1] == 'walk_wait':
                        self._commands['wait'].AfterDone = self._on_step_over
                        self._commands['wait'].Wait(m[2])
                        #print('dont support walk_wait in traverse.')
                    elif m[1] == 'cross_river':
                        # self._commands['river'].Execute(m[2])
                        self.mush.Error("module [searchnpc]: Don't support cross_river in traverse.")
                    else:
                        self.mush.Error("module [searchnpc]: Don't recognize the command: {}".format(step))
                else: 
                    if step in self._directions:
                        self._commands['walk'].Execute(step)
                        # print('yes, walk execute: ' + step)
                    else:
                        self._commands['noecho'].Execute(step)    
                        # print('yes, noecho execute: ' + step)
                     
            elif self._stepIndex == self._stepCount:
                self.mush.Error("module [searchnpc]: Traverse failed, don't find npc")
                self.mush.Execute('response traverse fail')    
                self._resetall()
                
                self._doEvent('AfterFail')
        # add CmdwalkDirection timeout/fail judgement
        elif (args.state == CommandState.Timeout) or (args.state == CommandState.Failed):
            self.mush.Error("module [searchnpc]: Traverse failed because of walk timeout, don't find npc")
            self.mush.Execute('response traverse fail')    
            self._resetall()
                
            self._doEvent('AfterFail')
    
    def _traverse(self, path, npcname, npcid, **params):
        self._stepList = path.split(';')
        self._stepCount = len(self._stepList)
        self._stepIndex = 0
        
        #npc_pattern = r'\s*(.*){}\({}{}\)'.format(npcname, npcid[0].upper(), npcid[1:])
        #self.npc_tri = Trigger(self, self.modulename, npc_pattern, self._npc_found, name = "npc_find")
        #self.npc_tri.Enabled = True
        
        for cmd in self._commands.values():
            cmd.Enable(True)
            cmd.AfterDone = self._on_step_over

        self._commands['wait'].AfterDone = self._on_wait_over
        
        self.mush.SendNoEcho('set brief 3')
        self._on_wait_over(self._commands['walk'], CommandEventArgs(CommandState.Success, None))
    
    def _start_from_current_location(self, mod, args):
        dbroomstart = args.result["dbroom"]
        self._wholecity = False
        self._deep = 4
        
        self._traverse_start_id = dbroomstart.id
        self._traverse_path = self._map.FindTraversal(self._traverse_start_id, wholecity=self._wholecity, deep=self._deep)
        
        if self._traverse_path.result:
            path = ';'.join(self._traverse_path.path)
            self.mush.Log('module [searchnpc]: start to traverse for npc: {}({}) with path: {}'.format(self._npcname, self._npcid, path))
            self._traverse(path, self._npcname, self._npcid)
        pass
    
    def _arrive_at_start(self, mod, args):
        
        if len(mod.destination) == 1:
            self._wholecity = self.options.get('wholecity', False)
            self._deep = self.options.get('deep', 4)
        else:
            self._wholecity = self.options.get('wholecity', True)
            self._deep = self.options.get('deep', 1)
        
        self._traverse_start_id = mod.destination_id    
        self._traverse_path = self._map.FindTraversal(self._traverse_start_id, wholecity=self._wholecity, deep=self._deep)
        
        if self._traverse_path.result:
            path = ';'.join(self._traverse_path.path)
            self.mush.Log('module [searchnpc]: start to traverse for npc: {}({}) with path: {}'.format(self._npcname, self._npcid, path))
            self._traverse(path, self._npcname, self._npcid)
        
    def _not_find_path(self, mod, args):
        self.mush.Error('module [searchnpc]: Can not find the path to the search start location.')
        self._doEvent('AfterFail')
    
    def Start(self, **options):
        ''' to == None means traverse from current location. '''
        to = options.get('to', None)
        self._npcname = options.get('npcname')
        self._npcid = options.get('npcid')

        if getattr(self, "npc_tri", None):
            self.npc_tri.__del__()
            self.npc_tri = None
            
        npc_pattern = r'\s*(.*){}\({}{}\)'.format(self._npcname, self._npcid[0].upper(), self._npcid[1:])
        self.npc_tri = Trigger(self, self.modulename, npc_pattern, self._npc_found, flag = TriggerFlag.Enabled | TriggerFlag.OneShot)

        if to:
            self.owner.RunModule('runto', afterDone=self._arrive_at_start, afterFail=self._not_find_path, to=to)
        else:
            self.owner.RunModule('randmove', afterDone=self._start_from_current_location, afterFail=self._not_find_path)   
        
    def Stop(self, **options):
        for cmd in self._commands.values():
            cmd.AfterDone = None
        self.AfterDone = None
        self.AfterFail = None
        
        self._doEvent('AfterStop')   