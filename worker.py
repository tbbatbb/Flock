#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, threading, gc, time
from queue import Queue, Full, Empty
from lib.logger import err, info

class Worker(threading.Thread):
  def __init__(self, target = None, task_queue = None, result_queue = None,
        delay = 0, exit_on_empty_task = False, exception_handler = None):
    '''
    Initialize A Worker

    @param target:
      Target Function To Be Execute
    '''
    # Check the parameters
    if (task_queue
        and not isinstance(task_queue, Queue)
        and not isinstance(task_queue, list)):
      err('Task Queue Should Be An Instance Of Queue Or Array.')
      return
    threading.Thread.__init__(self)
    # If the task_queue is an instance of queue
    if (task_queue and isinstance(task_queue, list)):
      # Initialize a new queue
      self.task_queue = Queue()
      for task in task_queue:
        # Put all the tasks in the task queue
        try:
          self.task_queue.put(task, block=False)
        except Full:
          # Output error message
          err('Task Queue Is Currently Full.')
          continue
    else:
      self.task_queue = task_queue
    self.result_queue = result_queue
    self.delay = delay
    self.running = True
    self.target = target
    self.exit_on_empty_task_queue = exit_on_empty_task
    self.exception_handler = exception_handler

  def run(self):
    '''
    Execute The Target Function
    '''
    if not self.target:
      err('Target Not Set')
      return
    if not isinstance(self.task_queue, Queue):
      while self.running:
        try:
          result = self.target()
          if (self.result_queue and isinstance(self.result_queue, Queue)):
            try:
              self.result_queue.put(result, block = True)
            except Full:
              err('Failed To Put Result Due To Full Result Queue')
          time.sleep(self.delay)
        except Exception as e:
          if self.exception_handler:
            self.exception_handler(e)
          else:
            err(e)
    else:
      while self.running:
        try:
          param = self.task_queue.get(block = False)
          result = self.target(*param)
          self.task_queue.task_done()
          if (self.result_queue and isinstance(self.result_queue, Queue)):
            try:
              self.result_queue.put(result, block = True)
            except Full:
              err('Failed To Put Result Due To Full Result Queue')
          time.sleep(self.delay)
        except Empty:
          if self.exit_on_empty_task_queue:
            break
        except Exception as e:
          if self.exception_handler:
            self.exception_handler(e)
          else:
            err(e)
    # When Finish
    info('Worker Exiting...')

  def stop(self):
    '''
    Stop The Worker
    '''
    self.running = False
    return self
  
  def pipe(self, next_worker, reuse_result_queue = True):
    '''
    Pipe Result To Next Worker

    @param next_worker
      Next One Who Receive The Output Of Self As Input
    @param reuse_result_queue
      Reuse Result Task Queue Of Self / Task Queue Of Next Worker
    '''
    if not (next_worker and isinstance(next_worker, Worker)):
      err('Can Only Pipe To Another Worker')
      return self
    if reuse_result_queue:
      if self.result_queue and isinstance(self.result_queue, Queue):
        next_worker.task_queue = self.result_queue
      elif next_worker.task_queue and isinstance(next_worker.task_queue, Queue):
        self.result_queue = next_worker.task_queue
      else:
        self.result_queue = next_worker.task_queue = Queue()
    else:
      if next_worker.task_queue and isinstance(next_worker.task_queue, Queue):
        self.result_queue = next_worker.task_queue
      if self.result_queue and isinstance(self.result_queue, Queue):
        next_worker.task_queue = self.result_queue
      else:
        self.result_queue = next_worker.task_queue = Queue()
    return next_worker
