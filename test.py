#!/usr/bin/python3
# -*- coding: utf-8 -*-

import signal
from flock import Flock
from lib.logger import err, info


def a(aa, bb, cc = 'acc'):
  print('Func_A:    AA: {0}  BB: {1}  CC:{2}'.format(aa, bb, cc))

def b(aa, bb, cc = 'bcc'):
  print('Func_B:    AA: {0}  BB: {1}  CC:{2}'.format(aa, bb, cc))
  return aa, bb, 'bcc'

def c(aa, bb, cc = 'ccc'):
  print('Func_C:    AA: {0}  BB: {1}  CC:{2}'.format(aa, bb, cc))
  return aa, bb, 'ccc'

def d():
  return 'Aa', 'Bb', 'Cc'

wa = Flock(target=a, delay=0)
wb = Flock(target=b, delay=0)
wc = Flock(target=c, delay=0)
wd = Flock(target=d, delay=0)

wd.pipe(wc).pipe(wb).pipe(wa)
wd.setDaemon().start()
wc.setDaemon().start()
wb.setDaemon().start()
wa.setDaemon().start()

# def test():
#   info('????????')

# Flock(target=test).start()

while True:
  pass
