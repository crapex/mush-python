# -*- coding:utf-8 -*-
from .mudCmd import MudCommand, TriggerDefinition

class CmdWalkDirection(MudCommand): 
    '''
    用于正常/重试行走的方向命令（正常行走：即该命令执行后会到下一个ROOM，会受到房间描述的命令）
    不仅仅包括n/w/e/s等等，如enter shudong，cai yanziwu等也可以使用
    
    '''
    _triList = (
                TriggerDefinition('dir_ok', r'^[> ]*(\S.*)\s*-\s*(?:\[(野外|城内|门派|0)\])?(?:\s*\[(存盘点|玩家储物柜)\])?$', '_onSuccess', 1),
                TriggerDefinition('dir_fail', r'^[> ]*这个方向没有出路。|^[> ]*你逃跑失败', '_onFail', 1),
                TriggerDefinition('dir_retry0', r'^[> ]*你的动作还没有完成，不能移动。$', '_onRetry', 1),
                TriggerDefinition('dir_retry1', r'^[> ]*你还在山中跋涉，一时半会恐怕走不出这(六盘山|藏边群山|西南地绵绵群山)！$', '_onRetry', 1),
                TriggerDefinition('dir_retry2', r'^[> ]*你小心翼翼往前挪动，遇到艰险难行处，只好放慢脚步。$', '_onRetry', 1),
                TriggerDefinition('dir_retry3', r'^[> ]*山路难行，你不小心给拌了一跤。$', '_onRetry', 1),
                TriggerDefinition('dir_retry4', r'^[> ]*青海湖畔美不胜收，你不由停下脚步，欣赏起了风景。$', '_onRetry', 1),
                TriggerDefinition('dir_retry5', r'^[> ]*(荒路|沙石地|沙漠中)几乎没有路了，你走不了那么快。$', '_onRetry', 1),
                TriggerDefinition('dir_retry6', r'^[> ]*你正要前行，有人大喝：黄河决堤啦，快跑啊！', '_onRetry', 1),
               )
               
    def _onRetry(self, sender, args):
        #self.ResetTimeout(1)                    # add 1 second for timeout
        self.mush.DoAfter(2, self._command)     # DoAfter, retry the direction after 2 second