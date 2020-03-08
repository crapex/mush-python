# -*- coding:utf-8 -*-

from .job import Job, TriggerDefinition, CommandState

class JobMurong(Job):
    JOB_NAME = '慕容信件'
    
    _initTriList = (
        TriggerDefinition("reaskjob", r"^[> ]*仆人对着你摇了摇头说：「你刚做过任务，先去休息休息吧。」$", "_reaskjob", 1),
        TriggerDefinition("getjob", r"^[> ]*仆人叹道：家贼难防，有人偷走了少爷的信件，据传曾在『(.*)』附近出现，你去把它找回来吧！$", "_getjob", 1),
        TriggerDefinition("pubusy", r"^[> ]*仆人忙着呢，等会吧。", "_pubusy", 1),
        TriggerDefinition("jobdone", r"^[> ]*你给仆人一封信件。$", "_jobdone", 1),
        TriggerDefinition("nofight", r"^[> ]*这里(不准|禁止)战斗。$", "_nofight", 1),
        TriggerDefinition("npcdead", r"^[> ]*慕容世家(家贼|内鬼)死了。$", "_npcdead", 1),
        TriggerDefinition("npcweapon", r"^[> ]*慕容世家.*「唰」的丿声抽出一把.*握在手中。|^[> ]*一道青光闪过，慕容世家.*手中已多了把.", "_npcweapon", 1),
        TriggerDefinition("imbusy", r"^[> ]*你正忙着呢！", "_nofight", 1),
        TriggerDefinition("walktofast", r"^[> ]*这里没有 jiazei。", "_searchagain", 1),
        )
    
    def __init__(self, owner, name='mr', **options):
        super().__init__(owner, name, **options)

        self._npcname = '%s发现的\s*慕容世家(内鬼|家贼)' % self._playername
        self._npcid = "%s's murong jiazei" % self._playerid

    def _jobstart(self, sender, args):
        self.mush.Execute('exert recover')
        self.mush.Execute('ask pu about job')

    def _getjob(self, sender, args):
        wildcards = args.wildcards
        self.location = wildcards[0]
        self.mush.InfoClear()
        self.mush.info('开始寻找位于 {} 的慕容家贼'.format(self.location))
        self._searchnpc()
        
    def _searchnpc(self):
        self._triggers['npcdead'].Enabled = True
        self.owner.RunModule('searchnpc', afterDone=self._npcfound, afterFail=self._npc_notfound, to=self.location, npcname=self._npcname, npcid=self._npcid)
    
    def _searchagain(self, sender, args):
        self._triggers['npcdead'].Enabled = True
        self.owner.RunModule('searchnpc', afterDone=self._npcfound, afterFail=self._npc_notfound, npcname=self._npcname, npcid=self._npcid)        
    
    def _reaskjob(self, sender, args):
        self.mush.DoAfter(5, 'ask pu about job')
    
    def _npcweapon(self, sender, args):
        self.mush.Execute('pr jiazei')
        pass
    
    def _npcfound(self, sender, args):
        self.owner.StopModule("runto")
        self.owner.StopModule("searchnpc")
        self._triggers["imbusy"].Enabled = True
        self.mush.Execute('follow jiazei')
        self.mush.Execute('ka jiazei')
        
    def _npc_notfound(self, sender, args):
        self.mush.InfoClear()
        self.mush.info('未找到位于 {} 的慕容家贼'.format(self.location))
        self.owner.RunModule('runto', afterDone=self._jobfail, to="mrf")
    
    def _nofight(self, sender, args):
        self.mush.Execute('ask jiazei about fight')
        self.mush.DoAfter(1, 'killall jiazei')

    def _npcdead(self, sender, args):
        self._triggers['npcdead'].Enabled = False
        self._triggers["imbusy"].Enabled = False
        self.mush.Execute('get all from corpse')
        self._cmdWait.AfterDone = self._waitforidle
        self._cmdWait.Wait(2)
        self.mush.InfoClear()
        self.mush.info('位于 {} 的慕容家贼已被干掉'.format(self.location))
  
    def _waitforidle(self, sender, args):
        if args.state == CommandState.Success:
            self._cmdWait.AfterDone = None
            self.mush.Execute('get all from corpse')
            self.owner.RunModule('sellthings', afterDone=self._aftersellall)
    
    def _aftersellall(self, mod, args):
        self.owner.RunModule('savemoney', afterDone=self._aftersavemoney)
    
    def _aftersavemoney(self, mod, args):
        self.owner.RunModule('runto', afterDone=self._backtopu, to="mrf")
  
    def _backtopu(self, mod, args):
        self.mush.Execute('give pu letter')
  
    def _pubusy(self, sender, args):
        self.mush.DoAfter(1, 'give pu letter')
        
    def _jobdone(self, sender, args):
        self.success += 1
        self.total += 1
        self.mush.InfoClear()
        self.mush.info('【慕容信件】 共进行{}次，其中成功{}次，失败{}次。'.format(self.total, self.success, self.failure))
        self._cmdWait.AfterDone = self._waitjobdone
        self._cmdWait.Wait(2)
        
    def _waitjobdone(self, sender, args):
        if args.state == CommandState.Success:
            self._cmdWait.AfterDone = None
            self.owner.RunModule('food', afterDone=self._afterfood)          

    def _jobfail(self, mod, args):
        self._triggers['npcdead'].Enabled = False
        self.failure += 1
        self.total += 1
        self.mush.InfoClear()
        self.mush.info('【慕容信件】 共进行{}次，其中成功{}次，失败{}次。'.format(self.total, self.success, self.failure))
        self.mush.Execute('ask pu about fail')
        self.owner.RunModule('liaoshang', afterDone=self._afterheal)

    def _afterfood(self, mod, args):
        self.owner.RunModule('liaoshang', afterDone=self._afterheal)
        
    def _afterheal(self, mod, args):
        self.owner.RunModule('dazuoto', afterDone=self._jobstart)
                
    def _ali_job_command(self, sender, args):
        param = args.wildcards[0]
        if param == 'start':
            self._enabled = True
            for tri in self._triggers.values():
                tri.Enabled = True
            self._afterheal(None, None)
        elif param == 'stop':
            self._enabled = False
            for tri in self._triggers.values():
                tri.Enabled = False
            self.mush.Log('任务：【慕容信件】 已被手动停止')
        elif param == 'fail':    
            self.owner.RunModule('runto', afterDone = self._jobfail, to = "mrf")
        elif param == 'where':
            self.mush.Log('慕容家贼在以下位罿: {}'.format(self.location))
        elif param == 'done':
            self._waitforidle(None, None)
        elif param == 'stat':
            self.mush.Log('任务：【慕容信件】 完成情况统计：共进行{}次，其中成功{}次，失败{}次。'.format(self.total, self.success, self.failure))
        else:
            # 当慕容地点为图片时，需要这个来推进
            self.location = param
            self._searchnpc()