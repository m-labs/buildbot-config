import re
from buildbot.steps.shell import ShellCommand

class CoverallsCommand(ShellCommand):
    command = ['coveralls']

    def createSummary(self, log):
        match = re.search(r"^https://coveralls.io/(.+)$", log.getText(), re.MULTILINE)
        if match:
            self.addURL("coverage", match.group())
