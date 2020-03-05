# -*- coding:utf-8 -*-

from .mudCmd import MudCommand

# 不判定返回信息的命令
class CmdNoEcho(MudCommand):
    '''
    用于不需要判断反馈信息的命令，如say、hire等等
    操作方式：执行命令后，直接向生成器发送Success视作完成
    '''
    def Execute(self, cmd, **params):
        super().Execute(cmd, **params)
        self._onSuccess(self, None)