import sys
from importlib import reload

_MODULE_PATH_ = r'D:\Programming\liclipse\mushclient'

if not _MODULE_PATH_ in sys.path:
    sys.path.append(_MODULE_PATH_)

import mushpy.player
reload(mushpy.player)

from mushpy.player import Player

myself = Player(world, ax)

myself.mush.Info('All modules have been loaded!')



#
#您上次是在Thu Mar  5 22:15:29 2020从101.88.117.218连线进入，请及时核对。
#如果与您实际经历不符，请立刻修改密码。

#目前权限：(player)

#重新连线完毕。