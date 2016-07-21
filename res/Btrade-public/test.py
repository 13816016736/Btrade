from pushengine.tasks import analysis_record
import time

r = analysis_record.apply_async()

print "Result:",r.get()