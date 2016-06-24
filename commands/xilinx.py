import re
from buildbot.status.results import FAILURE, SUCCESS
from buildbot.process.buildstep import LogLineObserver
from buildbot.steps.shell import ShellCommand

class XilinxLogObserver(LogLineObserver):
    ISE_RE    = re.compile(r"\d+ constraint not met\.")
    VIVADO_RE = re.compile(r"WARNING: \[Route \d+-\d+\] Router estimated timing not met\.")

    def __init__(self, maxLogs=None):
        LogLineObserver.__init__(self)
        self.timingMet = True

    def outLineReceived(self, line):
        if re.search(self.ISE_RE, line) or re.search(self.VIVADO_RE, line):
            self.timingMet = False

class XilinxCommand(ShellCommand):
    def __init__(self, *args, **kwargs):
        super(XilinxCommand, self).__init__(*args, **kwargs)
        self.logObserver = XilinxLogObserver()
        self.addLogObserver('stdio', self.logObserver)

    def evaluateCommand(self, cmd):
        # Always report failure if the command itself failed.
        if cmd.rc != 0:
            return FAILURE

        # Otherwise, report failure if timing is not met.
        if not self.logObserver.timingMet:
            return FAILURE

        return SUCCESS

    def describe(self, done=False):
        description = super(XilinxCommand, self).describe(done)
        if not self.logObserver.timingMet:
            description.append('timing not met')
        return description
