import re
from buildbot.steps.shell import ShellCommand

class XilinxCommand(ShellCommand):
    ISE_RE    = r"\d+ constraint not met\."
    VIVADO_RE = r"WARNING: \[Route \d+-\d+\] Router estimated timing not met\."

    def timingNotMet(self):
        log = self.getLog('stdio')
        if re.search(ISE_RE, log.getText()) or re.search(VIVADO_RE, log.getText()):
            return True
        else:
            return False

    def evaluateCommand(self, cmd):
      # Always report failure if the command itself failed.
      if cmd.rc != 0:
        return FAILURE

      # Otherwise, report failure if timing is not met.
      if self.timingNotMet():
        return FAILURE

      return SUCCESS

    def describe(self, done=False):
        description = super(XilinxCommand, self).describe(done)
        if self.timingNotMet():
            description.append('timing not met')
        return description
