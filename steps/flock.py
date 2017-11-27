import os
import errno
import fcntl
from twisted.internet import reactor
from buildbot.process.buildstep import BuildStep
from buildbot.status.results import SUCCESS, FAILURE, SKIPPED


class FlockStep(BuildStep):
    """A build step that acquires an exclusive advisory lock on a file."""
    parms = BuildStep.parms + ['filename', 'fdProp']

    def __init__(self, filename, fdProp='flock_fd', **kwargs):
        self.filename = filename
        self.fdProp = fdProp
        BuildStep.__init__(self, **kwargs)

    def start(self):
        self.step_status.setText(['locking', self.filename])

        self.fd = os.open(self.filename, os.O_RDONLY)
        if self.fd == 0:
            self.addCompleteLog('summary', "Cannot open file '{}'"
                                    .format(self.filename))
            self.finished(FAILURE)
        elif self.build.hasProperty(self.fdProp) and self.build.getProperty(self.fdProp):
            self.addCompleteLog('summary', "Property '{}' is already set"
                                    .format(self.fdProp))
            self.finished(FAILURE)
        else:
            self.tryLock()

    def tryLock(self):
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX|fcntl.LOCK_NB)

            self.build.setProperty(self.fdProp, self.fd, 'FlockStep')
            self.step_status.setText(['locked', self.filename])
            self.finished(SUCCESS)
        except IOError as e:
            if e.errno == errno.EACCES or e.errno == errno.EAGAIN:
                reactor.callLater(1, self.tryLock)
            else:
                raise


class FunlockStep(BuildStep):
    """A build step that releases an advisory lock on a file."""
    parms = BuildStep.parms + ['filename', 'fdProp']

    def __init__(self, filename, fdProp='flock_fd', **kwargs):
        self.filename = filename
        self.fdProp = fdProp
        BuildStep.__init__(self, alwaysRun=True, **kwargs)

    def start(self):
        if self.build.hasProperty(self.fdProp) and self.build.getProperty(self.fdProp):
            self.fd = self.build.getProperty(self.fdProp)
            os.close(self.fd)

            self.step_status.setText(['unlocked', self.filename])
            self.finished(SUCCESS)
        else:
            self.step_status.setText(['skipped', 'unlock', self.filename])
            self.finished(SKIPPED)

