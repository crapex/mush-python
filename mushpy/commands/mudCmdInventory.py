# -*- coding:utf-8 -*-


from .mudCmd import MudCommand, TriggerDefinition

# i2
class ItemDescription:
    def __init__(self, _id, name, count):
        self.id = _id
        self.name = name
        self.count = count
        
    def __repr__(self):
        return 'ItemDescription({}, {}, {})'.format(self.id, self.name, self.count)


class CmdInventory(MudCommand):
    _triList = (TriggerDefinition('iv_item', r'^(?:(\S+)(?:柄|把|盆|只|个|块|文|两))?(\S+)\((.*)\)$', '_onItemCapture', 1),
                # TriggerDefinition('iv_item', r'^(\S+)\((.*)\)$', '_onItemCapture', 1),
                TriggerDefinition('iv_right', r'你右手拿着：(.*)\((.*)\)', '_onWeaponCapture', 1),
                TriggerDefinition('iv_done', r'你身上穿着：|你正光着个身子呀！你身上什么也没穿！', '_onSuccess', 1),
                )
    
    _foodList = ('doufu', 'gan liang', 'mala doufu', 'liuli qiezi', 'shanhu baicai')
    _waterList = ('jiudai', 'qingshui hulu', 'hulu',)
    _trashList = ('shi tan', 'yun tie', 'huo tong', 'xuan bing', 'qingfeng sword')
    _sellList = ('changjian', 'duanjian', 'chang jian', 'armor', 'blade', 'xiao lingdang', 'fangtian ji', 'jun fu', 'junfu', 'changqiang', 'chang qiang')
    _sellDesc = ('长剑', '短剑', '铁甲', '钢刀', '小铃铛', '方天画戟', '军服', '长枪')

    def __init__(self, group, **params):
        super().__init__(group, **params)
        self._initVariables()
    
    def _initVariables(self):
        self.items = {}
        self.food = []
        self.water = []
        self.trash = []
        self.sells = []
        
        self.cash = 0
        self.gold = 0
        self.silver = 0
        self.coin = 0
    
    def _onItemCapture(self, sender, args):
        wildcards = args.wildcards
        item_cnt_ch = wildcards[0]
        item_id = wildcards[2].lower()
        item_desc = wildcards[1]
        if item_cnt_ch:
            item_cnt = self.mush.Word2Number(item_cnt_ch)
        else:
            item_cnt = 1
        
        item = ItemDescription(item_id, item_desc, item_cnt)
        # print(item_id, item_desc, item_cnt)
        # print(item)
        
        self.items[item_id] = item
        
        if item_id == 'thousand-cash':
            self.cash = item_cnt
        elif item_id == 'gold':
            self.gold = item_cnt
        elif item_id == 'silver':
            self.silver = item_cnt
        elif item_id == 'coin':
            self.coin = item_cnt
        elif item_id in self._foodList:
            self.food.append(item)
        elif item_id in self._waterList:
            self.water.append(item)
        elif item_id in self._trashList:
            # self.mush.Execute('drop {} {}'.format(item_cnt, item_id))
            self.mush.Execute('drop {}'.format(item_id))
        elif item_id in self._sellList:
            if item_desc in self._sellDesc:  # 防止ID相同的东西被判定，如Armor
                self.sells.append(item)

    def _onWeaponCapture(self, sender, args):
        wildcards = args.wildcards
        self.weapon_name = wildcards[0]
        self.weapon_id = wildcards[1]

    @property
    def totalMoney(self):
        # return self.cash * 10 + self.gold + self.silver / 100.0 + self.coin / 10000.0
        return (self.cash * 10 + self.gold) * 100 + self.silver + self.coin / 100.0
        # return '{}两黄金{}两白银{}文铜板'.format(self.cash * 10 + self.gold, self.silver, self.coin)
    
    def _beforeExecute(self, **params):
        self._initVariables()
        super()._beforeExecute(**params)

    def Execute(self, cmd='i2', **params):
        super().Execute(cmd, **params)