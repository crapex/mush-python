# -*- coding:utf-8 -*-

import math
import re
from datetime import datetime


class MushHelper:
    '''
    MushHelper 类型的变量用于与mushclient之间的接口，其使用singleton设计模式以确保只有1个全局对象。
    在mushclient的world的脚本文件前面要对该类型进行配置和初始化，以确保其他模块的正常使用。配置与初始化代码如下：
       helper = MushHelper(world, ax)
    '''
    
    # 处理逻辑： 在mushclient的全局命名空间（world.ax._scriptEngine_.globalNameSpaceModule）中注册3个函数，供python脚本创建的所有触发器、定时器、别名使用
    #     例如： mushclient中，触发器触发了脚本"trigger_func"（TriggerHandlerName），会调用MushHelper.triggers_handler函数，再由此函数进行触发器的二次分派（参见triggers_handler实现）
    TriggerHandlerName = 'trigger_func'     # mushclient中使用的所有trigger的脚本（script）均使用该名称，初始化时将此名称注册到pyengine的全局命名空间中， 下同 
    TimerHandlerName = 'timer_func'         # mushclient中使用的所有timer的脚本（script）均使用该名称
    AliasHandlerName = 'alias_func'         # mushclient中使用的所有alias的脚本（script）均使用该名称
    
    def __init__(self, world, ax):
        self._items = dict()                # _items词典用于储存所有的全局对象（属性），name, obj 键值对
        self._trigger_functions = dict()    # _trigger_functions词典用于存储所有注册至MushHelper中对应trigger的处理函数，name, func 键值对
        self._alias_functions = dict()      # _alias_functions词典用于存储所有注册至MushHelper中对应alias的处理函数，name, func 键值对
        self._timer_functions = dict()      # _timer_functions词典用于存储所有注册至MushHelper中对应timer的处理函数，name, func 键值对
        self._world = world                 # save local world object
        self._ax = ax                       # save local ax object
        self._pyengine = ax._scriptEngine_  # save local scriptEngine object
        
        self.initialization()
        
    def initialization(self):
        '''
        # 将 trigger, alias, timer 的处理函数注册到 pyengine 全局命名空间
        # 这样所有的 triggers, aliases, timers 的处理脚本名均可设置为trigger_func等
        '''
        #setattr(self.pyengine.globalNameSpaceModule, self.TriggerHandlerName, self.triggers_handler)
        #setattr(self.pyengine.globalNameSpaceModule, self.AliasHandlerName, self.aliases_handler)
        #setattr(self.pyengine.globalNameSpaceModule, self.TimerHandlerName, self.timers_handler)
        self.expose(self.TriggerHandlerName, self.triggers_handler)
        self.expose(self.AliasHandlerName, self.aliases_handler)
        self.expose(self.TimerHandlerName, self.timers_handler)
    
    def expose(self, name, func):
        ''' 将函数以name名称暴露到mush脚本命名空间，让mushclient可以直接通过名称访问 '''
        setattr(self.pyengine.globalNameSpaceModule, name, func)
    
    def __getattr__(self, name):
        '''
        利用python特点，将访问所有的MushHelper不存在的对象重新定向到world的同名对象上
        这样，就可以直接 MushHelper.EnableTriggerGroup，相当于 world.EnableTriggerGroup
        '''
        attr = getattr(self._world, name, 'None')
        if attr:
            return attr
        
        raise AttributeError('com-object "world" does not have attribute: %s' % name)
    
    @property
    def world(self):
        return self._world

    @property
    def pyengine(self):
        return self._pyengine
    
    def additem(self, name, item):
        self._items[name] = item
    
    def deleteitem(self, name):
        if name in self._items:
            del self._items[name]
    
    def register(self, typename, name, func):
        '''
        注册处理函数的通用程序
        '''
        if typename.lower() == "trigger":
            self._trigger_functions[name] = func
        elif typename.lower() == "alias":
            self._alias_functions[name] = func
        elif typename.lower() == "timer":
            self._timer_functions[name] = func
        else:
            raise KeyError('only allowed: trigger, alias or timer.')
    
    def LogCustom(self, msg, color = "green", bgColor = "black", timestamp = False, newline = False):
        if timestamp:
            msg = '{}: {}'.format(datetime.now().strftime('%x %X'), msg)
        
        msg = msg.replace(r'\r\n', r'\n')
        self.ColourTell(color, bgColor, msg)
        
        if newline:
            self.Tell('\n')
            
    def Log(self, msg, timestamp = True, newline = True):
        self.LogCustom(msg, "blue", "white", timestamp, newline)
            
    def Error(self, msg, timestamp = True, newline = True):
        self.LogCustom(msg, "red", "wheat", timestamp, newline)
        
    def Warning(self, msg, timestamp = True, newline = True):
        self.LogCustom(msg, "darkred", "lawngreen", timestamp, newline)
        
    def Info(self, msg, timestamp = False, newline = False):
        self.LogCustom(msg, timestamp = timestamp, newline = newline)
        
    def unregister(self, typename, name):
        '''
        注销处理函数的通用程序
        '''
        if typename.lower() == "trigger":
            if name in self._trigger_functions:
                self.DeleteTrigger(name)
                del self._trigger_functions[name]
        elif typename.lower() == "alias":
            if name in self._alias_functions:
                self.DeleteAlias(name)
                del self._alias_functions[name]
        elif typename.lower() == "timer":
            if name in self._timer_functions:
                self.DeleteTimer(name)
                del self._timer_functions[name]
        else:
            raise KeyError('only allowed: trigger, alias or timer.')
    
    def registerTrigger(self, name, func):
        '''
        注册Trigger处理函数
        '''
        self.register('trigger', name, func)
        
    def registerAlias(self, name, func):
        '''
        注册alias处理函数
        '''
        self.register('alias', name, func)
        
    def registerTimer(self, name, func):
        '''
        注册timer处理函数
        '''
        self.register('timer', name, func)

    def unregisterTrigger(self, name):
        '''
        注销Trigger处理函数
        '''
        self.unregister('trigger', name)
        
    def unregisterAlias(self, name):
        '''
        注销Alias处理函数
        '''
        self.unregister('alias', name)
        
    def unregisterTimer(self, name):
        '''
        注销Timer处理函数
        '''
        self.unregister('timer', name)
        
    def triggers_handler(self, name, line, wildcards):
        '''
        共用的Trigger处理函数，查找是否有注册号的对应函数，有则调用，否则调用默认的处理函数
        '''
        #print('trigger "%s" has been handled...' % name)
        if (name in self._trigger_functions) and callable(self._trigger_functions[name]):
            self._trigger_functions[name](name, line, wildcards)
        else:
            self._defaulthandler('trigger', name, line, wildcards)
            
    def aliases_handler(self, name, line, wildcards):
        '''
        共用的Alias处理函数，查找是否有注册号的对应函数，有则调用，否则调用默认的处理函数
        '''
        #print('alias "%s" has been handled...' % name)
        if (name in self._alias_functions) and callable(self._alias_functions[name]):
            self._alias_functions[name](name, line, wildcards)
        else:
            self._defaulthandler('alias', name, line, wildcards)
            
    def timers_handler(self, name):
        '''
        共用的Timer处理函数，查找是否有注册号的对应函数，有则调用，否则调用默认的处理函数
        '''
        #print('timer "%s" has been handled...' % name)
        if (name in self._timer_functions) and callable(self._timer_functions[name]):
            self._timer_functions[name](name)
        else:
            self._defaulthandler('timer', name, None, None)
            
    def _defaulthandler(self, typename, name, line, wildcards):
        '''
        默认的处理函数，输出黄色红色背景黄色字符的“处理器不存在"
        '''
        self.ColourNote('yellow', 'red', '{0} name({1}) handler does not exist.'.format(typename, name))
        
    def MoneyToString(self, coin):
        if coin == 0:
            return "不花钱"
    
        gold = math.floor(coin/10000)
        coin = coin - (gold * 10000)
        silver = math.floor(coin/100)
        coin = coin - (silver * 100)

        goldStr = '{}两黄金'.format(gold) if gold > 0 else ''
        silverStr = '{}两白银'.format(silver) if silver > 0 else ''
        coinStr = '{}文铜板'.format(coin) if coin > 0 else ''

        return "{}{}{}".format(goldStr, silverStr, coinStr)
    
    def _hz_to_number(self, hz):
        return '零一二三四五六七八九'.find(hz)

    def Word2Number(self, word):
        b, s, g = 0, 0, 0
        m = re.match(r"^(.+)百十(.+)$", word)
        if m:
            b = self._hz_to_number(m[1])
            s = 1
            g = self._hz_to_number(m[2])
        else:
            m = re.match(r"^(.+)百十$", word)
            if m:
                b = self._hz_to_number(m[1])
                s = 1
            else:
                m = re.match(r"^(.+)百$", word)
                if m:
                    b = self._hz_to_number(m[1])
                else:    
                    m = re.match(r"^(.+)百(.+)十$", word)
                    if m:
                        b = self._hz_to_number(m[1])
                        s = self._hz_to_number(m[2])
                    else:
                        m = re.match(r"^(.+)百(.+)十(.+)$", word)
                        if m:
                            b = self._hz_to_number(m[1])
                            s = self._hz_to_number(m[2])  
                            g = self._hz_to_number(m[3])  
                        else:
                            m = re.match(r"^(.+)百零(.+)$", word)
                            if m:
                                b = self._hz_to_number(m[1])
                                g = self._hz_to_number(m[2])  
                            else:
                                m = re.match(r"^(.+)十$", word)
                                if m:
                                    s = self._hz_to_number(m[1])
                                else:
                                    m = re.match(r"^(.+)十(.+)$", word)
                                    if m:
                                        s = self._hz_to_number(m[1])
                                        g = self._hz_to_number(m[2])
                                    else: 
                                        m = re.match(r"^十(.+)$", word)
                                        if m:
                                            s = 1
                                            g = self._hz_to_number(m[1])
                                        else:
                                            m = re.match(r"^(.+)$", word)
                                            if m:
                                                g = self._hz_to_number(m[1])
                                        
        total = b * 100 + s * 10 + g
        return total


def MushVariable(name):
    @property
    def prop(self):
        return self.mush.GetVariable(name)
    
    @prop.setter
    def prop(self, value):
        self.mush.SetVariable(name, value)
            
    return prop    
