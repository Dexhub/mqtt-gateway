# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2019-07-29
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================

# Systemd Service Notifications - https://github.com/bb4242/sdnotify
import sys
from email.utils import localtime
from time import strftime

import sdnotify
from unidecode import unidecode

sd_notifier = sdnotify.SystemdNotifier()


# Logging function
def print_line(text, error=False, warning=False, sd_notify=False, console=True):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:
        if error:
            print('[{}] '.format(timestamp) + '{}'.format(text), file=sys.stderr)
        elif warning:
            print('[{}] '.format(timestamp) + '{}'.format(text))
        else:
            print('[{}] '.format(timestamp) + '{}'.format(text))
    timestamp_sd = strftime('%b %d %H:%M:%S', localtime())
    if sd_notify:
        sd_notifier.notify('STATUS={} - {}.'.format(timestamp_sd, unidecode(text)))
