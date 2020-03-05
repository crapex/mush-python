# -*- coding:utf-8 -*-

from .mudCmd import MudCommand, TriggerDefinition

class CmdCrossRiver(MudCommand):
    '''
    过河/江步骤：
        1: ask shao gong about jiang/huanghe
            --> 有钱、没钱？
        2: yell boat (需重复/或省略)
        3: enter boat
        4: wait...
        5: arrived, out
    '''
    
    _triList = (
                 TriggerDefinition('rv_boat', r'^[> ]*一叶扁舟缓缓地驶了过来，艄公将一块踏脚板搭上堤岸，以便乘客|^[> ]*岸边一只渡船上的老艄公说道：正等着你', '_onBoat', 1),
                 TriggerDefinition('rv_wait', r'^[> ]*只听得江面上隐隐传来：“别急嘛，这儿正忙着呐……”$', '_onWait', 1),
                 TriggerDefinition('rv_arrived', r'^[> ]*艄公说“到啦，上岸吧”，随即把一块踏脚板搭上堤岸。$', '_onArrived', 1),
                 TriggerDefinition('rv_money', r'^[> ]*艄公一把拉住你，你还没付钱呢？$', '_onMoney', 1),
                 TriggerDefinition('rv_done', r'^[> ]*(\S*)\s*-\s*(?:\[(野外|城内|门派|0)\])?(?:\s*\[(存盘点|玩家储物柜)\])?$', '_onSuccess', 1),
               )               
        
    def _onBoat(self, sender, args):
        self._triggers['rv_boat'].Enabled = False
        self._triggers['rv_wait'].Enabled = False
        self._triggers['rv_arrived'].Enabled = True
        self.mush.SendNoEcho('halt')
        self.mush.SendNoEcho('enter')
        
    def _onWait(self, sender, args):
        self.mush.DoAfter(4, 'yell boat')
        
    def _onArrived(self, sender, args):
        self._triggers['rv_arrived'].Enabled = False
        self._triggers['rv_done'].Enabled = True
        self.mush.SendNoEcho('halt')
        self.mush.SendNoEcho('out')

    def _onMoney(self, sender, args):
        self.mush.Warning('You have not enough money to cross the river, please addvalue.')
        super()._onFail(sender, args)

    def _beforeExecute(self, **params):
        super()._beforeExecute(**params)
        
        self.Enable(False)
        self._triggers['rv_boat'].Enabled = True
        self._triggers['rv_wait'].Enabled = True

    def Execute(self, cmd, **params):    
        '''
        cmd = 'changjiang/huanghe'
        '''
        if (cmd == 'changjiang') or (cmd == '长江'):
            return super().Execute('ask shao gong about jiang', **params)
        elif (cmd == 'huanghe') or (cmd == '黄河'):
            return super().Execute('ask shao gong about huanghe', **params)
        else:
            raise Exception('The river can only be changjiang/huanghe!')       