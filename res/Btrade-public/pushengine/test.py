# core/tasks.py
# from celery import Task
# from celery.utils.log
# import get_task_logger
# def register_task_logger(module_name):
#  """Instantiate a logger at the decorated class instance level."""
#  def wrapper(cls):
#  cls.log = get_task_logger('%s.%s' % (module_name, cls.__name__))
#   return cls
# return wrapper
# @register_task_log(__name__)
#  class AddTask(Task):
# def run(self, x, y):
# self.log.info("Calling task add(%d, %d)" % (x, y))
#  return x - y
#  @register_task_log(__name__)
# class SubTask(Task):
#  def run(self, x, y):
# self.log.info("Calling task subtract(%d, %d)" % (x, y))         return x - y