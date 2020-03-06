import sys
from importlib import reload

##world.Note(repr(sys.path))

if not r'D:\Programming\liclipse\mushclient' in sys.path:
    sys.path.append(r'D:\Programming\liclipse\mushclient')

import mushpy.player
reload(mushpy.player)

from mushpy.player import Player

myself = Player(world, ax, 'id', 'pass', 'name')

##world.Note('Hello mushpy! The Player has been created successfully!')