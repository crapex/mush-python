# -*- coding:utf-8 -*-

import re
import difflib
from .module import *

class ModuleMapMisc(Module): 
    _dir_reverse = {
        "w" : "e", "e" : "w", "s" : "n", "n" : "s", "u": "d", 
        "d" : "u", "enter" : "out", "out" : "enter",
        "se" : "nw", "nw" : "se", "sw" : "ne", "ne" : "sw",
        "su" : "nd", "nd" : "su", "sd" : "nu", "nu" : "sd",
        "wu" : "ed", "eu" : "wd", "ed" : "wu", "wd" : "eu",
        }
    def __init__(self, owner, modulename="mapmisc", **options):
        super().__init__(owner, modulename, **options)
        self._map = owner._map
        self._cmdRoom = owner.Commands["room"]
        self._triResponse = owner.Triggers["response"]
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^(namehere|update|mklink|mklink2|rmlink|extractlink|cache|log|show)(\s.+)?$', self._aliasFunction, name='mapmisc')
    
    def _aliasFunction(self, sender, args):
        cmd, param = args.wildcards[0], args.wildcards[1]
        
        if cmd == "show":
            m = re.match('\s*(\d+)', param)
            try:
                self._show_id = int(m[1])
                self._cmdRoom.AfterDone = self._showDifference
                self._cmdRoom.Execute()
            except ValueError:
                self.mush.Error("the correct command style: 'show id', the id shall be number")
        elif cmd == "update":
            m = re.match('\s*(\d+)', param)
            try:
                self._update_id = int(m[1])
                self._cmdRoom.AfterDone = self._updateDatabase
                self._cmdRoom.Execute()
            except ValueError:
                self.mush.Error("the correct command style: 'update id', the id shall be number")
        elif cmd == "extractlink":
            m = re.match('\s*(\d+)', param)
            try:
                linkid = int(m[1])
                self._extractLink(linkid)
            except ValueError:
                self.mush.Error("the correct command style: 'extractlink id', the id shall be number")
        elif cmd == "namehere":
            m = re.match('\s*(\S+)', param)
            self._room_alias = m[1]
            self._cmdRoom.AfterDone = self._nameCurrentRoom
            self._cmdRoom.Execute()
        elif cmd == "log":
            if param:
                cmd = "look" + param
            else:
                cmd = "look"
            self._cmdRoom.AfterDone = self._logNewRoom
            self._cmdRoom.Execute(cmd)
        elif cmd == "mklink":
            m = re.match("\s(\d+)\s(\d+)\s(.+)", param)
            linkid = self._map.AddNewLink(m[1], m[2], m[3])
            self.mush.Log('Add new link (ID: {}) from {} to {} with path "{}" ok!'.format(linkid, m[1], m[2], m[3]))
        elif cmd == "mklink2":
            m = re.match("\s(\d+)\s(\d+)\s(.+)", param)
            linkid = self._map.AddNewLink(m[1], m[2], m[3])
            self.mush.Log('Add new link (ID: {}) from {} to {} with path "{}" ok!'.format(linkid, m[1], m[2], m[3]))
            linkid = self._map.AddNewLink(m[2], m[1], self._dir_reverse[m[3]])
            self.mush.Log('Add new link (ID: {}) from {} to {} with path "{}" ok!'.format(linkid, m[2], m[1], self._dir_reverse[m[3]]))
        elif cmd == "rmlink":
            m = re.match('\s*(\d+)', param)
            try:
                linkid = int(m[1])
                self._map.DeleteLink(linkid)
                self.mush.Log('Link ID: {} has been deleted.'.format(linkid))
            except ValueError:
                self.mush.Error("the correct command style: 'rmlink id', the id shall be number")
        elif cmd == "cache":
            self._map.RebuildLinksCache()
            self.mush.Log("map db link cache rebuild finished.")
        else:
            pass
        
    def _size(self, text):
        len1 = len(text)
        len2 = len(text.encode('utf-8'))
        return (len2 - len1) // 2 + len1    
        
    def _showDifference(self, sender, args):
        self._cmdRoom.AfterDone = None
        if args.state == CommandState.Success:
            mudroom = args.result["room"]
            rooms = self._map.FindRoomsById(self._show_id)
            if len(rooms) == 1:
                room = rooms[0]
                self.mush.Note('DB: %d' % room.id)
                self.mush.Note('DB: %s' % room.name)
                self.mush.Note('HH: %s' % mudroom.Name)
                
                diff = difflib.Differ()
                d = list(diff.compare(room.description, mudroom.Description))
                
                self.mush.Tell('DB: ')
                for cmp in d:
                    key = cmp[:2]
                    val = cmp[2:]
                    if key == '  ':
                        self.mush.Tell(val)
                    elif key == '+ ':
                        self.mush.Tell(' ' * self._size(val))
                    elif key == '- ':
                        self.mush.ColourTell('red', 'wheat', val)
                self.mush.Tell('\n')
                
                self.mush.Tell('HH: ')
                for cmp in d:
                    key = cmp[:2]
                    val = cmp[2:]
                    if key == '  ':
                        self.mush.Tell(val)
                    elif key == '- ':
                        self.mush.Tell(' ' * self._size(val))
                    elif key == '+ ':
                        self.mush.ColourTell('red', 'wheat', val)        
                self.mush.Tell('\n')

                self.mush.Note('DB: %s' % room.exits)
                self.mush.Note('HH: %s' % mudroom.Exit)
            else:
                self.mush.Error('cannot find the room with id: ' + self._show_id)
                
    def _updateDatabase(self, sender, args):
        if args.state == CommandState.Success:
            # update the information of here
            self._map.UpdateRoom(self._update_id, args.result["room"])
            self.mush.Log('update room (ID: {}) ok!'.format(self._update_id))
            
    def _nameCurrentRoom(self, sender, args):
        if args.state == CommandState.Success:
            rooms = self._map.FindRoomsByRoom(args.result["room"])
            if len(rooms) == 1:
                self._map.SetRoomAlias(rooms[0].id, self._room_alias)
                self.mush.Log('当前地点: {} {}(ID: {}) 别名设置为: {}'.format(rooms[0].city, rooms[0].name, rooms[0].id, self._room_alias))
            else:
                self.mush.Error('不能确定当前位置，请检查后重试！')
                
    def _logNewRoom(self, sender, args):
        if args.state == CommandState.Success:
            roomid = self._map.AddNewRoom(args.result["room"])
            self.mush.Log('Log new room with id: {} ok!'.format(roomid))
     
    def _addTwoRoomLinks(self, from_id, to_id, path_from):
        linkid = self._map.AddNewLink(from_id, to_id, path_from)
        self.mush.Log('Add new link (ID: {}) from {} to {} with path "{}" ok!'.format(linkid, from_id, to_id, path_from))
        linkid = self._map.AddNewLink(to_id, from_id, self._dir_reverse[path_from])
        self.mush.Log('Add new link (ID: {}) from {} to {} with path "{}" ok!'.format(linkid, to_id, from_id, self._dir_reverse[path_from]))
            
    def _extractLink(self, linkid):
        # make sure the startid has been record in the database
        #    and the path end is not a room in database. 
        # please recheck the path is correct to ensure all the data log.
        #################### program flow...
        # 1. check start, and log as the from_id
        # 2. get one step (if any), run the step, and log the step as linkpath
        # 3. log the room, and get the id as the to_id
        # 4. makelink from from_id to to_id with path linkpath
        # 5. makelink from to_id to from_id with path reverse(linkpath)
        # 6. set to_id to from_id
        # 8. loop to step 2.
        linkinfo = self._map.GetLinkInfo(linkid)
        link_path = linkinfo.path.split(';')
        
        self._coro_extractlink = None
        
        def _asyncGetRoomInfo(sender, args):
            if args.state == CommandState.Success:
                self._coro_extractlink.send(args.result["room"])

        def _asyncResponseStep(sender, args):
            resp = args.get('link', None)
            if resp == "step":
                try:
                    self._coro_extractlink.send(None)
                except StopIteration:
                    self.mush.Log("Path Extract Done!")

        def _extract_link_coroutine():
            self.mush.Execute('set brief 3')
            
            _to_id = linkinfo.linkfrom 
            stepcnt = len(link_path) - 1
            for i in range(stepcnt):
                _step_path = link_path[i]
                _from_id = _to_id
                self.mush.Execute(_step_path)
                self.mush.Execute('response link step')
                yield
                self._cmdRoom.AfterDone = _asyncGetRoomInfo
                self._cmdRoom.Execute("look")
                mudroom = yield
                _to_id = self._map.AddNewRoom(mudroom)
                self.mush.Log('Log new room with id: {} ok!'.format(_to_id))
                self._addTwoRoomLinks(_from_id, _to_id, _step_path)

            # the last one, the destination is a dbroom
            self._cmdRoom.AfterDone = None
            
            _from_id = _to_id
            _to_id = linkinfo.linkto
            _step_path = link_path[-1]
            
            self.mush.Execute(_step_path)
            self.mush.Execute('response link step')
            yield
            
            self._triResponse.RemoveCallback(_asyncResponseStep)           
            self._addTwoRoomLinks(_from_id, _to_id, _step_path)
            
            self.mush.Log('Extract link id {} ({}) done!'.format(linkid, linkinfo.path))
            return
        
        self._triResponse.AddCallback(_asyncResponseStep)
        self._coro_extractlink = _extract_link_coroutine()
        self._coro_extractlink.send(None)

            
            
            