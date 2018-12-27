from app import scheduler

def when_ready(server):
	server.log.info("Server is ready. Spawning workers")
	if scheduler.state == 1:
		scheduler.shutdown()
	scheduler.start()