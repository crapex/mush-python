# -*- coding:utf-8 -*-

from collections import namedtuple
from ..objects import MushObject, Trigger


TriggerDefinition = namedtuple('TriggerDefinition', ['name', 'regx', 'func', 'lines'])
CommandEventArgs = namedtuple("CommandEventArgs", ["state", "sender", "args"])

def Event(name):
    @property
    def prop(self):
        if not name in self._events.keys():
            self._events[name] = None
        return self._events[name]
    
    @prop.setter
    def prop(self, value):
        if value:
            assert(callable(value), 'The event shall be callable!')
            self._events[name] = value
        else:
            self._events[name] = None
            
    return prop

class CommandState:
    NotStart = 0
    Success = 1
    Failed = 2
    Timeout = 3
    
class MudCommand(MushObject):
    '''
    处理mud命令 的基础类
       mud命令执行后的三种状态：
           1、已定义的正常输出被触发 OnSuccess
           2、已定义的异常输出被触发 OnFail
           3、一段时间内未捕获到已定义的正常或异常输出，视作超时 OnTimeout
       mud命令执行前后可能需要执行的操作：
           1、执行前，使能该命令的相应Trigger, Timer, Alias组 BeforeExecute
           2、执行后，停用该命令的相应Trigger, Timer, Alias组 AfterExecute
       事件及执行点：
           1、类型被初始化完毕（内部函数）
               执行前  ----> _beforeExecute
                 三选一： 执行完并成功  ----> _onSuccess
                        执行完但失败  ----> _onFail
                        执行超时      ----> _onTimeout (取消超时判定，设置单个超时命令，用于多命令执行时判定超时)
               执行后  ----> _afterExecute
           2、可以为BeforeExecute和AfterExecute注册事件，即将函数引用加入_event
    '''  
    
    _initTriList = ()
    
    AfterDone = Event('AfterDone')
    AfterFail = Event('AfterFail')
    AfterHalt = Event('AfterHalt')
    AfterTimeout = Event('AfterTimeout')
    
    def __init__(self, owner, group):
        ''' group: group name in mushclient '''
        super().__init__(owner)
        self._group = group                         # group name
        self._events = {}                           # event list
        self.InitTriggers()                         # init all triggers
        
        self._state = CommandState.NotStart         # state
        
    def _initTriggers(self):
        '''
        初始化保存在元组（self._initTriList）中的触发器列表
        '''
        self._triggers = {}
        for tri in self._initTriList:
            if tri.lines > 1:
                self._triggers[tri.name] = Trigger(self.owner, self._group, tri.regx, getattr(self, tri.func), multiline = True, lines = tri.lines, name = tri.name)
            else:
                self._triggers[tri.name] = Trigger(self.owner, self._group, tri.regx, getattr(self, tri.func), name = tri.name)
            
    def _doEvent(self, name, args = None):
        if name in self._events.keys():
            func = self._events[name]
            if callable(func):
                #print('do_event: %s' % self.state)
                func(self, CommandEventArgs(self._state, args))
                #self._events[name] = None                           # all event only fire once.
    
    def _coroutine(self):
        state, sender, args = yield
        self._afterExecute(state, sender, args)
        
    def _onSuccess(self, sender, args):
        try:
            self._generator.send((CommandState.Success, sender, args))
        except StopIteration:
            #print("the command: '%s' has executed successfully" % self._command)
            pass
                
    def _onFail(self, sender, args):
        try:
            self._generator.send((CommandState.Failed, sender, args))
        except StopIteration:
            #print("the command: '%s' hasn't executed failed" % self._command)   
            pass
    
    def _onTimeout(self, sender, args):
        try:
            self._generator.send((CommandState.Timeout, sender, args))
        except StopIteration:
            #print("the command: '%s' hasn't executed timeout" .% self._command)   
            pass
    
    def _beforeExecute(self, **params):
        '''
        default before execute:
          enable the group
        '''
        en = params.get('autoenable', True)
        self.Enable(en)
    
    def _afterExecute(self, state, sender, args):
        self.Enable(False) 
        self._state = state
        self._doEvent("AfterDone", CommandEventArgs(state, sender, args))    
        self._state = CommandState.NotStart
 
    def Enable(self, value = True):  
        for tri in self._triggers.keys():
            self._triggers[tri].Enabled = value
    
    def Execute(self, cmd, **params):
        self._command = cmd                                         # command text
        self._beforeExecute(**params)
        self._generator = self._coroutine()
        next(self._generator)
        self.mush.Execute(self._command)