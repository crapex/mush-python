# -*- coding:utf-8 -*-

import re
import random
from ..commands import CommandEventArgs
from .module import *

class ModuleRunto(Module):   
    _mapxkx = '''
                                           【北大侠客行总图】

                                                                          
                                  ≈≈≈≈≈≈≈≈≈       蒙古                            ╔═══╗
                        明教    ≈                 ≈          ╲                          ║冰火岛║
                      ◎沙漠◎③                   ≈    ╭───张家口  关外              ╚═══╝
                    ╱楼兰   ≈    灵鹫           ≈ ╭─╯    黑木崖  ╲ │     黄河
            星宿-湟中╮      ②灵州★┤回部        ≈晋阳─────┴──-北京  ≈╔═══╗
     ◎扎陵湖◎  ╱   兰州◎≈│╲ 小镇╯╭───╯≈④≈≈≈≈       ★╭-┴─≈ ║神龙岛║
          藏民部落     ≈≈   │     ├长安-───┬洛阳-──╮≈≈≈  濮阳 ≈≈  ╚═══╝
           ╲   白驼  ≈①    │    汉中┴─╮    │ │      │    ≈≈⑤≈         泰山
            ◎沙漠◎≈        │     │ 全真┴古墓│-│少林─汝州      ╰──┬──╯
                ≈≈          │     │  │       ↓ │          ╮          │
                              │     │  ╰小村→华山│           许昌╮   ╭曲阜
                         ╭-─╯     │     ╰───南阳────-╯│ ╰淮北  │   丐帮
           雪山派  ╭──╯          │  绝情谷  ╭─╯            │      ╰-┤◎青竹林◎
             ╰─╮│                │ 武当←─襄阳───────信阳-───扬州╯
          大轮寺 ││                │          │       ╭───╯╰杀手帮←┤
            ↑   ├╯                │         荆州  ≈⑧≈≈        ≈≈≈≈≈⑥≈≈≈
            ╰─赞普                 │     ≈≈⑨≈≈ │     ≈⑦≈≈╭────┼镇江╮≈≈≈长江
                 │                  │ ╭←─┬岳阳╮ │ ╭─建康府─┤归云庄╮╰-┬-╯
                 │                  │ ╰╮  ↓ │ ╰江州╯  ╰─┼─┤慕容≈┴─苏州         ╔═══╗
                 ╰────────-成都─╯ 桃源│    │         │  ╰───╮   │╭明州城≈║桃花岛║
                                   ╱↓ 铁掌峰╯ │    │         ╰───-╮ ╰─嘉兴─牙山   ╚═══╝
                         无量山╮╱ 峨嵋         │    │   壮族山寨 梅庄-临安府★ ┼─岳王墓
                         天龙寺┤                ├←-南昌→◎老林◎←-──╯      │
                               │ 平西王府     ◎苗岭◎╰────────────武夷山─╮
                              大理★ │  ◎苗岭◎┤                                │╭-福州
                               ╰─-昆明╱      苗疆                              泉州≈╔═══╗
                                               五毒教                              ≈   ║钓鱼岛║
                                                                              ╔═══╗╚═══╝
                                                                              ║侠客岛║
                                                                              ╚═══╝

                                                                                   ┎──图例───┒ 
                                                                                   │   门派       │   
                                                                                   │   城市       │
                                                                                   │   都市       │
                                                                                   │   野外       │
                                                                                   │   ◎XX◎ 迷宫│
                                                                                   │   ≈≈≈ 黄河│
                                                                                   │   ≈≈≈ 长江│
                                                                                   │   ★     入职│
                                                                                   │   ≈≈≈ 水路│
                                                                                   │   ①～⑨ 渡口│
                                                                                   ┖───────┚ 
    
    '''
    
    _help = '''
       newstart的gps模块，使用方法如下：
           指令      用鿿
           rt map:   显示pkuxkx总图
           rt help:  显示本帮助信息
           rt here:  显示当前房间信息
           rt 数字:  移动到指定的房间（数字为房间ID）
           rt 英文:  移动到指定的房间（英文为房间别名）
           rt 中文:  移动到指定的房间（中文为城市+地名）
        '''
    
    _maze_list = {'heizhao' : 's;e;n;w;s;s;w',
                  'zsf' : 'w;sw;s;se;e;ne;n;nw;sw;s;e;open door;n',
                  'jinding' : 'n;n;w;e;s;e;e;n;n',
        }
    
    def __init__(self, owner, modulename="runto", **options):
        super().__init__(owner, modulename, **options)
        self._map = owner._map
        self._commands = {}
        self._commands["walk"]  = owner.Commands["walk"]
        self._commands["pause"] = owner.Commands["pause"]
        self._commands["wait"]  = owner.Commands["wait"]
        self._commands["river"] = owner.Commands["river"]
        self._commands["noecho"]= owner.Commands["noecho"]
        
        self._triRoomName = owner.Triggers["roomname"]
        self._triRoomName.AddCallback(self._checkRoomName)
        
        self._directions = owner._directions

        # create the alias for user.
        self._alias = Alias(self, self._group, r'^rt\s(\S+)$', self._aliasFunction, name = 'runto')
        self._aliasMaze = Alias(self, self._group, r'^maze(?:\s(\S+))?$', self._aliasMazeFunction, name = 'maze')
    
    def _aliasFunction(self, sender, args):
        ''' rt 指令 '''
        to = args.wildcards[0]
        if to == 'map':
            self.mush.Info(self._mapxkx)
            self.mush.Info('\n')
        elif to == 'help':
            self.mush.Info(self._help)
            self.mush.Info('\n')
        elif to == 'stop':
            self.Stop()
        elif to == 'here':
            self.mush.Execute('where')  # call the alias 'where' in ModuleWhere
        else:
            self.AfterDone = None
            self.AfterFail = None

            self.Start(to = to)     
    
    def _aliasMazeFunction(self, sender, args):
        ''' 身陷迷宫时使用maze heizhao指令走出来，免记 '''
        cmd, maze = args.line, args.wildcards[0]
        if cmd == 'maze':
            self.mush.Info("当前支持迷宫路径：\n")
            for name in self._maze_list.keys():
                self.mush.Info("    {}\n".format(name))
                
        elif maze in self._maze_list.keys():
            self.mush.Execute(self._maze_list[maze])
        else:
            print('未知迷宫，请重新检查指令：')
    
    def _checkRoomName(self, sender, args):
        self._current_room_name = sender.roomname
    
    def _one_step_over(self, sender, args):
        if args.state == CommandState.Success:           
            if self.stepIndex < self.stepCount:
                step = self.stepList[self.stepIndex]
                self.stepIndex += 1                                  
                
                m = re.match(r'(\S+)\((.+)\)', step)
                if m:
                    if m[1] == 'walk_busy':
                        self._commands['walk'].Execute(m[2])
                    elif m[1] == 'walk_pause':
                        self._commands['pause'].Execute(m[2])
                    elif m[1] == 'walk_retry':
                        self._commands['walk'].Execute(m[2])    
                    elif m[1] == 'walk_wait':
                        self._commands['wait'].Wait(m[2])
                    elif m[1] == 'cross_river':
                        self._commands['river'].Execute(m[2])
                    else:
                        self.mush.Error("module [runto]：Don't recognize the command: {}".format(step))
                else: 
                    if step in self._directions:
                        self._commands['walk'].Execute(step)
                    else:
                        self._commands['noecho'].Execute(step)    
                     
            elif self.stepIndex == self.stepCount:
                self.mush.Execute('set brief 1')
                
                self.mush.world.EchoInput = True
                self._commands['wait'].Wait(.2)  # wait 0.2s for the server echo.
                self.stepIndex += 1
                
            elif self.stepIndex > self.stepCount:  # check destination
                for cmd in self._commands.values():
                    cmd.AfterDone = None

                if self.destination_name == self._triRoomName.roomname:
                    self.mush.Log('module [runto]：到达目的地：{}(ID: {})'.format(self.destination_name, self.destination_id))
                    self.mush.Execute('response gps ok')
                    self._doEvent('AfterDone')
                elif self._retry_times < 1:
                    # 新增加的重试，未测试是否存在问题
                    self._retry_times += 1
                    self.mush.Log('module [runto]：未到达目的地：{}，当前地点{}。准备再试一次'.format(self.destination_name, self._triRoomName.roomname))
                    self.owner.RunModule('randmove', afterDone=self._check_start_location)
                else:
                    self.mush.Error("module [runto]：didn't arrive the destination {}, actual {}, please fix it manually".format(self.destination_name, self._triRoomName.roomname))
                    self.mush.Execute('response gps fail')
                    self._doEvent('AfterFail')
    
    def _run_path(self, path):
        ''' 行走路径 实现 '''
        self.stepList = path.split(';')
        
        self.stepCount = len(self.stepList)
        self.stepIndex = 0
        
        self.mush.world.EchoInput = False
        self.mush.Execute('set brief 3')
                                
        # init the runto commands (AfterExecute) 
        for cmd in self._commands.values():
            cmd.AfterDone = self._one_step_over
        
        # start the first step.
        self._one_step_over(self._commands['walk'], CommandEventArgs(CommandState.Success, None))
     
    def _check_start_location(self, sender, args):
        #rooms = mod.dbrooms
        mudroom = args.result["mudroom"]
        rooms = args.result["dbrooms"]
        if len(rooms) == 1:
            self.source = rooms[0]
            self._run_from_start_to_destination(self.source, self.destination)
        else:
            self.mush.Log('module [runto]：不能确定当前所在位置，开始随机移动...')
            exit_list = mudroom.Exit.split(';')
            rand_dir = random.choice(exit_list)
            self.owner.RunModule('randmove', afterDone=self._check_start_location, start=rand_dir)
                
    def _run_from_start_to_destination(self, source, destination):
        strfmt = '找到从[{0}]到目的地[{1}]的路径：{2}，预计花费：{3}，搜索耗时{4:.2f}秒：'
        strfmt2 = '未找到从当前房间[{0}]到目的地[{1}]的路径，可能是数据库不完整'

        str_from = '{} {}(ID:{})'.format(source.city, source.name, source.id)

        if isinstance(destination, str):
            # dbpath = self._map.FindPath(source.id, destination)
            dbpath = self._map.FindPathOrigin(source.id, destination)
            str_to = '最近的{}: {} {}(ID: {})'.format(self._map.RoomTypeList[destination], dbpath.room.city, dbpath.room.name, dbpath.room.id)         
        elif isinstance(destination, list):
            ids = []
            for item in destination:
                ids.append(item.id)
                
            # dbpath = self._map.FindPath(source.id, ids)
            dbpath = self._map.FindPathOrigin(source.id, ids)
            str_to = '{} {}(ID: {})'.format(dbpath.room.city, dbpath.room.name, dbpath.room.id)
       
        if dbpath.result:
            path = dbpath.path
            # path = ';'.join(dbpath.path)
            # print(strfmt.format(str_from, str_to, path, self.mush.MoneyToString(dbpath.money), dbpath.interval))    
            self.mush.Log(strfmt.format(str_from, str_to, path, self.mush.MoneyToString(dbpath.money), dbpath.interval))    
            self.destination_name = dbpath.room.name
            self.destination_id = dbpath.room.id
            self._run_path(path)
        elif source.id in ids:
            self.mush.Log('module [runto]：你已经在目的地!')
            self.destination_id = source.id
            self._doEvent('AfterDone')
        else:
            self.mush.Log(strfmt2.format(str_from, str_to))    
            self._doEvent('AfterFail')
    
    def Start(self, **options):
        to = options.get('to')
        self._retry_times = 0
        
        if to in self._map.RoomTypeList.keys():
            self.destination = to
        elif to.isdigit():
            self.destination = self._map.FindRoomsById(to)
        elif to.isascii():
            self.destination = self._map.FindRoomsByAlias(to)
        else:
            self.destination = self._map.FindRoomsByCityName(to)

        if len(self.destination) >= 1:
            self.owner.RunModule('randmove', afterDone=self._check_start_location)
        else:
            self.mush.Error('module [runto]：未找到目的地:{}，请检查后重试'.format(to))
            self._doEvent('AfterFail')            
        
    def Stop(self, **options):
        for cmd in self._commands.values():
            cmd.AfterDone = None
        
        self.AfterDone = None
        self.AfterFail = None
        
        self.mush.Warning('module [runto]：abort manually!')
        self._doEvent('AfterStop')   
