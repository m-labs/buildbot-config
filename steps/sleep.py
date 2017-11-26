from twisted.internet import reactor
from buildbot.process.buildstep import BuildStep
from buildbot.status.results import SUCCESS, EXCEPTION


class SleepStep(BuildStep):
    """A build step that does nothing for a predefined time."""
    parms = BuildStep.parms + ['delay']

    def __init__(self, delay, **kwargs):
        self.delay = delay
        BuildStep.__init__(self, **kwargs)

    def start(self):
        self.step_status.setText(["sleeping", "%g sec" % self.delay])
        reactor.callLater(self.delay, self.timeout)

    def timeout(self):
        self.step_status.setText(["slept", "%g sec" % self.delay])
        self.finished(SUCCESS)

    def interrupt(self, reason):
        BuildStep.interrupt(self, reason)
        self.finished(EXCEPTION)
