from buildbot.process.buildstep import BuildStep
from buildbot.status.results import SUCCESS

class Sleep(BuildStep):
    """
    A build step that does nothing for a predefined time.
    """
    parms = BuildStep.parms + ['delay']

    delay = None # in seconds

    def start(self):
        self.step_status.setText(["sleeping", "%g sec" % self.delay])
        reactor.callLater(self.delay, self.finished, SUCCESS)

    def finished(self, results):
        self.step_status.setText(["slept", "%g sec" % self.delay])
        buildstep.BuildStep.finished(self, results)
