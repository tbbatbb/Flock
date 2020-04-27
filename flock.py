#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, threading, gc, time
from queue import Queue, Full, Empty
from lib.logger import err, info
from worker import Worker

class Flock():
  def __init__(self, target = None, task_queue = None, result_queue = None,
        delay = 0, worker_count = 10, exit_on_empty_task = False, exception_handler = None,
        keyboard_interrupt_handler = None):
    '''
    Initialize A Flock Of Worker

    @param target:
      Target Function To Executed
    @param task_queue:
      Task Queue
    '''
    self.workers = []
    for i in range(worker_count):
      self.workers.append(
        Worker(target=target, task_queue=task_queue, result_queue=result_queue, delay=delay,
              exit_on_empty_task=exit_on_empty_task, exception_handler=exception_handler)
      )
    self.task_queue = task_queue
    self.result_queue = result_queue
  
  def start(self):
    for worker in self.workers:
      worker.start()
    return self
  
  def setDaemon(self, daemonic = True):
    for worker in self.workers:
      worker.setDaemon(daemonic)
    return self
  
  def stop(self):
    for worker in self.workers:
      worker.stop()
    return self
  
  def pipe(self, next_flock, reuse_result_queue = True):
    '''
    Pipe Result To Next Flock

    @param next_flock
      Next One Who Receive The Output Of Self As Input
    @param reuse_result_queue
      Reuse Result Task Queue Of Self / Task Queue Of Next Flock
    '''
    if not (next_flock and isinstance(next_flock, Flock)):
      err('Can Only Pipe To Another Flock')
      return self
    if reuse_result_queue:
      if self.result_queue and isinstance(self.result_queue, Queue):
        next_flock.task_queue = self.result_queue
      elif next_flock.task_queue and isinstance(next_flock.task_queue, Queue):
        self.result_queue = next_flock.task_queue
      else:
        self.result_queue = next_flock.task_queue = Queue()
    else:
      if next_flock.task_queue and isinstance(next_flock.task_queue, Queue):
        self.result_queue = next_flock.task_queue
      if self.result_queue and isinstance(self.result_queue, Queue):
        next_flock.task_queue = self.result_queue
      else:
        self.result_queue = next_flock.task_queue = Queue()
    for worker in self.workers:
      worker.result_queue = self.result_queue
    for worker in next_flock.workers:
      worker.task_queue = next_flock.task_queue
    return next_flock