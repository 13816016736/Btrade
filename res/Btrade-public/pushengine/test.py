from pushengine.tasks import task_excuse
import time

r = task_excuse.delay("11111")

print "Result:",r.get()