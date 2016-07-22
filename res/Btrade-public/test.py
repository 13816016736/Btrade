from pushengine.tasks import analysis_notify

r = analysis_notify.apply_async()

print "Result:",r.get()