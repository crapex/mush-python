# -*- coding:utf-8  -*-

from time import time
from collections import namedtuple
from pathlib import Path
import pickle
import sqlite3

class Map:
    RoomTypeList = {'bank' : '钱庄', 'pawnshop' : '当铺', 'home' : '储物箱', 'pawn1' : '荣宝斋'}
    DBRoom = namedtuple('DBRoom', ['id', 'name', 'relation', 'description', 'exits', 'city', 'zone', 'alias', 'alias2', 'type'])
    DBRoomLink = namedtuple('DBRoomLink', ['linkfrom', 'linkto', 'path', 'time', 'money', 'city', 'name', 'roomtype']) 
    ResultType = namedtuple('ResultType', ['result', 'path', 'rooms', 'time', 'money', 'interval', 'room'])

    _linksCache = dict()
    
    def __init__(self, database):
        self._db = sqlite3.connect(database)
        
        #for _id in range(1, self.RoomsCount + 1):
        #    links = self.FindRoomLinks(_id)
        #    self._linksCache[_id] = links

        print('gps database cached done.')
    
    def __del__(self):
        self._db.close()
    
    def AddNewRoom(self, mudroom, city=None):
        cur = self._db.cursor()
        if city:
            sql = 'insert into rooms (RoomName, RoomRelation, RoomDescription, RoomExits, RoomCity) values ( ?, ?, ?, ?, ?)'
            cur.execute(sql, (mudroom.Name, mudroom.Relation, mudroom.Description, mudroom.Exit, city))
        else:
            sql = 'insert into rooms (RoomName, RoomRelation, RoomDescription, RoomExits) values (?, ?, ?, ?)'
            cur.execute(sql, (mudroom.Name, mudroom.Relation, mudroom.Description, mudroom.Exit))
        self._db.commit()
    
    def UpdateRoom(self, id, mudroom):
        sql = 'update rooms set RoomName = ?, RoomRelation = ?, RoomDescription = ?, RoomExits = ? where RoomID = ?'
        cur = self._db.cursor()
        cur.execute(sql, (mudroom.Name, mudroom.Relation, mudroom.Description, mudroom.Exit, id))
        self._db.commit()
    
    def SetRoomAlias(self, id, alias):
        sql = 'update rooms set RoomAlias = ? where RoomID = ?'
        cur = self._db.cursor()
        cur.execute(sql, (id, alias))
        self._db.commit()
        
    def AddNewLink(self, frm, to, path, time=1, money=0):
        cur = self._db.cursor()
        sql = 'insert into links (LinkFrom, LinkTo, LinkPath, TimeCost, MoneyCost) values (?,?,?,?,?)'
        cur.execute(sql, (frm, to, path, time, money))
        self._db.commit()
    
    def _RoomsByFilter(self, filter, *args):
        cur = self._db.cursor()
        sql = 'select * from rooms' + filter

        if len(args) == 0:
            cur.execute(sql)
        else:
            cur.execute(sql, args)
            
        rooms = list()
        for room in cur.fetchall():
            rooms.append(self.DBRoom(*room))

        cur.close()
        
        return rooms
        
    def FindRoomsByDesc(self, descriptions, exits):
        ''' find room used by task, locate '''
        
        _filter = ''
        for val in descriptions.split(','):
            if _filter != '':
                _filter += ' and '
            _filter += 'RoomDescription like "%{0}%"'.format(val)
            
        for val in exits.split(','):
            if _filter != '':
                _filter += ' and '
            _filter += 'RoomExits like "%{0}%"'.format(val)    

        if _filter != '':
            _filter = ' where ' + _filter
        
        #print(_filter)
        return self._RoomsByFilter(_filter)
        
    def FindRoomsById(self, id):
        return self._RoomsByFilter(' where RoomId = ?', id)
        
    def FindRoomsByCityName(self, city_name):
        return self._RoomsByFilter(' where RoomCity || RoomName = ?', city_name)
        
    def FindRoomsByAlias(self, alias):
        return self._RoomsByFilter(' where RoomAlias = ? or RoomAlias2 = ?', alias, alias)
      
    def FindRoomsByCity(self, city):
        ''' find city center room, hyd task need '''
        return self._RoomsByFilter(' where RoomCity = ? and RoomAlias is not null', city)
        
    def FindRoomsByName(self, name):
        ''' find by name only '''
        return self._RoomsByFilter(' where RoomName = ?', name)        
        
    def FindRoomsByRoom(self, mudroom):
        ''' find room by look sentence 
            exceptions:
                洛阳 泥人铺，每次名字不一栿
        '''
        if mudroom.Name.find('泥人') >= 0:
            rooms = self._RoomsByFilter(' where RoomDescription = ?', mudroom.Description)
        else:
            rooms = self._RoomsByFilter(' where RoomName = ? and RoomDescription = ?', mudroom.Name, mudroom.Description)
        
        # 当仅通过名称、描述查找的房间数不止1个时，继续匹配出口
        # 匹配出口时，mud中的出口为数据库中存储出口的子集，即认为已匹配
        # 其原因是，（1）对于door, gate等房间，close时的出口更少，（2）树洞下、武当广场等出口数量大于7会换行（貌似已被修复）
        # 暂且不进行进一步优化，待发现bug时再行处理
        # 已发现bug，暂时将比对调整为必须mud的Exits和db的Exits完全匹配 （2020-3-6）
        locate_room_exits_set = set(mudroom.Exit.split(';'))

        if len(rooms) > 1:                   
            j = 0
            for _ in range(len(rooms)):
                dbRoom_exits_set = set(rooms[j].exits.split(';'))
                # if not locate_room_exits_set.issubset(dbRoom_exits_set):
                if locate_room_exits_set != dbRoom_exits_set:
                    rooms.pop(j)
                else:
                    j += 1

        return rooms
    
    def FindRoomLinks(self, id):
        cur = self._db.cursor()
        cur.execute('select distinct a.LinkFrom, a.LinkTo, a.LinkPath, a.TimeCost, a.MoneyCost, b.RoomCity, b.RoomName, b.RoomType from links a, rooms b where b.RoomID = a.LinkTo and a.LinkFrom = ?', (id,))
        
        links = list()
        for link in cur.fetchall():
            links.append(self.DBRoomLink(*link))

        cur.close()
        
        return links       
    
    def FindRoomLinks1(self, id):
        return self._linksCache[id]
    
    def GetRoomCity(self, id):
        cur = self._db.cursor()
        cur.execute('select RoomCity from rooms where RoomID = ?', (id,))
        
        row = cur.fetchone()
        cur.close()
        
        return row[0]
    
    def GetRoomsLinked(self, id1, id2):
        path1 = self.GetRoomsPath(id1, id2)
        path2 = self.GetRoomsPath(id2, id1)
        return path1 and path2
    
    def GetRoomsPath(self, fromId, toId):
        cur = self._db.cursor()
        cur.execute('select LinkPath from links where LinkFrom = ? and LinkTo = ?', (fromId, toId))
        
        row = cur.fetchone()
        cur.close()
        
        path = None if not row else row[0]
        return path
    
    @property
    def RoomsCount(self):
        cur = self._db.cursor()
        cur.execute('select count(RoomID) from rooms')
        
        row = cur.fetchone()
        cur.close()
        
        return row[0]
    
    def GetRoomType(self, id):
        cur = self._db.cursor()
        cur.execute('select RoomType from rooms where RoomID = ?', (id,))
        
        row = cur.fetchone()
        cur.close()
        
        return row[0]
    
    def GetRoomInfo(self, id):
        cur = self._db.cursor()
        cur.execute('select * from rooms where RoomID = ?', (id,))
        
        row = cur.fetchone()
        cur.close()
        
        return self.DBRoom(*row)
    
    def FindPathOrigin(self, fromID, toIdOrType=None, toType=None, costType='time'):
        MAX_COST = 99999

        def nextNode(nodes):
            mincost, nodeid = MAX_COST, -1
            for id, node in nodes.items():
                if (not node.closed) and (getattr(node, costType) < mincost):
                    mincost = getattr(node, costType)
                    nodeid = id
            return nodes[nodeid]
                
        class room_dijk:

            def __init__(self):
                self.id = 0
                self.type = ''
                self.closed = False
                self.time = MAX_COST
                self.money = MAX_COST
                self.nodepath = ''
                self.nodelist = ''
                
        starttime = time()
        allnodes = dict()
        modeType = True if isinstance(toIdOrType, str) else False
        toIDs = () if modeType else toIdOrType
        
        searchNode = room_dijk()
        searchNode.id = fromID
        searchNode.type = self.GetRoomType(fromID)
        searchNode.money = 0
        searchNode.time = 0
        searchNode.nodelist = str(searchNode.id)
        searchNode.nodepath = ''
        allnodes[fromID] = searchNode
        
        for _ in range(self.RoomsCount):
            searchNode.closed = True

            links = self.FindRoomLinks1(searchNode.id)

            for link in links:
                if not link.linkto in allnodes:
                    node = room_dijk()
                    node.id = link.linkto
                    node.type = link.roomtype
                    allnodes[link.linkto] = node
                else:
                    node = allnodes[link.linkto]
                    
                if not node.closed:
                    if getattr(node, costType) > getattr(searchNode, costType) + getattr(link, costType):
                        node.time = searchNode.time + link.time
                        node.money = searchNode.money + link.money
                        
                        if searchNode.nodepath == '':
                            node.nodepath = '%s' % link.path
                        else:
                            node.nodepath = '%s;%s' % (searchNode.nodepath, link.path)
                        node.nodelist = '%s;%d' % (searchNode.nodelist, link.linkto)
                        
            if (modeType and (searchNode.type == toIdOrType)) or \
               ((not modeType) and (searchNode.id in toIDs)):
                    destroom = self.GetRoomInfo(searchNode.id)
                    dest = allnodes[searchNode.id]
                    break

            searchNode = nextNode(allnodes)      
        
        return self.ResultType(dest.nodepath != '', dest.nodepath, dest.nodelist, node.time, node.money, time() - starttime, destroom)

    def FindPath(self, fromID, toIdOrType=None, toType=None, costType='time'):
        MAX_COST = 99999

        def nextNode(nodes):
            mincost, nodeid = MAX_COST, -1
            for id, node in nodes.items():
                if (not node.closed) and (getattr(node, costType) < mincost):
                    mincost = getattr(node, costType)
                    nodeid = id
            return nodes[nodeid]
                
        class room_dijk:

            def __init__(self):
                self.id = 0
                self.type = ''
                self.closed = False
                self.time = MAX_COST
                self.money = MAX_COST
                # self.nodepath = ''
                # self.nodelist = ''
                self.nodepath = []
                self.nodelist = []
                
        starttime = time()
        allnodes = dict()
        modeType = True if isinstance(toIdOrType, str) else False
        toIDs = () if modeType else toIdOrType
        
        searchNode = room_dijk()
        searchNode.id = fromID
        searchNode.type = self.GetRoomType(fromID)
        searchNode.money = 0
        searchNode.time = 0
        searchNode.nodelist.append(str(searchNode.id))
        # searchNode.nodepath = ''
        searchNode.nodepath = []
        allnodes[fromID] = searchNode
        
        for _ in range(self.RoomsCount):
            searchNode.closed = True

            links = self.FindRoomLinks1(searchNode.id)

            for link in links:
                if not link.linkto in allnodes:
                    node = room_dijk()
                    node.id = link.linkto
                    node.type = link.roomtype
                    allnodes[link.linkto] = node
                else:
                    node = allnodes[link.linkto]
                    
                if not node.closed:
                    if getattr(node, costType) > getattr(searchNode, costType) + getattr(link, costType):
                        node.time = searchNode.time + link.time
                        node.money = searchNode.money + link.money
                        
                        # if searchNode.nodepath == '':
                        #    node.nodepath = '%s' % link.path
                        # else:
                        #    node.nodepath = '%s;%s' % (searchNode.nodepath, link.path)
                        # node.nodelist = '%s;%d' % (searchNode.nodelist, link.linkto)

                        node.nodepath.extend(searchNode.nodepath)
                        node.nodepath.append(link.path)
                        node.nodelist.extend(searchNode.nodelist)
                        node.nodelist.append(link.linkto)
                        
            if (modeType and (searchNode.type == toIdOrType)) or \
               ((not modeType) and (searchNode.id in toIDs)):
                    destroom = self.GetRoomInfo(searchNode.id)
                    dest = allnodes[searchNode.id]
                    break

            searchNode = nextNode(allnodes)      
        
        return self.ResultType(dest.nodepath != '', dest.nodepath, dest.nodelist, node.time, node.money, time() - starttime, destroom)
      
    def FindTraversal(self, start, wholecity=False, deep=5):

        class room_dfs:

            def __init__(self):
                self.id = 0
                self.parent = None
                self.visited = False
                self.closed = False
                self.deep = 0
                self.city = ''
        
        def traversalIterator(_visitRooms, _fromRoom, _path, _nodes, _city):
            _deep = _fromRoom.deep
            _fromRoom.visited = True
            
            # if _wholecity:
            if wholecity:
                if _fromRoom.city != _city:
                    _deep -= 1
            else:
                _deep -= 1
            
            if _deep > -1:
                # cannot pass "walk_pause" or "cross_river" path, and cannot pass moneycost path
                # cannot pass "ban stone", "swim river", etc
                _links = self.FindRoomLinks1(_fromRoom.id)
                for _link in _links:
                    if (_link.money > 0) or (_link.path.find('ban') >= 0) or (_link.path.find('swin') >= 0) \
                        or (_link.path.find('cai') >= 0) or (_link.path.find('jump') >= 0) or               \
                        (_link.path.find('walk_pause') >= 0) or (_link.path.find('cross_river') >= 0):
                        continue

                    # if the link-to room is not visited:
                    if not _link.linkto in _visitRooms:
                        nextRoom = room_dfs()
                        nextRoom.id = _link.linkto
                        nextRoom.parent = _fromRoom
                        nextRoom.visited = True
                        nextRoom.deep = _deep
                        nextRoom.city = self.GetRoomCity(nextRoom.id)
                        
                        _visitRooms[nextRoom.id] = nextRoom
                        if self.GetRoomsLinked(_fromRoom.id, nextRoom.id):
                            # _path = '{}{};'.format(_path, _link.path)
                            # _nodes = '{}{};'.format(_nodes, nextRoom.id)
                            _path.append(str(_link.path))
                            _nodes.append(nextRoom.id)
                        
                        # _path, _nodes = 
                        traversalIterator(_visitRooms, nextRoom, _path, _nodes, _city)
                        
            _fromRoom.closed = True
            if _fromRoom.parent:
                _tracebackpath = self.GetRoomsPath(_fromRoom.id, _fromRoom.parent.id)
                # _path = '{}{};'.format(_path, _tracebackpath)
                # _nodes = '{}{};'.format(_nodes, _fromRoom.parent.id)
                _path.append(str(_tracebackpath))
                _nodes.append(_fromRoom.parent.id)
                
                if wholecity:
                    if _fromRoom.parent.city != _city:
                        _deep += 1
                else:
                    _deep += 1
                
            # return (_path, _nodes)
            
        startTime = time()
        rooms = self.FindRoomsById(start)
        city = rooms[0].city
        visitedRooms = dict()
        fromRoom = room_dfs()
        fromRoom.id = start
        fromRoom.deep = deep
        fromRoom.visited = True
        fromRoom.city = self.GetRoomCity(start)
        visitedRooms[start] = fromRoom

        # path = 'look;'
        # nodes = '%d;' % start
        path = ['look']
        nodes = [start]
        
        # path, nodes = 
        traversalIterator(visitedRooms, fromRoom, path, nodes, city)
        
        return self.ResultType(path != 'look;', path, nodes, 0, 0, time() - startTime, None)

    def FindTraversalOrigin(self, start, wholecity=False, deep=5):

        class room_dfs:

            def __init__(self):
                self.id = 0
                self.parent = None
                self.visited = False
                self.closed = False
                self.deep = 0
                self.city = ''
        
        def traversalIterator(_visitRooms, _fromRoom, _path, _nodes, _city):
            _deep = _fromRoom.deep
            _fromRoom.visited = True
            
            # if _wholecity:
            if wholecity:
                if _fromRoom.city != _city:
                    _deep -= 1
            else:
                _deep -= 1
            
            if _deep > -1:
                # cannot pass "walk_pause" or "cross_river" path, and cannot pass moneycost path
                _links = self.FindRoomLinks1(_fromRoom.id)
                for _link in _links:
                    if (_link.money > 0) or (_link.path.find('walk_pause') >= 0) or (_link.path.find('cross_river') >= 0):
                        continue

                    # if the link-to room is not visited:
                    if not _link.linkto in _visitRooms:
                        nextRoom = room_dfs()
                        nextRoom.id = _link.linkto
                        nextRoom.parent = _fromRoom
                        nextRoom.visited = True
                        nextRoom.deep = _deep
                        nextRoom.city = self.GetRoomCity(nextRoom.id)
                        
                        _visitRooms[nextRoom.id] = nextRoom
                        if self.GetRoomsLinked(_fromRoom.id, nextRoom.id):
                            _path = '{}{};'.format(_path, _link.path)
                            _nodes = '{}{};'.format(_nodes, nextRoom.id)
                        
                        _path, _nodes = traversalIterator(_visitRooms, nextRoom, _path, _nodes, _city)
                        
            _fromRoom.closed = True
            if _fromRoom.parent:
                _tracebackpath = self.GetRoomsPath(_fromRoom.id, _fromRoom.parent.id)
                _path = '{}{};'.format(_path, _tracebackpath)
                _nodes = '{}{};'.format(_nodes, _fromRoom.parent.id)
                if wholecity:
                    if _fromRoom.parent.city != _city:
                        _deep += 1
                else:
                    _deep += 1
                
            return (_path, _nodes)
            
        startTime = time()
        rooms = self.FindRoomsById(start)
        city = rooms[0].city
        visitedRooms = dict()
        fromRoom = room_dfs()
        fromRoom.id = start
        fromRoom.deep = deep
        fromRoom.visited = True
        fromRoom.city = self.GetRoomCity(start)
        visitedRooms[start] = fromRoom

        path = 'look;'
        nodes = '%d;' % start
        
        path, nodes = traversalIterator(visitedRooms, fromRoom, path, nodes, city)
        
        return self.ResultType(path != 'look;', path, nodes, 0, 0, time() - startTime, None) 

