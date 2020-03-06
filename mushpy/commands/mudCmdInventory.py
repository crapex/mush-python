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

    def __init__(self, owner, group, **params):
        super().__init__(owner, group, **params)
        self._initVariables()
    
    def _initVariables(self):
        self._result["items"] = {}
        self._result["food"] = []
        self._result["water"] = []
        self._result["trash"] = []
        self._result["sells"] = []
        
        self._result["cash"] = 0
        self._result["gold"] = 0
        self._result["silver"] = 0
        self._result["coin"] = 0
    
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
        
        self._result["items"][item_id] = item
        
        if item_id == 'thousand-cash':
            self._result["cash"] = item_cnt
        elif item_id == 'gold':
            self._result["gold"] = item_cnt
        elif item_id == 'silver':
            self._result["silver"] = item_cnt
        elif item_id == 'coin':
            self._result["coin"] = item_cnt
        elif item_id in self._foodList:
            self._result["food"].append(item)
        elif item_id in self._waterList:
            self._result["water"].append(item)
        elif item_id in self._trashList:
            self.mush.Execute('drop {}'.format(item_id))
        elif item_id in self._sellList:
            if item_desc in self._sellDesc:  # 防止ID相同的东西被判定，如Armor
                self._result["sells"].append(item)

    def _onWeaponCapture(self, sender, args):
        wildcards = args.wildcards
        self._result["weapon_name"] = wildcards[0]
        self._result["weapon_id"] = wildcards[1]

    @property
    def totalMoney(self):
        return (self._value["cash"] * 10 + self._value["gold"]) * 100 + self._value["silver"] + self._value["coin"] / 100.0
    
    def _beforeExecute(self, **params):
        self._initVariables()
        super()._beforeExecute(**params)

    def Execute(self, cmd='i2', **params):
        super().Execute(cmd, **params)