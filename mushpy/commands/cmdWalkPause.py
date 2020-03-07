# -*- coding:utf-8 -*-

from .mudCmd import MudCommand, TriggerDefinition

class CmdWalkPause(MudCommand):
    '''
    用于命令后需要等待一段时间（mud反馈到达信息）的命令，如path_pause(qu wuliang)
    '''
    _initTriList = (
        TriggerDefinition('pause_tiesuo', r'^[> ]*你终于来到了对面，心里的石头终于落地。$', '_onSuccess', 1),
        TriggerDefinition('pause_taohuasea', r'^[> ]*你沿着踏板走了上去。$', '_onSuccess', 1),
        TriggerDefinition('pause_murong', r'^[> ]*绿衣少女将小船系在树枝之上，你跨上岸去。$|^[> ]*小舟终于划到近岸，你从船上走了出来。$|^[> ]*不知过了多久，船终于靠岸了，你累得满头大汗。$', '_onSuccess', 1),
        #TriggerDefinition('pause_wuliang1', r'^崖间古松\s*-\s*$', '_onSuccess', 1),
        TriggerDefinition('pause_wuliang2', r'^[> ]*一条大瀑布如玉龙悬空，滚滚而下，倾入一座清澈异常的大湖之中.$', '_onSuccess', 1),
        TriggerDefinition('pause_wuliang3', r'^[> ]*你终于一步步的终于挨到了桥头.$', '_onSuccess', 1),
        TriggerDefinition('pause_wuliang4', r'^[> ]*突然你突然脚下踏了个空，向下一滑，身子登时堕下了去。$', '_onSuccess', 1),
        TriggerDefinition('pause_che', r'^[> ]*大车停稳了下来，你可以下车\(xia\)了。$', '_onCarArrived', 1),
        TriggerDefinition('pause_xiache', r'^[> ]*到达了目的地.+，你从马车上走了下来。$', '_onSuccess', 1),
        TriggerDefinition('pause_sld', r'^[> ]*你朝船夫挥了挥手便跨上岸去。$', '_onSuccess', 1),
        TriggerDefinition('pause_lxc', r'^[> ]*六名雪山弟子一齐转动机关，吊桥便又升了起来。', '_onSuccess', 1),
        )
    
    def _onCarArrived(self, sender, args):
        self.mush.Execute('xia')
        super()._onSuccess(sender, args)