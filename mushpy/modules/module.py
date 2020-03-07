# -*- coding:utf-8 -*-

from ..objects import Alias
from ..commands import TriggerDefinition, CommandState, MudCommand

# module is a special command
class Module(MudCommand):
    def __init__(self, owner, modulename, **options):
        super().__init__(owner, modulename)

        self.modulename = modulename
        
        self.options = options

    # the module is a special command, but it shall:
    # override the coroutine functions in MudCommand
    # to ensure it has proper reaction when start/stop.
    # the functions in MudCommand which are override are:
    #  _coroutine
    #  _onSuccess
    #  _onFail
    #  _onTimeout
    #  _beforeExecute
    #  _afterExecute
    #  Execute
    def _coroutine(self):
        pass
        
    def _onSuccess(self, sender, args):
        pass
                
    def _onFail(self, sender, args):
        pass
    
    def _onTimeout(self, sender, args):
        pass
    
    def _beforeExecute(self, **params):
        pass
        
    def _afterExecute(self, state, sender, args):
        pass
        
    def Execute(self, cmd, **params):
        pass

    def Start(self, **options):
        pass
        
    def Stop(self, **options):
        pass
    
__all__ = ['TriggerDefinition', 'CommandState', 'MudCommand', 'Alias', 'Module']