# -*- coding:utf-8 -*-
from ..objects import Timer
from .mudCmd import MudCommand

# 利用MUSHCLIENT定时器模拟命令
class CmdWait(MudCommand):
    '''
    延时等待，利用定时器等待
    '''
    def __init__(self, owner, group):
        super().__init__(owner, group)
        self._timeout = 1
        self._timer = Timer(owner, group, self._timeout, self._onTimeout, name = 'wait')
        
    def _onTimeout(self, sender, args):
        #print('on timer, the generator is:', self._generator)
        self._timer.Enabled = False
        super()._onTimeout(sender, args)
        
    def Execute(self, cmd, **params):
        self._timeout = cmd
        self._timer.SetTimeout(self._timeout) 
        self._timer.Reset()
        self._generator = self._coroutine()
        next(self._generator)
        
    def Wait(self, time):
        self.Execute(time)