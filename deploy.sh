#!/bin/sh -e

ssh lab.m-labs.hk '\
  cd /var/lib/buildbot/masters/artiq && \
  sudo -u buildbot git fetch && sudo -u buildbot git reset --hard origin/master && \
  sudo service buildmaster restart || \
  (tail -n50 twistd.log ; echo "Restart failed, see the reason above")'
