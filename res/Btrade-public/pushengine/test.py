from pushengine.tasks import analysis_record
import time

r = analysis_record.apply_async(args=[""])

print "Result:",r.get()